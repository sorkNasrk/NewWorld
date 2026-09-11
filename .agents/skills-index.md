# NewWorld Project Skill Index

Project-level skills may not be auto-listed by Codex. When a task matches one of these domains, read the listed local SKILL.md before acting.

## Project Skills

| Trigger | Skill path | Key references |
| --- | --- | --- |
| UE5.8 project rules, architecture, module boundaries | .codex/skills/project/ue58-project-standards/SKILL.md | references/newworld-standards.md |
| Build, UBT, Automation, Data Validation | .codex/skills/project/ue58-build-test-runner/SKILL.md | references/validation-matrix.md; Tools/AI/check_ai_readiness.ps1 |
| AIART, AI Voice, generated assets, Blender handoff | .codex/skills/project/ue58-asset-pipeline/SKILL.md | references/asset-flow.md; Docs/Prompts/PROMPT_CONTRACTS.md |
| Content naming, redirectors, budgets, provenance | .codex/skills/project/ue58-content-audit/SKILL.md | references/content-checklist.md; Docs/Assets/AI_ASSET_QA_CHECKLISTS.md |
| UE code/content review | .codex/skills/project/ue58-review-checklist/SKILL.md | references/ue-review-risk-map.md |
| Repeated AI mistakes and rule updates | .codex/skills/project/ue58-ai-production-retro/SKILL.md | references/rule-writing.md; Docs/Planning/AI_PRODUCTION_RETROSPECTIVES.md |
| UE MCP and editor automation safety | .codex/skills/project/ue58-mcp-editor-automation/SKILL.md | references/mcp-operation-review.md; Docs/Planning/MCP_OPERATION_AUDIT.md; Tools/MCP/check_mcp_readiness.ps1 |
| Blender MCP modeling, cleanup, screenshots, export | .codex/skills/project/ue58-blender-mcp-asset/SKILL.md | references/blender-mcp-decision-tree.md; Tools/MCP/start_blender_mcp_session.ps1 |
| SFX, VO, BGM, Ambient, MetaSound, Sound Cue | .codex/skills/project/ue58-audio-pipeline/SKILL.md | references/audio-prompt-fields.md; Docs/Audio/AUDIO_BRIEF.md |

## Vendored Skills

| Source | Ref | License | Installed scope |
| --- | --- | --- | --- |
| gamedev-skills/awesome-gamedev-agent-skills | b105e1cf617adf0b68ed98790a716bbb60993179 | Apache-2.0 | router, disciplines, unreal, workflows |
| quodsoler/unreal-engine-skills | 231c8571be6f3335685edc566a28ec6f9621361d | MIT | all skills |

Vendored roots:

- .codex/skills/vendor/gamedev-skills
- .codex/skills/vendor/quodsoler-unreal-engine-skills

Use vendored skills as project dependencies only. Do not install these into C:/Users/happyelements/.codex/skills unless a later task explicitly promotes a project-proven skill to user scope.
