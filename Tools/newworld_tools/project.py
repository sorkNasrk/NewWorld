from __future__ import annotations

import json
import os
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any


PROJECT_NAME = "NewWorld"
DEFAULT_UE_ROOT = Path("G:/UnrealEngineInstalled/UE_5.8")
DEFAULT_BLENDER_EXE = Path("G:/blender-5.2.1-windows-x64/blender.exe")
DEFAULT_UVX = Path("C:/Users/happyelements/.local/bin/uvx.exe")


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / "NewWorld.uproject").exists() and (candidate / "AGENTS.md").exists():
            return candidate

    raise RuntimeError(f"Could not find {PROJECT_NAME} project root from {current}")


def add_tools_to_sys_path(script_file: str) -> Path:
    tools_root = Path(script_file).resolve().parents[1]
    if str(tools_root) not in sys.path:
        sys.path.insert(0, str(tools_root))
    return tools_root


def resolve_project_path(project_root: Path, value: str | Path, must_exist: bool = False) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    resolved = candidate.resolve(strict=must_exist)
    if must_exist and not resolved.exists():
        raise FileNotFoundError(str(resolved))
    return resolved


def normalized_path_text(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(str(path))).rstrip("\\/")


def is_under(path: str | Path, root: str | Path) -> bool:
    normalized_path = normalized_path_text(path)
    normalized_root = normalized_path_text(root)
    return normalized_path == normalized_root or normalized_path.startswith(normalized_root + os.sep)


def normalize_manifest_path(value: str | Path) -> str:
    return str(PurePosixPath(str(value).replace("\\", "/")))


def normalize_ue_path(value: str) -> str:
    normalized = value.replace("\\", "/").rstrip("/")
    if not normalized.startswith("/Game/"):
        raise ValueError(f"UE content path must start with /Game/: {value}")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_stdout(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False))


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def ue_root() -> Path:
    return Path(os.environ.get("NEWWORLD_UE_ROOT", str(DEFAULT_UE_ROOT))).resolve(strict=False)


def unreal_editor_exe() -> Path:
    return ue_root() / "Engine/Binaries/Win64/UnrealEditor.exe"


def unreal_editor_cmd_exe() -> Path:
    return ue_root() / "Engine/Binaries/Win64/UnrealEditor-Cmd.exe"


def unreal_build_tool_dotnet() -> Path:
    return ue_root() / "Engine/Binaries/ThirdParty/DotNet/10.0/win-x64/dotnet.exe"


def unreal_build_tool_dll() -> Path:
    return ue_root() / "Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll"


def unreal_build_bat() -> Path:
    return ue_root() / "Engine/Build/BatchFiles/Build.bat"


def project_file(project_root: Path) -> Path:
    return project_root / "NewWorld.uproject"


def blender_exe(project_root: Path | None = None) -> Path:
    configured = os.environ.get("NEWWORLD_BLENDER_EXE")
    if configured:
        return Path(configured).resolve(strict=False)

    if project_root is not None:
        try:
            config = codex_config(project_root)
            blender_env = config.get("mcp_servers", {}).get("blender", {}).get("env", {})
            env_path = blender_env.get("BLENDER_PATH") or blender_env.get("BLENDER_EXE")
            if env_path:
                return Path(env_path).resolve(strict=False)
        except Exception:
            pass

    return DEFAULT_BLENDER_EXE.resolve(strict=False)


def codex_config(project_root: Path) -> dict[str, Any]:
    return load_toml(project_root / ".codex/config.toml")


def blender_mcp_runtime(project_root: Path) -> dict[str, Any]:
    config = codex_config(project_root)
    blender = config.get("mcp_servers", {}).get("blender", {})
    args = list(blender.get("args", []))
    python_path = None
    for index, arg in enumerate(args[:-1]):
        if arg == "--python":
            python_path = args[index + 1]
            break

    uvx_path = os.environ.get("NEWWORLD_UVX") or blender.get("command") or str(DEFAULT_UVX)
    return {
        "command": str(uvx_path),
        "args": args,
        "python": python_path,
        "env": dict(blender.get("env", {})),
        "blender": str(blender_exe(project_root)),
    }
