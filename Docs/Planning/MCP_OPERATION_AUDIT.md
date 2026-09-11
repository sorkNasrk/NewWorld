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
