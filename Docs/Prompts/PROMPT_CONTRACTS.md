# Prompt Contracts

Use these contracts before calling AIART, AI Voice, model generation, texture generation, or MCP-based asset creation. Approved prompts must be copied to Docs/Prompts/APPROVED_PROMPTS.md before production calls.

## Universal Fields

- Asset/task id:
- Intended UE use:
- Target path:
- Audience/player context:
- References:
- Required model/provider and parameters:
- Candidate count:
- Negative constraints:
- Rework threshold:
- QA checklist:
- Provenance/license note:

## AIART Image Prompt

Required detail: subject, silhouette, components, game context, camera/view, material, color/value, lighting constraints, background policy, technical exclusions, and output use.

Default call policy: pass inferenceMode "gpt" unless the task explicitly selects another mode. Pass the approved prompt verbatim.

## Reference Pack Prompt

Require front, side, back, top orthographic views without perspective distortion, plus 3/4 beauty view, silhouette, material swatches, part callouts, and scale reference.

## 3D Generation Prompt

Required detail: asset role, dimensions, view readability, primary forms, separable parts, material groups, topology expectations, UV/texture needs, forbidden defects, export format, candidate count, and cleanup path.

Default quality policy: use the strongest available quality tier that fits the task. Use Hyper3D modelVariant "extremeHigh" when supported and suitable. Use Tripo textureQuality "detailed" when supported and suitable.

## Blender MCP Prompt

Required detail: asset id, dimensions, units, reference image paths, collections to create, blockout steps, target export path, screenshot views, QA list, and write scope.

Blender MCP should start with scene inspection and should write to staging files or export folders before production Content.

## Texture And Material Prompt

Required detail: target mesh/material, map set, tileability, PBR interpretation, color space, resolution, wear/dirt policy, normal strength, roughness/metalness behavior, forbidden baked lighting, and UE material target.

## Rigging And Animation Prompt

Required detail: skeleton, retarget source, clip purpose, root motion policy, loop/transition needs, notifies, pose constraints, contact points, camera readability, and known deformation risks.

## Audio/Music/Voice Prompt

Required detail: trigger, duration, loop, BPM/meter/rhythm, timbre/instrumentation, attack/decay/tail, space, variations, forbidden references, UE routing, and audition criteria. Voice also requires exact text, speaker, language, emotion, pace, pauses, pronunciation, subtitle key, and localization plan.

## UI/Icon Prompt

Required detail: screen/widget use, states, icon semantics, line weight, fill/stroke style, target size, background/alpha policy, color states, readability, localization impact, and forbidden text/watermark artifacts.
