#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from newworld_tools.processes import start_detached
from newworld_tools.project import blender_exe, blender_mcp_runtime, find_project_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or open the NewWorld Blender MCP runtime.")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--open-blender", action="store_true")
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args()

    project_root = args.project_root.resolve() if args.project_root else find_project_root(Path(__file__))
    runtime = blender_mcp_runtime(project_root)
    uvx = Path(runtime["command"])
    python_path = Path(runtime["python"]) if runtime.get("python") else None
    blender = blender_exe(project_root)

    for label, path in (("uvx", uvx), ("python", python_path), ("blender", blender)):
        if path is None or not path.exists():
            raise FileNotFoundError(f"Missing required Blender MCP path: {label}={path}")

    if runtime.get("env", {}).get("BLENDER_MCP_SAFE_MODE") != "1":
        raise RuntimeError("BLENDER_MCP_SAFE_MODE=1 is required in .codex/config.toml.")

    print(f"uvx={uvx}")
    print(f"python={python_path}")
    print(f"blender={blender}")
    print("Codex launches blender-mcp from .codex/config.toml with BLENDER_MCP_SAFE_MODE=1.")
    print("Use one Blender instance and one MCP client per asset task.")

    if args.open_blender:
        process = start_detached([blender], cwd=project_root, visible=args.visible)
        print(f"Started Blender PID={process.pid}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
