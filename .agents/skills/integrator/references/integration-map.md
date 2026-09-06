# Integration Map

This document tracks which modules interact and through what interfaces.

## Cross-Module Interfaces

| Source Module | Target Module | Interface | Type |
|--------------|---------------|-----------|------|
| Character | Weapons | `ABRCharacter::EquipWeapon(ABRWeaponBase*)` | Function call |
| Character | Building | `ABRCharacter::EnterBuildMode()` | Function call |
| Weapons | Character | `UBRHealthComponent::ApplyDamage()` | Delegate/Event |
| AI | Character | `ABRBotCharacter` extends `ABRCharacter` | Inheritance |
| AI | Weapons | Bot uses weapon classes for firing | Composition |
| AI | Building | Bot builds structures | Component call |
| GameLoop | Core | `ABRGameMode` manages `ABRGameState` | UE5 Framework |
| GameLoop | Character | Storm damage applied to characters | Event |
| Network | Core | `ABRGameState` replication | UE5 Replication |
| Network | Character | Hit validation against character hitboxes | Raycast |
| All Modules | Data | Shared enums, structs, constants | Header include |

## Shared Types (Data/BRTypes.h)
All modules may include BRTypes.h. Any change to this file must be coordinated through the Orchestrator.

Key shared types:
- `EBRWeaponType` — Used by Weapons, AI, Network
- `EBRMaterialType` — Used by Building, AI
- `EBRBotState` — Used by AI, GameLoop
- `FBRWeaponData` — Used by Weapons, AI
- `FBRDamageInfo` — Used by Weapons, Character, Network
