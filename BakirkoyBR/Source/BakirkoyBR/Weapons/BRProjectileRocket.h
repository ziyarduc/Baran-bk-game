#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"

class USphereComponent;
class UStaticMeshComponent;
class UProjectileMovementComponent;

#include "BRProjectileRocket.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRProjectileRocket : public AActor
{
	GENERATED_BODY()

public:
	ABRProjectileRocket();

	UFUNCTION()
	void OnHit(
		UPrimitiveComponent* HitComp,
		AActor* OtherActor,
		UPrimitiveComponent* OtherComp,
		FVector NormalImpulse,
		const FHitResult& Hit
	);

protected:
	virtual void BeginPlay() override;

	// Collision sphere subobject
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USphereComponent> CollisionComp;

	// Visual static mesh component
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> ProjectileMesh;

	// Projectile movement physics component
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UProjectileMovementComponent> ProjectileMovement;

	// Direct hit impact damage
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Damage")
	float DirectDamage;

	// Epicenter splash damage
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Damage")
	float BaseSplashDamage;

	// Minimum damage applied at outer perimeter
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Damage")
	float MinimumDamage;

	// Full-damage epicenter radius in centimeters (100 cm = 1 m)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Damage")
	float DamageInnerRadius;

	// Maximum splash radius in centimeters (400 cm = 4 m)
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Damage")
	float DamageOuterRadius;

	// Falloff curve exponent
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Damage")
	float DamageFalloff;
};
