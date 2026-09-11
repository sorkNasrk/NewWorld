---
name: ue58-project-standards
description: Use for NewWorld UE5.8 project standards, architecture, C++/Blueprint boundaries, asset directories, naming, and project-wide AI workflow.
---

# UE5.8 Project Standards

Before changing project structure, modules, plugins, assets, or gameplay ownership, read AGENTS.md, .agents/ue-project-context.md, and Docs/AI_Codex_UE58_GameDev_Guide.md.

Rules:

- Stable runtime systems belong in C++.
- Designer-facing composition and tuning belong in Blueprint, DataAssets, DataTables, or Gameplay Tags.
- Production assets live under Content/NewWorld after staging and QA.
- Generated or AI-assisted assets start under Content/NewWorld/AIWork.
- Experimental UE MCP plugins remain disabled until a sandbox task explicitly evaluates them.
- Every substantial change needs a clear validation path before it is considered done.
