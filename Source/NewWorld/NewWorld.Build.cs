// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class NewWorld : ModuleRules
{
	public NewWorld(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"NewWorld",
			"NewWorld/Variant_Platforming",
			"NewWorld/Variant_Platforming/Animation",
			"NewWorld/Variant_Combat",
			"NewWorld/Variant_Combat/AI",
			"NewWorld/Variant_Combat/Animation",
			"NewWorld/Variant_Combat/Gameplay",
			"NewWorld/Variant_Combat/Interfaces",
			"NewWorld/Variant_Combat/UI",
			"NewWorld/Variant_SideScrolling",
			"NewWorld/Variant_SideScrolling/AI",
			"NewWorld/Variant_SideScrolling/Gameplay",
			"NewWorld/Variant_SideScrolling/Interfaces",
			"NewWorld/Variant_SideScrolling/UI"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
