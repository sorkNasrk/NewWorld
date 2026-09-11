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
    "staging_path": str,
    "target_path": str,
    "prompt": dict,
    "provenance": dict,
    "qa": dict,
    "validation": dict,
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


def validate_manifest(data):
    errors = []
    for key, expected_type in ROOT_REQUIRED.items():
        if key not in data:
            errors.append(f"missing root key: {key}")
        elif not isinstance(data[key], expected_type):
            errors.append(f"root key {key} must be {expected_type.__name__}")

    if data.get("project") != "NewWorld":
        errors.append("project must be NewWorld")

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
        staging_path = normalize_path(asset.get("staging_path", ""))
        if staging_path and not staging_path.startswith("Content/NewWorld/AIWork"):
            errors.append(f"{prefix}.staging_path must be under Content/NewWorld/AIWork")
        target_path = normalize_path(asset.get("target_path", ""))
        if target_path and target_path != "TBD" and not target_path.startswith("Content/NewWorld"):
            errors.append(f"{prefix}.target_path must be under Content/NewWorld or TBD")
        prompt = asset.get("prompt", {})
        if isinstance(prompt, dict) and prompt.get("approved") is True and not prompt.get("text"):
            errors.append(f"{prefix}.prompt.text is required when prompt.approved is true")
        provenance = asset.get("provenance", {})
        if isinstance(provenance, dict) and asset.get("status") not in (None, "draft_prompt", "approved_prompt") and not provenance.get("source_tool"):
            errors.append(f"{prefix}.provenance.source_tool is required after generation")

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
