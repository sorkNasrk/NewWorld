---
name: ue58-blender-mcp-asset
description: Use for NewWorld Blender MCP modeling, image-plane reference matching, blockout, AI 3D cleanup, hard-surface assets, module kits, UVs, collision proxies, LOD prep, screenshots, and UE export staging.
---

# Blender MCP Asset Workflow

Use Blender MCP as a scriptable DCC workstation. It is strongest for reference-based blockout, hard-surface construction, cleanup, naming, material slots, pivots, collision, LOD prep, export, and screenshot evidence.

Read [references/blender-mcp-decision-tree.md](references/blender-mcp-decision-tree.md) before deciding whether to generate a 3D model first or build directly in Blender.

## Required Inputs

- Asset id, dimensions, unit scale, target UE path, and gameplay/camera context.
- Front, side, back, top orthographic references when modeling to a design.
- 3/4 beauty view, silhouette, material swatches, and scale reference.
- Target collections: REF, BLOCKOUT, HIGH, LOW, COLLISION, and EXPORT.
- Project MCP config: .codex/config.toml.
- Runtime preflight: Tools/MCP/start_blender_mcp_session.py.
- StaticMesh FBX export script: Tools/Assets/export_blender_static_mesh_fbx.py.

## Workflow

1. Inspect scene units, objects, collections, materials, cameras, and selection.
2. Place locked image planes for references before shape work.
3. Block out proportions first, then iterate part by part.
4. Use staged .blend and export paths; do not overwrite production Content directly.
5. Before export, check applied transforms, scale, normals, non-manifold geometry, duplicate vertices, UVs, material slots, object names, pivot/origin, collision, and LOD/Nanite policy.
6. Capture front, side, 3/4, wireframe, and material-preview screenshots.
7. Use Tools/Assets/export_blender_static_mesh_fbx.py for static mesh FBX export to UE staging. Pass explicit object names for render meshes and UCX collision meshes whenever possible.
8. Treat GLB/GLTF as Blender or AI 3D interchange formats. The verified UE MCP StaticMesh import path uses FbxFactory through StaticMeshTools.import_file, so export FBX or OBJ before UE MCP import.

## Output

Return changed objects, collection structure, screenshots, export paths, QA results, UE import notes, and reasons for any manual artist follow-up.

## Verification

- Run Tools/MCP/start_blender_mcp_session.py before a Blender MCP task.
- Confirm BLENDER_MCP_SAFE_MODE=1 in .codex/config.toml.
- Run Tools/Assets/export_blender_static_mesh_fbx.py for staged static mesh FBX export; it defaults to Content/NewWorld/AIWork and uses UE centimeter scale.
- Capture front, side, 3/4, wireframe, and material-preview screenshots before UE import.
