// Copyright Epic Games, Inc. All Rights Reserved.

#include "NewWorldAssetPolicyValidator.h"

#include "Dom/JsonObject.h"
#include "Misc/Char.h"
#include "Misc/DataValidation.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

#define LOCTEXT_NAMESPACE "NewWorldAssetPolicyValidator"

namespace NewWorldAssetPolicy
{
const TCHAR* GameRoot = TEXT("/Game/NewWorld");
const TCHAR* GameRootWithSlash = TEXT("/Game/NewWorld/");
const TCHAR* AiWorkRoot = TEXT("/Game/NewWorld/AIWork");
const TCHAR* AiWorkRootWithSlash = TEXT("/Game/NewWorld/AIWork/");

struct FManifestEntry
{
	FString Path;
	FString Status;
};

struct FManifestLoadResult
{
	bool bLoaded = false;
	FString Error;
	TArray<FManifestEntry> Entries;
};

bool IsNewWorldAsset(const FAssetData& AssetData)
{
	const FString PackageName = AssetData.PackageName.ToString();
	return PackageName.Equals(GameRoot) || PackageName.StartsWith(GameRootWithSlash);
}

bool IsInAiWork(const FString& PackageName)
{
	return PackageName.Equals(AiWorkRoot) || PackageName.StartsWith(AiWorkRootWithSlash);
}

FString NormalizeContentPath(FString Path)
{
	Path.ReplaceInline(TEXT("\\"), TEXT("/"));
	while (Path.Contains(TEXT("//")))
	{
		Path.ReplaceInline(TEXT("//"), TEXT("/"));
	}
	if (Path.StartsWith(TEXT("./")))
	{
		Path.RightChopInline(2);
	}

	const FString Extension = FPaths::GetExtension(Path, false).ToLower();
	static const TSet<FString> KnownExtensions = {
		TEXT("uasset"), TEXT("umap"), TEXT("fbx"), TEXT("glb"), TEXT("gltf"), TEXT("blend"), TEXT("png"), TEXT("jpg"), TEXT("jpeg"),
		TEXT("exr"), TEXT("tga"), TEXT("psd"), TEXT("wav"), TEXT("flac"), TEXT("ogg"), TEXT("json")
	};
	if (KnownExtensions.Contains(Extension))
	{
		Path.LeftChopInline(Extension.Len() + 1);
	}
	return Path;
}

FString ContentPathFromPackageName(const FString& PackageName)
{
	FString ContentPath = PackageName;
	if (ContentPath.StartsWith(TEXT("/Game/")))
	{
		ContentPath = TEXT("Content/") + ContentPath.RightChop(6);
	}
	return NormalizeContentPath(ContentPath);
}

bool HasPathMarker(const FString& Value, const TCHAR* Marker)
{
	return Value.Contains(FString::Printf(TEXT("/%s/"), Marker), ESearchCase::IgnoreCase)
		|| Value.Contains(FString::Printf(TEXT("/%s_"), Marker), ESearchCase::IgnoreCase)
		|| Value.Contains(FString::Printf(TEXT("_%s_"), Marker), ESearchCase::IgnoreCase)
		|| Value.StartsWith(FString::Printf(TEXT("%s_"), Marker), ESearchCase::IgnoreCase);
}

bool IsAiMarked(const FString& PackageName, const FString& AssetName)
{
	return HasPathMarker(PackageName, TEXT("AI")) || HasPathMarker(AssetName, TEXT("AI"));
}

bool IsMcpMarked(const FString& PackageName, const FString& AssetName)
{
	return HasPathMarker(PackageName, TEXT("MCP")) || HasPathMarker(AssetName, TEXT("MCP"));
}

const TArray<FString>& SupportedPrefixes()
{
	static const TArray<FString> Prefixes = {
		TEXT("Font_"), TEXT("PHYS_"), TEXT("SKEL_"), TEXT("ABP_"), TEXT("IKR_"), TEXT("RTG_"), TEXT("IMC_"), TEXT("WBP_"),
		TEXT("SFX_"), TEXT("BGM_"), TEXT("AMB_"), TEXT("VO_"), TEXT("MI_"), TEXT("MF_"), TEXT("NS_"), TEXT("NE_"),
		TEXT("SW_"), TEXT("SC_"), TEXT("MS_"), TEXT("DA_"), TEXT("DT_"), TEXT("GA_"), TEXT("GE_"), TEXT("GC_"),
		TEXT("IA_"), TEXT("LS_"), TEXT("BP_"), TEXT("SM_"), TEXT("SK_"), TEXT("AS_"), TEXT("CR_"), TEXT("UI_"),
		TEXT("GT_"), TEXT("M_"), TEXT("T_"), TEXT("L_")
	};
	return Prefixes;
}

bool HasValidAssetNameShape(const FString& AssetName)
{
	for (const FString& Prefix : SupportedPrefixes())
	{
		if (!AssetName.StartsWith(Prefix))
		{
			continue;
		}

		const FString Remainder = AssetName.RightChop(Prefix.Len());
		if (Remainder.IsEmpty() || !Remainder.Contains(TEXT("_")) || Remainder.Contains(TEXT("__")))
		{
			return false;
		}

		TArray<FString> Segments;
		Remainder.ParseIntoArray(Segments, TEXT("_"), false);
		if (Segments.Num() < 2)
		{
			return false;
		}

		for (const FString& Segment : Segments)
		{
			if (Segment.IsEmpty())
			{
				return false;
			}
		}

		for (const TCHAR Character : Remainder)
		{
			if (!(FChar::IsAlnum(Character) || Character == TEXT('_')))
			{
				return false;
			}
		}
		return true;
	}
	return false;
}

void AddManifestPath(const TSharedPtr<FJsonObject>& AssetObject, const TCHAR* FieldName, const FString& Status, TArray<FManifestEntry>& Entries)
{
	FString Path;
	if (!AssetObject->TryGetStringField(FieldName, Path) || Path.IsEmpty() || Path.Equals(TEXT("TBD"), ESearchCase::IgnoreCase))
	{
		return;
	}

	Entries.Add({ NormalizeContentPath(Path), Status });
}

FManifestLoadResult LoadManifest()
{
	FManifestLoadResult Result;
	const FString ManifestPath = FPaths::ProjectDir() / TEXT("Docs/Assets/AI_ASSET_MANIFEST.json");
	FString ManifestText;
	if (!FFileHelper::LoadFileToString(ManifestText, *ManifestPath))
	{
		Result.Error = FString::Printf(TEXT("AI asset manifest could not be read: %s"), *ManifestPath);
		return Result;
	}

	TSharedPtr<FJsonObject> RootObject;
	const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(ManifestText);
	if (!FJsonSerializer::Deserialize(Reader, RootObject) || !RootObject.IsValid())
	{
		Result.Error = FString::Printf(TEXT("AI asset manifest is not valid JSON: %s"), *ManifestPath);
		return Result;
	}

	const TArray<TSharedPtr<FJsonValue>>* Assets = nullptr;
	if (!RootObject->TryGetArrayField(TEXT("assets"), Assets))
	{
		Result.Error = FString::Printf(TEXT("AI asset manifest is missing the assets array: %s"), *ManifestPath);
		return Result;
	}

	for (const TSharedPtr<FJsonValue>& AssetValue : *Assets)
	{
		if (!AssetValue.IsValid())
		{
			continue;
		}

		const TSharedPtr<FJsonObject> AssetObject = AssetValue->AsObject();
		if (!AssetObject.IsValid())
		{
			continue;
		}

		FString Status;
		AssetObject->TryGetStringField(TEXT("status"), Status);
		AddManifestPath(AssetObject, TEXT("staging_path"), Status, Result.Entries);
		AddManifestPath(AssetObject, TEXT("target_path"), Status, Result.Entries);
	}

	Result.bLoaded = true;
	return Result;
}

bool ManifestPathMatches(const FString& ManifestPath, const FString& AssetContentPath)
{
	return ManifestPath.Equals(AssetContentPath, ESearchCase::IgnoreCase)
		|| AssetContentPath.StartsWith(ManifestPath + TEXT("/"), ESearchCase::IgnoreCase);
}

const FManifestEntry* FindManifestEntry(const FManifestLoadResult& Manifest, const FString& AssetContentPath)
{
	for (const FManifestEntry& Entry : Manifest.Entries)
	{
		if (ManifestPathMatches(Entry.Path, AssetContentPath))
		{
			return &Entry;
		}
	}
	return nullptr;
}

bool IsAcceptedProductionStatus(const FString& Status)
{
	return Status.Equals(TEXT("qa_passed"), ESearchCase::IgnoreCase)
		|| Status.Equals(TEXT("promoted"), ESearchCase::IgnoreCase);
}
}

bool UNewWorldAssetPolicyValidator::CanValidateAsset_Implementation(const FAssetData& InAssetData, UObject* InObject, FDataValidationContext& InContext) const
{
	return InObject != nullptr && NewWorldAssetPolicy::IsNewWorldAsset(InAssetData);
}

EDataValidationResult UNewWorldAssetPolicyValidator::ValidateLoadedAsset_Implementation(const FAssetData& InAssetData, UObject* InAsset, FDataValidationContext& InContext)
{
	check(InAsset);

	const FString PackageName = InAssetData.PackageName.ToString();
	const FString AssetName = InAssetData.AssetName.ToString();
	const FString AssetContentPath = NewWorldAssetPolicy::ContentPathFromPackageName(PackageName);
	const bool bIsInAiWork = NewWorldAssetPolicy::IsInAiWork(PackageName);
	const bool bIsAiMarked = NewWorldAssetPolicy::IsAiMarked(PackageName, AssetName);
	const bool bIsMcpMarked = NewWorldAssetPolicy::IsMcpMarked(PackageName, AssetName);

	if (bIsInAiWork)
	{
		AssetWarning(InAsset, FText::Format(LOCTEXT("AiWorkStaging", "{0} is in AIWork staging and is not production-ready."), FText::FromString(PackageName)));
	}
	else if (!NewWorldAssetPolicy::HasValidAssetNameShape(AssetName))
	{
		AssetFails(InAsset, FText::Format(
			LOCTEXT("BadAssetName", "{0} must follow [Prefix]_[Name]_[Descriptor]_[Variant] with a supported NewWorld prefix."),
			FText::FromString(AssetName)));
	}

	const bool bNeedsManifestReview = bIsInAiWork || bIsAiMarked || bIsMcpMarked;
	if (bNeedsManifestReview)
	{
		const NewWorldAssetPolicy::FManifestLoadResult Manifest = NewWorldAssetPolicy::LoadManifest();
		if (!Manifest.bLoaded)
		{
			AssetFails(InAsset, FText::FromString(Manifest.Error));
		}
		else if (const NewWorldAssetPolicy::FManifestEntry* Entry = NewWorldAssetPolicy::FindManifestEntry(Manifest, AssetContentPath))
		{
			if (!bIsInAiWork && !NewWorldAssetPolicy::IsAcceptedProductionStatus(Entry->Status))
			{
				AssetFails(InAsset, FText::Format(
					LOCTEXT("ProductionAiAssetNotApproved", "{0} is recorded in the AI asset manifest but status '{1}' is not ready for production. Required: qa_passed or promoted."),
					FText::FromString(PackageName),
					FText::FromString(Entry->Status)));
			}
		}
		else if (bIsInAiWork)
		{
			AssetWarning(InAsset, FText::Format(
				LOCTEXT("AiWorkManifestMissing", "{0} is staged in AIWork but has no matching AI_ASSET_MANIFEST entry yet."),
				FText::FromString(PackageName)));
		}
		else
		{
			AssetFails(InAsset, FText::Format(
				LOCTEXT("ProductionAiAssetMissingManifest", "{0} appears AI/MCP-assisted but has no matching AI_ASSET_MANIFEST entry."),
				FText::FromString(PackageName)));
		}
	}

	if (bIsMcpMarked && !bIsInAiWork)
	{
		AssetFails(InAsset, FText::Format(
			LOCTEXT("McpAssetOutsideStaging", "{0} appears MCP-assisted and must remain under /Game/NewWorld/AIWork until reviewed."),
			FText::FromString(PackageName)));
	}

	if (GetValidationResult() != EDataValidationResult::Invalid)
	{
		AssetPasses(InAsset);
	}
	return GetValidationResult();
}

#undef LOCTEXT_NAMESPACE
