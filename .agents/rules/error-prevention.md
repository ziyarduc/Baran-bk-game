# UE5 C++ Error Prevention & Anti-Pattern Catalogue

> **Bakırköy BR Project Rule**  
> **Status**: MANDATORY & HARD-LOCKED  
> **Applicable To**: All Agents, Orchestrator, Workers, QA Reviewer, and Integrator  
> **Reference**: Requirement R1 (Hata Önleyici MCP ve Skill'lerin Entegrasyonu)

---

## 1. Executive Summary & Purpose

Unreal Engine 5 C++ requires strict adherence to engine-specific reflection, memory management, and networking paradigms. Large Language Models (LLMs) and automated agents frequently produce code that fails Unreal Header Tool (UHT) parsing, triggers garbage collection (GC) memory corruption, violates network authority, or introduces ABI incompatibilities through standard C++ library (STL) usage.

This document serves as the project's **Anti-Pattern Catalogue** and **Error Prevention Manual**. Every rule in this catalogue is absolute; violations will be flagged by automated static analyzers, caught by the QA Reviewer gate, and cause immediate task rejection.

---

## 2. Comprehensive Anti-Pattern Catalogue

### Anti-Pattern 1: Header Inclusion Order Violation (`.generated.h` Not Strictly Last)

- **The Flaw**: Placing any `#include`, macro invocation, or code directive after `#include "ClassName.generated.h"`.
- **Engine Consequence**: Fatal Unreal Header Tool (UHT) compilation error (`fatal error : #include found after .generated.h: ClassName.generated.h must be the last include in your header!`).
- **Rule**: In any header declaring a `UCLASS`, `USTRUCT`, `UENUM`, or `UINTERFACE`, `#include "ClassName.generated.h"` **MUST ALWAYS BE THE VERY LAST `#include` STATEMENT**. No `#include` statements, type definitions, or forward declarations may appear after it.

#### ❌ Incorrect Pattern
```cpp
// ABRWeaponBase.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BRWeaponBase.generated.h" // ❌ FATAL: Include placed before other includes!
#include "Data/BRTypes.h"
#include "NiagaraSystem.h"

UCLASS()
class BAKIRKOYBR_API ABRWeaponBase : public AActor
{
    GENERATED_BODY()
};
```

#### ✅ Compliant Pattern
```cpp
// ABRWeaponBase.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Data/BRTypes.h"
// Forward declarations for pointer types
class UNiagaraSystem;
class UStaticMeshComponent;

// Strictly the final include
#include "BRWeaponBase.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRWeaponBase : public AActor
{
    GENERATED_BODY()
};
```

---

### Anti-Pattern 2: Garbage Collection Pointer Safety (`TObjectPtr<>` vs Raw Pointers)

- **The Flaw**: Storing raw C++ pointers (`UObject*`, `AActor*`, `UActorComponent*`) as member variables without `UPROPERTY()` reflection tracking, or failing to use modern UE5 `TObjectPtr<>`.
- **Engine Consequence**:
  1. The Unreal Garbage Collector (GC) runs sweeps and marks unreferenced `UObject`s for deletion. A raw non-reflected pointer is invisible to GC, leaving a **dangling pointer** that causes catastrophic null-pointer or access-violation crashes when dereferenced.
  2. In UE5.0+, raw pointers bypass access tracking, lazy loading, and editor resolution features provided by `TObjectPtr<>`.
- **Rule**:
  1. All `UObject`-derived member pointers inside `UCLASS` or `USTRUCT` **MUST** be wrapped in `TObjectPtr<T>` and annotated with `UPROPERTY()`.
  2. For non-owning or cross-actor cached references that might be destroyed during gameplay, use `TWeakObjectPtr<T>`.
  3. **NEVER** use C++ raw `new` or `delete` operators for `UObject` instances. Use `NewObject<T>()` for `UObject`s and `GetWorld()->SpawnActor<T>()` for `AActor`s.

#### ❌ Incorrect Pattern
```cpp
UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter
{
    GENERATED_BODY()

private:
    // ❌ FATAL: Raw pointer without UPROPERTY. GC will collect this under memory pressure!
    USkeletalMeshComponent* WeaponMesh;

    // ❌ FATAL: Raw pointer in UE5 header. Bypasses engine access tracking.
    UPROPERTY(VisibleAnywhere)
    UBRHealthComponent* HealthComponent;

    // ❌ FATAL: Memory leak / crash: allocating UObject via new
    void InitCustomData() {
        UBRDataAsset* NewData = new UBRDataAsset(); // FORBIDDEN!
    }
};
```

#### ✅ Compliant Pattern
```cpp
UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ABRCharacter();

private:
    // ✅ Modern UE5 TObjectPtr with UPROPERTY reflection tracking
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<USkeletalMeshComponent> WeaponMesh;

    // ✅ Subobject component tracking
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<UBRHealthComponent> HealthComponent;

    // ✅ Weak pointer for non-owning actor reference (e.g. current target)
    UPROPERTY(Transient)
    TWeakObjectPtr<AActor> CurrentTargetActor;

    // ✅ Allocation via NewObject / SpawnActor
    void SpawnDrop(TSubclassOf<AActor> ActorClass, const FTransform& Transform)
    {
        if (GetWorld() && *ActorClass)
        {
            FActorSpawnParameters SpawnParams;
            SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
            GetWorld()->SpawnActor<AActor>(ActorClass, Transform, SpawnParams);
        }
    }
};
```

---

### Anti-Pattern 3: Reflection Macro Misuse & Formatting Errors

- **The Flaw**: Semicolons after macro declarations, missing `GENERATED_BODY()`, incorrect class macro prefixes, or omitting `BlueprintReadOnly`/`EditDefaultsOnly` encapsulation.
- **Engine Consequence**: UHT parse failures or broken reflection introspection in Blueprint/Editor.
- **Rule**:
  1. `UCLASS()`, `USTRUCT()`, `UENUM()`, `UPROPERTY()`, and `UFUNCTION()` **NEVER** take a trailing semicolon.
  2. `GENERATED_BODY()` **MUST** be placed on the first line inside the class/struct body, followed by a newline, with no semicolon.
  3. Enums must use `UENUM(BlueprintType)` and derive from `uint8` (`enum class EBRWeaponType : uint8`).
  4. Structs must use `USTRUCT(BlueprintType)` with `GENERATED_BODY()`.

#### ❌ Incorrect Pattern
```cpp
UCLASS(); // ❌ Syntax error: trailing semicolon
class BAKIRKOYBR_API ABRProjectile : public AActor
{
    // ❌ Missing GENERATED_BODY()
    UPROPERTY(); // ❌ Trailing semicolon
    float Speed; // ❌ Primitive without category or accessor control
};

UENUM()
enum EBRMaterial // ❌ Missing BlueprintType and : uint8 enum class specification
{
    Moloz,
    Tugla,
    Celik
};
```

#### ✅ Compliant Pattern
```cpp
UENUM(BlueprintType)
enum class EBRMaterialType : uint8
{
    Moloz UMETA(DisplayName = "Moloz (Debris)"),
    Tugla UMETA(DisplayName = "Tuğla (Brick)"),
    Celik UMETA(DisplayName = "Çelik (Steel)")
};

USTRUCT(BlueprintType)
struct FBRWeaponStats
{
    GENERATED_BODY()

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
    float BaseDamage = 30.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
    float FireRate = 600.0f;
};

UCLASS()
class BAKIRKOYBR_API ABRProjectile : public AActor
{
    GENERATED_BODY()

public:
    ABRProjectile();

protected:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Projectile")
    float InitialSpeed = 4000.0f;
};
```

---

### Anti-Pattern 4: Replication Boilerplate & Network Authority Bypass

- **The Flaw**:
  1. Setting `UPROPERTY(Replicated)` or `UPROPERTY(ReplicatedUsing = OnRep_...)` without implementing `GetLifetimeReplicatedProps`.
  2. Omitting `#include "Net/UnrealNetwork.h"` in `.cpp`.
  3. Declaring `ReplicatedUsing = OnRep_XYZ` but forgetting `UFUNCTION()` on the `OnRep_XYZ` declaration.
  4. Modifying authoritative gameplay state (Health, Shield, Inventory, Storm) on the simulated client.
  5. Declaring Server RPCs without `WithValidation` or failing to validate bounds.
- **Engine Consequence**:
  - Missing `DOREPLIFETIME` causes property updates never to serialize across the network.
  - Missing `UFUNCTION()` on `OnRep_` callback causes silent failure (the client never calls the function when the property updates).
  - Client-side authoritative modification causes desync and desynchronization exploits.
- **Rule**:
  1. Every class with replicated properties **MUST** override `virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;`.
  2. The `.cpp` implementation **MUST** include `"Net/UnrealNetwork.h"` and call `DOREPLIFETIME(AClassName, PropertyName)`.
  3. All `OnRep_` functions **MUST** have the `UFUNCTION()` macro.
  4. All state mutations must occur strictly inside `HasAuthority()` checks on the server. Client initiates action via `UFUNCTION(Server, Reliable, WithValidation)`.

#### ❌ Incorrect Pattern
```cpp
// Header
UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter
{
    GENERATED_BODY()

    // ❌ FATAL: OnRep callback declared without UFUNCTION()! Will never be invoked!
    UPROPERTY(ReplicatedUsing = OnRep_Health)
    float CurrentHealth;

    void OnRep_Health(); // ❌ Missing UFUNCTION() macro
};

// Source
void ABRCharacter::TakeDamageLocally(float DamageAmount)
{
    // ❌ FATAL: Client mutating authoritative health directly
    CurrentHealth -= DamageAmount; 
}
```

#### ✅ Compliant Pattern
```cpp
// Header (BRCharacter.h)
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "BRCharacter.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ABRCharacter();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UFUNCTION(Server, Reliable, WithValidation)
    void Server_ApplyDamage(float DamageAmount, AActor* DamageCauser);

protected:
    UPROPERTY(ReplicatedUsing = OnRep_Health, BlueprintReadOnly, Category = "Health")
    float CurrentHealth = 100.0f;

    // ✅ Properly reflected OnRep callback
    UFUNCTION()
    virtual void OnRep_Health(float OldHealth);
};

// Source (BRCharacter.cpp)
#include "Character/BRCharacter.h"
#include "Net/UnrealNetwork.h" // ✅ Mandatory include for DOREPLIFETIME

ABRCharacter::ABRCharacter()
{
    bReplicates = true;
}

void ABRCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    // ✅ Explicit replication registration
    DOREPLIFETIME(ABRCharacter, CurrentHealth);
}

bool ABRCharacter::Server_ApplyDamage_Validate(float DamageAmount, AActor* DamageCauser)
{
    // ✅ Server-side bounds validation
    return DamageAmount >= 0.0f && DamageAmount <= 1000.0f;
}

void ABRCharacter::Server_ApplyDamage_Implementation(float DamageAmount, AActor* DamageCauser)
{
    // ✅ Server authoritative mutation
    if (HasAuthority())
    {
        const float OldHealth = CurrentHealth;
        CurrentHealth = FMath::Clamp(CurrentHealth - DamageAmount, 0.0f, 100.0f);
        OnRep_Health(OldHealth); // Invoke manually on listen-server host
    }
}

void ABRCharacter::OnRep_Health(float OldHealth)
{
    // Client-side visual / UI update
}
```

---

### Anti-Pattern 5: Use of Standard C++ Library (STL) Types

- **The Flaw**: Using `std::string`, `std::vector`, `std::map`, `std::unordered_map`, `std::shared_ptr`, `std::unique_ptr` in game code, especially inside `UCLASS`, `USTRUCT`, or `UFUNCTION` interfaces.
- **Engine Consequence**:
  1. UHT does not support STL types in reflection macros. Compilation fails instantly.
  2. Memory allocator mismatch between Unreal's `FMalloc` / `FMemory` and standard CRT allocators.
  3. Performance degradation: Unreal containers (`TArray`, `TMap`) provide cache-friendly inline allocation, memory tracking, and seamless serialization.
- **Rule**: Standard library containers and primitives are strictly banned in all project code. Use Unreal equivalents exclusively:

| Standard C++ (STL) ❌ | Unreal Engine Native Type ✅ | Notes |
|---|---|---|
| `std::string` | `FString` | Dynamic string |
| `const char*` / identifier | `FName` | Fast, case-insensitive hashed name |
| localized string | `FText` | Localized UI display text |
| `std::vector<T>` | `TArray<T>` | Dynamically sized array |
| `std::map<K, V>` | `TMap<KeyType, ValueType>` | Hashed key-value map |
| `std::set<T>` | `TSet<ElementType>` | Fast hashing set |
| `std::shared_ptr<T>` | `TSharedPtr<T>` | Non-UObject reference counted pointer |
| `std::weak_ptr<T>` | `TWeakPtr<T>` | Non-UObject weak pointer |
| `std::unique_ptr<T>` | `TUniquePtr<T>` | Sole ownership pointer |
| `UObject*` raw ptr | `TObjectPtr<T>` | UObject member pointer |
| `std::pair<T1, T2>` | `TTuple<T1, T2>` | Tuple type |
| `std::cout`, `printf` | `UE_LOG(LogTemp, ...)` | Engine structured logging |

---

### Anti-Pattern 6: Circular Header Inclusion & Header Bloat

- **The Flaw**: Including `#include "BRWeaponBase.h"` inside `BRCharacter.h`, while `#include "BRCharacter.h"` is included in `BRWeaponBase.h`.
- **Engine Consequence**: Circular dependency compilation errors, catastrophic compilation time bloat, fragile header order.
- **Rule**:
  1. Headers (`.h`) **MUST** use forward declarations (`class ABRWeaponBase;`, `class UBRHealthComponent;`) whenever a type is used only as a pointer or reference parameter.
  2. Include the concrete header (`#include "Weapons/BRWeaponBase.h"`) only in the `.cpp` file.
  3. Every header file must begin with `#pragma once` on line 1.

---

### Anti-Pattern 7: Violation of Write Boundaries & Agent Artifact Contamination

- **The Flaw**: Placing source code (`.h`, `.cpp`), game assets (`.uasset`), or tests inside `.agents/` or placing agent plan/metadata files inside `Source/`.
- **Engine Consequence**: Corrupts project build graph, pollutes git repo, and violates multi-agent isolation contracts.
- **Rule**:
  - `Source/BakirkoyBR/` is strictly for C++ source code and headers.
  - `Config/` is strictly for engine `.ini` configuration files.
  - `scripts/` is strictly for standalone operational and validation scripts.
  - `.agents/` is strictly for metadata, rules, and handoffs. **NEVER** write game source code here.

---

## 3. Pre-Commit Quality Gate & Verification Checklist

Before submitting code, finalizing a task, or creating a handoff, every agent must verify the following checklist:

- [ ] **Include Order**: `#include "ClassName.generated.h"` is strictly the last `#include` in every header.
- [ ] **Pragma Once**: `#pragma once` is the first non-comment line in every header.
- [ ] **Naming Standard**: All gameplay classes start with `BR` (`ABR...`, `UBR...`, `FBR...`, `EBR...`, `IBR...`).
- [ ] **GC Safety**: All `UObject*` member pointers use `TObjectPtr<>` and are annotated with `UPROPERTY()`.
- [ ] **No STL**: Zero instances of `std::string`, `std::vector`, `std::map`, or standard pointers in engine-facing code.
- [ ] **Replication Setup**: Any replicated property has `GetLifetimeReplicatedProps` implemented with `DOREPLIFETIME` and `"Net/UnrealNetwork.h"` included.
- [ ] **RPC Safety**: Server RPCs have `Server, Reliable, WithValidation` and both `_Implementation` and `_Validate` bodies defined.
- [ ] **Authority Check**: Gameplay mutations (HP, Shield, Inventory, Storm) are executed on the server under `HasAuthority()`.
- [ ] **Forward Declarations**: Headers use forward declarations; heavy headers are included only in `.cpp`.
- [ ] **Zero Compilation Warnings**: Code builds with `/W4` or `-Wall` without warnings.
