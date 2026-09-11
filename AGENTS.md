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

## Codex Workflow

- Keep tasks scoped to one coherent player-visible or production-visible outcome.
- For complex UE work, gather evidence first, then implement.
- Use subagents for read-heavy exploration, logs, docs, asset audits, and trace analysis.
- Do not run large live-editor, Blueprint, or Content changes without a Git recovery point.
- When the same mistake happens twice, write a short retrospective and propose a rule or skill update.

## MCP Workflow

- Treat UE MCP, Blender MCP, and editor toolsets as automation with side effects.
- Start with read-only discovery and scene/asset queries.
- Do not enable UE ModelContextProtocol auto-start by default.
- Do not overwrite .codex/config.toml from UE tools; generate a draft or merge manually.
- Blender MCP writes should stay in a staging .blend or export folder until QA passes.
- After any MCP write batch, report changed objects/assets, screenshot evidence, logs, and remaining risk.

## Unreal Conventions

- Use UE5.8 APIs and verify version-specific behavior.
- Follow Epic-style asset prefixes and [Prefix]_[Name]_[Descriptor]_[Variant].
- Stable runtime logic belongs in C++; designer-facing tuning belongs in Blueprint/DataAssets.
- Avoid Tick unless justified by behavior and budget.
- UObject references must be GC-safe with UPROPERTY/TObjectPtr or other explicit ownership.
- Editor-only code belongs in an Editor module or Editor Utility workflow.

## AI Asset Rules

- AIART image generation defaults to inferenceMode: "gpt".
- Quality is preferred over speed/cost unless the task says otherwise.
- Hyper3D should use modelVariant: "extremeHigh" when available and suitable.
- Tripo texture should use textureQuality: "detailed" when available and suitable.
- Image, audio, music, video, and 3D prompts must be drafted and approved before tool calls when the task asks for production assets.
- For AIART and AI Voice generation calls, pass the approved prompt verbatim unless the user explicitly authorizes a rewrite.
- AI assets enter Content/NewWorld/AIWork first.
- Production assets require provenance, QA, UE import review, and Data Validation.

## Verification

- Compile after C++ header/reflection changes.
- Run targeted Automation tests when available.
- Run Data Validation before accepting asset-heavy changes.
- For UI, verify keyboard/mouse/gamepad and multiple resolutions.
- For performance claims, provide trace/stat/log evidence.

## Code Review Rules

- Flag unsafe UObject lifetime, missing UPROPERTY/TObjectPtr, invalid async captures, unnecessary Tick, unbounded spawning, hard references that should be soft references, replication mistakes, editor/runtime module leaks, missing validation, and unreviewed AI assets.
