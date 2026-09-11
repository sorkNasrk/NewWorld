param(
    [switch]$RequireUnrealRunning,
    [switch]$CheckCodexCli
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    $failures.Add($Message) | Out-Null
}

function Require-Path {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        Add-Failure "Missing path: $Path"
    }
}

function Test-TcpPort {
    param(
        [string]$HostName,
        [int]$Port,
        [int]$TimeoutMs = 1000
    )

    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect($HostName, $Port, $null, $null)
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

$requiredPaths = @(
    ".codex\config.toml",
    "Config\DefaultEditorPerProjectUserSettings.ini",
    "Config\DefaultGameplayTags.ini",
    "NewWorld.uproject"
)

foreach ($path in $requiredPaths) {
    Require-Path $path
}

try {
    $uproject = Get-Content -LiteralPath "NewWorld.uproject" -Raw | ConvertFrom-Json
    $enabledPlugins = @($uproject.Plugins | Where-Object { $_.Enabled } | ForEach-Object { $_.Name })
    $requiredPlugins = @(
        "ModelContextProtocol",
        "MCPClientToolset",
        "EditorToolset",
        "GameplayTagsToolset",
        "UMGToolSet",
        "NiagaraToolsets",
        "PCGToolset",
        "AIModuleToolset",
        "AutomationTestToolset",
        "SlateInspectorToolset"
    )
    foreach ($plugin in $requiredPlugins) {
        if ($enabledPlugins -notcontains $plugin) {
            Add-Failure "Required MCP plugin is not enabled: $plugin"
        }
    }
    foreach ($plugin in @("AllToolsets", "AIAssistant")) {
        if ($enabledPlugins -contains $plugin) {
            Add-Failure "Forbidden experimental plugin is enabled for this phase: $plugin"
        }
    }
} catch {
    Add-Failure "NewWorld.uproject JSON parse failed: $($_.Exception.Message)"
}

if (Test-Path -LiteralPath "Config\DefaultEditorPerProjectUserSettings.ini") {
    $editorSettings = Get-Content -LiteralPath "Config\DefaultEditorPerProjectUserSettings.ini" -Raw
    if ($editorSettings -notmatch "\[/Script/ModelContextProtocolEngine\.ModelContextProtocolSettings\]") {
        Add-Failure "Missing ModelContextProtocol settings section."
    }
    if ($editorSettings -notmatch "ServerUrlPath=/mcp") {
        Add-Failure "MCP ServerUrlPath must be /mcp."
    }
    if ($editorSettings -notmatch "ServerPortNumber=8000") {
        Add-Failure "MCP ServerPortNumber must be 8000."
    }
    if ($editorSettings -match "bAutoStartServer\s*=\s*True") {
        Add-Failure "MCP bAutoStartServer must remain False."
    }
    if ($editorSettings -notmatch "bEnableToolSearch=True") {
        Add-Failure "MCP bEnableToolSearch must be True."
    }
}

if (Test-Path -LiteralPath ".codex\config.toml") {
    $codexConfig = Get-Content -LiteralPath ".codex\config.toml" -Raw
    if ($codexConfig -notmatch "\[mcp_servers\.unreal-mcp\]") {
        Add-Failure "Project Codex config missing unreal-mcp server."
    }
    if ($codexConfig -notmatch 'url\s*=\s*"http://127\.0\.0\.1:8000/mcp"') {
        Add-Failure "unreal-mcp URL must be http://127.0.0.1:8000/mcp."
    }
    if ($codexConfig -notmatch "\[mcp_servers\.blender\]") {
        Add-Failure "Project Codex config missing blender server."
    }
    if ($codexConfig -notmatch 'BLENDER_MCP_SAFE_MODE\s*=\s*"1"') {
        Add-Failure "Blender MCP safe mode must be enabled."
    }
    if ($codexConfig -match "0\.0\.0\.0") {
        Add-Failure "MCP config must not bind to 0.0.0.0."
    }
}

$uvxPath = "C:\Users\happyelements\.local\bin\uvx.exe"
$pythonPath = "C:\Users\happyelements\AppData\Local\Programs\Python\Python312\python.exe"
$blenderPath = "G:\blender-5.2.1-windows-x64\blender.exe"

foreach ($path in @($uvxPath, $pythonPath, $blenderPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Failure "Missing MCP runtime path: $path"
    }
}

if ($RequireUnrealRunning) {
    if (-not (Test-TcpPort -HostName "127.0.0.1" -Port 8000 -TimeoutMs 1500)) {
        Add-Failure "UE MCP server is not reachable on 127.0.0.1:8000."
    }
} else {
    $isRunning = Test-TcpPort -HostName "127.0.0.1" -Port 8000 -TimeoutMs 250
    Write-Host "unrealMcpPort8000Reachable=$isRunning"
}

if ($CheckCodexCli) {
    $codex = Get-Command codex -ErrorAction SilentlyContinue
    if (-not $codex) {
        Add-Failure "codex CLI is not available."
    } else {
        & codex -C $projectRoot mcp get blender | Out-Host
        if ($LASTEXITCODE -ne 0) {
            Add-Failure "codex could not read the blender MCP server configuration."
        }
    }
}

Write-Host "mcpConfig=.codex/config.toml"
Write-Host "unrealMcpUrl=http://127.0.0.1:8000/mcp"
Write-Host "blenderPath=$blenderPath"

if ($failures.Count -gt 0) {
    Write-Host "MCP readiness check failed:"
    foreach ($failure in $failures) {
        Write-Host "- $failure"
    }
    exit 1
}

Write-Host "MCP readiness check passed."
