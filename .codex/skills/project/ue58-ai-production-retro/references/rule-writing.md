# Rule Writing

Write rules only when they prevent future rework.

## Required Rule Shape

- Trigger: when the rule applies.
- Bad example: the pattern that caused failure.
- Correct behavior: what the agent must do instead.
- Verification: command, inspection, or review evidence.
- Scope: global, asset pipeline, build/test, MCP, UI, audio, or one subsystem.
- Expiration: when to revisit or remove the rule.

## Where To Write

| Rule type | Destination |
| --- | --- |
| Stable global default | AGENTS.md |
| Asset/import/generation workflow | ue58-asset-pipeline or ue58-content-audit |
| MCP/editor automation safety | ue58-mcp-editor-automation |
| Build/test behavior | ue58-build-test-runner |
| One-off incident | Docs/Planning/AI_PRODUCTION_RETROSPECTIVES.md |

Avoid adding rules that simply restate normal engineering judgment.
