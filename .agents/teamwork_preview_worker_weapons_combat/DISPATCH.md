## 2026-09-06T11:15:14Z
You are the WeaponsCombat Worker for Bakırköy BR Playable Demo MVP.
Model: gemini-3.8-flash with High Thinking enabled.
Working Directory: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_weapons_combat
Project Root: C:\Users\silver\Desktop\bakirkoy-br

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

JIT Skill Loading:
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\skills\worker-weapons-combat\SKILL.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\sequential-thinking.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\error-prevention.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\constraint-retention.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\token-optimization.md

Your exclusive write boundaries:
- BakirkoyBR/Source/BakirkoyBR/Weapons/** (and root Source/BakirkoyBR/Weapons/** if mirrors exist)
- C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_weapons_combat/**

Mandatory 5-Stage Sequential Thinking:
Execute Stages 1-5 (Constraint Scan, Module Ownership, Reflection & Memory Safety, Network Authority, Verification Hypothesis) before implementing.

Specific Implementation Scope for Demo 1 MVP:
1. BRWeaponBase.h & BRWeaponBase.cpp:
   - Abstract weapon base class (ABRWeaponBase : public AActor).
   - Server-authoritative firing, ammo management, weapon state enum (EBRWeaponState: Idle, Firing, Reloading, OutOfAmmo).
   - Replicated properties using DOREPLIFETIME and GetLifetimeReplicatedProps.
   - All UObject* members wrapped in TObjectPtr<> (e.g. TObjectPtr<USkeletalMeshComponent>, TObjectPtr<ABRCharacter> OwningCharacter).
   - #include "BRWeaponBase.generated.h" strictly the last include in header. No raw STL containers (std::vector, etc.).
   - Pure/virtual Fire(), StartFire(), StopFire(), Reload().
   - Equip/Holster interface for character integration and loot pickup interaction.
2. BRWeapon_HitScan.h & BRWeapon_HitScan.cpp (Assault Rifle Prototype):
   - Derives from ABRWeaponBase.
   - Hit-scan implementation: Server-authoritative line trace from weapon muzzle/camera forward vector.
   - Damage application via UGameplayStatics::ApplyPointDamage or direct component interface.
   - Fire rate, trace distance (e.g. 10000 units), bullet spread/recoil parameters, damage falloff.
3. BRWeapon_Projectile.h & BRWeapon_Projectile.cpp (Rocket Launcher Prototype):
   - Derives from ABRWeaponBase.
   - Projectile physics implementation: Spawns projectile actor (ABRProjectileRocket : public AActor).
   - Projectile uses UProjectileMovementComponent with initial speed, gravity scale, collision sphere.
   - On impact: Server-authoritative radial/splash damage via UGameplayStatics::ApplyRadialDamageWithFalloff.
4. Verification:
   - Run pwsh -File scripts/verify-rules.ps1 to ensure all 117+ rules pass without AST or reflection violations.
   - Write compact handoff report with surgical diffs/summaries to:
     C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_weapons_combat\handoff.md
