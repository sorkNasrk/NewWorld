---
name: ue58-build-test-runner
description: Use for NewWorld UE5.8 UBT project files, editor builds, Automation tests, Data Validation, packaging checks, generated IDE files, and log review.
---

# UE5.8 Build And Test Runner

Use the UE-bundled .NET 10 runtime for UBT. Read [references/validation-matrix.md](references/validation-matrix.md) when deciding which checks are required for a task.

## Core Commands

Generate project files:

~~~powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/ThirdParty/DotNet/10.0/win-x64/dotnet.exe G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll -ProjectFiles -Project=G:/NewWorld/NewWorld.uproject -Game -Progress
~~~

Build editor target:

~~~powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Build/BatchFiles/Build.bat NewWorldEditor Win64 Development -Project=G:/NewWorld/NewWorld.uproject -WaitMutex -NoHotReload
~~~

Run Data Validation:

~~~powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe G:/NewWorld/NewWorld.uproject -run=DataValidation -unattended -nop4 -nosplash
~~~

Data Validation includes the NewWorldEditor asset policy validator for /Game/NewWorld naming, AIWork staging, AI_ASSET_MANIFEST status, and MCP staging markers.

AI readiness check:

~~~powershell
powershell -ExecutionPolicy Bypass -File Tools/AI/check_ai_readiness.ps1
~~~

Manifest check:

~~~powershell
python Tools/AI/validate_ai_asset_manifest.py Docs/Assets/AI_ASSET_MANIFEST.json
~~~

## Workflow

1. Run only checks relevant to the touched surface.
2. Use exact UE5.8 paths from .agents/ue-project-context.md.
3. Inspect logs when a command fails or exits with warnings that affect acceptance.
4. Do not claim success from skipped checks.
5. For asset-heavy changes, run Data Validation before acceptance.
6. After changing Source/NewWorldEditor or validation policy, regenerate project files before building NewWorldEditor.

## Output

Report exact command, exit code, pass/fail status, relevant log excerpt, and untested risk. If a check is intentionally skipped, state the reason.
