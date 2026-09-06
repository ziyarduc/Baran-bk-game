---
name: ue5-world-interaction
description: UE5.6-UE5.8 world interaction systems for pickups, spawners, overlap/trace checks, and visual feedback. Use when requests involve interactive world actors, spawn logic, pickup behavior, interaction radius checks, success/failure feedback, and actor lifecycle control.
---

# Quick Start
- Define interaction model: overlap-driven, trace-driven, or explicit use key.
- Define actor set: pickup actor, optional spawner, optional visual mapping data asset.
- Output runtime state transitions from spawn to interaction resolution.

# API Anchors (UE5.6-UE5.8)
- Detection anchors:
  - `USphereComponent`, `UBoxComponent`
  - `UPrimitiveComponent::OnComponentBeginOverlap`
  - `UPrimitiveComponent::OnComponentEndOverlap`
  - `FHitResult`
- Trace anchors:
  - `UWorld::LineTraceSingleByChannel(...)`
  - `UWorld::SweepSingleByChannel(...)`
  - `UKismetSystemLibrary::SphereTraceSingle(...)`
- Lifecycle anchors:
  - `AActor::SetActorHiddenInGame(...)`
  - `AActor::SetActorEnableCollision(...)`
  - `AActor::Destroy(...)`
  - `AActor::SetActorTickEnabled(...)`
- Networking anchors:
  - server authority validation for interaction success
  - replicated result state for client feedback

# Interaction Stage Contract
- Every interaction feature must define:
  - Detection source (overlap/trace/use-key)
  - Eligibility checks (distance, tags, inventory/capacity, authority)
  - Success and failure result payloads
  - Feedback path (VFX/SFX/UI)
  - Post-interaction lifecycle policy (destroy/disable/cooldown/respawn)
- If any item is missing, interaction behavior is underspecified.

# Workflow
## 1) Actor and Component Setup
- Build root + collision + visual components with explicit collision channels.
- Define default states (`active`, `cooldown`, `consumed`) and replication needs.
- Keep collision shape and bounds aligned with intended interaction distance.

## 2) Detection Path
- Overlap model: bind begin/end overlap delegates on collision component.
- Trace model: run line/sphere traces on input request and validate hit actor/component.
- Keep detection deterministic by explicit channels/profiles.

## 3) Eligibility and Authority
- Validate target state, range, actor validity, and gameplay conditions.
- In multiplayer, validate success on server before mutating shared state.
- Return structured failure reason on rejection.

## 4) Resolve Interaction
- On success: apply effect (grant item, trigger state change, start cooldown).
- On failure: keep state stable and emit reason-specific feedback.
- Prevent re-entrant execution during in-progress resolution.

## 5) Feedback Path
- Emit VFX/SFX/UI feedback for both success and failure paths.
- Separate cosmetic-only effects from authoritative gameplay mutations.
- Keep feedback idempotent for repeated client updates.

## 6) Lifecycle and Cleanup
- Choose lifecycle explicitly: destroy, hide+disable collision, or reuse via respawn timer.
- If spawner exists, track spawned instances and cleanup on reset/despawn.
- Disable tick for dormant interaction actors when not needed.

# Constraints
- Keep interaction validation server-authoritative in multiplayer.
- Ensure collision channels and trace responses are explicit.
- Keep spawner randomization deterministic when reproducibility is needed.
- Avoid hidden side effects in `Tick` without clear need.
- Do not destroy actors before broadcasting required success/failure feedback.
- Keep overlap and trace paths functionally equivalent when both are enabled.

# Failure Handling
- Symptom: overlap never triggers.
  - Locate: collision enabled state, overlap flags, collision channel responses.
  - Fix: enable overlap generation, set proper channel responses, verify component bounds.
- Symptom: trace path misses obvious targets.
  - Locate: trace channel/profile and ignore actor list.
  - Fix: align trace channel/profile and reduce self/owner ignore misuse.
- Symptom: interaction triggers multiple times.
  - Locate: missing in-progress guard and duplicated delegate bindings.
  - Fix: add state guard and ensure single bind per component.
- Symptom: client sees success but server rejects.
  - Locate: authority checks and RPC validation path.
  - Fix: move final validation to server and replicate authoritative result.
- Symptom: consumed pickup remains interactable.
  - Locate: lifecycle state and collision disable logic.
  - Fix: disable collision/interaction immediately after confirmed success.
- Symptom: spawned interactables leak over time.
  - Locate: spawner bookkeeping and reset cleanup path.
  - Fix: track spawned instances and destroy/disable stale instances on respawn cycle.
- Symptom: frame spikes near dense interaction areas.
  - Locate: per-frame trace/overlap workload and unnecessary ticking.
  - Fix: reduce polling frequency, gate traces by input/distance, disable idle tick.

# Interaction Authority Ops
- Use server-validated interaction resolution for shared gameplay effects.
- Use client-side prediction only for cosmetic feedback when acceptable.
- Replicate result state, not raw input spam.
- Keep cooldown/timer ownership on authority side for deterministic multiplayer behavior.

# UE5.6-UE5.8 Compatibility Notes
- Overlap, trace, and actor lifecycle APIs listed above are stable across UE5.6-UE5.8.
- Prefer explicit collision profile/channel configuration across all supported versions.

# Escalation
- Escalate when design requires persistent world state synchronization across sessions.
- Escalate when system must integrate with GAS ability targeting rules.
---

## Bakırköy BR Core Constraints & MVP Directives

When applying this skill to the **Bakırköy BR** project, you MUST strictly adhere to:

### 1. The 7 Core Constraints
1. **No Interior Spaces**: Buildings are exterior-only collision volumes. No interior rooms, furniture, or interior NavMesh. Rooftop/terrace access is strictly via external stairs, ladders, or fire escapes.
2. **Solo BR Only**: First prototype supports Solo mode only. No squad logic, duos, revives, DBNO (Down-But-Not-Out), or team chat.
3. **Server-Authoritative**: Dedicated server validates and executes all gameplay state changes (HP, Shield, ammo, damage, storm, eliminations). Client predicts locally, server reconciles.
4. **3rd Person Camera**: Over-the-shoulder perspective only. ADS tightens camera FOV and spring arm length, but NEVER switches to 1st person.
5. **3 Build Materials**: Exactly 3 materials: Moloz (Debris: 60 start / 100 max HP), Tuğla (Brick: 80 start / 200 max HP), and Çelik (Steel: 100 start / 350 max HP). Never 4 materials.
6. **Hybrid Hit Detection**: AR, SMG, Shotgun, Sniper use server Hit-Scan line traces (`LineTraceSingleByChannel`). Rocket Launcher uses Chaos Projectile physics (`ABRProjectile` actor with 35 m/s velocity and radial splash damage).
7. **Mandatory C++ `BR` Prefix**: Every gameplay class, struct, and enum MUST be prefixed with `BR` (e.g. `ABRCharacter`, `UBRHealthComponent`, `FBRWeaponData`, `EBRBuildMaterial`).

### 2. Demo 1 Playable MVP Directives
- **10 Bots Test Scenario**: AI count is strictly limited to 10 bots. GameMode and AI logic must be optimized for this 10-bot vertical slice.
- **2 Weapon Prototypes**: Initial loot pool and combat mechanics test the hybrid hit detection using exactly 2 weapons: 1 Assault Rifle (Hit-Scan) and 1 Rocket Launcher (Projectile physics + splash damage).
- **Dual GameModes**: Support 2 distinct playable GameModes: Mode 1 Free-For-All (FFA / Deathmatch with score/time limit) and Mode 2 Classic Battle Royale (Last Man Standing with shrinking storm circle).
- **Building System Paused**: Building system is paused for Demo 1. Players and bots rely entirely on natural environment cover (vehicles, alleys, street walls).

