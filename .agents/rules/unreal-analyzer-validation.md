# C++ Code Analysis & Reflection Validation Standards

> **Bakırköy BR Project Rule**  
> **Status**: MANDATORY & HARD-LOCKED  
> **Applicable To**: QA Reviewer, Integrator, and All C++ Workers  
> **Reference**: Requirement R1 (`unreal-analyzer-mcp` and Static Code Quality)

---

## 1. Executive Summary & Purpose

The **Unreal Analyzer Validation Standards** define the static analysis, Abstract Syntax Tree (AST) validation, and Clang inspection rules applied across all Bakırköy BR C++ source code. These rules guarantee that code compiles cleanly under Unreal Header Tool (UHT), adheres to Unreal Engine 5 garbage collection and memory safety standards, preserves server-authoritative networking contracts, and prevents compilation regressions.

Static verification is enforced through:
1. **`unreal-analyzer-mcp`** AST inspection tools (`analyze_class`, `find_references`, `get_best_practices`).
2. Clang and MSVC compilation passes (`/W4` / `-Wall`).
3. Automated test scripts (`scripts/verify-rules.ps1`).

---

## 2. AST Inspection & Class Structure Rules

### Rule 1.1: Root Base Class & Hierarchy Validation
- Every gameplay actor class must derive from an appropriate engine base class or project base class:
  - Characters: `ABRCharacter` -> `ACharacter` -> `APawn` -> `AActor`
  - Weapons: `ABRWeaponBase` -> `AActor`
  - Projectiles: `ABRProjectile` -> `AActor`
  - Components: `UBRHealthComponent` -> `UActorComponent`
  - Game Modes: `ABRGameMode` -> `AGameModeBase`
  - Game States: `ABRGameState` -> `AGameStateBase`
  - Player States: `ABRPlayerState` -> `APlayerState`
  - Player Controllers: `ABRPlayerController` -> `APlayerController`
  - AI Controllers: `ABRAIController` -> `AAIController`
- Interfaces must be prefixed with `I` (e.g. `IBRDamageable`) and derive from `UInterface`.
- Multi-inheritance is permitted **only** when deriving from a single `UObject` base class plus one or more `UInterface`s.

### Rule 1.2: Macro Placement & Ordering in AST
1. **`UCLASS(...)`**: Must appear immediately above the class declaration without any intervening code, comments, or trailing semicolons:
   ```cpp
   UCLASS(Blueprintable, ClassGroup = (BakirkoyBR))
   class BAKIRKOYBR_API ABRCharacter : public ACharacter
   {
       GENERATED_BODY()
   ```
2. **`GENERATED_BODY()`**:
   - Must appear on the first non-comment line inside the class or struct body.
   - Must **NEVER** have a trailing semicolon.
   - Access specifier following `GENERATED_BODY()` must be explicitly declared (`public:`, `protected:`, or `private:`).
3. **`USTRUCT(BlueprintType)`**:
   - Structs passed across Blueprint or network boundaries must declare `USTRUCT(BlueprintType)` and contain `GENERATED_BODY()`.
4. **`UENUM(BlueprintType)`**:
   - Must use `enum class` deriving from `uint8` (`enum class EBRGamePhase : uint8`).

---

## 3. Header Hygiene & Include Hierarchy

### Rule 2.1: The Absolute Last Include Directive
- In any header file containing Unreal reflection (`UCLASS`, `USTRUCT`, `UENUM`, `UINTERFACE`), the generated header `#include "ClassName.generated.h"` **MUST BE STRICTLY THE LAST `#include` DIRECTIVE**.
- **AST / Regex Verification**:
  ```regex
  #include\s+["<].*\.generated\.h[">](?![\s\S]*#include)
  ```
  If any `#include` appears after `.generated.h`, the file fails AST validation.

### Rule 2.2: Forward Declarations Over Header Inclusions
- Headers (`.h`) must use forward declarations for all referenced pointer types:
  ```cpp
  class USkeletalMeshComponent;
  class UNiagaraSystem;
  class ABRWeaponBase;
  ```
- Concrete includes (`#include "Weapons/BRWeaponBase.h"`) belong exclusively in `.cpp` files.
- Exception: Base classes and structs passed by value must be included in the header.

### Rule 2.3: Header Guard Integrity
- Every header file must begin with `#pragma once` on line 1.
- Traditional `#ifndef` / `#define` include guards are discouraged in favor of `#pragma once`.

---

## 4. Reflection, Garbage Collection & Pointer Validation

### Rule 3.1: Raw UObject Pointer Prohibition
- Any member variable pointing to a `UObject`, `AActor`, or `UActorComponent` must be declared as:
  ```cpp
  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
  TObjectPtr<UStaticMeshComponent> MeshComponent;
  ```
- **AST / Regex Violation Pattern**:
  ```regex
  ^\s*(?:const\s+)?([UAF][A-Z][a-zA-Z0-9_]*)\s*\*\s*([a-zA-Z0-9_]+)\s*;
  ```
  Any raw pointer matching this pattern inside a class without `TObjectPtr<>` is flagged.

### Rule 3.2: Non-Owning Cached References
- Member references to external actors that may be destroyed at runtime (e.g., target actor, last damage causer) must use `TWeakObjectPtr<AActor>` rather than a strong `TObjectPtr<>` to prevent preventing garbage collection sweeps.

### Rule 3.3: Strict Ban on Standard C++ Library (STL) Types
- AST checks flag any occurrence of:
  - `std::string` -> use `FString` / `FText` / `FName`
  - `std::vector` -> use `TArray`
  - `std::map` / `std::unordered_map` -> use `TMap`
  - `std::set` -> use `TSet`
  - `std::shared_ptr` / `std::unique_ptr` -> use `TSharedPtr` / `TUniquePtr` / `TObjectPtr`

---

## 5. Replication & RPC Network Validation

### Rule 4.1: Property Replication Mirroring
- If a property is marked `UPROPERTY(Replicated)` or `UPROPERTY(ReplicatedUsing = OnRep_XYZ)`:
  1. The class header must declare:
     ```cpp
     virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
     ```
  2. The `.cpp` file must implement `DOREPLIFETIME(AClassName, PropertyName)`.
  3. The `.cpp` file must include `"Net/UnrealNetwork.h"`.
  4. If `ReplicatedUsing = OnRep_XYZ` is specified, `UFUNCTION() void OnRep_XYZ(...)` must exist.

### Rule 4.2: Server RPC Validation Contract
- Every Server RPC must follow this declaration signature:
  ```cpp
  UFUNCTION(Server, Reliable, WithValidation)
  void Server_ExecuteFire(const FVector& AimOrigin, const FVector_NetQuantizeNormal& ShootDir);
  ```
- Both implementations must be present in `.cpp`:
  - `bool AClassName::Server_ExecuteFire_Validate(...)`
  - `void AClassName::Server_ExecuteFire_Implementation(...)`
- Validation bounds: `_Validate` must verify that vectors are normalized, floats are non-negative, and values are within plausible gameplay ranges.

---

## 6. Clang Checks & Static Analysis Standards

Code must satisfy the following Clang-tidy and compiler checks:
1. **`-Wall -Wextra -Werror` / `/W4 /WX`**: Zero compilation warnings.
2. **Readability**:
   - PascalCase for all methods and variables.
   - Prefix `b` for all booleans (`bIsFiring`, `bHasShield`).
   - Prefix `BR` for all project classes.
3. **No Dangling References**: References passed into asynchronous tasks or timers must use weak pointers or value copies.

---

## 7. QA Automated Audit Procedure

When auditing code, QA Reviewer executes the following multi-layer inspection:

1. **Step 1: AST Scan via `unreal-analyzer-mcp`**:
   - Run `analyze_class` on modified classes.
   - Run `get_best_practices` to check memory safety and reflection specifiers.
2. **Step 2: Scripted Regex & Inclusion Audit**:
   - Run `powershell -ExecutionPolicy Bypass -File scripts/verify-rules.ps1`.
   - Verify zero errors reported across all headers and source files.
3. **Step 3: Network Authority Verification**:
   - Inspect all damage-dealing methods to confirm they execute exclusively on the server (`HasAuthority()`).
