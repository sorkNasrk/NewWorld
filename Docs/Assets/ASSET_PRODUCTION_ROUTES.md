# Asset Production Routes

Use this route table before drafting prompts, generating assets, using Blender MCP, or importing content into UE. Every manifest entry records the chosen route in `creation_route` and explains the reason in `route_decision_reason`.

| Route | Use For | Primary Tools | Required Evidence | Rework Threshold |
| --- | --- | --- | --- | --- |
| `ai_image_reference` | concept art, style boards, orthographic reference packs, UI/icon source images | AIART image generation with `inferenceMode: "gpt"` unless explicitly overridden | approved prompt, references, candidate sheet, selected reason, license/provenance | regenerate if subject, silhouette, view, or style language is wrong after two prompt revisions |
| `ai_3d_then_blender` | natural rocks, ruins, vegetation block-ins, rough creature bases, mid-distance organic props | AI 3D generation, Blender cleanup, FBX export | model/provider/parameters, candidate count, GLB/OBJ/FBX source, Blender screenshots, cleanup notes | regenerate when category, silhouette, proportions, pose, or topology are fundamentally wrong |
| `blender_mcp_direct` | modular architecture, hard-surface props, measured set pieces, collision proxies, LOD prep, pivot/origin fixes | Blender MCP or Blender background Python | reference image planes, dimensions, object list, material slots, collision objects, export summary | rebuild in Blender when shape is dimensionally wrong; do not switch to AI 3D for precision problems |
| `ue_mcp_assembly` | UE staging imports, metadata, actor/Widget/PCG/Niagara prototypes, readback and screenshots | UE MCP selected toolsets | MCP audit, changed asset list, screenshot or thumbnail, Data Validation plan | stop on unexpected production Content writes or incomplete readback |
| `procedural_tool_generated` | deterministic PCG, batch-generated meshes, scripted variants, repeatable UI/icon sheets | project scripts, Blender Python, UE PCG/Niagara/UMG tools | script name/version, seed, parameters, generated file list, validation output | rerun with fixed parameters if repeatability or naming fails |
| `manual_dcc_required` | hero characters, facial rigs, hair, cloth, final weights, final animation, high-end deformation | Blender/Maya/Substance/Reaper/manual specialist work | artist notes, source files, review screenshots, import settings, QA owner | AI output is only a rough candidate; specialist review is mandatory before UE promotion |
| `hybrid` | assets needing more than one route, such as AI concept -> Blender model -> UE MCP import | task-specific combination | evidence from every route used and a single promotion checklist | stop after three failed loops and write an AI production retrospective |

## Default Decisions

- Use AI first when variety, silhouette exploration, natural irregularity, or visual direction is the unknown.
- Use Blender MCP or deterministic tools first when dimensions, snap, pivots, collision, LOD, material slots, or repeatability are the unknown.
- Use UE MCP for import, assembly, metadata, readback, screenshots, and editor-side validation, not as the source of truth for final art quality.
- Use manual DCC review for deformation quality, face/hair/cloth, hero animation, final skin weights, and assets seen close to the camera.

## Manifest Fields

Each asset entry must include:

~~~json
{
  "creation_route": "ai_3d_then_blender",
  "route_decision_reason": "Organic mid-distance rock where silhouette variation matters more than exact dimensions.",
  "authoring_tools": ["AIART 3D", "Blender", "UE MCP"],
  "reference_pack_required": true,
  "route_review_status": "approved"
}
~~~

Allowed `route_review_status` values are `pending`, `approved`, `rejected`, and `not_required`.

## Promotion Gate

Before an asset moves out of `Content/NewWorld/AIWork`, the route, prompt/provenance, source files, UE import readback, screenshots, QA checklist, and Data Validation result must agree. A route mismatch is a production blocker, even when the imported `.uasset` loads correctly.

