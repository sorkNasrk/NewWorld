param(
    [int]$Port = 8000,
    [switch]$Visible
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$projectPath = Join-Path $projectRoot "NewWorld.uproject"
$unrealEditor = "G:\UnrealEngineInstalled\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"

if (-not (Test-Path -LiteralPath $projectPath)) {
    throw "Project file not found: $projectPath"
}
if (-not (Test-Path -LiteralPath $unrealEditor)) {
    throw "UnrealEditor.exe not found: $unrealEditor"
}

$arguments = @(
    $projectPath,
    "-ModelContextProtocolStartServer",
    "-ModelContextProtocolPort=$Port",
    "-log",
    "-nosplash"
)

$startInfo = @{
    FilePath = $unrealEditor
    ArgumentList = $arguments
    WorkingDirectory = $projectRoot
    PassThru = $true
}

if (-not $Visible) {
    $startInfo.WindowStyle = "Hidden"
}

$process = Start-Process @startInfo
Write-Host "Started Unreal Editor PID=$($process.Id)"
Write-Host "MCP URL: http://127.0.0.1:$Port/mcp"
Write-Host "Use Tools/MCP/check_mcp_readiness.ps1 -RequireUnrealRunning after the server finishes loading."
