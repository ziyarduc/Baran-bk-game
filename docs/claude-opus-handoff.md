# LLM Handoff & Audit Briefing: Bakırköy Battle Royale

**Target Audience:** Claude 3 Opus (or any advanced LLM acting as an auditor/supervisor)
**Project Name:** Bakırköy: Son Çember
**Engine:** Unreal Engine 5 (C++ based, leveraging Nanite & Lumen)
**Current Stage:** Phase 1 Complete (System Design, Architecture, C++ Skeleton, and Multi-Agent Orchestration Pipeline are fully established. No gameplay logic has been implemented yet.)

## 1. Context & Purpose
This document serves as a complete memory state and context initializer. Google Gemini (Antigravity) has established the foundational architecture for a 3D Shooter Battle Royale game. Your role is to audit, review, or continue development based strictly on the constraints and systems defined below.

## 2. Core Game Design Constraints (STRICT - DO NOT VIOLATE)
When evaluating or generating code, you must adhere to the following hard constraints decided by the user:
1. **No Interior Spaces (Exterior Only):** Buildings are purely collision shells. No interior geometry, no interior NavMesh, and no indoor gameplay. Players can access rooftops/terraces via external assets (ramps, stairs, fire escapes).
2. **Solo BR Only:** The prototype is explicitly Solo. Do NOT write code for Squads, Duos, revives, or team-based logic.
3. **Server-Authoritative:** All critical state changes (Health, Shield, Damage, Storm interactions) must be server-authoritative. Clients run prediction, server validates.
4. **Camera:** 3rd Person (Over-the-shoulder) only. ADS (Aim Down Sights) applies FOV zoom but does not switch to a 1st person mesh.
5. **Hybrid Hit Detection:** 
   - Hit-Scan: Assault Rifles (AR), SMGs, Sniper Rifles.
   - Projectile Physics: Rocket Launchers / Grenades.
6. **Building System:** Exactly 3 materials allowed: `Debris (Moloz)`, `Brick (Tuğla)`, `Steel (Çelik)`.

## 3. Development Methodology (Multi-Agent System)
The project is designed to be built autonomously using a multi-agent orchestration setup via Google Antigravity. 
- **Orchestrator (Gemini 3.1 Pro):** Acts as the Lead Developer/Manager. Assigns tasks to workers, coordinates module dependencies.
- **Workers (Gemini 3.7 Flash & 3.5 Flash-Lite):** 5 domain-specific agents (`worker-map-world`, `worker-weapons-combat`, `worker-ai-agents`, `worker-gameloop-backend`, `worker-building-system`). They only touch code within their specific UE5 module.
- **QA & Integrator (Gemini 3.7 Flash):** Reviews code for UE5 standards and ensures cross-module compilation succeeds.

*Note for Claude Opus:* If you are generating code, you must adopt the persona of the specific Worker agent responsible for that module, or act as the QA Reviewer.

## 4. Repository & File Structure
The project is physically mapped on a Windows OS (`C:\Users\silver\Desktop\bakirkoy-br\`).
- **`.agents/`**: Contains the intelligence of the project.
  - `AGENTS.md` (Global rules)
  - `rules/` (UE5 Coding standards, naming conventions, no-interior constraint)
  - `skills/` (System prompts (`SKILL.md`) and reference markdown files for each of the 8 agents)
- **`docs/`**: Human-readable design documents.
  - `STD_v1.md` (System Design Document detailing Weapons, AI FSM, POIs, etc.)
  - `geliştirme-yol-haritası.md` (Roadmap)
  - `agent-takım-yapısı.md` (Team Structure)
- **`BakirkoyBR/`**: The Unreal Engine 5 project.
  - `BakirkoyBR.uproject`
  - `Source/BakirkoyBR/`
    - `Core/` (GameMode, GameState, PlayerState, PlayerController)
    - `Character/` (Base Character, HealthComponent)
    - `Data/` (Enums, Structs, GameConstants)

## 5. UE5 Coding Standards Enforced
- **Prefixes:** `ABR` for Actors, `UBR` for Objects/Components, `FBR` for Structs, `EBR` for Enums.
- **Macros:** `UPROPERTY`, `UFUNCTION`, `UCLASS` must be strictly utilized.
- **Replication:** Uses `DOREPLIFETIME` and `GetLifetimeReplicatedProps`. RPCs must be clearly categorized (`Server`, `Client`, `NetMulticast`).
- **Language Policy:** C++ Code/Comments/Variables are in English. High-level documentation is in Turkish.

## 6. Audit Directives for Claude Opus
If you are asked to review this project, check for:
1. **Constraint Leaks:** Ensure no interior logic (e.g., room pathfinding) has been hallucinated into the AI or Map modules.
2. **Replication Security:** Verify that `BRHealthComponent` and weapon firing mechanisms are protected against client-side spoofing.
3. **Agent Scope:** Ensure that the `worker-weapons-combat` agent hasn't accidentally modified the `Core` GameState files (which belongs to `worker-gameloop-backend`).

---
*End of Briefing. You are now synchronized with the current project state.*
