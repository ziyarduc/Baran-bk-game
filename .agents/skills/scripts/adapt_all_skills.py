#!/usr/bin/env python3
"""
Adapt all 66 skills in .agents/skills/ to inject Bakırköy BR Core Constraints and MVP Directives.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STANDARD_COMPLIANCE_BLOCK = """
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
"""

DOMAIN_SPECIFIC_CALLOUTS = {
    "ue5-pcg-building": """
### Domain Adaptation: PCG & Building Generation
- **Exterior Only**: PCG graphs must ONLY generate exterior facade shells and bounding collision hulls. Never generate internal partitions, rooms, doors, or furniture.
- **Rooftop Navigation**: Generate external staircases, scaffolding, or fire escapes on building exteriors to enable vertical gameplay to rooftops.
- **NavMesh Exclusion**: Ensure generated building footprints write to `NavArea_Null` so navigation mesh generates exclusively on outdoor streets, alleys, and exterior stairways.
""",
    "ai-and-navigation": """
### Domain Adaptation: AI & Navigation
- **10 Bots Scenario**: Configure AIController and NavMesh querying for a 10-bot test scenario. Optimize patrol paths, perception update frequency, and combat engagement for 10 active bots.
- **Exterior NavMesh**: Place `NavModifierVolume(NavArea_Null)` over all building footprints. NavMesh must generate exclusively on outdoor streets, alleys, plazas, and exterior fire escapes/stairs leading to rooftops.
- **Combat Behavior**: Bots must navigate to loot spawns, pick up the 2 weapon prototypes (AR Hit-Scan and Rocket Launcher Projectile), and use natural environment cover (vehicles, corners, walls) rather than player builds.
""",
    "gameplay-framework": """
### Domain Adaptation: Gameplay Framework & GameModes
- **Dual GameModes**:
  1. `ABRGameMode_FFA`: Free-For-All deathmatch with score/kill limit and match countdown timer.
  2. `ABRGameMode_BR`: Classic Battle Royale with 7-phase shrinking storm circle and Last Man Standing victory condition.
- **Solo BR Architecture**: `ABRGameState` and `ABRPlayerState` track individual players and bots only. No squad structures, team IDs, or shared inventories.
- **10-Bot Match Loop**: Server spawns 1 player and 10 bots across outdoor spawn points.
- **Server Authority**: All state transitions (match state, storm phase, score, eliminations) execute strictly on the server.
""",
    "character-and-movement": """
### Domain Adaptation: Character & Camera
- **3rd Person Camera**: Player character `ABRCharacter` must use an over-the-shoulder camera setup with `USpringArmComponent` (TargetArmLength ~250cm, SocketOffset ~[0, 50, 20]).
- **ADS Zoom Only**: Aim Down Sights (ADS) tightens the spring arm and lowers camera FOV, but MUST NEVER transition to a first-person camera or mesh hide.
- **Server-Authoritative Movement**: Use standard `UCharacterMovementComponent` with client prediction and server validation.
- **Building Mode Paused**: Build mode inputs and component activation are disabled for Demo 1.
""",
    "enhanced-input": """
### Domain Adaptation: Input & Controls
- **Camera Controls**: Input actions for aiming (ADS) must interpolate spring arm offset and camera FOV; never toggle first-person camera modes.
- **Building Actions Paused**: Input mapping contexts for building pieces (Wall, Ramp, Floor) must be disabled or unmapped for Demo 1.
- **Weapon Switching**: Bind weapon slot keys for the 2 prototype weapons (AR Hit-Scan on Slot 1, Rocket Launcher Projectile on Slot 2).
""",
    "networking-and-replication": """
### Domain Adaptation: Networking & Replication
- **Server Authority**: Health, Shield, weapon fire validation, and storm circles must only be modified on the server. Clients send input RPCs (`ServerFireHitScan`, `ServerFireProjectile`).
- **Solo State Only**: Do not replicate squad or team data. Replicate `AlivePlayerCount`, `Kills`, and storm parameters to all clients.
- **10-Bot Optimization**: Bot AI runs exclusively on the server; replicate bot transform, animation state, and weapon firing to clients.
""",
    "physics-and-chaos": """
### Domain Adaptation: Physics & Hit Detection
- **Hybrid Hit Detection**:
  * AR Hit-Scan: Server line trace (`LineTraceSingleByChannel`) using `ECC_GameTraceChannel1` (Weapon).
  * Rocket Launcher: Spawns `ABRProjectile` actor with `UProjectileMovementComponent` (35 m/s) and radial damage sweep on impact.
- **Natural Cover Physics**: Vehicle meshes, concrete barriers, and street props must have robust Chaos collision profiles (`BlockAll` or `BlockWeaponTrace`).
- **Building Pieces Paused**: Structure destruction physics are paused for Demo 1.
""",
    "levels-and-world-partition": """
### Domain Adaptation: World & Map Structure
- **Bakırköy Urban Map**: Map dimensions ~3.2km × 2.1km covering Bakırköy district with narrow streets, alleys, and open plazas.
- **Exterior Only**: All building actors are solid meshes. No interior rooms or corridors.
- **Vertical Rooftop Access**: Place exterior fire escapes, steel stairs, and ramps linking street level to rooftops.
- **Outdoor Loot Spawns**: All loot chests and weapon spawn locations must be situated in outdoor streets, courtyards, and rooftops.
""",
    "coding-standards": """
### Domain Adaptation: C++ Coding Standards & Naming
- **Mandatory `BR` Prefix**: Every gameplay class, struct, and enum in Bakırköy BR MUST start with `BR`:
  * `ABRCharacter`, `ABRPlayerController`, `ABRGameModeBase`
  * `UBRHealthComponent`, `UBRPerceptionComponent`
  * `FBRWeaponData`, `FBRLootSpawnRow`
  * `EBRHitScanType`, `EBRGameModeType`
- **Reflection & GC**: Always use `UPROPERTY()`, `UFUNCTION()`, `TObjectPtr<T>`, and `#include "ClassName.generated.h"` as the final include.
""",
    "gameplay-ability-system": """
### Domain Adaptation: Gameplay Ability System (GAS)
- **Solo BR Rules**: No Down-But-Not-Out (DBNO) or team revive gameplay abilities. When health reaches 0, trigger immediate elimination gameplay effect.
- **Server Authority**: Ability System Component (`UBRAbilitySystemComponent`) and Attribute Set (`UBRAttributeSet`) must be server-authoritative. Replicate attributes (HP 0-100, Shield 0-100) to owner client.
- **Naming**: All GAS classes and tags must use the `BR.` namespace and `BR` prefix (`UBRGameplayAbility`, `BR.Status.Shield`).
""",
    "mover-movement-system": """
### Domain Adaptation: Mover Movement
- **3rd Person Restraint**: Mover trajectory generation and root motion must preserve over-the-shoulder 3rd person camera tracking.
- **Network Resimulation**: Server-authoritative rollback and resimulation for the solo player and 10 bot pawns.
""",
    "umg-and-slate": """
### Domain Adaptation: UI & HUD
- **Solo BR & FFA HUD**: HUD displays player Health, Shield, weapon ammo, alive player count (out of 11: 1 player + 10 bots), and storm timer / score tracker.
- **No Squad UI**: Do not create teammate status panels, squad markers, or revive indicators.
- **3rd Person Crosshair**: Reticle centered on 3rd person aim point with hit markers and damage numbers.
""",
    "ue5-ui-umg-slate": """
### Domain Adaptation: UI & HUD
- **Solo BR & FFA HUD**: HUD displays player Health, Shield, weapon ammo, alive player count (out of 11: 1 player + 10 bots), and storm timer / score tracker.
- **No Squad UI**: Do not create teammate status panels, squad markers, or revive indicators.
- **3rd Person Crosshair**: Reticle centered on 3rd person aim point with hit markers and damage numbers.
""",
    "audio-and-metasounds": """
### Domain Adaptation: Audio & MetaSounds
- **Exterior Acoustic Model**: MetaSounds patches should simulate outdoor urban acoustics (narrow street reverb, alley reflections, open rooftop spatialization).
- **Prototype Weapon Audio**: Audio synthesis for AR firing/reloading and Rocket Launcher launch/explosion.
- **Storm Warning**: Audio siren and atmospheric bass hum for the shrinking storm boundary.
""",
    "niagara-vfx": """
### Domain Adaptation: Niagara Visual Effects
- **Combat VFX**: Niagara systems for AR hit-scan tracer lines, muzzle flashes, surface impact sparks, and Rocket Launcher projectile trail / radial explosion blast.
- **Storm Barrier VFX**: Cylindrical energy wall effect representing the shrinking storm circle.
- **Outdoor Environment**: Ambient dust and leaves on streets; no interior atmospheric lighting effects.
""",
    "worker-weapons-combat": """
### Domain Adaptation: Weapons Worker
- **Demo 1 MVP Focus**: Implement and test exactly 2 weapon prototypes first:
  1. Assault Rifle "İstanbul Fırtınası": Hit-Scan, server line trace, 8 rps, 35m falloff.
  2. Rocket Launcher "Deprem": Projectile physics, `ABRProjectile` actor, 35 m/s speed, radial splash damage.
- **Hybrid System**: Test both Hit-Scan and Projectile code paths thoroughly on server.
""",
    "worker-building-system": """
### Domain Adaptation: Building System Worker
- **STATUS: PAUSED FOR DEMO 1**: Per user directive, the building system is PAUSED for Demo 1 to focus on shooting, movement, and 10-bot combat.
- **3 Materials Constraint**: When development resumes, strictly 3 materials must be implemented: Moloz (60/100 HP), Tuğla (80/200 HP), Çelik (100/350 HP). Never 4 materials.
- **Natural Cover**: Ensure code allows bots and players to use natural environment props for cover.
""",
    "worker-gameloop-backend": """
### Domain Adaptation: GameLoop & Backend Worker
- **Demo 1 GameModes**:
  1. `BRGameMode_FFA`: Free-For-All deathmatch (score/kill limit).
  2. `BRGameMode_BR`: Classic Solo Battle Royale with 7-phase shrinking storm circle.
- **10-Bot Scenario**: Implement match startup and spawn point distribution for 1 player + 10 bots.
- **Server Authority**: Health, Shield, storm phase, and player eliminations run strictly on dedicated server.
""",
    "worker-ai-agents": """
### Domain Adaptation: AI Agents Worker
- **10 Bots Scenario**: Focus entirely on a 10-bot test scenario.
- **Combat & Looting Priority**:
  * 10 bots actively navigate to loot spawns and equip either AR Hit-Scan or Rocket Launcher Projectile.
  * Bots engage player and each other using Hit-Scan and Projectile weapon attacks.
  * Bots use natural cover (vehicles, alley walls) rather than building structures.
- **Vertical Navigation**: NavMesh and behavior trees must guide bots up exterior stairs and fire escapes from streets to rooftops.
- **No Interior Entry**: Bots must never enter building interiors.
""",
    "worker-map-world": """
### Domain Adaptation: Map & World Worker
- **Demo 1 Focus**: Narrow urban streets, alleys, and rooftops emphasizing vertical gameplay.
- **Exterior Only**: All buildings are solid exterior hulls. No interior geometry or interior NavMesh.
- **Exterior Stairs & Fire Escapes**: Design and place outdoor stairs and ladders connecting street level to rooftops.
- **Street-to-Rooftop NavMesh**: Verify NavMesh properly connects street level to rooftops via exterior stairs.
- **Natural Cover**: Place vehicles, dumpsters, concrete planters, and walls across streets for tactical combat.
""",
    "orchestrator": """
### Domain Adaptation: Master Orchestrator
- **Demo 1 Alignment**: Prioritize vertical slice tasks: 10 bots scenario, 2 weapon prototypes (AR Hit-Scan + Rocket Launcher Projectile), exterior NavMesh, dual GameModes, paused building.
- **Constraint Enforcement**: Gate all worker tasks against the 7 Core Constraints. Reject any task that introduces interior spaces, squads/duos, client authority, or 1st person cameras.
""",
    "qa-reviewer": """
### Domain Adaptation: QA Reviewer
- **Constraint Checklist**:
  * [ ] Zero interior spaces, zero interior NavMesh
  * [ ] Solo mode only (no squad arrays, no revive logic)
  * [ ] Server-authoritative gameplay state (HP, damage, storm)
  * [ ] 3rd person camera only (ADS zooms FOV/spring arm, no 1st person)
  * [ ] 3 build materials only (Moloz, Tuğla, Çelik) - building paused for Demo 1
  * [ ] Hybrid hit detection (AR=Hit-Scan, Rocket=Projectile)
  * [ ] All C++ classes prefixed with `BR`
- **Demo 1 MVP Verification**: Confirm 10 bots scenario, 2 weapon prototypes, and dual GameModes.
""",
    "integrator": """
### Domain Adaptation: Integrator
- **Cross-Module Verification**: Verify all modules use `BR` prefix (`BRTypes.h`, `ABRCharacter`, `ABRWeaponBase`).
- **Dependency Guard**: Ensure AI, Map, and Combat modules do not reference building system during Demo 1.
- **GameMode Compatibility**: Verify both FFA and Classic BR GameModes compile cleanly with shared character and weapon types.
"""
}

def adapt_skill(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Skipping {skill_dir.name}: no SKILL.md")
        return False

    raw = skill_md.read_bytes()
    text = raw.decode("utf-8", errors="replace")

    # Check if already adapted
    marker = "## Bakırköy BR Core Constraints & MVP Directives"
    if marker in text:
        print(f"Already adapted: {skill_dir.name}")
        return False

    # Prepare adaptation text
    addition = STANDARD_COMPLIANCE_BLOCK
    skill_key = skill_dir.name
    if skill_key in DOMAIN_SPECIFIC_CALLOUTS:
        addition += DOMAIN_SPECIFIC_CALLOUTS[skill_key]

    new_text = text.rstrip() + "\n" + addition.lstrip() + "\n"
    skill_md.write_text(new_text, encoding="utf-8")
    print(f"Adapted: {skill_dir.name} (+{len(addition.splitlines())} lines)")
    return True

def main():
    skill_dirs = sorted([d for d in ROOT.iterdir() if d.is_dir() and d.name not in ("assets", "scripts")])
    print(f"Adapting {len(skill_dirs)} skills...")
    count = 0
    for sd in skill_dirs:
        if adapt_skill(sd):
            count += 1
    print(f"\nDone! Adapted {count} skills. Total skills in catalog: {len(skill_dirs)}.")

if __name__ == "__main__":
    main()
