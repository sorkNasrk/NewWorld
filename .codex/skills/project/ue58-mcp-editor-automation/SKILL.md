---
name: ue58-mcp-editor-automation
description: Use for NewWorld UE MCP, Blender MCP, editor automation, tool discovery, recovery points, write scope, screenshots, logs, and Data Validation.
---

# UE5.8 MCP Editor Automation

MCP tools can modify editor state and assets. Treat them as side-effectful automation.

Rules:

- Start with read-only discovery and describe/list calls.
- Do not enable UE ModelContextProtocol auto-start by default.
- Do not overwrite .codex/config.toml from UE tools; generate a draft or merge manually.
- Write only to explicitly scoped staging paths unless the task names a reviewed production target.
- After each write batch, collect changed assets/objects, screenshot or PIE evidence, logs, and Data Validation plan.
- Stop and inspect logs after incomplete tool returns instead of retrying blindly.
