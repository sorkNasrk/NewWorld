param(
    [switch]$OpenBlender,
    [switch]$Visible
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$uvxPath = "C:\Users\happyelements\.local\bin\uvx.exe"
$pythonPath = "C:\Users\happyelements\AppData\Local\Programs\Python\Python312\python.exe"
$blenderPath = "G:\blender-5.2.1-windows-x64\blender.exe"

foreach ($path in @($uvxPath, $pythonPath, $blenderPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required Blender MCP path: $path"
    }
}

Write-Host "uvx=$uvxPath"
Write-Host "python=$pythonPath"
Write-Host "blender=$blenderPath"
Write-Host "Codex launches blender-mcp from .codex/config.toml with BLENDER_MCP_SAFE_MODE=1."
Write-Host "Use one Blender instance and one MCP client per asset task."

if ($OpenBlender) {
    $startInfo = @{
        FilePath = $blenderPath
        WorkingDirectory = $projectRoot
        PassThru = $true
    }
    if (-not $Visible) {
        $startInfo.WindowStyle = "Hidden"
    }
    $process = Start-Process @startInfo
    Write-Host "Started Blender PID=$($process.Id)"
}
