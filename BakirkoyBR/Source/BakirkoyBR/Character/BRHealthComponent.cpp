#include "Character/BRHealthComponent.h"
#include "Data/BRGameConstants.h"
#include "Net/UnrealNetwork.h"

UBRHealthComponent::UBRHealthComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    SetIsReplicatedByDefault(true);
}

void UBRHealthComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(UBRHealthComponent, Health);
    DOREPLIFETIME(UBRHealthComponent, Shield);
}

void UBRHealthComponent::ApplyDamage(const FBRDamageInfo& DamageInfo)
{
    if (!GetOwner()->HasAuthority()) return;

    float RemainingDamage = DamageInfo.Damage;

    // Shield absorbs first
    float ShieldDamage = FMath::Min(RemainingDamage, Shield);
    Shield -= ShieldDamage;
    RemainingDamage -= ShieldDamage;

    // Remaining hits HP
    Health -= RemainingDamage;
    Health = FMath::Max(Health, 0.f);

    OnHealthChanged.Broadcast(Health, Shield, DamageInfo);

    if (Health <= 0.f)
    {
        OnPlayerEliminated.Broadcast(DamageInfo.Instigator ? DamageInfo.Instigator->GetInstigatorController() : nullptr);
    }
}

void UBRHealthComponent::Heal(float Amount)
{
    if (!GetOwner()->HasAuthority()) return;
    Health = FMath::Min(Health + Amount, BRConstants::MAX_HEALTH);
    OnHealthChanged.Broadcast(Health, Shield, FBRDamageInfo());
}

void UBRHealthComponent::AddShield(float Amount)
{
    if (!GetOwner()->HasAuthority()) return;
    Shield = FMath::Min(Shield + Amount, BRConstants::MAX_SHIELD);
    OnHealthChanged.Broadcast(Health, Shield, FBRDamageInfo());
}

bool UBRHealthComponent::IsAlive() const
{
    return Health > 0.f;
}

float UBRHealthComponent::GetMaxHealth() const
{
    return BRConstants::MAX_HEALTH;
}

float UBRHealthComponent::GetMaxShield() const
{
    return BRConstants::MAX_SHIELD;
}

void UBRHealthComponent::OnRep_Health()
{
    OnHealthChanged.Broadcast(Health, Shield, FBRDamageInfo());
}

void UBRHealthComponent::OnRep_Shield()
{
    OnHealthChanged.Broadcast(Health, Shield, FBRDamageInfo());
}
