# UE Project Context

Engine version: Unreal Engine 5.8
Engine install: G:/UnrealEngineInstalled/UE_5.8
Project root: G:/NewWorld
Project file: G:/NewWorld/NewWorld.uproject
Template baseline: UE5.8 ThirdPerson C++
Baseline commit: 9d989d0 Initial UE5.8 Codex project setup
Target platforms: Windows first, others TBD
Renderer: UE5.8 default ThirdPerson template settings
Source build or launcher build: local installed engine

## Modules

Primary game module: NewWorld
Runtime modules: NewWorld
Editor modules: TBD
Template dependencies: Core, CoreUObject, Engine, InputCore, EnhancedInput, AIModule, StateTreeModule, GameplayStateTreeModule, UMG, Slate
Template plugins: ModelingToolsEditorMode, StateTree, GameplayStateTree
Experimental AI/MCP plugins to evaluate only in sandbox: ModelContextProtocol, AIAssistant, MCPClientToolset, UMGToolSet, NiagaraToolsets, PCGToolset, AIModuleToolset

## Project Rules

C++ owns stable runtime systems.
Blueprint owns designer-facing composition and tuning.
DataAssets/DataTables/Gameplay Tags own content configuration.
AIWork is staging only.
Formal assets need naming, import review, metadata, and validation.
Project-level Codex skills remain in .codex/skills/project or .codex/skills/vendor.

## AI Workflow Artifacts

- Main handbook: Docs/AI_Codex_UE58_GameDev_Guide.md
- Skill routing: .agents/skills-index.md
- Prompt contracts: Docs/Prompts/PROMPT_CONTRACTS.md
- Approved prompts: Docs/Prompts/APPROVED_PROMPTS.md
- Asset manifest: Docs/Assets/AI_ASSET_MANIFEST.json
- Asset register: Docs/Assets/AI_ASSET_REGISTER.md
- Asset QA: Docs/Assets/AI_ASSET_QA_CHECKLISTS.md
- MCP audit: Docs/Planning/MCP_OPERATION_AUDIT.md
- Retrospectives: Docs/Planning/AI_PRODUCTION_RETROSPECTIVES.md
- Readiness script: Tools/AI/check_ai_readiness.ps1
- Manifest script: Tools/AI/validate_ai_asset_manifest.py

## Verification Commands

Generate project files:
~~~powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/ThirdParty/DotNet/10.0/win-x64/dotnet.exe G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll -ProjectFiles -Project=G:/NewWorld/NewWorld.uproject -Game -Progress
~~~

Build editor target:
~~~powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Build/BatchFiles/Build.bat NewWorldEditor Win64 Development -Project=G:/NewWorld/NewWorld.uproject -WaitMutex -NoHotReload
~~~

Data Validation:
~~~powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe G:/NewWorld/NewWorld.uproject -run=DataValidation -unattended -nop4 -nosplash
~~~

AI readiness:
~~~powershell
powershell -ExecutionPolicy Bypass -File Tools/AI/check_ai_readiness.ps1
~~~

Manifest validation:
~~~powershell
python Tools/AI/validate_ai_asset_manifest.py Docs/Assets/AI_ASSET_MANIFEST.json
~~~

## MCP Policy

UE MCP default assumption: experimental, disabled, manual start.
Blender MCP default assumption: safe mode on when available, one client connected, staging only.
No MCP tool may batch-write production Content without manifest, recovery point, screenshot/log evidence, and Data Validation plan.
