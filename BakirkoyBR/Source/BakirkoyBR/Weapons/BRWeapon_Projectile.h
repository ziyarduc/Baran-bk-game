#pragma once

#include "CoreMinimal.h"
#include "Weapons/BRWeaponBase.h"

class ABRProjectileRocket;

#include "BRWeapon_Projectile.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRWeapon_Projectile : public ABRWeaponBase
{
	GENERATED_BODY()

public:
	ABRWeapon_Projectile();

	virtual void Fire() override;

protected:
	// Rocket projectile actor class to spawn
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Projectile")
	TSubclassOf<ABRProjectileRocket> ProjectileClass;

	// Initial speed configured for launched projectile in cm/s (3500 cm/s = 35 m/s)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Projectile")
	float LaunchSpeed;

	// Maximum trace distance from camera to resolve crosshair target point in cm
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Projectile")
	float AimTraceDistance;
};
