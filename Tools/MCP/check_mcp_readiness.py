#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from newworld_tools.net import tcp_port_reachable
from newworld_tools.project import blender_exe, blender_mcp_runtime, find_project_root, load_json, load_toml


REQUIRED_MCP_PLUGINS = {
    "ModelContextProtocol",
    "MCPClientToolset",
    "EditorToolset",
    "GameplayTagsToolset",
    "UMGToolSet",
    "NiagaraToolsets",
    "PCGToolset",
    "AIModuleToolset",
    "AutomationTestToolset",
    "SlateInspectorToolset",
}
FORBIDDEN_PLUGINS = {"AllToolsets", "AIAssistant"}


def add_failure(failures: list[str], message: str) -> None:
    failures.append(message)


def require_path(project_root: Path, relative_path: str, failures: list[str]) -> Path:
    path = project_root / relative_path
    if not path.exists():
        add_failure(failures, f"Missing path: {relative_path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check NewWorld project MCP readiness.")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--require-unreal-running", action="store_true")
    parser.add_argument("--check-codex-cli", action="store_true")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    project_root = args.project_root.resolve() if args.project_root else find_project_root(Path(__file__))
    failures: list[str] = []

    require_path(project_root, ".codex/config.toml", failures)
    require_path(project_root, "Config/DefaultEditorPerProjectUserSettings.ini", failures)
    require_path(project_root, "Config/DefaultGameplayTags.ini", failures)
    require_path(project_root, "NewWorld.uproject", failures)

    try:
        uproject = load_json(project_root / "NewWorld.uproject")
        enabled_plugins = {plugin["Name"] for plugin in uproject.get("Plugins", []) if plugin.get("Enabled")}
        for plugin in sorted(REQUIRED_MCP_PLUGINS):
            if plugin not in enabled_plugins:
                add_failure(failures, f"Required MCP plugin is not enabled: {plugin}")
        for plugin in sorted(FORBIDDEN_PLUGINS):
            if plugin in enabled_plugins:
                add_failure(failures, f"Forbidden experimental plugin is enabled for this phase: {plugin}")
    except Exception as exc:
        add_failure(failures, f"NewWorld.uproject JSON parse failed: {exc}")

    editor_settings_path = project_root / "Config/DefaultEditorPerProjectUserSettings.ini"
    if editor_settings_path.exists():
        editor_settings = editor_settings_path.read_text(encoding="utf-8")
        required_markers = [
            "[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]",
            "ServerUrlPath=/mcp",
            "ServerPortNumber=8000",
            "bEnableToolSearch=True",
        ]
        for marker in required_markers:
            if marker not in editor_settings:
                add_failure(failures, f"Missing MCP settings marker: {marker}")
        if "bAutoStartServer=True" in editor_settings:
            add_failure(failures, "MCP bAutoStartServer must remain False.")

    try:
        codex_config = load_toml(project_root / ".codex/config.toml")
        servers = codex_config.get("mcp_servers", {})
        unreal_mcp = servers.get("unreal-mcp", {})
        if unreal_mcp.get("url") != "http://127.0.0.1:8000/mcp":
            add_failure(failures, "unreal-mcp URL must be http://127.0.0.1:8000/mcp.")
        blender = servers.get("blender", {})
        if not blender:
            add_failure(failures, "Project Codex config missing blender server.")
        if blender.get("env", {}).get("BLENDER_MCP_SAFE_MODE") != "1":
            add_failure(failures, "Blender MCP safe mode must be enabled.")
        if "0.0.0.0" in (project_root / ".codex/config.toml").read_text(encoding="utf-8"):
            add_failure(failures, "MCP config must not bind to 0.0.0.0.")
    except Exception as exc:
        add_failure(failures, f".codex/config.toml parse failed: {exc}")

    runtime = blender_mcp_runtime(project_root)
    for label, path_text in (
        ("uvx", runtime.get("command")),
        ("python", runtime.get("python")),
        ("blender", str(blender_exe(project_root))),
    ):
        if not path_text or not Path(path_text).exists():
            add_failure(failures, f"Missing MCP runtime path: {label}={path_text}")

    reachable = tcp_port_reachable("127.0.0.1", args.port, timeout_seconds=1.5 if args.require_unreal_running else 0.25)
    if args.require_unreal_running:
        if not reachable:
            add_failure(failures, f"UE MCP server is not reachable on 127.0.0.1:{args.port}.")
    else:
        print(f"unrealMcpPort{args.port}Reachable={reachable}")

    if args.check_codex_cli:
        codex = "codex"
        try:
            subprocess.run([codex, "-C", str(project_root), "mcp", "get", "blender"], check=True)
        except Exception as exc:
            add_failure(failures, f"codex could not read the blender MCP server configuration: {exc}")

    print("mcpConfig=.codex/config.toml")
    print("unrealMcpUrl=http://127.0.0.1:8000/mcp")
    print(f"blenderPath={blender_exe(project_root)}")

    if failures:
        print("MCP readiness check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("MCP readiness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

