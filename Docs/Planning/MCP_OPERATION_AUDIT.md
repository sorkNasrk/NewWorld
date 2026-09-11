# MCP Operation Audit

Use this template before and after UE MCP, Blender MCP, editor scripting, or any tool call that can modify editor state, assets, Blueprint graphs, materials, scenes, generated files, or Codex config.

## Operation Template

- Date:
- Operator/agent:
- Tool/server:
- Mode: UE MCP / Blender MCP / editor script / other
- Purpose:
- Git recovery point:
- Project MCP config checked: .codex/config.toml / other
- UE MCP state: not running / running at 127.0.0.1:8000/mcp / not applicable
- Blender MCP safe mode confirmed: yes / no / not applicable
- Read-only discovery commands:
- Target paths/assets/objects:
- Allowed write scope:
- Explicitly forbidden paths:
- Python/script execution needed: yes / no
- Network access needed: yes / no
- .codex/config.toml risk: none / read-only / draft only / manual merge
- Manifest/provenance update:
- Screenshot evidence required:
- Logs required:
- Validation plan:
- Rollback plan:
- Preflight reviewer:
- Result:
- Changed assets/objects:
- Screenshots/logs captured:
- Validation result:
- Remaining risk:

## Stop Conditions

- Tool attempts to write outside allowed scope.
- Tool attempts to overwrite .codex/config.toml or user-level Codex config.
- UE MCP is not reachable after a task requires live UE tooling.
- Blender MCP safe mode is not confirmed before Blender writes.
- AllToolsets or AIAssistant is enabled without a separate reviewed task.
- Generated or modified assets lack manifest/provenance path.
- Screenshots or logs cannot be captured for a visual/editor change.
- Repeated repair attempts reach the threshold defined in the relevant skill.

## Current Project Defaults

- UE MCP server: http://127.0.0.1:8000/mcp.
- UE MCP startup: manual only through Tools/MCP/start_ue_mcp_editor.ps1.
- UE MCP tool discovery: bEnableToolSearch=True.
- Blender MCP: project-level .codex/config.toml, BLENDER_MCP_SAFE_MODE=1.
- Production Content writes: forbidden unless the task names the exact reviewed target and rollback path.

## Operation Records

### 2026-09-11 UE MCP Read-Only Smoke Test

- Date: 2026-09-11 Asia/Shanghai.
- Operator/agent: Codex.
- Tool/server: unreal-mcp at http://127.0.0.1:8000/mcp.
- Mode: UE MCP.
- Purpose: Verify project-level Codex can connect to UE5.8 MCP, discover toolsets, run read-only log and Gameplay Tag queries, and shut down the temporary Editor process.
- Git recovery point: b1176b742d0b00f6985ef310e9e02f8b6ca00f6e.
- Project MCP config checked: .codex/config.toml.
- UE MCP state: started manually through Tools/MCP/start_ue_mcp_editor.ps1 -Port 8000; port became reachable.
- Blender MCP safe mode confirmed: not applicable.
- Read-only discovery commands: codex -C G:\NewWorld mcp list; codex -C G:\NewWorld mcp get unreal-mcp; JSON-RPC initialize; notifications/initialized; ping; tools/list; resources/list; list_toolsets; describe_toolset for Logs, AssetTools, and GameplayTags; LogsToolset.GetLogCategories; LogsToolset.GetLogEntries; GameplayTags.ListTags; GameplayTags.GetTagInfo.
- Target paths/assets/objects: none.
- Allowed write scope: none through MCP.
- Explicitly forbidden paths: production Content, .codex/config.toml, user-level Codex config.
- Python/script execution needed: no.
- Network access needed: local loopback only.
- .codex/config.toml risk: read-only.
- Manifest/provenance update: not applicable; no assets generated or modified.
- Screenshot evidence required: no visual/editor state changed.
- Logs required: LogModelContextProtocol entries captured through LogsToolset.GetLogEntries.
- Validation plan: MCP readiness, Gameplay Tag readback, port shutdown check, AI readiness.
- Rollback plan: revert this audit entry plus Config/DefaultGameplayTags.ini and Tools/AI/check_ai_readiness.ps1 if the tag config change is not wanted.
- Preflight reviewer: project MCP rules in ue58-mcp-editor-automation.
- Result: pass after fixing Gameplay Tags config syntax.
- Changed assets/objects: none.
- Changed repo files: Config/DefaultGameplayTags.ini changed from repeated GameplayTagList assignment to additive +GameplayTagList entries; Tools/AI/check_ai_readiness.ps1 now verifies additive project tags; this audit record added.
- Screenshots/logs captured: LogModelContextProtocol reported three meta-tools and up to 31 discoverable toolsets; calls were logged for list_toolsets, LogsToolset.GetLogCategories, GameplayTags.ListTags, and GameplayTags.GetTagInfo.
- Validation result: MCP readiness passed before and after restart; GameplayTags.ListTags returned NewWorld.Asset.AIWork, NewWorld.Asset.ProvenanceRequired, NewWorld.MCP.Staging, and NewWorld.Validation.Required after the config fix; temporary MCP sessions were deleted; temporary Editor PIDs 92332 and 52564 were stopped; no listener remained on 127.0.0.1:8000.
- Remaining risk: no live MCP write batch was exercised; Blender MCP remains untested in this record.
