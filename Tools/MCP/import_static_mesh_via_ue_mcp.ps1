param(
    [Parameter(Mandatory = $true)]
    [string]$SourceFile,

    [Parameter(Mandatory = $true)]
    [string]$FolderPath,

    [Parameter(Mandatory = $true)]
    [string]$AssetName,

    [int]$Port = 8000,

    [switch]$AllowOverwrite,

    [bool]$ImportMaterials = $false,

    [bool]$ImportTextures = $false,

    [bool]$CombineMeshes = $true,

    [string]$EvidenceDirectory,

    [switch]$AllowOutsideAIWork
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

$mcpPath = "/mcp"
$script:NextMcpRequestId = 1
$script:McpSessionId = $null

function Resolve-ProjectPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [switch]$MustExist
    )

    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) {
        $Path
    } else {
        Join-Path $projectRoot $Path
    }

    $fullPath = [System.IO.Path]::GetFullPath($candidate)
    if ($MustExist) {
        return (Resolve-Path -LiteralPath $fullPath).Path
    }
    return $fullPath
}

function ConvertTo-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path).TrimEnd([char[]]@('\', '/')).ToLowerInvariant()
}

function Test-PathUnderRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )

    $normalizedPath = ConvertTo-NormalizedPath $Path
    $normalizedRoot = ConvertTo-NormalizedPath $Root
    return $normalizedPath -eq $normalizedRoot -or $normalizedPath.StartsWith($normalizedRoot + "\")
}

function Test-TcpPort {
    param(
        [string]$HostName,
        [int]$TcpPort,
        [int]$TimeoutMs = 1500
    )

    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect($HostName, $TcpPort, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne($TimeoutMs, $false)) {
            return $false
        }
        $client.EndConnect($async)
        return $true
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

function Test-McpRawResponseComplete {
    param([Parameter(Mandatory = $true)][string]$RawResponse)

    $headerEnd = $RawResponse.IndexOf([string][char]13 + [string][char]10 + [string][char]13 + [string][char]10)
    if ($headerEnd -lt 0) {
        return $false
    }

    $headerText = $RawResponse.Substring(0, $headerEnd)
    $bodyText = $RawResponse.Substring($headerEnd + 4)

    if ($headerText -match "(?im)^HTTP/\S+\s+202\s+") {
        return $true
    }

    if ($headerText -match "(?im)^Content-Length:\s*(\d+)\s*$") {
        $expectedBytes = [int]$Matches[1]
        $actualBytes = [System.Text.Encoding]::UTF8.GetByteCount($bodyText)
        return $actualBytes -ge $expectedBytes
    }

    if ($bodyText -match "(?m)^data:\s*\{.*\}") {
        return $true
    }

    $trimmed = $bodyText.Trim()
    return $trimmed.StartsWith("{") -and $trimmed.EndsWith("}")
}

function ConvertFrom-McpRawHttpResponse {
    param([Parameter(Mandatory = $true)][string]$RawResponse)

    $separator = [string][char]13 + [string][char]10 + [string][char]13 + [string][char]10
    $headerEnd = $RawResponse.IndexOf($separator)
    if ($headerEnd -lt 0) {
        throw "MCP response did not contain HTTP headers."
    }

    $headerText = $RawResponse.Substring(0, $headerEnd)
    $bodyText = $RawResponse.Substring($headerEnd + 4)
    $headerLines = [regex]::Split($headerText, "\r\n")
    $statusLine = $headerLines[0]
    if ($statusLine -notmatch "^HTTP/\S+\s+(\d+)") {
        throw "Unable to parse MCP HTTP status line: $statusLine"
    }

    $headers = @{}
    if ($headerLines.Length -gt 1) {
        for ($i = 1; $i -lt $headerLines.Length; $i++) {
            $line = $headerLines[$i]
            $colon = $line.IndexOf(":")
            if ($colon -gt 0) {
                $key = $line.Substring(0, $colon).Trim().ToLowerInvariant()
                $value = $line.Substring($colon + 1).Trim()
                $headers[$key] = $value
            }
        }
    }

    [pscustomobject]@{
        StatusCode = [int]$Matches[1]
        Headers = $headers
        Body = $bodyText
        Raw = $RawResponse
    }
}

function ConvertFrom-McpBodyJson {
    param([Parameter(Mandatory = $true)]$Response)

    $body = [string]$Response.Body
    $trimmed = $body.Trim()
    if ($trimmed.Length -eq 0) {
        return $null
    }

    if ($trimmed.StartsWith("{")) {
        return $trimmed | ConvertFrom-Json
    }

    $dataLines = New-Object System.Collections.Generic.List[string]
    foreach ($line in ([regex]::Split($body, "\r?\n"))) {
        if ($line -match "^data:\s?(.*)$") {
            $data = $Matches[1].Trim()
            if ($data -and $data -ne "[DONE]") {
                $dataLines.Add($data) | Out-Null
            }
        }
    }

    for ($index = $dataLines.Count - 1; $index -ge 0; $index--) {
        $candidate = $dataLines[$index]
        if ($candidate.StartsWith("{")) {
            return $candidate | ConvertFrom-Json
        }
    }

    throw "MCP response body was not JSON or SSE data: $($body.Substring(0, [Math]::Min(200, $body.Length)))"
}

function Invoke-McpRawRequest {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        $Params = $null,
        [string]$SessionId = $null,
        [switch]$Notification,
        [int]$TimeoutMs = 60000
    )

    $body = [ordered]@{
        jsonrpc = "2.0"
        method = $Method
    }

    if (-not $Notification) {
        $body.id = $script:NextMcpRequestId
        $script:NextMcpRequestId++
    }

    if ($null -ne $Params) {
        $body.params = $Params
    }

    $json = $body | ConvertTo-Json -Depth 80 -Compress
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $client = New-Object System.Net.Sockets.TcpClient
    $connect = $client.BeginConnect("127.0.0.1", $Port, $null, $null)

    if (-not $connect.AsyncWaitHandle.WaitOne(3000, $false)) {
        $client.Close()
        throw "UE MCP server is not reachable on 127.0.0.1:$Port. Start it with Tools/MCP/start_ue_mcp_editor.ps1 -Port $Port."
    }

    try {
        $client.EndConnect($connect)
        $stream = $client.GetStream()
        $stream.ReadTimeout = 1000
        $stream.WriteTimeout = 5000

        $crlf = [string][char]13 + [string][char]10
        $headers = New-Object System.Collections.Generic.List[string]
        $headers.Add("POST $mcpPath HTTP/1.1") | Out-Null
        $headers.Add("Host: 127.0.0.1:$Port") | Out-Null
        $headers.Add("Content-Type: application/json") | Out-Null
        $headers.Add("Accept: application/json, text/event-stream") | Out-Null
        $headers.Add("Content-Length: $($bodyBytes.Length)") | Out-Null
        $headers.Add("Connection: close") | Out-Null
        if ($SessionId) {
            $headers.Add("Mcp-Session-Id: $SessionId") | Out-Null
        }
        $headers.Add("") | Out-Null
        $headers.Add("") | Out-Null

        $requestHead = [System.Text.Encoding]::ASCII.GetBytes(($headers -join $crlf))
        $stream.Write($requestHead, 0, $requestHead.Length)
        $stream.Write($bodyBytes, 0, $bodyBytes.Length)
        $stream.Flush()

        $memory = New-Object System.IO.MemoryStream
        $buffer = New-Object byte[] 8192
        $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMs)

        while ([DateTime]::UtcNow -lt $deadline) {
            try {
                $read = $stream.Read($buffer, 0, $buffer.Length)
                if ($read -le 0) {
                    break
                }
                $memory.Write($buffer, 0, $read)
            } catch [System.IO.IOException] {
                if ($memory.Length -eq 0) {
                    continue
                }
            }

            $rawSoFar = [System.Text.Encoding]::UTF8.GetString($memory.ToArray())
            if (Test-McpRawResponseComplete -RawResponse $rawSoFar) {
                break
            }
        }

        if ($memory.Length -eq 0) {
            throw "MCP request '$Method' produced no response before timeout."
        }

        $rawResponse = [System.Text.Encoding]::UTF8.GetString($memory.ToArray())
        $response = ConvertFrom-McpRawHttpResponse -RawResponse $rawResponse
        if ($response.StatusCode -ge 400) {
            throw "MCP request '$Method' failed with HTTP $($response.StatusCode): $($response.Body.Trim())"
        }
        return $response
    } finally {
        $client.Close()
    }
}

function Invoke-McpJsonRpc {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        $Params = $null,
        [string]$SessionId = $null,
        [switch]$Notification,
        [int]$TimeoutMs = 60000
    )

    $response = Invoke-McpRawRequest -Method $Method -Params $Params -SessionId $SessionId -Notification:$Notification -TimeoutMs $TimeoutMs
    $json = ConvertFrom-McpBodyJson -Response $response

    if ($null -ne $json -and $json.error) {
        $message = if ($json.error.message) { $json.error.message } else { ($json.error | ConvertTo-Json -Depth 20 -Compress) }
        throw "MCP JSON-RPC '$Method' failed: $message"
    }

    [pscustomobject]@{
        Http = $response
        Json = $json
    }
}

function Get-McpSession {
    $params = @{
        protocolVersion = "2025-11-25"
        capabilities = @{}
        clientInfo = @{
            name = "NewWorld.Tools.MCP.ImportStaticMesh"
            version = "1.0"
        }
    }

    $initialize = Invoke-McpJsonRpc -Method "initialize" -Params $params -TimeoutMs 15000
    $headers = $initialize.Http.Headers
    $sessionId = $headers["mcp-session-id"]
    if (-not $sessionId) {
        throw "MCP initialize succeeded but did not return Mcp-Session-Id."
    }

    Invoke-McpJsonRpc -Method "notifications/initialized" -SessionId $sessionId -Notification -TimeoutMs 5000 | Out-Null
    return $sessionId
}

function Close-McpSession {
    param([string]$SessionId)

    if (-not $SessionId) {
        return
    }

    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $connect = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne(1000, $false)) {
            return
        }
        $client.EndConnect($connect)
        $stream = $client.GetStream()
        $stream.WriteTimeout = 1000
        $crlf = [string][char]13 + [string][char]10
        $request = "DELETE $mcpPath HTTP/1.1" + $crlf + "Host: 127.0.0.1:$Port" + $crlf + "Mcp-Session-Id: $SessionId" + $crlf + "Connection: close" + $crlf + $crlf
        $bytes = [System.Text.Encoding]::ASCII.GetBytes($request)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()
    } catch {
    } finally {
        $client.Close()
    }
}

function Get-McpToolValue {
    param($ToolResult)

    if ($null -eq $ToolResult) {
        return $null
    }

    if ($ToolResult.PSObject.Properties.Name -contains "structuredContent" -and $null -ne $ToolResult.structuredContent) {
        if ($ToolResult.structuredContent.PSObject.Properties.Name -contains "returnValue") {
            return $ToolResult.structuredContent.returnValue
        }
        return $ToolResult.structuredContent
    }

    if ($ToolResult.content) {
        $texts = @($ToolResult.content | Where-Object { $_.type -eq "text" } | ForEach-Object { $_.text })
        if ($texts.Count -eq 1) {
            $text = [string]$texts[0]
            $trimmed = $text.Trim()
            if ($trimmed.Length -gt 0) {
                try {
                    $parsed = $trimmed | ConvertFrom-Json
                    if ($parsed.PSObject.Properties.Name -contains "returnValue") {
                        return $parsed.returnValue
                    }
                    return $parsed
                } catch {
                    return $text
                }
            }
            return $text
        }
        if ($texts.Count -gt 1) {
            return $texts
        }
    }

    return $ToolResult
}

function Get-McpToolText {
    param($ToolResult)

    if ($null -eq $ToolResult -or -not $ToolResult.content) {
        return ""
    }

    return (@($ToolResult.content | Where-Object { $_.type -eq "text" } | ForEach-Object { $_.text }) -join [Environment]::NewLine)
}

function Invoke-McpTool {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        $Arguments = @{},
        [int]$TimeoutMs = 60000
    )

    $params = @{
        name = $Name
        arguments = $Arguments
    }
    $response = Invoke-McpJsonRpc -Method "tools/call" -Params $params -SessionId $script:McpSessionId -TimeoutMs $TimeoutMs
    $result = $response.Json.result
    if ($result -and $result.isError) {
        $message = Get-McpToolText -ToolResult $result
        throw "MCP tool '$Name' failed: $message"
    }
    return $result
}

function Invoke-UeToolsetTool {
    param(
        [Parameter(Mandatory = $true)][string]$ToolsetName,
        [Parameter(Mandatory = $true)][string]$ToolName,
        $Arguments = @{},
        [int]$TimeoutMs = 60000
    )

    return Invoke-McpTool -Name "call_tool" -Arguments @{
        toolset_name = $ToolsetName
        tool_name = $ToolName
        arguments = $Arguments
    } -TimeoutMs $TimeoutMs
}

function ConvertTo-ContentFolderPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $normalized = $Path.Replace("\", "/").TrimEnd("/")
    if (-not $normalized.StartsWith("/Game/")) {
        throw "FolderPath must be a UE content-browser path such as /Game/NewWorld/AIWork/MCP_DryRun: $Path"
    }
    return $normalized
}

$sourceFullPath = Resolve-ProjectPath -Path $SourceFile -MustExist
$extension = [System.IO.Path]::GetExtension($sourceFullPath).ToLowerInvariant()
if ($extension -eq ".glb" -or $extension -eq ".gltf") {
    throw "StaticMeshTools.import_file rejected .glb in the 2026-09-11 NewWorld UE5.8 test; the current toolset path uses FbxFactory and observed supported source extensions are fbx and obj. Export or convert to .fbx or .obj before this MCP import path."
}
if ($extension -notin @(".fbx", ".obj")) {
    throw "SourceFile must be .fbx or .obj for StaticMeshTools.import_file: $sourceFullPath"
}

$contentFolderPath = ConvertTo-ContentFolderPath -Path $FolderPath
if (-not $AllowOutsideAIWork -and -not $contentFolderPath.StartsWith("/Game/NewWorld/AIWork")) {
    throw "FolderPath must stay under /Game/NewWorld/AIWork unless -AllowOutsideAIWork is set: $contentFolderPath"
}

if ($AssetName -notmatch "^SM_[A-Za-z0-9]+_[A-Za-z0-9]+_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)?$") {
    throw "AssetName must follow the NewWorld static mesh format SM_[Name]_[Descriptor]_[Variant]: $AssetName"
}

$assetPath = "$contentFolderPath/$AssetName"
$evidencePath = $null
if ($EvidenceDirectory) {
    $evidencePath = Resolve-ProjectPath -Path $EvidenceDirectory
    $evidenceRoot = Resolve-ProjectPath -Path "Docs\Planning\MCP_Evidence"
    if (-not (Test-PathUnderRoot -Path $evidencePath -Root $evidenceRoot)) {
        throw "EvidenceDirectory must stay under Docs\Planning\MCP_Evidence: $evidencePath"
    }
    if (-not (Test-Path -LiteralPath $evidencePath)) {
        New-Item -ItemType Directory -Force -Path $evidencePath | Out-Null
    }
}

if (-not (Test-TcpPort -HostName "127.0.0.1" -TcpPort $Port -TimeoutMs 1500)) {
    throw "UE MCP server is not reachable on 127.0.0.1:$Port. Start it with Tools/MCP/start_ue_mcp_editor.ps1 -Port $Port."
}

try {
    $script:McpSessionId = Get-McpSession

    $toolsListResponse = Invoke-McpJsonRpc -Method "tools/list" -SessionId $script:McpSessionId -TimeoutMs 15000
    $toolNames = @($toolsListResponse.Json.result.tools | ForEach-Object { $_.name })
    foreach ($requiredTool in @("list_toolsets", "describe_toolset", "call_tool")) {
        if ($toolNames -notcontains $requiredTool) {
            throw "UE MCP tool-search mode did not expose required meta tool: $requiredTool"
        }
    }

    $staticMeshDescriptionResult = Invoke-McpTool -Name "describe_toolset" -Arguments @{ toolset_name = "editor_toolset.toolsets.static_mesh.StaticMeshTools" } -TimeoutMs 15000
    $staticMeshDescriptionText = Get-McpToolText -ToolResult $staticMeshDescriptionResult
    if ($staticMeshDescriptionText -notmatch "import_file") {
        throw "StaticMeshTools description did not include import_file."
    }

    Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.asset.AssetTools" -ToolName "create_folder" -Arguments @{ path = $contentFolderPath } -TimeoutMs 30000 | Out-Null

    $existsBefore = [bool](Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.asset.AssetTools" -ToolName "exists" -Arguments @{ path = $assetPath } -TimeoutMs 15000))
    if ($existsBefore -and -not $AllowOverwrite) {
        throw "Target asset already exists: $assetPath. Re-run with -AllowOverwrite only for reviewed staging overwrites."
    }
    if ($existsBefore) {
        Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.asset.AssetTools" -ToolName "delete" -Arguments @{ path = $assetPath } -TimeoutMs 30000 | Out-Null
    }

    $imported = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.static_mesh.StaticMeshTools" -ToolName "import_file" -Arguments @{
        folder_path = $contentFolderPath
        asset_name = $AssetName
        source_file = $sourceFullPath
        import_materials = [bool]$ImportMaterials
        import_textures = [bool]$ImportTextures
        combine_meshes = [bool]$CombineMeshes
    } -TimeoutMs 120000)

    Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.asset.AssetTools" -ToolName "load_asset" -Arguments @{ asset_path = $assetPath } -TimeoutMs 30000 | Out-Null

    $metadata = @{
        "NewWorld.Workflow" = "UE_MCP_StaticMesh_Import"
        "NewWorld.Staging" = "AIWork"
        "NewWorld.MCP" = "true"
        "NewWorld.SourceFile" = $sourceFullPath
        "NewWorld.ImportedBy" = "Tools/MCP/import_static_mesh_via_ue_mcp.ps1"
        "NewWorld.ImportedAtUtc" = (Get-Date).ToUniversalTime().ToString("o")
    }
    Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.asset.AssetTools" -ToolName "update_metadata_tags" -Arguments @{
        asset_path = $assetPath
        set_tags = $metadata
    } -TimeoutMs 30000 | Out-Null

    $saveResult = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.asset.AssetTools" -ToolName "save_assets" -Arguments @{ asset_paths = @($assetPath) } -TimeoutMs 60000)

    $assetClass = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.asset.AssetTools" -ToolName "get_asset_class" -Arguments @{ asset_path = $assetPath } -TimeoutMs 15000)
    $meshRef = @{ refPath = "$assetPath.$AssetName" }
    $materialSlots = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.static_mesh.StaticMeshTools" -ToolName "get_material_slots" -Arguments @{ mesh = $meshRef } -TimeoutMs 15000)
    $bounds = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.static_mesh.StaticMeshTools" -ToolName "get_bounds" -Arguments @{ mesh = $meshRef } -TimeoutMs 15000)
    $triangleCount = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.static_mesh.StaticMeshTools" -ToolName "get_triangle_count" -Arguments @{ mesh = $meshRef; lod_index = 0 } -TimeoutMs 15000)
    $vertexCount = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.static_mesh.StaticMeshTools" -ToolName "get_vertex_count" -Arguments @{ mesh = $meshRef; lod_index = 0 } -TimeoutMs 15000)
    $lodCount = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.static_mesh.StaticMeshTools" -ToolName "get_lod_count" -Arguments @{ mesh = $meshRef } -TimeoutMs 15000)
    $naniteEnabled = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.static_mesh.StaticMeshTools" -ToolName "is_nanite_enabled" -Arguments @{ mesh = $meshRef } -TimeoutMs 15000)
    $metadataReadback = Get-McpToolValue -ToolResult (Invoke-UeToolsetTool -ToolsetName "editor_toolset.toolsets.asset.AssetTools" -ToolName "get_metadata_tags" -Arguments @{ asset_path = $assetPath } -TimeoutMs 15000)

    $thumbnailPath = $null
    if ($evidencePath) {
        $captureResult = Invoke-UeToolsetTool -ToolsetName "EditorToolset.EditorAppToolset" -ToolName "CaptureAssetImage" -Arguments @{ AssetPath = $assetPath } -TimeoutMs 60000
        $captureValue = Get-McpToolValue -ToolResult $captureResult
        $imageData = $null
        if ($captureValue -and ($captureValue.PSObject.Properties.Name -contains "data")) {
            $imageData = $captureValue.data
        } else {
            $imageContent = @($captureResult.content | Where-Object { $_.type -eq "image" } | Select-Object -First 1)
            if ($imageContent) {
                $imageData = $imageContent.data
            }
        }
        if (-not $imageData) {
            throw "CaptureAssetImage did not return image content for $assetPath."
        }
        $thumbnailPath = Join-Path $evidencePath ("{0}_ue_asset_thumbnail.png" -f $AssetName)
        [System.IO.File]::WriteAllBytes($thumbnailPath, [System.Convert]::FromBase64String($imageData))
    }

    $summary = [ordered]@{
        mcp_url = "http://127.0.0.1:$Port$mcpPath"
        source_file = $sourceFullPath
        folder_path = $contentFolderPath
        asset_name = $AssetName
        asset_path = $assetPath
        existed_before = $existsBefore
        allow_overwrite = [bool]$AllowOverwrite
        import_materials = [bool]$ImportMaterials
        import_textures = [bool]$ImportTextures
        combine_meshes = [bool]$CombineMeshes
        imported = $imported
        saved = $saveResult
        readback = [ordered]@{
            class = $assetClass
            material_slots = $materialSlots
            bounds = $bounds
            triangles_lod0 = $triangleCount
            vertices_lod0 = $vertexCount
            lod_count = $lodCount
            nanite_enabled = $naniteEnabled
            metadata = $metadataReadback
        }
        evidence_thumbnail = $thumbnailPath
    }

    $summary | ConvertTo-Json -Depth 40
} finally {
    Close-McpSession -SessionId $script:McpSessionId
}
