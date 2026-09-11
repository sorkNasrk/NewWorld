# MCP Operation Review

Use this before UE MCP, Blender MCP, editor scripting, or any tool that can modify assets or editor state.

## Preflight

- Identify server/tool name and whether it is UE MCP, Blender MCP, or another editor bridge.
- Confirm read-only discovery commands are run first.
- Confirm target paths, assets, or objects are scoped.
- Confirm current Git recovery point.
- Confirm no tool will overwrite .codex/config.toml or user-level Codex config.
- Confirm network exposure and Python/script execution are understood.

## Write Batch Rules

Keep write batches small enough to review. For each batch, record changed assets/objects, screenshots, logs, generated files, and validation plan. Stop on incomplete tool results, unexpected changed paths, missing screenshots, or changed production Content outside scope.

## Sandbox Defaults

UE ModelContextProtocol, AIAssistant, MCPClientToolset, UMGToolSet, NiagaraToolsets, PCGToolset, and AIModuleToolset are treated as experimental. Validate them in a sandbox before making them production dependencies.
