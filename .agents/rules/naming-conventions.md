# Naming Conventions & Project Taxonomy

> **Bakırköy BR Project Rule**  
> **Status**: MANDATORY  
> **Related Rules**: [ue5-coding-standards.md](ue5-coding-standards.md), [constraint-retention.md](constraint-retention.md)

---

## 1. File Names
- C++ Headers & Source: `BR{SystemName}.h` / `BR{SystemName}.cpp` (e.g., `BRCharacter.h`, `BRWeaponBase.cpp`)
- Blueprint Assets: `BP_BR{SystemName}` (e.g., `BP_BRCharacter`, `BP_BRRifle`)
- Data Tables: `DT_BR{TableName}` (e.g., `DT_BRWeapons`, `DT_BRLootTable`)
- Materials: `M_BR{MaterialName}` (e.g., `M_BRBrick`, `M_BRSteel`)
- Material Instances: `MI_BR{MaterialName}`
- User Interface Widgets: `WBP_BR{WidgetName}` (e.g., `WBP_BRHUD`, `WBP_BRHealthBar`)
- Niagara Systems: `NS_BR{EffectName}` (e.g., `NS_BRMuzzleFlash`, `NS_BRExplosion`)

---

## 2. Code Names
- **Classes**: PascalCase with engine prefix + project prefix `BR` (`ABRCharacter`, `UBRHealthComponent`, `ABRWeaponBase`, `ABRProjectile`)
- **Interfaces**: `IBR` prefix (`IBRDamageable`, `IBRInteractable`)
- **Structs**: `FBR` prefix (`FBRWeaponStats`, `FBRLootEntry`)
- **Enums**: `EBR` prefix with `uint8` (`EBRMaterialType`, `EBRWeaponState`, `EBRGamePhase`)
- **Delegates**: `FOnBR` prefix (`FOnBRHealthChanged`, `FOnBRWeaponFired`)
- **Variables**: PascalCase with descriptive names (`CurrentHealth`, `MaxShield`, `BaseDamage`)
- **Booleans**: Prefix with `b` (`bIsAlive`, `bIsFiring`, `bHasAuthority`)
- **Pointers**: No raw prefix, wrapped in `TObjectPtr<>` for `UObject` members
- **Constants**: ALL_CAPS with underscores (`MAX_PLAYERS`, `DEFAULT_HEALTH`, `MAX_BOTS_MVP`)

---

## 3. Module Folders & Ownership
| Folder | Contents | Assigned Worker | MVP Status |
|--------|----------|-----------------|------------|
| `Core/` | GameMode, GameState, PlayerState, PlayerController | GameLoop Worker | Active (FFA + Classic BR) |
| `Character/` | Player character, movement, camera, health | GameLoop Worker | Active (3rd Person over-shoulder) |
| `Weapons/` | Hit-scan AR, Rocket Launcher projectile, damage | WeaponsCombat Worker | Active (Dual Prototype Slice) |
| `AI/` | Bot AI, BehaviorTree/StateTree, perception | AIAgents Worker | Active (10-Bot Scenario) |
| `Building/` | Grid building, piece preview, material data | Building Worker | Paused for Demo 1 |
| `GameLoop/` | Storm circle, zone collapse, loot management | GameLoop Worker | Active |
| `Network/` | Hit validation, server rewind, replication | GameLoop Worker | Active |
| `Data/` | Shared types, enums, structs, constants | All Workers (coordinated) | Active (`BRTypes.h`, `BRGameConstants.h`) |
