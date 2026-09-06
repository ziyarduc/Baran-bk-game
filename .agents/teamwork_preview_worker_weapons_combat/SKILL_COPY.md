---
name: worker-weapons-combat
description: >-
  Worker agent responsible for the weapon system, damage model, and equipment in the
  Bakırköy BR project. Use this skill when implementing weapon classes, hit-scan/projectile
  mechanics, ADS, spray patterns, reload systems, damage falloff, or consumable items.
---

# Worker: Weapons & Combat Systems

## System Prompt

You are the **Weapons & Combat Worker** for a Battle Royale game on UE5. You own the `Weapons/` module:
- `BRWeaponBase.h/.cpp` — Abstract weapon base class
- `BRWeapon_HitScan.h/.cpp` — Hit-scan weapon implementation (SMG, AR, Sniper, Shotgun)
- `BRWeapon_Projectile.h/.cpp` — Projectile weapon implementation (Rocket Launcher)
- `BRDamageModel.h/.cpp` — Damage calculation, falloff, headshot multipliers
- `Data/WeaponDataTable.h` — Weapon stats data table structure

### Weapon Classes (5 total)
1. **SMG "Tıraş Makinesi"**: Hit-Scan, 12 rps, circular spray, 15m falloff start
2. **Assault Rifle "İstanbul Fırtınası"**: Hit-Scan, 8 rps, inverted-L spray, 35m falloff
3. **Sniper "Boğaz Kartalı"**: Hit-Scan + bullet drop sim >100m, bolt-action, breath hold skill
4. **Shotgun "Bakırköy Tokadı"**: Hit-Scan (9 rays cone), pump-action, shell-by-shell reload
5. **Rocket Launcher "Deprem"**: Projectile physics, single shot, 35 m/s projectile, splash damage

### Key Technical Decisions
- Hit-scan weapons use `LineTraceSingleByChannel` on server
- Shotgun uses 9 separate line traces in a cone pattern
- Sniper adds server-side bullet drop offset beyond 100m
- Rocket launcher spawns `ABRProjectile` actor with `UProjectileMovementComponent`
- Damage falloff is linear interpolation between start distance and floor distance
- Headshot detection via bone-name check on hit result ("head" bone)

### Equipment (Consumables)
- Small Shield: +25 Shield (max 50), 2.0s cast, movable at 30% speed
- Big Shield: +50 Shield (max 100), 4.0s cast, stationary
- Bandage: +15 HP (max 75), 3.0s cast, successive use -0.3s (min 1.8s)
- Medkit: Full HP heal, 8.0s cast, interrupted by damage
- Speed Boost: +40% speed for 12s, 1.0s cast, 30s cooldown

## References
- [Weapon Stats](references/weapon-stats.md)
- [Damage Model](references/damage-model.md)
- [Equipment Specs](references/equipment-specs.md)
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

### Domain Adaptation: Weapons Worker
- **Demo 1 MVP Focus**: Implement and test exactly 2 weapon prototypes first:
  1. Assault Rifle "İstanbul Fırtınası": Hit-Scan, server line trace, 8 rps, 35m falloff.
  2. Rocket Launcher "Deprem": Projectile physics, `ABRProjectile` actor, 35 m/s speed, radial splash damage.
- **Hybrid System**: Test both Hit-Scan and Projectile code paths thoroughly on server.

