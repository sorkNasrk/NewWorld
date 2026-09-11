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
- StaticMesh assets imported through UE MCP should come from FBX/OBJ, not direct GLB/GLTF; check the Tools/MCP/import_static_mesh_via_ue_mcp.py summary for source file, bounds, material slots, triangle count, vertex count, LOD count, Nanite state, metadata, and evidence thumbnail.
- UE Data Validation hard-checks /Game/NewWorld prefix shape, AIWork staging, AI_ASSET_MANIFEST readiness, creation_route records, MCP staging markers, and first-pass StaticMesh/Texture/Material quality through NewWorldEditor.
- Manual QA still covers visual quality, topology, UVs, material setup, audio audition, UI focus, localization readability, and screenshots.

## Output

Lead with blocking findings. Include asset path, violated rule, fix, verification command, and whether the asset can stay staged or must be regenerated.
