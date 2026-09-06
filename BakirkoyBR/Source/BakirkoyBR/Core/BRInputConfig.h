#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "BRInputConfig.generated.h"

class UInputAction;
class UInputMappingContext;

/**
 * Data asset holding Enhanced Input Actions and Mapping Context for BakirkoyBR.
 */
UCLASS(BlueprintType, Const)
class BAKIRKOYBR_API UBRInputConfig : public UDataAsset
{
	GENERATED_BODY()

public:
	UBRInputConfig();

	/** Default Input Mapping Context applied to the local player */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input|Mapping")
	TObjectPtr<UInputMappingContext> DefaultMappingContext;

	/** Move action (Vector2D: X=Right, Y=Forward) */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input|Action")
	TObjectPtr<UInputAction> MoveAction;

	/** Look action (Vector2D: X=Yaw, Y=Pitch) */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input|Action")
	TObjectPtr<UInputAction> LookAction;

	/** Jump action (Bool) */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input|Action")
	TObjectPtr<UInputAction> JumpAction;

	/** Fire weapon action (Bool) */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input|Action")
	TObjectPtr<UInputAction> FireAction;

	/** Reload weapon action (Bool) */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input|Action")
	TObjectPtr<UInputAction> ReloadAction;

	/** Aim Down Sights (ADS) action (Bool) */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input|Action")
	TObjectPtr<UInputAction> ADSAction;
};
