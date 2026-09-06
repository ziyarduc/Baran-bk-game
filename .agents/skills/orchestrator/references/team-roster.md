# Team Roster — Agent Capabilities

## Worker Agents

### Worker 1: MapWorld (worker-map-world)
- **Model**: gemini-3.8-flash (High Thinking)
- **Module Ownership**: `GameLoop/BRStormCircle.*`, `GameLoop/BRLootManager.*`, `GameLoop/BRSafeZoneManager.*`
- **Capabilities**: POI configuration, storm circle algorithm, loot tier system, NavMesh configuration
- **Depends On**: Core (GameState), Data (BRTypes)
- **Strengths**: Spatial reasoning, game balance, world systems
- **Limitations**: Should not touch Character or Weapons code

### Worker 2: WeaponsCombat (worker-weapons-combat)
- **Model**: gemini-3.8-flash (High Thinking)
- **Module Ownership**: `Weapons/` (all files)
- **Capabilities**: 5 weapon classes, damage model, ADS/spray/reload mechanics, equipment system
- **Depends On**: Character (for weapon attachment), Data (BRTypes for weapon enums)
- **Strengths**: Combat math, weapon balancing, hit-scan/projectile implementation
- **Limitations**: Should not implement hit validation (that's Network/)

### Worker 3: AIAgents (worker-ai-agents)
- **Model**: gemini-3.8-flash (High Thinking)
- **Module Ownership**: `AI/` (all files)
- **Capabilities**: FSM state machine, perception system, 3 agent roles, AI skills, pathfinding
- **Depends On**: Character, Weapons (for bot weapon usage), Building (for bot building), Data
- **Strengths**: AI architecture, behavior trees alternative (FSM), navigation
- **Limitations**: Most dependent worker — needs stable APIs from Character, Weapons, Building

### Worker 4: GameLoop (worker-gameloop-backend)
- **Model**: gemini-3.8-flash (High Thinking)
- **Module Ownership**: `Core/`, `Character/`, `Network/`
- **Capabilities**: GameMode, GameState, PlayerState, PlayerController, character movement, health, server rewind
- **Depends On**: Data (BRTypes)
- **Strengths**: Template-heavy UE5 boilerplate, replication setup
- **Limitations**: High reasoning ceiling with High Thinking enabled

### Worker 5: Building (worker-building-system)
- **Model**: gemini-3.8-flash (High Thinking)
- **Module Ownership**: `Building/` (all files)
- **Capabilities**: 3 materials, 4 build pieces, edit system, Turbo Build, build preview
- **Depends On**: Character (for build mode input), Data (BRTypes for material enums)
- **Strengths**: Structural game systems, grid-based placement
- **Limitations**: High reasoning ceiling with High Thinking enabled

## Support Agents

### QA Reviewer (qa-reviewer)
- **Model**: gemini-3.1-pro-preview (High Thinking)
- **Review Scope**: All code produced by all workers
- **Checks**: UE5 coding standards, naming conventions, replication correctness, no-interior rule, STD alignment

### Integrator (integrator)
- **Model**: gemini-3.1-pro-preview (High Thinking)
- **Integration Scope**: Cross-module #include chains, forward declarations, shared type consistency
- **Checks**: Compile feasibility, circular dependency detection, API contract matching
