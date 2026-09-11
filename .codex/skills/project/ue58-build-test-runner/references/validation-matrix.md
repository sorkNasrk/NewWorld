# Validation Matrix

Choose the smallest check set that proves the changed surface.

| Change | Required checks |
| --- | --- |
| Docs, AGENTS, skills, agents | JSON/TOML parse when applicable; rg visibility; AI readiness script |
| .uproject, plugins, modules, Target.cs, Build.cs | UBT project files; NewWorldEditor build |
| C++ headers, reflection, UObject ownership | NewWorldEditor build; targeted tests if behavior exists |
| Blueprint or Content runtime asset | Data Validation; PIE/screenshot evidence when visual or interactive |
| AI asset staging | Manifest validation; asset QA checklist; provenance entry |
| MCP write batch | MCP audit record; changed object list; screenshots/logs; Data Validation plan |
| UI/font/localization | Widget focus/input check; longest text check; Font Asset check; localization compile when used |
| Audio/music/VO | Prompt/provenance; loudness/peak note; loop and variation audition; UE routing note |

Generated IDE files, caches, logs, and .vscode compile command output should stay ignored unless a later task intentionally creates curated editor settings.
