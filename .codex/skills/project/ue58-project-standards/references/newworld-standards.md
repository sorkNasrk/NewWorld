# NewWorld Standards Reference

Use this reference when a task changes architecture, ownership, project policy, or more than one subsystem.

## Ownership

Runtime code owns deterministic behavior, replication, save/load, input consumption, asset loading, and performance-critical loops. Blueprint owns composition, designer-facing values, simple event wiring, UI layout, level scripting, and prototype-only behavior.

DataAssets, DataTables, Gameplay Tags, and config files should own content data when designers or AI-assisted production need repeatable edits without touching C++.

## Project Paths

- Runtime source: Source/NewWorld
- Production content: Content/NewWorld
- AI staging content: Content/NewWorld/AIWork
- Project instructions: AGENTS.md, .agents/*, .codex/skills/project/*
- Main handbook: Docs/AI_Codex_UE58_GameDev_Guide.md

All project content belongs under Content/NewWorld, including production assets and AIWork staging. Removed engine-template content is not a project dependency and must not be recreated outside this root.

## Change Gates

- C++ reflection or Build.cs changes: regenerate project files when needed and build NewWorldEditor.
- Content or asset import changes: run Data Validation before acceptance.
- AI-generated assets: register prompt, model, provenance, candidate count, QA, and import settings.
- MCP writes: require recovery point, scoped target, audit record, screenshot/log evidence, and rollback path.
