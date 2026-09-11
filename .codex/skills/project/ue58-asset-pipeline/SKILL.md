---
name: ue58-asset-pipeline
description: Use for NewWorld AIART, AI Voice, generated assets, approved prompts, manifests, provenance, Blender handoff, UE import, QA, and Data Validation.
---

# UE5.8 Asset Pipeline

Generated assets are candidates until they pass prompt approval, provenance recording, DCC cleanup, UE import review, in-scene validation, and Data Validation.

Required records:

- Asset id, role, target UE path, and status.
- Approved prompt and rule to pass it verbatim during tool calls.
- Model/provider, parameters, task id, references, and candidate count.
- License/provenance note.
- DCC cleanup: scale, pivot, normals, topology, UV, materials, collision, LOD or Nanite strategy.
- UE import QA and gameplay/context review.

AIART defaults:

- Image generation uses inferenceMode: "gpt" unless the task explicitly overrides it.
- Hyper3D uses modelVariant: "extremeHigh" when available and suitable.
- Tripo texture uses textureQuality: "detailed" when available and suitable.

Use Docs/Assets/AI_ASSET_REGISTER.md and Docs/Assets/AI_ASSET_MANIFEST.json as the source of truth.
