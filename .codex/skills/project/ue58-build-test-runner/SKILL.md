---
name: ue58-build-test-runner
description: Use for NewWorld UE5.8 build, UBT, project files, Automation tests, Data Validation, packaging, and log review.
---

# UE5.8 Build And Test Runner

Use the UE-bundled .NET 10 runtime for UBT:

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

Report exact commands, pass/fail status, and relevant log excerpts. Do not claim success from a skipped check.
