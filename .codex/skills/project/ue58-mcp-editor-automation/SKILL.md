---
name: ue58-mcp-editor-automation
description: Use for NewWorld UE MCP, Blender MCP, editor automation, tool discovery, operation audit, recovery points, write scope, screenshots, logs, and Data Validation planning.
---

# UE5.8 MCP Editor Automation

MCP tools can modify editor state, assets, Blueprint graphs, materials, scene objects, and config files. Treat them as side-effectful automation.

Read [references/mcp-operation-review.md](references/mcp-operation-review.md) and use Docs/Planning/MCP_OPERATION_AUDIT.md before any MCP write batch.

## Defaults

- Start with read-only discovery and scene/asset queries.
- UE ModelContextProtocol is enabled for Editor targets only and must be manually started with Tools/MCP/start_ue_mcp_editor.ps1.
- Project MCP configuration lives in .codex/config.toml with unreal-mcp at http://127.0.0.1:8000/mcp.
- Keep bAutoStartServer=False and bEnableToolSearch=True.
- Use list_toolsets and describe_toolset before call_tool.
- For UE MCP static mesh imports, use Tools/MCP/import_static_mesh_via_ue_mcp.ps1 after the editor MCP server is reachable.
- The static mesh import script calls tools/list, describe_toolset, and call_tool with full toolset names such as editor_toolset.toolsets.static_mesh.StaticMeshTools and editor_toolset.toolsets.asset.AssetTools.
- StaticMeshTools.import_file currently uses FbxFactory; it accepts the observed FBX/OBJ path and rejects GLB/GLTF. Convert GLB/GLTF through Blender before this UE MCP path.
- UObject parameters for StaticMeshTools readback must use full object refPath values such as /Game/Folder/Asset.Asset.
- Do not let UE tools overwrite .codex/config.toml; generate a draft or merge manually.
- Write only to explicitly scoped staging paths unless the task names a reviewed production target.
- Blender MCP safe mode should be enabled when available.

## Required Before Writes

- Git recovery point or explicit confirmation that the current work can be discarded.
- Exact tool/server, target path, operation list, and rollback plan.
- Screenshot/log/Data Validation plan.
- Manifest/provenance plan for generated assets.

## Output

Return changed objects/assets, screenshots needed or captured, log locations, validation status, rollback path, and residual risk.

## Verification

- Run Tools/MCP/check_mcp_readiness.ps1 after config or plugin changes.
- Run Tools/AI/check_ai_readiness.ps1 after project workflow changes.
- For live UE MCP sessions, start the editor manually and require 127.0.0.1:8000 to be reachable before tool calls.
- After staged static mesh import, verify the script JSON summary, thumbnail evidence when requested, Data Validation, and Git LFS status for generated binary files.
