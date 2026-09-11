---
name: ue58-mcp-editor-automation
description: Use for NewWorld UE MCP, Blender MCP, editor automation, tool discovery, operation audit, recovery points, write scope, screenshots, logs, and Data Validation planning.
---

# UE5.8 MCP Editor Automation

MCP tools can modify editor state, assets, Blueprint graphs, materials, scene objects, and config files. Treat them as side-effectful automation.

Read [references/mcp-operation-review.md](references/mcp-operation-review.md) and use Docs/Planning/MCP_OPERATION_AUDIT.md before any MCP write batch.

## Defaults

- Start with read-only discovery and scene/asset queries.
- UE ModelContextProtocol stays disabled and manually evaluated in sandbox.
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
