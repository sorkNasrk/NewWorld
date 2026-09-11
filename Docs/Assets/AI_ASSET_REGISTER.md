# AI Asset Register

This register tracks generated or AI-assisted assets before they become production content. Current project state: no generated production assets have been approved yet.

Use this file for human-readable production history. Keep machine-readable state in Docs/Assets/AI_ASSET_MANIFEST.json.

## Entry Template

Copy this block when a task creates or materially edits a generated asset.

~~~markdown
### Asset ID: SM_AI_Rock_Cliff_A_WIP

- Role:
- Asset type: concept / reference / static_mesh / skeletal_mesh / texture / material / animation / vfx / audio / music / voice / ui / font / cinematic / localization
- Status: draft_prompt / approved_prompt / generated / dcc_cleanup / ue_imported / qa_passed / promoted / rejected
- creation_route: ai_image_reference / ai_3d_then_blender / blender_mcp_direct / ue_mcp_assembly / procedural_tool_generated / manual_dcc_required / hybrid
- route_decision_reason:
- authoring_tools:
- reference_pack_required: true / false
- route_review_status: pending / approved / rejected / not_required
- Source tool:
- Model/provider:
- Parameters:
- Prompt status: draft / approved / generated
- Approved prompt:
- Prompt call rule: pass approved prompt verbatim; no silent rewrite
- References: front/side/back/top orthographic, 3/4 beauty, silhouette, material swatches, scale reference, audio reference, or UI flow
- Generated at:
- Task/request id:
- Candidate count:
- Selected candidate reason:
- Blender staging file:
- Blender MCP screenshots: front, side, 3/4, wireframe, material preview
- Staging path: Content/NewWorld/AIWork/...
- Final path:
- License/provenance:
- DCC cleanup: scale, pivot, normals, topology, UV, materials, collision, LOD/Nanite, skeleton/rig as applicable
- UE import QA: import settings, material slots, texture groups, Sound Cue/MetaSound, Font Asset, UI states, Data Validation
- Approval owner/date:
- Rejection or rework threshold:
~~~

## Promotion Rule

An asset can move from AIWork to a production path only after the manifest entry, QA checklist, provenance, UE import review, and required validation are complete.
