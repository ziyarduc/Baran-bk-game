#include "Weapons/BRProjectileRocket.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

ABRProjectileRocket::ABRProjectileRocket()
{
	PrimaryActorTick.bCanEverTick = false;
	bReplicates = true;
	SetReplicateMovement(true);

	CollisionComp = CreateDefaultSubobject<USphereComponent>(TEXT("CollisionComp"));
	CollisionComp->InitSphereRadius(15.0f);
	CollisionComp->SetCollisionProfileName(TEXT("BlockAllDynamic"));
	CollisionComp->OnComponentHit.AddDynamic(this, &ABRProjectileRocket::OnHit);
	CollisionComp->SetWalkableSlopeOverride(FWalkableSlopeOverride(WalkableSlope_Unwalkable, 0.0f));
	CollisionComp->CanCharacterStepUpOn = ECB_No;
	RootComponent = CollisionComp;

	ProjectileMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ProjectileMesh"));
	ProjectileMesh->SetupAttachment(RootComponent);
	ProjectileMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	ProjectileMovement = CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("ProjectileMovement"));
	ProjectileMovement->UpdatedComponent = CollisionComp;
	ProjectileMovement->InitialSpeed = 3500.0f; // 35 m/s
	ProjectileMovement->MaxSpeed = 3500.0f;
	ProjectileMovement->bRotationFollowsVelocity = true;
	ProjectileMovement->bShouldBounce = false;
	ProjectileMovement->ProjectileGravityScale = 0.2f;

	DirectDamage = 110.0f;
	BaseSplashDamage = 85.0f;
	MinimumDamage = 25.0f;
	DamageInnerRadius = 100.0f; // 1 meter
	DamageOuterRadius = 400.0f; // 4 meters
	DamageFalloff = 1.0f;

	InitialLifeSpan = 10.0f;
}

void ABRProjectileRocket::BeginPlay()
{
	Super::BeginPlay();
}

void ABRProjectileRocket::OnHit(
	UPrimitiveComponent* HitComp,
	AActor* OtherActor,
	UPrimitiveComponent* OtherComp,
	FVector NormalImpulse,
	const FHitResult& Hit)
{
	if (!HasAuthority())
	{
		return;
	}

	AController* InstigatorController = GetInstigatorController();

	// Direct point damage on hit actor
	if (OtherActor && OtherActor != this)
	{
		UGameplayStatics::ApplyPointDamage(
			OtherActor,
			DirectDamage,
			GetVelocity().GetSafeNormal(),
			Hit,
			InstigatorController,
			this,
			nullptr
		);
	}

	// Radial splash damage with falloff (MVP M2 / Constraint C6)
	TArray<TObjectPtr<AActor>> IgnoreActors;
	IgnoreActors.Add(this);
	if (OtherActor)
	{
		IgnoreActors.Add(OtherActor);
	}

	TArray<AActor*> RawIgnoreActors;
	for (const TObjectPtr<AActor>& ActorPtr : IgnoreActors)
	{
		if (ActorPtr)
		{
			RawIgnoreActors.Add(ActorPtr.Get());
		}
	}

	UGameplayStatics::ApplyRadialDamageWithFalloff(
		this,
		BaseSplashDamage,
		MinimumDamage,
		Hit.ImpactPoint,
		DamageInnerRadius,
		DamageOuterRadius,
		DamageFalloff,
		nullptr,
		RawIgnoreActors,
		this,
		InstigatorController,
		ECC_Visibility
	);

	Destroy();
}
