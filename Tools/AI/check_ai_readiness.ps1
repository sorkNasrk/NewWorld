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

$requiredPaths = @(
    "AGENTS.md",
    ".agents\ue-project-context.md",
    ".agents\skills-index.md",
    ".codex\agents",
    ".codex\skills\project",
    ".codex\skills\vendor\gamedev-skills",
    ".codex\skills\vendor\quodsoler-unreal-engine-skills",
    "Docs\AI_Codex_UE58_GameDev_Guide.md",
    "Docs\Assets\AI_ASSET_REGISTER.md",
    "Docs\Assets\AI_ASSET_MANIFEST.json",
    "Docs\Assets\AI_ASSET_QA_CHECKLISTS.md",
    "Docs\Prompts\PROMPT_CONTRACTS.md",
    "Docs\Prompts\APPROVED_PROMPTS.md",
    "Docs\Audio\AUDIO_BRIEF.md",
    "Docs\Art\ART_DIRECTION_BRIEF.md",
    "Docs\Planning\MCP_OPERATION_AUDIT.md",
    "Docs\Planning\AI_PRODUCTION_RETROSPECTIVES.md",
    "Tools\AI\validate_ai_asset_manifest.py",
    "Tools\MCP\check_mcp_readiness.ps1",
    "Tools\MCP\start_ue_mcp_editor.ps1",
    "Tools\MCP\start_blender_mcp_session.ps1",
    ".codex\config.toml",
    "Config\DefaultEditorPerProjectUserSettings.ini",
    "Config\DefaultGameplayTags.ini",
    "NewWorld.uproject"
)

foreach ($path in $requiredPaths) {
    Require-Path $path
}

if (Test-Path -LiteralPath ".ignore") {
    $badIgnore = Get-Content -LiteralPath ".ignore" | Where-Object { $_ -match '^\s*/?(AGENTS\.md|Docs|\.agents|\.codex|Source|Config|Content)(/|$)' }
    if ($badIgnore) {
        Add-Failure ".ignore hides project-critical paths: $($badIgnore -join ', ')"
    } else {
        Add-Failure ".ignore exists at project root; remove it unless there is an explicit reviewed need."
    }
}

$gitignore = if (Test-Path -LiteralPath ".gitignore") { Get-Content -LiteralPath ".gitignore" } else { @() }
foreach ($pattern in @('.vscode/', '*.code-workspace', 'Binaries/', 'Intermediate/', 'Saved/', 'DerivedDataCache/')) {
    if (-not ($gitignore -contains $pattern)) {
        Add-Failure ".gitignore missing pattern: $pattern"
    }
}

try {
    $manifest = Get-Content -LiteralPath "Docs\Assets\AI_ASSET_MANIFEST.json" -Raw | ConvertFrom-Json
    if ($manifest.project -ne "NewWorld") { Add-Failure "Manifest project is not NewWorld." }
    if ($null -eq $manifest.assets) { Add-Failure "Manifest missing assets array." }
} catch {
    Add-Failure "Manifest JSON parse failed: $($_.Exception.Message)"
}

try {
    $uproject = Get-Content -LiteralPath "NewWorld.uproject" -Raw | ConvertFrom-Json
    $enabledPlugins = @($uproject.Plugins | Where-Object { $_.Enabled } | ForEach-Object { $_.Name })
    $requiredMcpPlugins = @(
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
    foreach ($plugin in $requiredMcpPlugins) {
        if ($enabledPlugins -notcontains $plugin) {
            Add-Failure "Required selected MCP plugin not enabled: $plugin"
        }
    }
    foreach ($plugin in @("AllToolsets", "AIAssistant")) {
        if ($enabledPlugins -contains $plugin) {
            Add-Failure "Forbidden experimental plugin enabled for this phase: $plugin"
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

$projectSkillCount = @(Get-ChildItem -Path ".codex\skills\project" -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") }).Count
$agentCount = @(Get-ChildItem -Path ".codex\agents" -Filter "*.toml" -ErrorAction SilentlyContinue).Count
$gamedevCount = @(Get-ChildItem -Path ".codex\skills\vendor\gamedev-skills" -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") }).Count
$quodCount = @(Get-ChildItem -Path ".codex\skills\vendor\quodsoler-unreal-engine-skills" -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") }).Count

if ($projectSkillCount -ne 9) { Add-Failure "Expected 9 project skills, found $projectSkillCount." }
if ($agentCount -ne 14) { Add-Failure "Expected 14 project agents, found $agentCount." }
if ($gamedevCount -ne 26) { Add-Failure "Expected 26 gamedev vendored skills, found $gamedevCount." }
if ($quodCount -ne 27) { Add-Failure "Expected 27 quodsoler vendored skills, found $quodCount." }

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python -c "import pathlib,tomllib; [tomllib.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('.codex/agents').glob('*.toml')]; print('agent-toml-ok')"
    if ($LASTEXITCODE -ne 0) { Add-Failure "Agent TOML parse check failed." }
} else {
    Add-Failure "python is not available for TOML validation."
}

$rg = Get-Command rg -ErrorAction SilentlyContinue
if ($rg) {
    & rg -n "Prompt Contracts" Docs .codex | Out-Null
    if ($LASTEXITCODE -ne 0) { Add-Failure "rg could not find project docs/skills; check ignore rules." }
} else {
    Add-Failure "rg is not available for visibility check."
}

Write-Host "projectSkillCount=$projectSkillCount"
Write-Host "agentCount=$agentCount"
Write-Host "gamedevVendorSkillCount=$gamedevCount"
Write-Host "quodsolerVendorSkillCount=$quodCount"

& powershell -ExecutionPolicy Bypass -File "Tools\MCP\check_mcp_readiness.ps1"
if ($LASTEXITCODE -ne 0) { Add-Failure "MCP readiness check failed." }

if ($failures.Count -gt 0) {
    Write-Host "AI readiness check failed:"
    foreach ($failure in $failures) { Write-Host "- $failure" }
    exit 1
}

Write-Host "AI readiness check passed."
