# Asset Flow

Use this flow for generated or AI-assisted images, models, textures, UI art, audio, and reference packs.

## Intake

Create or update a register entry before generation. Minimum fields: asset id, purpose, asset type, target path, references, approved prompt status, model/provider, parameters, candidate count, staging path, final path, license/provenance, QA owner, and validation plan.

## Prompt Approval

Draft prompts in Docs/Prompts/APPROVED_PROMPTS.md using Docs/Prompts/PROMPT_CONTRACTS.md. Do not silently expand an approved prompt during the tool call. If a prompt needs improvement, revise it in the doc first.

## Production Route

- Concept/style/UI/reference image: use AIART image generation when a bitmap reference helps.
- Natural props, rough creatures, mood exploration, or mid-distance organic assets: generate 3D candidates, then clean in Blender/DCC.
- Modular architecture, measured props, hard surface, collision, LOD, or batch repair: use Blender MCP or manual DCC directly.
- Characters, cloth, hair, facial expressions, weights, and high-quality animation: use generated baselines only as rough candidates; expect specialist DCC/manual correction.

## UE Import

Prefer GLB/FBX staging for review. Final UE import must check scale, pivot, normals, UVs, material slots, texture settings, collision, LOD/Nanite, skeleton/retargeting, and Data Validation.
