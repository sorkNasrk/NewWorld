# MCP Operation Audit

Use this template before and after UE MCP, Blender MCP, editor scripting, or any tool call that can modify editor state, assets, Blueprint graphs, materials, scenes, generated files, or Codex config.

## Operation Template

- Date:
- Operator/agent:
- Tool/server:
- Mode: UE MCP / Blender MCP / editor script / other
- Purpose:
- Git recovery point:
- Read-only discovery commands:
- Target paths/assets/objects:
- Allowed write scope:
- Explicitly forbidden paths:
- Python/script execution needed: yes / no
- Network access needed: yes / no
- .codex/config.toml risk: none / draft only / manual merge
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
- Generated or modified assets lack manifest/provenance path.
- Screenshots or logs cannot be captured for a visual/editor change.
- Repeated repair attempts reach the threshold defined in the relevant skill.
