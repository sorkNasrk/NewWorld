#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import PurePosixPath

ROOT_REQUIRED = {
    "schema_version": int,
    "project": str,
    "staging_root": str,
    "production_root": str,
    "assets": list,
}

ASSET_REQUIRED = {
    "asset_id": str,
    "asset_type": str,
    "status": str,
    "creation_route": str,
    "route_decision_reason": str,
    "authoring_tools": list,
    "reference_pack_required": bool,
    "route_review_status": str,
    "staging_path": str,
    "target_path": str,
    "prompt": dict,
    "provenance": dict,
    "qa": dict,
    "validation": dict,
}

VALID_CREATION_ROUTES = {
    "ai_image_reference",
    "ai_3d_then_blender",
    "blender_mcp_direct",
    "ue_mcp_assembly",
    "procedural_tool_generated",
    "manual_dcc_required",
    "hybrid",
}

AI_ROUTES = {
    "ai_image_reference",
    "ai_3d_then_blender",
    "hybrid",
}

TOOL_ROUTES = {
    "blender_mcp_direct",
    "ue_mcp_assembly",
    "procedural_tool_generated",
    "hybrid",
}

VALID_ROUTE_REVIEW_STATUSES = {
    "pending",
    "approved",
    "rejected",
    "not_required",
}

VALID_STATUSES = {
    "draft_prompt",
    "approved_prompt",
    "generated",
    "dcc_cleanup",
    "ue_imported",
    "qa_passed",
    "promoted",
    "rejected",
}

VALID_TYPES = {
    "concept",
    "reference_pack",
    "static_mesh",
    "skeletal_mesh",
    "texture",
    "material",
    "animation",
    "rig",
    "vfx",
    "audio",
    "music",
    "voice",
    "ui",
    "icon",
    "font",
    "cinematic",
    "localization",
}


def normalize_path(value):
    return str(PurePosixPath(str(value).replace('\\\\', '/').replace('\\', '/')))


def status_is_after_generation(status):
    return status in {
        "generated",
        "dcc_cleanup",
        "ue_imported",
        "qa_passed",
        "promoted",
        "rejected",
    }


def validate_manifest(data):
    errors = []
    for key, expected_type in ROOT_REQUIRED.items():
        if key not in data:
            errors.append(f"missing root key: {key}")
        elif not isinstance(data[key], expected_type):
            errors.append(f"root key {key} must be {expected_type.__name__}")

    if data.get("project") != "NewWorld":
        errors.append("project must be NewWorld")
    if data.get("schema_version") != 2:
        errors.append("schema_version must be 2")

    staging_root = normalize_path(data.get("staging_root", "Content/NewWorld/AIWork"))
    production_root = normalize_path(data.get("production_root", "Content/NewWorld"))
    if staging_root != "Content/NewWorld/AIWork":
        errors.append("staging_root must be Content/NewWorld/AIWork")
    if production_root != "Content/NewWorld":
        errors.append("production_root must be Content/NewWorld")

    assets = data.get("assets", [])
    if not isinstance(assets, list):
        return errors

    seen_ids = set()
    for index, asset in enumerate(assets):
        prefix = f"assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{prefix} must be object")
            continue
        for key, expected_type in ASSET_REQUIRED.items():
            if key not in asset:
                errors.append(f"{prefix} missing key: {key}")
            elif not isinstance(asset[key], expected_type):
                errors.append(f"{prefix}.{key} must be {expected_type.__name__}")
        asset_id = asset.get("asset_id")
        if asset_id:
            if asset_id in seen_ids:
                errors.append(f"duplicate asset_id: {asset_id}")
            seen_ids.add(asset_id)
        if asset.get("asset_type") and asset["asset_type"] not in VALID_TYPES:
            errors.append(f"{prefix}.asset_type is not recognized: {asset['asset_type']}")
        if asset.get("status") and asset["status"] not in VALID_STATUSES:
            errors.append(f"{prefix}.status is not recognized: {asset['status']}")
        creation_route = asset.get("creation_route")
        if creation_route and creation_route not in VALID_CREATION_ROUTES:
            errors.append(f"{prefix}.creation_route is not recognized: {creation_route}")
        route_review_status = asset.get("route_review_status")
        if route_review_status and route_review_status not in VALID_ROUTE_REVIEW_STATUSES:
            errors.append(f"{prefix}.route_review_status is not recognized: {route_review_status}")
        if isinstance(asset.get("authoring_tools"), list) and status_is_after_generation(asset.get("status")) and not asset["authoring_tools"]:
            errors.append(f"{prefix}.authoring_tools must not be empty after generation")
        if status_is_after_generation(asset.get("status")) and not str(asset.get("route_decision_reason", "")).strip():
            errors.append(f"{prefix}.route_decision_reason is required after generation")
        if status_is_after_generation(asset.get("status")) and asset.get("status") != "rejected" and route_review_status != "approved":
            errors.append(f"{prefix}.route_review_status must be approved after generation")
        staging_path = normalize_path(asset.get("staging_path", ""))
        if staging_path and not staging_path.startswith("Content/NewWorld/AIWork"):
            errors.append(f"{prefix}.staging_path must be under Content/NewWorld/AIWork")
        target_path = normalize_path(asset.get("target_path", ""))
        if target_path and target_path != "TBD" and not target_path.startswith("Content/NewWorld"):
            errors.append(f"{prefix}.target_path must be under Content/NewWorld or TBD")
        prompt = asset.get("prompt", {})
        if isinstance(prompt, dict) and prompt.get("approved") is True and not prompt.get("text"):
            errors.append(f"{prefix}.prompt.text is required when prompt.approved is true")
        if isinstance(prompt, dict) and creation_route in AI_ROUTES and status_is_after_generation(asset.get("status")):
            if not prompt.get("text"):
                errors.append(f"{prefix}.prompt.text is required for AI creation routes after generation")
            if not (prompt.get("model") or prompt.get("provider")):
                errors.append(f"{prefix}.prompt.model or prompt.provider is required for AI creation routes after generation")
            if not isinstance(prompt.get("parameters"), dict) or not prompt.get("parameters"):
                errors.append(f"{prefix}.prompt.parameters is required for AI creation routes after generation")
        provenance = asset.get("provenance", {})
        if isinstance(provenance, dict) and asset.get("status") not in (None, "draft_prompt", "approved_prompt") and not provenance.get("source_tool"):
            errors.append(f"{prefix}.provenance.source_tool is required after generation")
        if isinstance(provenance, dict) and creation_route in TOOL_ROUTES and status_is_after_generation(asset.get("status")):
            if not any(provenance.get(key) for key in ("source_tool", "script", "operation_record", "seed")):
                errors.append(f"{prefix}.provenance must record source_tool, script, operation_record, or seed for tool-generated routes")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate NewWorld AI asset manifest.")
    parser.add_argument("manifest", nargs="?", default="Docs/Assets/AI_ASSET_MANIFEST.json")
    args = parser.parse_args()

    try:
        with open(args.manifest, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:
        print(f"manifest-error: failed to read JSON: {exc}", file=sys.stderr)
        return 1

    errors = validate_manifest(data)
    if errors:
        print("manifest-error:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"manifest-ok: {args.manifest}; assets={len(data.get('assets', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
