---
name: ue58-asset-pipeline
description: Use for NewWorld AIART, AI Voice, generated images, generated 3D, textures, models, provenance, approved prompts, manifests, Blender handoff, UE import, QA, and Data Validation.
---

# UE5.8 Asset Pipeline

Generated assets are candidates until they pass prompt approval, provenance recording, DCC cleanup, UE import review, in-scene validation, and Data Validation.

Read [references/asset-flow.md](references/asset-flow.md) for multi-step asset work. Use Docs/Prompts/PROMPT_CONTRACTS.md, Docs/Assets/AI_ASSET_QA_CHECKLISTS.md, Docs/Assets/AI_ASSET_REGISTER.md, and Docs/Assets/AI_ASSET_MANIFEST.json as the project source of truth.

## Required Inputs

- Asset id, type, role, target gameplay/context use, and target UE path.
- Approved prompt or explicit instruction to draft one for approval.
- References: orthographic views, 3/4 view, silhouette, material swatches, scale reference, audio reference, or UI flow as applicable.
- Model/provider, parameters, candidate count, and license/provenance plan.
- Acceptance checklist and return threshold.

## Defaults

- AIART image generation uses inferenceMode: "gpt" unless the task explicitly overrides it.
- Prefer the highest-quality available model or quality tier that fits the task constraints.
- Hyper3D uses modelVariant: "extremeHigh" when available and suitable.
- Tripo texture uses textureQuality: "detailed" when available and suitable.
- Pass approved prompts verbatim in generation calls unless the user explicitly authorizes a rewrite.
- Stage generated assets under Content/NewWorld/AIWork before promotion.
- Choose and record creation_route before generation. Use Docs/Assets/ASSET_PRODUCTION_ROUTES.md for AI vs Blender MCP vs procedural tool vs manual DCC decisions.
- Treat GLB/GLTF as AI 3D or Blender interchange for static meshes. Use Tools/Assets/export_blender_static_mesh_fbx.py to produce staged FBX before the verified UE MCP StaticMesh import path.

## Return Thresholds

- Regenerate when silhouette, category, scale, pose, or topology is fundamentally wrong.
- Send to Blender/DCC cleanup when issues are limited to pivot, scale, normals, UVs, material slots, collision, naming, or minor mesh defects.
- Stop after three failed repair/regeneration loops and write a retrospective candidate.

## Output

Return generated candidates, creation_route, route_decision_reason, prompt/model/parameter or script/seed record, staging path, Blender cleanup/export result, UE import settings, Data Validation status, and remaining risks.
