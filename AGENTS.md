# AGENTS.md

## Project

- Project name: NewWorld
- Engine: Unreal Engine 5.8
- UE install: G:/UnrealEngineInstalled/UE_5.8
- Primary workspace: G:/NewWorld
- Main handbook: Docs/AI_Codex_UE58_GameDev_Guide.md
- Use Chinese for project docs and user-facing planning unless requested otherwise.

## Required Context

- Start by reading this file and .agents/ue-project-context.md.
- For Codex/AI game-development policy, read Docs/AI_Codex_UE58_GameDev_Guide.md before changing project structure, assets, MCP, agents, or skills.
- Project-level skills live under .codex/skills/project and vendored skills live under .codex/skills/vendor. They may not appear in the global Codex skill list, so read the matching local SKILL.md path from .agents/skills-index.md when a task matches.
- Do not create a root .ignore that hides AGENTS.md, Docs, .agents, .codex, Source, Config, or Content from rg-based inspection.

## Codex Workflow

- Keep tasks scoped to one coherent player-visible or production-visible outcome.
- For complex UE work, gather evidence first, then implement.
- Use subagents for read-heavy exploration, logs, docs, asset audits, and trace analysis.
- Do not run large live-editor, Blueprint, or Content changes without a Git recovery point.
- When the same mistake happens twice, write a short retrospective and propose a rule or skill update.
- Do not install project skills or vendored repositories into C:/Users/happyelements/.codex/skills unless the user explicitly asks to promote them.

## Git Commit Rules

- Use a concise imperative subject plus a body for non-trivial changes.
- The body should explain what changed, why it changed, and which validation commands passed.
- Mention intentional limits, skipped checks, and known follow-up work when relevant.
- Avoid one-line commits for UE plugin, MCP, asset workflow, build, or project-rule changes.
- For detailed project commits, append a short Chinese translation or summary at the end for Chinese readers.

## MCP Workflow

- Treat UE MCP, Blender MCP, and editor toolsets as automation with side effects.
- Project MCP config lives in .codex/config.toml. Do not use codex mcp add for this project unless the user explicitly asks to modify user-level Codex config.
- Selected UE5.8 MCP plugins are enabled for Editor targets only: ModelContextProtocol, MCPClientToolset, EditorToolset, GameplayTagsToolset, UMGToolSet, NiagaraToolsets, PCGToolset, AIModuleToolset, AutomationTestToolset, and SlateInspectorToolset.
- Start with read-only discovery and scene/asset queries.
- Do not enable UE ModelContextProtocol auto-start by default; start it with Tools/MCP/start_ue_mcp_editor.ps1 when needed.
- Do not overwrite .codex/config.toml from UE tools; generate a draft or merge manually.
- Blender MCP writes should stay in a staging .blend or export folder until QA passes.
- Keep Blender MCP safe mode enabled with BLENDER_MCP_SAFE_MODE=1.
- Use Docs/Planning/MCP_OPERATION_AUDIT.md before any MCP write batch.
- After any MCP write batch, report changed objects/assets, screenshot evidence, logs, validation status, rollback path, and remaining risk.

## Unreal Conventions

- Use UE5.8 APIs and verify version-specific behavior.
- Follow Epic-style asset prefixes and [Prefix]_[Name]_[Descriptor]_[Variant].
- Stable runtime logic belongs in C++; designer-facing tuning belongs in Blueprint/DataAssets.
- Avoid Tick unless justified by behavior and budget.
- UObject references must be GC-safe with UPROPERTY/TObjectPtr or other explicit ownership.
- Editor-only code belongs in an Editor module or Editor Utility workflow.
- Project asset policy validation belongs in the NewWorldEditor module and runs through UE Data Validation.

## AI Asset Rules

- AIART image generation defaults to inferenceMode: "gpt".
- Quality is preferred over speed/cost unless the task says otherwise.
- Hyper3D should use modelVariant: "extremeHigh" when available and suitable.
- Tripo texture should use textureQuality: "detailed" when available and suitable.
- Image, audio, music, video, and 3D prompts must be drafted and approved before tool calls when the task asks for production assets.
- For AIART and AI Voice generation calls, pass the approved prompt verbatim unless the user explicitly authorizes a rewrite.
- AI assets enter Content/NewWorld/AIWork first.
- Production assets require provenance, QA, UE import review, and Data Validation.
- Use Docs/Prompts/PROMPT_CONTRACTS.md and Docs/Assets/AI_ASSET_QA_CHECKLISTS.md for generated asset tasks.

## Verification

- Compile after C++ header/reflection changes.
- Run targeted Automation tests when available.
- Run Data Validation before accepting asset-heavy changes.
- Data Validation includes NewWorld asset policy checks for /Game/NewWorld naming, AIWork staging, manifest status, and MCP staging markers.
- Run Tools/AI/check_ai_readiness.ps1 after changing AGENTS, .agents, .codex, project docs, or AI workflow scripts.
- Run Tools/MCP/check_mcp_readiness.ps1 after changing MCP plugins, Config, .codex/config.toml, or Tools/MCP scripts.
- Run Tools/AI/validate_ai_asset_manifest.py after changing Docs/Assets/AI_ASSET_MANIFEST.json.
- For UI, verify keyboard/mouse/gamepad and multiple resolutions.
- For performance claims, provide trace/stat/log evidence.

## Code Review Rules

- Flag unsafe UObject lifetime, missing UPROPERTY/TObjectPtr, invalid async captures, unnecessary Tick, unbounded spawning, hard references that should be soft references, replication mistakes, editor/runtime module leaks, missing validation, and unreviewed AI assets.
