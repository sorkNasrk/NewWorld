#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from newworld_tools.project import blender_exe, find_project_root, is_under, resolve_project_path


BLENDER_EXPORT_SCRIPT = r'''
import bpy
import json
import os
import sys


def main():
    output_fbx = os.environ["NEWWORLD_OUTPUT_FBX"]
    object_names = json.loads(os.environ.get("NEWWORLD_EXPORT_OBJECTS", "[]"))

    if object_names:
        objects = []
        missing = []
        not_mesh = []
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if obj is None:
                missing.append(name)
                continue
            if obj.type != "MESH":
                not_mesh.append(f"{name}:{obj.type}")
                continue
            objects.append(obj)
        if missing:
            raise RuntimeError("Missing requested Blender objects: " + ", ".join(missing))
        if not_mesh:
            raise RuntimeError("Requested objects must be MESH: " + ", ".join(not_mesh))
    else:
        objects = [
            obj for obj in bpy.context.scene.objects
            if obj.type == "MESH"
            and not obj.hide_get()
            and not obj.name.startswith("REF_")
            and "ReferencePlane" not in obj.name
        ]

    objects = sorted(objects, key=lambda obj: obj.name)
    if not objects:
        raise RuntimeError("No mesh objects were selected for FBX export.")

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

    os.makedirs(os.path.dirname(output_fbx), exist_ok=True)

    bpy.ops.export_scene.fbx(
        filepath=output_fbx,
        use_selection=True,
        object_types={"MESH"},
        global_scale=100.0,
        axis_forward="-Z",
        axis_up="Y",
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        bake_space_transform=False,
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        use_tspace=True,
        path_mode="AUTO",
    )

    summary = {
        "blend_path": bpy.data.filepath,
        "output_fbx": output_fbx,
        "object_count": len(objects),
        "objects": [
            {
                "name": obj.name,
                "type": obj.type,
                "vertices": len(obj.data.vertices),
                "polygons": len(obj.data.polygons),
                "dimensions": [round(value, 6) for value in obj.dimensions],
                "location": [round(value, 6) for value in obj.location],
                "scale": [round(value, 6) for value in obj.scale],
                "material_slots": [slot.name for slot in obj.material_slots],
            }
            for obj in objects
        ],
    }

    print("NEWWORLD_FBX_EXPORT_SUMMARY " + json.dumps(summary, sort_keys=True))


try:
    main()
except Exception as exc:
    print("NEWWORLD_FBX_EXPORT_ERROR " + repr(exc))
    sys.exit(2)
'''


def split_object_names(values: list[str]) -> list[str]:
    names: list[str] = []
    for value in values:
        names.extend(part.strip() for part in value.split(",") if part.strip())
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description="Export staged Blender mesh objects to an FBX for NewWorld UE import.")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--blend-path", required=True)
    parser.add_argument("--output-fbx", required=True)
    parser.add_argument("--object-names", action="append", default=[])
    parser.add_argument("--allow-outside-aiwork", action="store_true")
    parser.add_argument("--blender-path", type=Path)
    args = parser.parse_args()

    project_root = args.project_root.resolve() if args.project_root else find_project_root(Path(__file__))
    blend_path = resolve_project_path(project_root, args.blend_path, must_exist=True)
    output_fbx = resolve_project_path(project_root, args.output_fbx, must_exist=False)
    blender = args.blender_path.resolve(strict=False) if args.blender_path else blender_exe(project_root)

    if not blender.exists():
        raise FileNotFoundError(f"Blender executable not found: {blender}")
    if blend_path.suffix.lower() != ".blend":
        raise ValueError(f"--blend-path must point to a .blend file: {blend_path}")
    if output_fbx.suffix.lower() != ".fbx":
        raise ValueError(f"--output-fbx must end in .fbx: {output_fbx}")

    aiwork_root = resolve_project_path(project_root, "Content/NewWorld/AIWork", must_exist=True)
    if not args.allow_outside_aiwork and not is_under(output_fbx, aiwork_root):
        raise ValueError(f"--output-fbx must stay under Content/NewWorld/AIWork unless --allow-outside-aiwork is set: {output_fbx}")

    output_fbx.parent.mkdir(parents=True, exist_ok=True)
    object_names = split_object_names(args.object_names)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".py", delete=False) as handle:
        temp_script = Path(handle.name)
        handle.write(BLENDER_EXPORT_SCRIPT)

    env = os.environ.copy()
    env["NEWWORLD_OUTPUT_FBX"] = str(output_fbx)
    env["NEWWORLD_EXPORT_OBJECTS"] = json.dumps(object_names, ensure_ascii=False)

    try:
        completed = subprocess.run(
            [str(blender), "--background", str(blend_path), "--python", str(temp_script)],
            cwd=str(project_root),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finally:
        temp_script.unlink(missing_ok=True)

    if completed.returncode != 0:
        raise RuntimeError(f"Blender FBX export failed with exit code {completed.returncode}.\n{completed.stdout.strip()}")
    if not output_fbx.exists():
        raise RuntimeError(f"Blender reported success but the FBX was not created: {output_fbx}")

    summary_line = None
    for line in completed.stdout.splitlines():
        if line.startswith("NEWWORLD_FBX_EXPORT_SUMMARY "):
            summary_line = line
    if summary_line is None:
        tail = "\n".join(completed.stdout.splitlines()[-20:])
        raise RuntimeError(f"Blender export completed but did not return a NewWorld summary line.\n{tail}")

    summary = json.loads(summary_line[len("NEWWORLD_FBX_EXPORT_SUMMARY "):])
    summary["output_size_bytes"] = output_fbx.stat().st_size
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
