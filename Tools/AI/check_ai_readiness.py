#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from newworld_tools.project import blender_exe, codex_config, find_project_root, load_json


REQUIRED_PATHS = [
    "AGENTS.md",
    ".agents/ue-project-context.md",
    ".agents/skills-index.md",
    ".codex/agents",
    ".codex/skills/project",
    ".codex/skills/vendor/gamedev-skills",
    ".codex/skills/vendor/quodsoler-unreal-engine-skills",
    ".codex/config.toml",
    "Docs/AI_Codex_UE58_GameDev_Guide.md",
    "Docs/Assets/AI_ASSET_REGISTER.md",
    "Docs/Assets/AI_ASSET_MANIFEST.json",
    "Docs/Assets/AI_ASSET_QA_CHECKLISTS.md",
    "Docs/Assets/ASSET_PRODUCTION_ROUTES.md",
    "Docs/Prompts/PROMPT_CONTRACTS.md",
    "Docs/Prompts/APPROVED_PROMPTS.md",
    "Docs/Audio/AUDIO_BRIEF.md",
    "Docs/Art/ART_DIRECTION_BRIEF.md",
    "Docs/Planning/MCP_OPERATION_AUDIT.md",
    "Docs/Planning/AI_PRODUCTION_RETROSPECTIVES.md",
    "Tools/newworld_tools/__init__.py",
    "Tools/newworld_tools/project.py",
    "Tools/newworld_tools/net.py",
    "Tools/newworld_tools/processes.py",
    "Tools/newworld_tools/mcp_client.py",
    "Tools/AI/check_ai_readiness.py",
    "Tools/AI/validate_ai_asset_manifest.py",
    "Tools/Assets/export_blender_static_mesh_fbx.py",
    "Tools/MCP/check_mcp_readiness.py",
    "Tools/MCP/start_ue_mcp_editor.py",
    "Tools/MCP/start_blender_mcp_session.py",
    "Tools/MCP/import_static_mesh_via_ue_mcp.py",
    "Config/DefaultEditorPerProjectUserSettings.ini",
    "Config/DefaultGameplayTags.ini",
    "Source/NewWorldEditor.Target.cs",
    "Source/NewWorldEditor/NewWorldEditor.Build.cs",
    "Source/NewWorldEditor/Private/NewWorldEditorModule.cpp",
    "Source/NewWorldEditor/Private/NewWorldAssetPolicyValidator.h",
    "Source/NewWorldEditor/Private/NewWorldAssetPolicyValidator.cpp",
    "NewWorld.uproject",
]

ACTIVE_REFERENCE_FILES = [
    "AGENTS.md",
    ".agents/ue-project-context.md",
    ".agents/skills-index.md",
    "Docs/AI_Codex_UE58_GameDev_Guide.md",
    "Docs/Assets/AI_ASSET_QA_CHECKLISTS.md",
    "Docs/Assets/ASSET_PRODUCTION_ROUTES.md",
    "Docs/Prompts/PROMPT_CONTRACTS.md",
]

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


def add_failure(failures: list[str], message: str) -> None:
    failures.append(message)


def require_marker(path: Path, marker: str, failures: list[str]) -> None:
    if marker not in path.read_text(encoding="utf-8"):
        add_failure(failures, f"{path.as_posix()} missing marker: {marker}")


def count_skill_dirs(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for child in path.iterdir() if child.is_dir() and (child / "SKILL.md").exists())


def main() -> int:
    project_root = find_project_root(Path(__file__))
    failures: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (project_root / relative_path).exists():
            add_failure(failures, f"Missing path: {relative_path}")

    legacy_script_suffix = ".ps" + "1"
    ps1_files = [path for path in (project_root / "Tools").rglob("*" + legacy_script_suffix)]
    for path in ps1_files:
        add_failure(failures, f"Legacy PowerShell script remains under Tools: {path.relative_to(project_root).as_posix()}")

    for relative_path in ACTIVE_REFERENCE_FILES:
        path = project_root / relative_path
        if path.exists() and legacy_script_suffix in path.read_text(encoding="utf-8"):
            add_failure(failures, f"Active project reference still mentions legacy PowerShell scripts: {relative_path}")

    if (project_root / ".ignore").exists():
        add_failure(failures, ".ignore exists at project root; remove it unless there is an explicit reviewed need.")

    gitignore = (project_root / ".gitignore").read_text(encoding="utf-8").splitlines() if (project_root / ".gitignore").exists() else []
    for pattern in [".vscode/", "*.code-workspace", "Binaries/", "Intermediate/", "Saved/", "DerivedDataCache/"]:
        if pattern not in gitignore:
            add_failure(failures, f".gitignore missing pattern: {pattern}")

    try:
        manifest = load_json(project_root / "Docs/Assets/AI_ASSET_MANIFEST.json")
        for key in ["schema_version", "project", "staging_root", "production_root", "assets"]:
            if key not in manifest:
                add_failure(failures, f"Manifest missing root key: {key}")
        if manifest.get("project") != "NewWorld":
            add_failure(failures, "Manifest project is not NewWorld.")
        if manifest.get("schema_version") != 2:
            add_failure(failures, "Manifest schema_version must be 2.")
        if not isinstance(manifest.get("assets"), list):
            add_failure(failures, "Manifest missing assets array.")
    except Exception as exc:
        add_failure(failures, f"Manifest JSON parse failed: {exc}")

    try:
        uproject = load_json(project_root / "NewWorld.uproject")
        module_names = {module.get("Name") for module in uproject.get("Modules", [])}
        if "NewWorldEditor" not in module_names:
            add_failure(failures, "NewWorld.uproject missing NewWorldEditor module.")
        enabled_plugins = {plugin.get("Name") for plugin in uproject.get("Plugins", []) if plugin.get("Enabled")}
        for plugin in sorted(REQUIRED_MCP_PLUGINS):
            if plugin not in enabled_plugins:
                add_failure(failures, f"Required selected MCP plugin not enabled: {plugin}")
        for plugin in ("AllToolsets", "AIAssistant"):
            if plugin in enabled_plugins:
                add_failure(failures, f"Forbidden experimental plugin enabled for this phase: {plugin}")
        if "DataValidation" not in enabled_plugins:
            add_failure(failures, "DataValidation plugin must be enabled for project asset policy checks.")
    except Exception as exc:
        add_failure(failures, f"NewWorld.uproject JSON parse failed: {exc}")

    build_cs = project_root / "Source/NewWorldEditor/NewWorldEditor.Build.cs"
    if build_cs.exists():
        for module in ["UnrealEd", "DataValidation", "AssetRegistry", "Json", "Engine"]:
            require_marker(build_cs, f'"{module}"', failures)

    validator = project_root / "Source/NewWorldEditor/Private/NewWorldAssetPolicyValidator.cpp"
    if validator.exists():
        for marker in [
            "/Game/NewWorld",
            "/Game/NewWorld/AIWork",
            "AI_ASSET_MANIFEST.json",
            "qa_passed",
            "promoted",
            "UStaticMesh",
            "UTexture2D",
            "UMaterialInterface",
            "creation_route",
        ]:
            require_marker(validator, marker, failures)

    editor_settings = project_root / "Config/DefaultEditorPerProjectUserSettings.ini"
    if editor_settings.exists():
        text = editor_settings.read_text(encoding="utf-8")
        for marker in [
            "[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]",
            "ServerUrlPath=/mcp",
            "ServerPortNumber=8000",
            "bEnableToolSearch=True",
        ]:
            if marker not in text:
                add_failure(failures, f"Missing ModelContextProtocol settings marker: {marker}")
        if "bAutoStartServer=True" in text:
            add_failure(failures, "MCP bAutoStartServer must remain False.")

    try:
        config = codex_config(project_root)
        servers = config.get("mcp_servers", {})
        if servers.get("unreal-mcp", {}).get("url") != "http://127.0.0.1:8000/mcp":
            add_failure(failures, "unreal-mcp URL must be http://127.0.0.1:8000/mcp.")
        if servers.get("blender", {}).get("env", {}).get("BLENDER_MCP_SAFE_MODE") != "1":
            add_failure(failures, "Blender MCP safe mode must be enabled.")
    except Exception as exc:
        add_failure(failures, f".codex/config.toml parse failed: {exc}")

    for script, markers in {
        "Tools/Assets/export_blender_static_mesh_fbx.py": [
            "Content/NewWorld/AIWork",
            "global_scale=100.0",
            'object_types={"MESH"}',
            "NEWWORLD_FBX_EXPORT_SUMMARY",
        ],
        "Tools/MCP/import_static_mesh_via_ue_mcp.py": [
            "/Game/NewWorld/AIWork",
            "StaticMeshTools.import_file",
            ".glb",
            "call_tool",
            "refPath",
            "NewWorld.SourceFile",
        ],
        "Tools/newworld_tools/mcp_client.py": [
            "Mcp-Session-Id",
            "tools/call",
            "text/event-stream",
        ],
        "Docs/Assets/ASSET_PRODUCTION_ROUTES.md": [
            "ai_3d_then_blender",
            "blender_mcp_direct",
            "manual_dcc_required",
        ],
        "Docs/Prompts/PROMPT_CONTRACTS.md": [
            "creation_route",
            "route_decision_reason",
            "authoring_tools",
        ],
    }.items():
        path = project_root / script
        if path.exists():
            for marker in markers:
                require_marker(path, marker, failures)

    project_skill_count = count_skill_dirs(project_root / ".codex/skills/project")
    agent_count = len(list((project_root / ".codex/agents").glob("*.toml"))) if (project_root / ".codex/agents").exists() else 0
    gamedev_count = count_skill_dirs(project_root / ".codex/skills/vendor/gamedev-skills")
    quod_count = count_skill_dirs(project_root / ".codex/skills/vendor/quodsoler-unreal-engine-skills")

    if project_skill_count != 9:
        add_failure(failures, f"Expected 9 project skills, found {project_skill_count}.")
    if agent_count != 14:
        add_failure(failures, f"Expected 14 project agents, found {agent_count}.")
    if gamedev_count != 26:
        add_failure(failures, f"Expected 26 gamedev vendored skills, found {gamedev_count}.")
    if quod_count != 27:
        add_failure(failures, f"Expected 27 quodsoler vendored skills, found {quod_count}.")

    try:
        for path in (project_root / ".codex/agents").glob("*.toml"):
            with path.open("rb") as handle:
                tomllib.load(handle)
        print("agent-toml-ok")
    except Exception as exc:
        add_failure(failures, f"Agent TOML parse check failed: {exc}")

    print(f"projectSkillCount={project_skill_count}")
    print(f"agentCount={agent_count}")
    print(f"gamedevVendorSkillCount={gamedev_count}")
    print(f"quodsolerVendorSkillCount={quod_count}")

    mcp_check = subprocess.run(
        [sys.executable, str(project_root / "Tools/MCP/check_mcp_readiness.py")],
        cwd=str(project_root),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(mcp_check.stdout, end="")
    if mcp_check.returncode != 0:
        add_failure(failures, "MCP readiness check failed.")

    if not blender_exe(project_root).exists():
        add_failure(failures, f"Blender executable not found: {blender_exe(project_root)}")

    if failures:
        print("AI readiness check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("AI readiness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
