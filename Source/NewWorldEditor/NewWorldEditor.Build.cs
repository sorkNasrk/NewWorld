// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class NewWorldEditor : ModuleRules
{
	public NewWorldEditor(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine"
		});

		PrivateDependencyModuleNames.AddRange(new string[] {
			"AssetRegistry",
			"DataValidation",
			"Json",
			"UnrealEd"
		});
	}
}
