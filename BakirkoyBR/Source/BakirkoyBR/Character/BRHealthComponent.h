#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Data/BRTypes.h"
#include "BRHealthComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnHealthChanged, float, NewHealth, float, NewShield, const FBRDamageInfo&, DamageInfo);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPlayerEliminated, AController*, Killer);

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class BAKIRKOYBR_API UBRHealthComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UBRHealthComponent();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UFUNCTION(BlueprintCallable, Category = "Health")
    void ApplyDamage(const FBRDamageInfo& DamageInfo);

    UFUNCTION(BlueprintCallable, Category = "Health")
    void Heal(float Amount);

    UFUNCTION(BlueprintCallable, Category = "Health")
    void AddShield(float Amount);

    UFUNCTION(BlueprintPure, Category = "Health")
    bool IsAlive() const;

    UFUNCTION(BlueprintPure, Category = "Health")
    float GetHealth() const { return Health; }

    UFUNCTION(BlueprintPure, Category = "Health")
    float GetShield() const { return Shield; }

    UFUNCTION(BlueprintPure, Category = "Health")
    float GetMaxHealth() const;

    UFUNCTION(BlueprintPure, Category = "Health")
    float GetMaxShield() const;

    UPROPERTY(BlueprintAssignable)
    FOnHealthChanged OnHealthChanged;

    UPROPERTY(BlueprintAssignable)
    FOnPlayerEliminated OnPlayerEliminated;

protected:
    UPROPERTY(ReplicatedUsing = OnRep_Health, BlueprintReadOnly, Category = "Health")
    float Health = 100.f;

    UPROPERTY(ReplicatedUsing = OnRep_Shield, BlueprintReadOnly, Category = "Health")
    float Shield = 0.f;

    UFUNCTION()
    void OnRep_Health();

    UFUNCTION()
    void OnRep_Shield();
};
