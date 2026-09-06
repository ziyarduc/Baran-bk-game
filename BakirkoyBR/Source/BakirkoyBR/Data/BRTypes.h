#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
class AActor;
#include "BRTypes.generated.h"

// ── Weapon Types ──
UENUM(BlueprintType)
enum class EBRWeaponType : uint8
{
    Pistol        UMETA(DisplayName = "Pistol"),
    SMG           UMETA(DisplayName = "SMG"),
    AssaultRifle  UMETA(DisplayName = "Assault Rifle"),
    Sniper        UMETA(DisplayName = "Sniper Rifle"),
    Shotgun       UMETA(DisplayName = "Shotgun"),
    RocketLauncher UMETA(DisplayName = "Rocket Launcher")
};

// ── Weapon Rarity ──
UENUM(BlueprintType)
enum class EBRRarity : uint8
{
    Common,
    Uncommon,
    Rare,
    Epic,
    Legendary
};

// ── Build Material ──
UENUM(BlueprintType)
enum class EBRMaterialType : uint8
{
    Moloz   UMETA(DisplayName = "Debris"),
    Tugla   UMETA(DisplayName = "Brick"),
    Celik   UMETA(DisplayName = "Steel")
};

// ── Build Piece Type ──
UENUM(BlueprintType)
enum class EBRBuildPieceType : uint8
{
    Wall,
    Ramp,
    Floor,
    HalfWall
};

// ── Build Edit Type ──
UENUM(BlueprintType)
enum class EBREditType : uint8
{
    None,
    Door,
    Window,
    HalfCut,
    Arch
};

// ── Bot State ──
UENUM(BlueprintType)
enum class EBRBotState : uint8
{
    Idle,
    Patrol,
    Chase,
    Attack,
    Hide,
    Heal
};

// ── Bot Role ──
UENUM(BlueprintType)
enum class EBRBotRole : uint8
{
    Assault,
    Sniper,
    Support
};

// ── Bot Difficulty ──
UENUM(BlueprintType)
enum class EBRBotDifficulty : uint8
{
    Easy,
    Medium,
    Hard,
    Elite
};

// ── Player Status ──
UENUM(BlueprintType)
enum class EBRPlayerStatus : uint8
{
    Alive,
    Downed,
    Eliminated,
    Spectating,
    Disconnected
};

// ── Match Phase ──
UENUM(BlueprintType)
enum class EBRMatchPhase : uint8
{
    Lobby,
    PreGame,
    Skydive,
    Active,
    PostGame
};

// ── Movement State ──
UENUM(BlueprintType)
enum class EBRMovementState : uint8
{
    Idle,
    Walking,
    Sprinting,
    Crouching,
    Jumping,
    Falling,
    Gliding,
    Building,
    Downed
};

// ── Consumable Type ──
UENUM(BlueprintType)
enum class EBRConsumableType : uint8
{
    SmallShield,
    BigShield,
    Bandage,
    Medkit,
    SpeedBoost
};

// ── Ammo Type ──
UENUM(BlueprintType)
enum class EBRAmmoType : uint8
{
    Light,
    Medium,
    Heavy,
    Shells,
    Rockets
};

// ── Loot Tier ──
UENUM(BlueprintType)
enum class EBRLootTier : uint8
{
    Common,
    Uncommon,
    Rare,
    Epic,
    Legendary
};

// ── Structs ──

USTRUCT(BlueprintType)
struct FBRDamageInfo
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    float Damage = 0.f;

    UPROPERTY(BlueprintReadOnly)
    bool bIsHeadshot = false;

    UPROPERTY(BlueprintReadOnly)
    EBRWeaponType WeaponType = EBRWeaponType::Pistol;

    UPROPERTY(BlueprintReadOnly)
    TObjectPtr<AActor> Instigator = nullptr;

    UPROPERTY(BlueprintReadOnly)
    float Distance = 0.f;
};

USTRUCT(BlueprintType)
struct FBRWeaponData : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    EBRWeaponType WeaponType = EBRWeaponType::Pistol;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    EBRRarity Rarity = EBRRarity::Common;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float BodyDamage = 0.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float HeadshotMultiplier = 2.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float FireRate = 1.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    int32 MagSize = 30;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float ReloadTime = 2.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float ADSTime = 0.25f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float ADSMoveSpeedMultiplier = 0.75f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float DamageFalloffStart = 35.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float DamageFalloffFloorDistance = 80.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float DamageFalloffFloorMultiplier = 0.55f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    bool bIsProjectile = false;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta = (EditCondition = "bIsProjectile"))
    float ProjectileSpeed = 0.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta = (EditCondition = "bIsProjectile"))
    float SplashRadius = 0.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta = (EditCondition = "bIsProjectile"))
    float SplashDamage = 0.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    EBRAmmoType AmmoType = EBRAmmoType::Medium;
};

USTRUCT(BlueprintType)
struct FBRBuildMaterialData
{
    GENERATED_BODY()

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    EBRMaterialType MaterialType = EBRMaterialType::Moloz;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    int32 HarvestRate = 25;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    int32 MaxStack = 300;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float PlaceTime = 0.6f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float TurboMinTime = 0.3f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    int32 StartHP = 60;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    int32 MaxHP = 100;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float HardenTime = 5.f;
};

USTRUCT(BlueprintType)
struct FBRThreatEntry
{
    GENERATED_BODY()

    UPROPERTY()
    FGuid TargetID;

    UPROPERTY()
    FVector LastKnownPosition = FVector::ZeroVector;

    UPROPERTY()
    float LastSeenTime = 0.f;

    UPROPERTY()
    float ThreatScore = 0.f;

    UPROPERTY()
    bool bIsVisible = false;
};

USTRUCT(BlueprintType)
struct FBRLootSpawnRow : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditDefaultsOnly)
    FVector SpawnLocation = FVector::ZeroVector;

    UPROPERTY(EditDefaultsOnly)
    EBRLootTier Tier = EBRLootTier::Common;

    UPROPERTY(EditDefaultsOnly)
    float LegendaryMultiplier = 1.f;
};
