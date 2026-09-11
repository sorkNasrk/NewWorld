# UE Project Context

Engine version: Unreal Engine 5.8
Engine install: G:/UnrealEngineInstalled/UE_5.8
Project root: G:/NewWorld
Project file: G:/NewWorld/NewWorld.uproject
Project baseline: UE5.8 C++ project; unused template content has been removed
Baseline commit: 9d989d0 Initial UE5.8 Codex project setup
Target platforms: Windows first, others TBD
Renderer: UE5.8 project renderer settings
Source build or launcher build: local installed engine

## Modules

Primary game module: NewWorld
Runtime modules: NewWorld
Editor modules: NewWorldEditor
Runtime dependencies retained for future development: Core, CoreUObject, Engine, InputCore, EnhancedInput, AIModule, StateTreeModule, GameplayStateTreeModule, UMG, Slate
Template-derived plugins retained for future development: ModelingToolsEditorMode, StateTree, GameplayStateTree
Selected MCP plugins enabled for Editor targets: ModelContextProtocol, MCPClientToolset, EditorToolset, GameplayTagsToolset, UMGToolSet, NiagaraToolsets, PCGToolset, AIModuleToolset, AutomationTestToolset, SlateInspectorToolset
Experimental AI plugin kept disabled: AIAssistant

## Project Rules

C++ owns stable runtime systems.
Blueprint owns designer-facing composition and tuning.
DataAssets/DataTables/Gameplay Tags own content configuration.
AIWork is staging only.
Formal assets need naming, import review, metadata, and validation.
All project content lives under Content/NewWorld; UE template content and its external actor/object sidecars are not project dependencies.
UE Data Validation enforces NewWorld asset policy for /Game/NewWorld through NewWorldEditor, including naming, AIWork staging, manifest route/status, MCP staging, and first-pass StaticMesh/Texture/Material checks.
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
- MCP config: .codex/config.toml
- MCP scripts: Tools/MCP/check_mcp_readiness.py, Tools/MCP/start_ue_mcp_editor.py, Tools/MCP/start_blender_mcp_session.py
- Blender static mesh FBX export: Tools/Assets/export_blender_static_mesh_fbx.py
- UE MCP static mesh import: Tools/MCP/import_static_mesh_via_ue_mcp.py
- Asset production routes: Docs/Assets/ASSET_PRODUCTION_ROUTES.md
- UE asset policy validator: Source/NewWorldEditor/Private/NewWorldAssetPolicyValidator.cpp
- Retrospectives: Docs/Planning/AI_PRODUCTION_RETROSPECTIVES.md
- Readiness script: Tools/AI/check_ai_readiness.py
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

Data Validation currently checks /Game/NewWorld assets for supported prefixes, [Prefix]_[Name]_[Descriptor]_[Variant] shape, AIWork staging, AI_ASSET_MANIFEST status, creation_route records, MCP staging markers, and first-pass StaticMesh/Texture/Material quality.

AI readiness:
~~~powershell
python Tools/AI/check_ai_readiness.py
~~~

Manifest validation:
~~~powershell
python Tools/AI/validate_ai_asset_manifest.py Docs/Assets/AI_ASSET_MANIFEST.json
~~~

MCP readiness:
~~~powershell
python Tools/MCP/check_mcp_readiness.py
~~~

Start UE MCP manually:
~~~powershell
python Tools/MCP/start_ue_mcp_editor.py --port 8000
~~~

Export a staged Blender static mesh FBX:
~~~powershell
python Tools/Assets/export_blender_static_mesh_fbx.py --blend-path Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.blend --output-fbx Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.fbx
~~~

Import a staged StaticMesh through UE MCP:
~~~powershell
python Tools/MCP/import_static_mesh_via_ue_mcp.py --source-file Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.fbx --folder-path /Game/NewWorld/AIWork/MCP_DryRun --asset-name SM_MCP_DryRun_Blockout_A --allow-overwrite
~~~

## MCP Policy

UE MCP default assumption: experimental, Editor target only, manual start, 127.0.0.1:8000/mcp, tool search enabled.
UE MCP StaticMesh import path currently uses StaticMeshTools.import_file through FbxFactory; use FBX/OBJ for that path, and treat GLB/GLTF as Blender/AI 3D interchange formats that need conversion before UE MCP import.
Blender MCP default assumption: safe mode on, one client connected, staging only.
No MCP tool may batch-write production Content without manifest, recovery point, screenshot/log evidence, and Data Validation plan.
