---
name: ue58-content-audit
description: Use for NewWorld UE content audits: asset naming, redirectors, missing materials, texture budgets, references, AIWork staging, and provenance.
---

# UE5.8 Content Audit

Audit Content changes before they move out of AIWork.

Check:

- Asset names follow [Prefix]_[Name]_[Descriptor]_[Variant].
- Generated assets have manifest/register entries.
- No WIP asset is placed directly in final Content paths.
- Texture sizes, sRGB, compression, mips, and TextureGroup are appropriate.
- Static meshes have scale, pivot, materials, collision, bounds, and LOD/Nanite policy.
- Skeletal meshes have skeleton, root, weights, PhysicsAsset, retarget pose, and clipping review.
- Redirectors and missing references are resolved before acceptance.
