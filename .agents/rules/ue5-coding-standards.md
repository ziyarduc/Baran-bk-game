# UE5 C++ Coding Standards

> **Bakırköy BR Project Rule**  
> **Status**: MANDATORY  
> **Related Rules**: [error-prevention.md](error-prevention.md), [unreal-analyzer-validation.md](unreal-analyzer-validation.md), [constraint-retention.md](constraint-retention.md)

---

## 1. Naming Conventions
- Classes deriving from `AActor`: `ABR*` (e.g., `ABRCharacter`, `ABRWeaponBase`, `ABRProjectile`)
- Classes deriving from `UObject`: `UBR*` (e.g., `UBRHealthComponent`, `UBRSpawnManager`)
- Interfaces: `IBR*` (e.g., `IBRDamageable`, `IBRInteractable`)
- Structs: `FBR*` (e.g., `FBRWeaponData`, `FBRWeaponStats`)
- Enums: `EBR*` (e.g., `EBRMaterialType`, `EBRGamePhase`)
- Delegates: `FOnBR*` (e.g., `FOnBRHealthChanged`, `FOnBRPlayerEliminated`)
- Data Tables: `DT_BR*`
- Blueprints: `BP_BR*`

---

## 2. UPROPERTY Specifiers & GC Safety
- **Pointer Member Safety**: Always use `TObjectPtr<>` for `UObject`-derived member pointers.
- Replicated gameplay state: `UPROPERTY(ReplicatedUsing = OnRep_*, BlueprintReadOnly, Category = "Gameplay")`
- Server-only transient state: `UPROPERTY(Transient)`
- Data Asset / Data Table configuration: `UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Data")`
- Component subobjects: `UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))`
- Non-owning actor references: `TWeakObjectPtr<AActor>` (Transient)

---

## 3. UFUNCTION Specifiers & Network RPCs
- **Server RPCs**: `UFUNCTION(Server, Reliable, WithValidation)` for authoritative actions. Must implement both `_Validate` and `_Implementation`.
- **Client RPCs**: `UFUNCTION(Client, Reliable)` for targeted client feedback (HUD, sound triggers).
- **Multicast**: `UFUNCTION(NetMulticast, Unreliable)` for cosmetic VFX/SFX (e.g., muzzle flashes, impact sparks).
- **Blueprint-Callable**: `UFUNCTION(BlueprintCallable, Category = "BakirkoyBR|...")`
- **Replication Callbacks**: `UFUNCTION() void OnRep_*(...)` — `UFUNCTION()` is mandatory for OnRep callbacks.

---

## 4. Header File Template
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Data/BRTypes.h"

// Forward declarations
class UStaticMeshComponent;
class UNiagaraSystem;

// Strictly the final include
#include "ClassName.generated.h"

UCLASS(Blueprintable, ClassGroup = (BakirkoyBR))
class BAKIRKOYBR_API AClassName : public AParentClass
{
    GENERATED_BODY()

public:
    AClassName();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UStaticMeshComponent> MeshComponent;

private:
    // private members
};
```

---

## 5. Replication Rules
1. Always implement `GetLifetimeReplicatedProps` in classes containing replicated properties.
2. In the `.cpp` file, include `"Net/UnrealNetwork.h"` and register properties using `DOREPLIFETIME` or `DOREPLIFETIME_CONDITION`.
3. Every property utilizing `ReplicatedUsing = OnRep_XYZ` must have a matching `UFUNCTION() void OnRep_XYZ(...)`.
4. State mutation occurs exclusively on the server inside `HasAuthority()`. Clients request mutations via Server RPCs.
