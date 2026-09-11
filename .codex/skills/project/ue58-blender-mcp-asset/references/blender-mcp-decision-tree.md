# Blender MCP Decision Tree

## Generate First, Then Clean In Blender

Use `ai_3d_then_blender` for natural rocks, ruins, vegetation block-ins, rough creatures, style exploration, mid-distance props, and assets where silhouette variety matters more than exact dimensions.

Reject and regenerate when category, silhouette, proportions, pose, or topology are fundamentally wrong.

## Build Directly In Blender MCP

Use `blender_mcp_direct` for modular architecture, hard-surface props, measured set pieces, collision proxies, LOD preparation, pivot/origin fixes, UV/material-slot cleanup, and batch repairs.

Require orthographic references and dimensions before asking Blender MCP to build precise assets.

## Specialist DCC Required

Use `manual_dcc_required` for characters, facial rigs, hair, cloth, final skin weights, hero animation, and high-quality deformation. Blender MCP can stage, inspect, rename, and export, but should not be the only quality gate.

## Reference Images

Best reference packs include front, side, back, and top orthographic views without perspective distortion; one 3/4 beauty view; silhouette; material swatches; callouts for separable parts; and a scale object.

## NewWorld MCP Defaults

Use the project-level .codex/config.toml blender server. It launches uvx with Python 3.12 and BLENDER_MCP_SAFE_MODE=1. Do not modify user-level Codex MCP registrations for project work.

Before using Blender MCP, run:

~~~powershell
python Tools/MCP/start_blender_mcp_session.py
~~~
