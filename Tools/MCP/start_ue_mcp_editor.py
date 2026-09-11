#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from newworld_tools.processes import start_detached
from newworld_tools.project import find_project_root, project_file, unreal_editor_exe


def main() -> int:
    parser = argparse.ArgumentParser(description="Start Unreal Editor with the NewWorld UE MCP server.")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args()

    project_root = args.project_root.resolve() if args.project_root else find_project_root(Path(__file__))
    uproject = project_file(project_root)
    editor = unreal_editor_exe()

    if not uproject.exists():
        raise FileNotFoundError(f"Project file not found: {uproject}")
    if not editor.exists():
        raise FileNotFoundError(f"UnrealEditor.exe not found: {editor}")

    process = start_detached(
        [
            editor,
            uproject,
            "-ModelContextProtocolStartServer",
            f"-ModelContextProtocolPort={args.port}",
            "-log",
            "-nosplash",
        ],
        cwd=project_root,
        visible=args.visible,
    )

    print(f"Started Unreal Editor PID={process.pid}")
    print(f"MCP URL: http://127.0.0.1:{args.port}/mcp")
    print(f"Use python Tools/MCP/check_mcp_readiness.py --require-unreal-running after the server finishes loading.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
