# AI Asset QA Checklists

Use these checklists before generated or AI-assisted assets move out of Content/NewWorld/AIWork.

| Type | Must Pass |
| --- | --- |
| Concept / Styleboard | In-game camera readability, shape language, color/value grouping, Do/Don't examples, asset breakdown, no misleading baked effects |
| AI Image Prompt | Approved prompt records subject, context, view, material, style, technical limits, negative constraints, model/provider, and exact call parameters |
| Reference Pack | Front/side/back/top orthographic, 3/4 view, silhouette, material swatches, part callouts, scale reference, no perspective distortion |
| AI 3D Candidate | Correct category, readable silhouette, plausible scale, separable material groups, acceptable topology path, no fused critical parts |
| Blender MCP Output | Scene inspected, image planes placed, units set, collections named, transforms applied, screenshots captured, staging export only |
| Static Mesh | Scale, pivot, normals, UVs, material slots, collision, bounds, LOD/Nanite policy, naming, Data Validation |
| Skeletal Mesh | Skeleton, root, weights, PhysicsAsset, retarget pose, deformation review, clipping review, import settings |
| Animation | Skeleton match, root motion policy, loop/transition quality, notifies, contacts, foot sliding, blend/montage use |
| Texture | Map purpose, sRGB/compression, mips, TextureGroup, resolution, tileability, PBR plausibility, no baked lighting unless intended |
| Material | Master/instance split, parameter names, material slots, shader cost, translucency/Nanite compatibility, runtime parameter policy |
| VFX / Niagara | Readable gameplay timing, bounds, spawn budget, overdraw, material cost, exposed parameters, validation plan |
| Audio / Music | Approved prompt, loudness/peak note, loop check, variation fatigue check, routing, attenuation/concurrency, in-game audition |
| Voice | Exact text, speaker, language, pronunciation, subtitle key, localization plan, file naming, audition notes |
| UI / Icon | State coverage, safe area, input focus, target size, longest localized text, Font Asset, contrast, no baked text unless approved |
| Font | License, glyph coverage, runtime cached Font Asset, fallback plan, localization coverage |
| Cinematic | Shot purpose, camera readability, sequence naming, asset references, audio sync, render/preview validation |
| Localization | Stable keys, source text, PO import/export plan, compile LocRes when used, longest text review |
| Provenance | Prompt, model/provider, parameters, date, task id, candidate count, selected reason, references, license, final path |

Blocking failures require either regeneration, DCC cleanup, or a retrospective when the same failure repeats.
