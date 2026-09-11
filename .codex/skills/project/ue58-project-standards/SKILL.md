---
name: ue58-project-standards
description: Use for NewWorld UE5.8 project standards, architecture, module boundaries, C++/Blueprint ownership, asset roots, Git recovery points, and project-wide AI workflow.
---

# UE5.8 Project Standards

Before changing project structure, modules, plugins, gameplay ownership, asset policy, agents, or skills, read AGENTS.md, .agents/ue-project-context.md, .agents/skills-index.md, and the relevant section of Docs/AI_Codex_UE58_GameDev_Guide.md.

Use [references/newworld-standards.md](references/newworld-standards.md) when the task touches more than one subsystem, introduces a new module/plugin, changes asset ownership, or changes AI workflow policy.

## Required Inputs

- Intended player-visible or production-visible outcome.
- Target files, modules, assets, or docs when known.
- Whether the task changes runtime code, editor tooling, generated assets, or project policy.
- Validation expected by the task owner.

## Project Defaults

- Stable runtime systems belong in C++.
- Designer-facing composition and tuning belong in Blueprint, DataAssets, DataTables, or Gameplay Tags.
- Production assets live under Content/NewWorld after staging and QA.
- Generated or AI-assisted assets start under Content/NewWorld/AIWork.
- Project-level skills live in .codex/skills/project; vendored skills live in .codex/skills/vendor.
- Do not install project-proven skills into user scope unless a later task explicitly asks for promotion.
- UE5.8 Experimental MCP/AIAssistant plugins remain disabled until a sandbox task explicitly evaluates them.

## Workflow

1. Confirm the current Git state before meaningful changes.
2. Identify the project skill(s) and vendored skill(s) that apply.
3. Keep the change scoped to one coherent outcome.
4. State the C++/Blueprint/data ownership boundary before implementation.
5. Define the validation path before calling the work done.
6. Update project docs or skills only when the rule will change future decisions.

## Output

Report the chosen ownership boundary, changed systems, validation performed, and any assumptions left for design review. If the task is purely planning or docs, say which executable workflow or template it changes.
