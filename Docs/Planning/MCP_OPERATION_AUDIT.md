# MCP Operation Audit

Use this template before and after UE MCP, Blender MCP, editor scripting, or any tool call that can modify editor state, assets, Blueprint graphs, materials, scenes, generated files, or Codex config.

## Operation Template

- Date:
- Operator/agent:
- Tool/server:
- Mode: UE MCP / Blender MCP / editor script / other
- Purpose:
- Git recovery point:
- Project MCP config checked: .codex/config.toml / other
- UE MCP state: not running / running at 127.0.0.1:8000/mcp / not applicable
- Blender MCP safe mode confirmed: yes / no / not applicable
- Read-only discovery commands:
- Target paths/assets/objects:
- Allowed write scope:
- Explicitly forbidden paths:
- Python/script execution needed: yes / no
- Network access needed: yes / no
- .codex/config.toml risk: none / read-only / draft only / manual merge
- Manifest/provenance update:
- Screenshot evidence required:
- Logs required:
- Validation plan:
- Rollback plan:
- Preflight reviewer:
- Result:
- Changed assets/objects:
- Screenshots/logs captured:
- Validation result:
- Remaining risk:

## Stop Conditions

- Tool attempts to write outside allowed scope.
- Tool attempts to overwrite .codex/config.toml or user-level Codex config.
- UE MCP is not reachable after a task requires live UE tooling.
- Blender MCP safe mode is not confirmed before Blender writes.
- AllToolsets or AIAssistant is enabled without a separate reviewed task.
- Generated or modified assets lack manifest/provenance path.
- Screenshots or logs cannot be captured for a visual/editor change.
- Repeated repair attempts reach the threshold defined in the relevant skill.

## Current Project Defaults

- UE MCP server: http://127.0.0.1:8000/mcp.
- UE MCP startup: manual only through Tools/MCP/start_ue_mcp_editor.ps1.
- UE MCP tool discovery: bEnableToolSearch=True.
- Blender MCP: project-level .codex/config.toml, BLENDER_MCP_SAFE_MODE=1.
- Production Content writes: forbidden unless the task names the exact reviewed target and rollback path.

## Operation Records

### 2026-09-11 UE MCP GLB Import Staging Dry Run

- Date: 2026-09-11 Asia/Shanghai.
- Operator/agent: Codex.
- Tool/server: unreal-mcp at http://127.0.0.1:8000/mcp.
- Mode: UE MCP.
- Purpose: Import the Blender MCP dry-run mesh source into UE staging content, verify imported assets through read-only MCP queries, run Data Validation, and shut down the temporary Editor process.
- Git recovery point: eb738f0c2a0037d3cc0cc739aa9a0cfbef827d57.
- Project MCP config checked: .codex/config.toml.
- UE MCP state: pending manual script start through Tools/MCP/start_ue_mcp_editor.ps1 -Port 8000.
- Blender MCP safe mode confirmed: not applicable.
- Read-only discovery commands: codex -C G:\NewWorld mcp list; codex -C G:\NewWorld mcp get unreal-mcp; JSON-RPC initialize; tools/list; resources/list; list_toolsets; describe_toolset for AssetTools, StaticMeshTools, and Logs before import.
- Target paths/assets/objects: source files Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.glb and fallback FBX export; UE package path /Game/NewWorld/AIWork/MCP_DryRun.
- Allowed write scope: /Game/NewWorld/AIWork/MCP_DryRun and matching Content/NewWorld/AIWork/MCP_DryRun filesystem packages only.
- Explicitly forbidden paths: production Content/NewWorld directories outside AIWork, .codex/config.toml, user-level Codex config, user-level skills, Project Settings outside import side effects.
- Python/script execution needed: yes for deterministic Blender background FBX export after UE MCP reported that StaticMeshTools.import_file uses FbxFactory and does not support .glb.
- Network access needed: local loopback only.
- .codex/config.toml risk: read-only.
- Manifest/provenance update: not applicable; this is a committed dry-run staging asset, not production AI generation or promotion.
- Screenshot evidence required: UE asset thumbnail captured after import; no level placement planned.
- Logs required: UE MCP tool outputs, LogModelContextProtocol and import/log excerpts, generated package list, process shutdown check.
- Validation plan: MCP readiness with UE running, Data Validation, AI readiness, manifest validation, git diff --check, Git LFS status.
- Rollback plan: delete imported .uasset files under Content/NewWorld/AIWork/MCP_DryRun and this audit record if the dry run should be discarded.
- Preflight reviewer: project MCP rules in ue58-mcp-editor-automation, ue58-content-audit, and ue58-build-test-runner.
- Result: pass for UE MCP staging import after GLB fallback.
- Changed assets/objects: UE MCP StaticMeshTools.import_file first rejected SM_MCP_DryRun_Blockout_A.glb because the tool uses FbxFactory and supports only fbx/obj. A deterministic Blender background export created Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.fbx from the existing staging .blend. UE MCP then imported /Game/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A as a StaticMesh and saved Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.uasset. Metadata tags were added for NewWorld.Workflow=UE_MCP_Import_DryRun, NewWorld.Staging=AIWork, NewWorld.MCP=true, SourceBlend, SourceFbx, SourceGlbUnsupportedByMcpImport=true, and GitRecoveryPoint.
- Screenshots/logs captured: Saved UE asset thumbnail at Docs/Planning/MCP_Evidence/2026-09-11_UE_MCP_Import_DryRun/SM_MCP_DryRun_Blockout_A_ue_asset_thumbnail.png. MCP logs captured the GLB rejection, FBX FactoryCreateFile, FBX scene load, static mesh build, and SavePackage for the imported asset. MCP readback returned class StaticMesh, material slots M_MCP_DryRun_Blockout_Grey and M_MCP_DryRun_Blockout_Blue, bounds min -100/-60/0 and max 100/60/170 cm, 84 triangles, 144 vertices, 1 LOD, Nanite=false, and save_assets=true.
- Validation result: Data Validation passed with 0 errors and 2 expected warnings from NewWorldAssetPolicyValidator: the asset is in AIWork staging and has no matching manifest entry yet. MCP readiness passed after shutdown with unrealMcpPort8000Reachable=False; AI readiness passed; AI_ASSET_MANIFEST.json validation passed with assets=0; git diff --check passed; Git LFS filter applies to the .fbx, .uasset, and UE thumbnail .png files; temporary Unreal Editor PID 83784 was stopped and no UnrealEditor process remained.
- Remaining risk: GLB is not accepted by UE MCP StaticMeshTools.import_file in this UE5.8 toolset, so Blender/AI 3D output needs FBX or OBJ conversion before this MCP import path. This did not test production asset promotion, manifest qa_passed flow, in-level placement, collision behavior in PIE, Nanite/LOD edits, or imported materials/textures.

### 2026-09-11 Blender MCP Safe-Mode Dry Run

- Date: 2026-09-11 Asia/Shanghai.
- Operator/agent: Codex.
- Tool/server: blender via project-level .codex/config.toml.
- Mode: Blender MCP.
- Purpose: Verify project-level Codex can connect to Blender MCP in safe mode, read scene/addon state, create a non-production staging blockout, capture viewport evidence, export a staging GLB, and shut down the temporary Blender process.
- Git recovery point: 7dfb369f078650e5273e852dcd8caa9f6cffc166.
- Project MCP config checked: .codex/config.toml.
- UE MCP state: not running; not applicable for this dry run.
- Blender MCP safe mode confirmed: yes. .codex/config.toml contains BLENDER_MCP_SAFE_MODE=1, and the first write attempt was rejected by safe mode because it imported os.
- Read-only discovery commands: codex -C G:\NewWorld mcp list; codex -C G:\NewWorld mcp get blender; Tools/MCP/start_blender_mcp_session.ps1; blender get_addon_status; blender get_scene_info.
- Target paths/assets/objects: BLD_MCP_DryRun_Blockout test objects only.
- Allowed write scope: Content/NewWorld/AIWork/MCP_DryRun/ and Docs/Planning/MCP_Evidence/2026-09-11_BlenderMCP_DryRun/.
- Explicitly forbidden paths: production Content/NewWorld directories outside AIWork, .codex/config.toml, user-level Codex config, user-level skills, UE project config.
- Python/script execution needed: yes, only Blender Python through MCP for scene setup, blockout creation, screenshot staging, .blend save, and GLB export.
- Network access needed: no.
- .codex/config.toml risk: read-only.
- Manifest/provenance update: not applicable; no production asset generated or promoted.
- Screenshot evidence required: viewport screenshot after creating the staging blockout.
- Logs required: Blender MCP tool outputs, exported file list, process shutdown check.
- Validation plan: MCP readiness, AI readiness, manifest validation, git diff --check.
- Rollback plan: delete the dry-run staging directory, evidence directory, and this audit record if the dry run should be discarded.
- Preflight reviewer: project MCP rules in ue58-mcp-editor-automation and ue58-blender-mcp-asset.
- Result: pass for live Blender MCP safe-mode dry run.
- Changed assets/objects: Created a non-production staging Blender scene and GLB under Content/NewWorld/AIWork/MCP_DryRun. Blender scene objects: SM_MCP_DryRun_Blockout_A_Base, SM_MCP_DryRun_Blockout_A_Step, SM_MCP_DryRun_Blockout_A_Pillar, UCX_SM_MCP_DryRun_Blockout_A_00, SM_MCP_DryRun_Blockout_A_ReferencePlane, REF_MCP_DryRun_OneMeter, CAM_MCP_DryRun_ThreeQuarter, and L_MCP_DryRun_Key.
- Screenshots/logs captured: Saved front, side, and three-quarter evidence screenshots under Docs/Planning/MCP_Evidence/2026-09-11_BlenderMCP_DryRun. MCP get_addon_status reported protocol_version 5, addon_version 1.6, Blender 5.2.1 LTS, telemetry_consent false, and no warning. MCP get_scene_info returned 8 objects after the write. MCP get_object_info confirmed SM_MCP_DryRun_Blockout_A_Base has applied scale 1.0 and bounds from -1.0/-0.6/0.0 to 1.0/0.6/0.5. MCP viewport screenshot returned an image/png block.
- Validation result: MCP readiness passed; AI readiness passed; AI_ASSET_MANIFEST.json validation passed with assets=0; git diff --check passed; Git LFS filter applies to the .blend, .glb, and .png evidence files; temporary Blender PID 56652 was stopped and no Blender process remained.
- Remaining risk: This did not test AI 3D generation, reference image planes from real concept art, UE import, Data Validation on imported .uasset files, or any production Content write.

### 2026-09-11 UE MCP Read-Only Smoke Test

- Date: 2026-09-11 Asia/Shanghai.
- Operator/agent: Codex.
- Tool/server: unreal-mcp at http://127.0.0.1:8000/mcp.
- Mode: UE MCP.
- Purpose: Verify project-level Codex can connect to UE5.8 MCP, discover toolsets, run read-only log and Gameplay Tag queries, and shut down the temporary Editor process.
- Git recovery point: b1176b742d0b00f6985ef310e9e02f8b6ca00f6e.
- Project MCP config checked: .codex/config.toml.
- UE MCP state: started manually through Tools/MCP/start_ue_mcp_editor.ps1 -Port 8000; port became reachable.
- Blender MCP safe mode confirmed: not applicable.
- Read-only discovery commands: codex -C G:\NewWorld mcp list; codex -C G:\NewWorld mcp get unreal-mcp; JSON-RPC initialize; notifications/initialized; ping; tools/list; resources/list; list_toolsets; describe_toolset for Logs, AssetTools, and GameplayTags; LogsToolset.GetLogCategories; LogsToolset.GetLogEntries; GameplayTags.ListTags; GameplayTags.GetTagInfo.
- Target paths/assets/objects: none.
- Allowed write scope: none through MCP.
- Explicitly forbidden paths: production Content, .codex/config.toml, user-level Codex config.
- Python/script execution needed: no.
- Network access needed: local loopback only.
- .codex/config.toml risk: read-only.
- Manifest/provenance update: not applicable; no assets generated or modified.
- Screenshot evidence required: no visual/editor state changed.
- Logs required: LogModelContextProtocol entries captured through LogsToolset.GetLogEntries.
- Validation plan: MCP readiness, Gameplay Tag readback, port shutdown check, AI readiness.
- Rollback plan: revert this audit entry plus Config/DefaultGameplayTags.ini and Tools/AI/check_ai_readiness.ps1 if the tag config change is not wanted.
- Preflight reviewer: project MCP rules in ue58-mcp-editor-automation.
- Result: pass after fixing Gameplay Tags config syntax.
- Changed assets/objects: none.
- Changed repo files: Config/DefaultGameplayTags.ini changed from repeated GameplayTagList assignment to additive +GameplayTagList entries; Tools/AI/check_ai_readiness.ps1 now verifies additive project tags; this audit record added.
- Screenshots/logs captured: LogModelContextProtocol reported three meta-tools and up to 31 discoverable toolsets; calls were logged for list_toolsets, LogsToolset.GetLogCategories, GameplayTags.ListTags, and GameplayTags.GetTagInfo.
- Validation result: MCP readiness passed before and after restart; GameplayTags.ListTags returned NewWorld.Asset.AIWork, NewWorld.Asset.ProvenanceRequired, NewWorld.MCP.Staging, and NewWorld.Validation.Required after the config fix; temporary MCP sessions were deleted; temporary Editor PIDs 92332 and 52564 were stopped; no listener remained on 127.0.0.1:8000.
- Remaining risk: no live MCP write batch was exercised; Blender MCP remains untested in this record.
