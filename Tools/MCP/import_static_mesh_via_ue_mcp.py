#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from newworld_tools.mcp_client import McpClient, tool_text, tool_value
from newworld_tools.net import tcp_port_reachable
from newworld_tools.project import find_project_root, is_under, normalize_ue_path, resolve_project_path


ASSET_NAME_RE = re.compile(r"^SM_[A-Za-z0-9]+_[A-Za-z0-9]+_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)?$")
AIWORK_ROOT = "/Game/NewWorld/AIWork"


def under_ue_aiwork(path: str) -> bool:
    return path == AIWORK_ROOT or path.startswith(AIWORK_ROOT + "/")


def capture_image_data(result: dict[str, Any]) -> str | None:
    value = tool_value(result)
    if isinstance(value, dict) and value.get("data"):
        return str(value["data"])
    for item in result.get("content", []) or []:
        if isinstance(item, dict) and item.get("type") == "image" and item.get("data"):
            return str(item["data"])
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a staged StaticMesh into NewWorld through UE MCP.")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--source-file", required=True)
    parser.add_argument("--folder-path", required=True)
    parser.add_argument("--asset-name", required=True)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--import-materials", action="store_true")
    parser.add_argument("--import-textures", action="store_true")
    parser.add_argument("--no-combine-meshes", dest="combine_meshes", action="store_false", default=True)
    parser.add_argument("--evidence-directory")
    parser.add_argument("--allow-outside-aiwork", action="store_true")
    args = parser.parse_args()

    project_root = args.project_root.resolve() if args.project_root else find_project_root(Path(__file__))
    source_file = resolve_project_path(project_root, args.source_file, must_exist=True)
    extension = source_file.suffix.lower()
    if extension in {".glb", ".gltf"}:
        raise RuntimeError(
            "StaticMeshTools.import_file rejected .glb/.gltf in the 2026-09-11 NewWorld UE5.8 test; "
            "the current toolset path uses FbxFactory and observed supported source extensions are .fbx and .obj. "
            "Export or convert to .fbx or .obj before this MCP import path."
        )
    if extension not in {".fbx", ".obj"}:
        raise ValueError(f"--source-file must be .fbx or .obj for StaticMeshTools.import_file: {source_file}")

    folder_path = normalize_ue_path(args.folder_path)
    if not args.allow_outside_aiwork and not under_ue_aiwork(folder_path):
        raise ValueError(f"--folder-path must stay under /Game/NewWorld/AIWork unless --allow-outside-aiwork is set: {folder_path}")

    if not ASSET_NAME_RE.match(args.asset_name):
        raise ValueError(f"--asset-name must follow the NewWorld static mesh format SM_[Name]_[Descriptor]_[Variant]: {args.asset_name}")

    asset_path = f"{folder_path}/{args.asset_name}"
    evidence_path: Path | None = None
    if args.evidence_directory:
        evidence_path = resolve_project_path(project_root, args.evidence_directory, must_exist=False)
        evidence_root = resolve_project_path(project_root, "Docs/Planning/MCP_Evidence", must_exist=False)
        if not is_under(evidence_path, evidence_root):
            raise ValueError(f"--evidence-directory must stay under Docs/Planning/MCP_Evidence: {evidence_path}")
        evidence_path.mkdir(parents=True, exist_ok=True)

    if not tcp_port_reachable("127.0.0.1", args.port, timeout_seconds=1.5):
        raise RuntimeError(
            f"UE MCP server is not reachable on 127.0.0.1:{args.port}. "
            f"Start it with python Tools/MCP/start_ue_mcp_editor.py --port {args.port}."
        )

    with McpClient(port=args.port, client_name="NewWorld.Tools.MCP.ImportStaticMesh") as client:
        tools_response = client.json_rpc("tools/list", timeout_seconds=15)
        tool_names = {
            tool.get("name")
            for tool in tools_response["json"].get("result", {}).get("tools", [])
            if isinstance(tool, dict)
        }
        for required_tool in ("list_toolsets", "describe_toolset", "call_tool"):
            if required_tool not in tool_names:
                raise RuntimeError(f"UE MCP tool-search mode did not expose required meta tool: {required_tool}")

        static_mesh_description = client.tool(
            "describe_toolset",
            {"toolset_name": "editor_toolset.toolsets.static_mesh.StaticMeshTools"},
            timeout_seconds=15,
        )
        if "import_file" not in tool_text(static_mesh_description):
            raise RuntimeError("StaticMeshTools description did not include import_file.")

        client.toolset_tool(
            "editor_toolset.toolsets.asset.AssetTools",
            "create_folder",
            {"path": folder_path},
            timeout_seconds=30,
        )

        exists_before = bool(tool_value(client.toolset_tool(
            "editor_toolset.toolsets.asset.AssetTools",
            "exists",
            {"path": asset_path},
            timeout_seconds=15,
        )))
        if exists_before and not args.allow_overwrite:
            raise RuntimeError(f"Target asset already exists: {asset_path}. Re-run with --allow-overwrite only for reviewed staging overwrites.")
        if exists_before:
            client.toolset_tool(
                "editor_toolset.toolsets.asset.AssetTools",
                "delete",
                {"path": asset_path},
                timeout_seconds=30,
            )

        imported = tool_value(client.toolset_tool(
            "editor_toolset.toolsets.static_mesh.StaticMeshTools",
            "import_file",
            {
                "folder_path": folder_path,
                "asset_name": args.asset_name,
                "source_file": str(source_file),
                "import_materials": bool(args.import_materials),
                "import_textures": bool(args.import_textures),
                "combine_meshes": bool(args.combine_meshes),
            },
            timeout_seconds=120,
        ))

        client.toolset_tool(
            "editor_toolset.toolsets.asset.AssetTools",
            "load_asset",
            {"asset_path": asset_path},
            timeout_seconds=30,
        )

        metadata = {
            "NewWorld.Workflow": "UE_MCP_StaticMesh_Import",
            "NewWorld.Staging": "AIWork",
            "NewWorld.MCP": "true",
            "NewWorld.SourceFile": str(source_file),
            "NewWorld.ImportedBy": "Tools/MCP/import_static_mesh_via_ue_mcp.py",
            "NewWorld.ImportedAtUtc": dt.datetime.now(dt.UTC).isoformat(),
        }
        client.toolset_tool(
            "editor_toolset.toolsets.asset.AssetTools",
            "update_metadata_tags",
            {
                "asset_path": asset_path,
                "set_tags": metadata,
            },
            timeout_seconds=30,
        )

        save_result = tool_value(client.toolset_tool(
            "editor_toolset.toolsets.asset.AssetTools",
            "save_assets",
            {"asset_paths": [asset_path]},
            timeout_seconds=60,
        ))

        mesh_ref = {"refPath": f"{asset_path}.{args.asset_name}"}
        readback = {
            "class": tool_value(client.toolset_tool("editor_toolset.toolsets.asset.AssetTools", "get_asset_class", {"asset_path": asset_path}, timeout_seconds=15)),
            "material_slots": tool_value(client.toolset_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools", "get_material_slots", {"mesh": mesh_ref}, timeout_seconds=15)),
            "bounds": tool_value(client.toolset_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools", "get_bounds", {"mesh": mesh_ref}, timeout_seconds=15)),
            "triangles_lod0": tool_value(client.toolset_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools", "get_triangle_count", {"mesh": mesh_ref, "lod_index": 0}, timeout_seconds=15)),
            "vertices_lod0": tool_value(client.toolset_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools", "get_vertex_count", {"mesh": mesh_ref, "lod_index": 0}, timeout_seconds=15)),
            "lod_count": tool_value(client.toolset_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools", "get_lod_count", {"mesh": mesh_ref}, timeout_seconds=15)),
            "nanite_enabled": tool_value(client.toolset_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools", "is_nanite_enabled", {"mesh": mesh_ref}, timeout_seconds=15)),
            "metadata": tool_value(client.toolset_tool("editor_toolset.toolsets.asset.AssetTools", "get_metadata_tags", {"asset_path": asset_path}, timeout_seconds=15)),
        }

        thumbnail_path = None
        if evidence_path:
            capture_result = client.toolset_tool(
                "EditorToolset.EditorAppToolset",
                "CaptureAssetImage",
                {"AssetPath": asset_path},
                timeout_seconds=60,
            )
            image_data = capture_image_data(capture_result)
            if not image_data:
                raise RuntimeError(f"CaptureAssetImage did not return image content for {asset_path}.")
            thumbnail = evidence_path / f"{args.asset_name}_ue_asset_thumbnail.png"
            thumbnail.write_bytes(base64.b64decode(image_data))
            thumbnail_path = str(thumbnail)

    summary = {
        "mcp_url": f"http://127.0.0.1:{args.port}/mcp",
        "source_file": str(source_file),
        "folder_path": folder_path,
        "asset_name": args.asset_name,
        "asset_path": asset_path,
        "existed_before": exists_before,
        "allow_overwrite": bool(args.allow_overwrite),
        "import_materials": bool(args.import_materials),
        "import_textures": bool(args.import_textures),
        "combine_meshes": bool(args.combine_meshes),
        "imported": imported,
        "saved": save_result,
        "readback": readback,
        "evidence_thumbnail": thumbnail_path,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
