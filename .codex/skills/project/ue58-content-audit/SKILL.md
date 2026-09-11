---
name: ue58-content-audit
description: "Use for NewWorld UE content audits: asset naming, AIWork staging, redirectors, missing references, materials, texture budgets, mesh import settings, audio/UI assets, LFS, and provenance."
---

# UE5.8 Content Audit

Audit content before it moves out of Content/NewWorld/AIWork or before accepting broad asset changes. Read [references/content-checklist.md](references/content-checklist.md) for asset-specific checks.

## Required Inputs

- Changed asset paths or folders.
- Asset type and intended runtime use.
- Source/provenance record or reason it is not AI-generated.
- Expected platform or performance budget when known.

## Checks

- Names follow [Prefix]_[Name]_[Descriptor]_[Variant].
- Generated assets have register and manifest entries.
- WIP assets do not live directly in final production paths.
- LFS tracks binary/source art formats.
- Redirectors and missing references are resolved before acceptance.
- Import settings match type: mesh, skeletal mesh, texture, material, audio, UI, font, Niagara, cinematic, or localization.
- UE Data Validation hard-checks /Game/NewWorld prefix shape, AIWork staging, AI_ASSET_MANIFEST readiness for promoted AI assets, and MCP staging markers through NewWorldEditor.
- Manual QA still covers visual quality, topology, UVs, material setup, audio audition, UI focus, localization readability, and screenshots.

## Output

Lead with blocking findings. Include asset path, violated rule, fix, verification command, and whether the asset can stay staged or must be regenerated.
