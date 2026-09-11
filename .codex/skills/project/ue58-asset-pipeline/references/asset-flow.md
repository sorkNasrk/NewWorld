# Asset Flow

Use this flow for generated or AI-assisted images, models, textures, UI art, audio, and reference packs.

## Intake

Create or update a register entry before generation. Minimum fields: asset id, purpose, asset type, creation_route, route_decision_reason, authoring_tools, route_review_status, target path, references, approved prompt status, model/provider, parameters, candidate count, staging path, final path, license/provenance, QA owner, and validation plan.

## Prompt Approval

Draft prompts in Docs/Prompts/APPROVED_PROMPTS.md using Docs/Prompts/PROMPT_CONTRACTS.md. Do not silently expand an approved prompt during the tool call. If a prompt needs improvement, revise it in the doc first.

## Production Route

- Concept/style/UI/reference image: use `ai_image_reference` with AIART image generation when a bitmap reference helps.
- Natural props, rough creatures, mood exploration, or mid-distance organic assets: use `ai_3d_then_blender`, then clean in Blender/DCC.
- Modular architecture, measured props, hard surface, collision, LOD, or batch repair: use `blender_mcp_direct` or `procedural_tool_generated`.
- UE import, metadata, PCG/Niagara/UMG assembly, readback, and screenshots: use `ue_mcp_assembly`.
- Characters, cloth, hair, facial expressions, weights, and high-quality animation: use `manual_dcc_required`; generated baselines are rough candidates only.
- Mixed workflows use `hybrid` and must keep evidence from every route used.

## UE Import

Prefer GLB/FBX staging for review. Final UE import must check scale, pivot, normals, UVs, material slots, texture settings, collision, LOD/Nanite, skeleton/retargeting, creation_route, provenance, and Data Validation.
