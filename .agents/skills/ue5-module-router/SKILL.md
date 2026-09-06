---
name: ue5-module-router
description: Route UE5.6-UE5.8 questions to the most precise skill using module names, aliases, intent keywords, and layer context. Works for explicit module prompts (RenderCore, AIModule, AssetRegistry) and natural language requests.
---

# Quick Start
- Extract explicit module names from user prompt first.
- If module is found, route by exact module mapping before keyword heuristics.
- If module is not found, use aliases and layer context.

# Workflow
- Parse prompt for module candidates (for example `RenderCore`, `AIModule`, `AssetRegistry`).
- Lookup module in `ue5-module-routing-table-final.csv`.
- If multiple hits, prioritize:
  1. exact module name match
  2. Build.cs path similarity
  3. alias overlap with prompt keywords
- Return routing payload:
  - `primary_skill`
  - `secondary_skill`
  - `recommended_mcp_tools[]`
  - `route_confidence`
  - `route_reason`
- Use `secondary_skill` when request spans multiple concerns in one module context.

# Constraints
- Prefer deterministic routing; avoid broad guesses if exact module match exists.
- Keep one primary target skill unless user explicitly asks cross-module analysis.
- If module maps to `ue5-architecture`, answer module-boundary/design first.
- Prefer dedicated MCP tools before `execute_script`.

# Failure Handling
- If no module is recognized, fallback to closest capability skill and state reason.
- If confidence is low, provide top 2 candidates and request module confirmation.
- Use `execute_script` only when dedicated MCP tools are insufficient and explain why.
- If mapping is outdated, regenerate from `ue5-architecture/scripts/generate_module_index_v2.py`.

# Escalation
- Escalate for large cross-cutting refactors across many modules.
- Escalate when requested module belongs to plugin source outside indexed scope.
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

