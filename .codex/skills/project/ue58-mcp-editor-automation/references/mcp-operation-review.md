# MCP Operation Review

Use this before UE MCP, Blender MCP, editor scripting, or any tool that can modify assets or editor state.

## Preflight

- Identify server/tool name and whether it is UE MCP, Blender MCP, or another editor bridge.
- Confirm read-only discovery commands are run first.
- Confirm target paths, assets, or objects are scoped.
- Confirm current Git recovery point.
- Confirm no tool will overwrite .codex/config.toml or user-level Codex config.
- Confirm project .codex/config.toml contains unreal-mcp and blender servers without secrets.
- Confirm UE MCP uses 127.0.0.1:8000/mcp, bAutoStartServer=False, and bEnableToolSearch=True.
- Confirm network exposure and Python/script execution are understood.

## Write Batch Rules

Keep write batches small enough to review. For each batch, record changed assets/objects, screenshots, logs, generated files, and validation plan. Stop on incomplete tool results, unexpected changed paths, missing screenshots, or changed production Content outside scope.

## Sandbox Defaults

Selected UE MCP toolsets are enabled for Editor targets only: ModelContextProtocol, MCPClientToolset, EditorToolset, GameplayTagsToolset, UMGToolSet, NiagaraToolsets, PCGToolset, AIModuleToolset, AutomationTestToolset, and SlateInspectorToolset. AIAssistant and AllToolsets stay disabled for this phase.

## Project Commands

~~~powershell
powershell -ExecutionPolicy Bypass -File Tools/MCP/check_mcp_readiness.ps1
powershell -ExecutionPolicy Bypass -File Tools/MCP/start_ue_mcp_editor.ps1 -Port 8000
~~~

Use -RequireUnrealRunning on the readiness script only after the editor has finished loading.
