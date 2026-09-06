#pragma once

#include "CoreMinimal.h"
#include "Weapons/BRWeaponBase.h"

class UParticleSystem;
class UNiagaraSystem;
class USoundBase;

#include "BRWeapon_HitScan.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRWeapon_HitScan : public ABRWeaponBase
{
	GENERATED_BODY()

public:
	ABRWeapon_HitScan();

	virtual void Fire() override;

protected:
	// Maximum trace distance in centimeters (10000 cm = 100 m)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|HitScan")
	float MaxTraceDistance;

	// Cone half-angle spread in degrees
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|HitScan")
	float BaseSpreadAngle;

	// Spread multiplier when Aiming Down Sights (ADS)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|HitScan")
	float ADSSpreadMultiplier;

	// Distance where damage falloff begins in centimeters (3500 cm = 35 m)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Falloff")
	float DamageFalloffStart;

	// Distance where damage reaches floor multiplier in centimeters (8000 cm = 80 m)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Falloff")
	float DamageFalloffFloorDistance;

	// Lowest damage multiplier applied beyond floor distance (e.g. 0.55 = 55%)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Falloff")
	float DamageFalloffFloorMultiplier;

	// Bullet tracer cascade particle system
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Cosmetics")
	TObjectPtr<UParticleSystem> TracerFX;

	// Bullet tracer Niagara system
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Cosmetics")
	TObjectPtr<UNiagaraSystem> NiagaraTracerFX;

	// Parameter name for tracer endpoint
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Cosmetics")
	FName TracerEndParamName;

	// Impact cascade particle system
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Cosmetics")
	TObjectPtr<UParticleSystem> ImpactFX;

	// Impact Niagara system
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Cosmetics")
	TObjectPtr<UNiagaraSystem> NiagaraImpactFX;

	// Impact sound effect
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Cosmetics")
	TObjectPtr<USoundBase> ImpactSound;

	// Plays cosmetic tracer and impact effects immediately
	void PlayTracerAndImpactEffects(const FVector& MuzzleLoc, const FVector& EndPoint, const FHitResult& HitResult, bool bHit);

	// Linear interpolation damage falloff calculation
	float CalculateDamageFalloff(float Distance) const;

	// Resolves trace start and base direction from character aim or muzzle
	void GetTraceOriginAndDirection(FVector& OutTraceStart, FVector& OutDirection) const;
};
