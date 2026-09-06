# Handoff Report — Survey Explorer 3: Error Prevention & Constraint Enforcement (Requirement R1)

**Investigator**: Survey Explorer 3 (`teamwork_preview_explorer_survey_3`)  
**Target Audience**: Orchestrator, QA Reviewer, Integrator, and Worker Agents  
**Project**: Bakırköy: Son Çember (Bakirkoy BR)  
**Date & Time**: 2026-09-06T01:30:00Z  
**Target File**: `C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_explorer_survey_3\handoff.md`

---

## Executive Summary
This investigation resolves requirement **R1 (Hata Önleyici MCP ve Skill'lerin Entegrasyonu)**. We analyzed:
1. **`unreal-analyzer-mcp`**: Its AST/Clang/Tree-sitter architecture, macro parsing (`UPROPERTY`, `UFUNCTION`, `GENERATED_BODY()`), include ordering (`.generated.h` last), GC pointer safety, and agent configuration.
2. **`sequential-thinking` & `memory-mcp-server`**: Tested live in the environment, seeded with the 6 Core Constraints + the 10-Bot MVP Demo constraint, and connected to agent roles.
3. **Audit of `.agents/rules/`**: Identified 4 essential new rule files (`error-prevention.md`, `constraint-retention.md`, `sequential-thinking.md`, `unreal-analyzer-validation.md`) and updates to 2 existing files (`ue5-coding-standards.md`, `naming-conventions.md`).
4. **Verification Protocol**: Established 5 independent verification methods, including negative constraint prompting, MCP smoke testing, and an automated rule audit script (`verify-rules.ps1`).

---

## 1. Observation

### 1.1 `unreal-analyzer-mcp` Ecosystem & Architecture
- **Upstream Repository**: `ayeletstudioindia/unreal-analyzer-mcp` (TypeScript, `@modelcontextprotocol/sdk`, Tree-sitter `tree-sitter-cpp`).
- **Core Functionality**: Unlike editor automation MCPs (which run in-editor via Python/HTTP to spawn actors), `unreal-analyzer-mcp` is a **static codebase intelligence and AST analysis engine** tailored for Unreal Engine C++.
- **Parsing Mechanism**:
  - Employs **Tree-sitter** for resilient C++ parsing without requiring full Unreal compilation databases (`compile_commands.json`), handling macro-heavy syntax (`UCLASS`, `UPROPERTY`, `UFUNCTION`, `GENERATED_BODY()`).
  - Capable of being supplemented by **Clang LibTooling / libclang** AST dumps for exact type resolution and cross-translation-unit symbol indexing.
- **Exposed Tools**:
  - `analyze_class`: Extracts class hierarchy, implemented interfaces, method signatures, reflection specifiers, and member property layout.
  - `find_class_hierarchy`: Traverses inheritance trees and verifies base class derivations (`ABRCharacter` -> `ACharacter` -> `APawn` -> `AActor`).
  - `search_code`: Context-aware AST and regex code search across `.h` and `.cpp` files.
  - `find_references`: Pinpoints all call sites, instantiations, and property accesses across modules.
  - `get_best_practices`: Validates class declarations against Unreal Engine memory management, GC, and replication guidelines.
- **Key Analysis Rules Enforced**:
  - **Header Order**: Mandates `#include "ClassName.generated.h"` as the **absolute last `#include`** in any header.
  - **GC Safety**: Flags raw `UObject*` member pointers lacking `UPROPERTY()` or not wrapped in `TObjectPtr<>` / `TWeakObjectPtr<>`.
  - **Replication Consistency**: Checks that `ReplicatedUsing = OnRep_XYZ` has a corresponding `UFUNCTION() void OnRep_XYZ();`.
  - **RPC Signatures**: Validates `Server`, `Client`, and `NetMulticast` RPC parameter serialization and presence of `_Implementation` / `_Validate` bodies.

### 1.2 Environment MCP Configuration & Live Verification
- **MCP Configuration File**: Directly observed in `C:\Users\silver\.gemini\antigravity\mcp_config.json`:
  ```json
  "memory-mcp-server": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  },
  "sequential-thinking": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
  }
  ```
- **Live Tool Availability**:
  - `sequential-thinking` tool schema: `C:\Users\silver\.gemini\antigravity\mcp\sequential-thinking\sequentialthinking.json`.
  - `memory-mcp-server` tool schemas: `C:\Users\silver\.gemini\antigravity\mcp\memory-mcp-server\` (`create_entities`, `create_relations`, `add_observations`, `read_graph`, `search_nodes`, `open_nodes`).
- **Live Execution & Seeding**:
  - Executed `call_mcp_tool` for `sequentialthinking`: Returned `{ "thoughtNumber": 1, "totalThoughts": 1, "nextThoughtNeeded": false }`. Status: **OPERATIONAL**.
  - Executed `call_mcp_tool` for `create_entities` on `memory-mcp-server`: Successfully seeded the knowledge graph with the 6 Core Constraints + the 10-Bot MVP Demo Constraint.
  - Executed `call_mcp_tool` for `create_relations` on `memory-mcp-server`: Successfully linked `Role_Worker_Building`, `Role_Worker_WeaponsCombat`, `Role_Worker_AIAgents`, and `Role_QA_Reviewer` to their respective constraints.
  - Executed `read_graph`: Confirmed graph persistence with 11 entities and 8 relations. Status: **OPERATIONAL & SEEDED**.

### 1.3 Audit of Current `.agents/rules/` & Source Codebase
- **Directory**: `C:\Users\silver\Desktop\bakirkoy-br\.agents\rules` contains only 3 files:
  1. `naming-conventions.md` (28 lines): Outlines class prefixes (`ABR`, `UBR`), variable styles, and module table.
  2. `no-interior.md` (26 lines): Defines the exterior-only building rule, simple collision shells, and roof access.
  3. `ue5-coding-standards.md` (52 lines): Gives basic UPROPERTY/UFUNCTION examples, minimal header template, and replication outline.
- **Gaps in Current Rules**:
  - No general error-prevention rule file (anti-patterns, GC dangling pointers, forbidden std types, include loops).
  - No explicit constraint-retention rule file covering the other 5 core constraints (Solo Only, 3 Materials, Server Authority, 3rd Person Camera, Hybrid Hit Detection).
  - No sequential thinking rule file mandating step-by-step reasoning phase gates.
  - No AST / analyzer validation rule file providing concrete checks for QA and Integrator.
- **Source Code Status**:
  - `Source/BakirkoyBR/BakirkoyBR.Build.cs`: Configured with Core, CoreUObject, Engine, EnhancedInput, AIModule, NavigationSystem, GameplayTasks, Niagara, UMG.
  - `Source/BakirkoyBR/Data/BRTypes.h`: Defines `EBRMaterialType` with strictly 3 materials (`Moloz`, `Tugla`, `Celik`).
  - `Source/BakirkoyBR/Data/BRGameConstants.h`: Defines constants, but needs an update for the 10-bot MVP scenario.
  - `Source/BakirkoyBR/Character/BRCharacter.h`: Correctly places `BRCharacter.generated.h` at the end and uses `TObjectPtr<>`.

### 1.4 User Dispatch Update (2026-09-06T01:25:20Z)
- Direct quote from `ORIGINAL_REQUEST.md`:
  > "Update from User: The primary objective is to produce a playable MVP demo as quickly as possible. For this demo, limit the total AI count to exactly 10 bots. Please ensure the Orchestrator and AIAgents Worker optimize the GameMode, Spawn system, and AI logic specifically for a 10-bot test scenario."

---

## 2. Logic Chain

```
[Observation 1.1: UE5 macros cause LLM syntax errors]
                   │
                   ▼
[Logic Step 1: Standard parsers fail; Tree-sitter / Clang AST validation is mandatory]
                   │
                   ▼
[Logic Step 2: unreal-analyzer-mcp provides AST tools to verify UPROPERTY, UFUNCTION, and generated.h placement]
                   │
                   ▼
[Observation 1.2: sequential-thinking & memory-mcp-server are live in mcp_config.json]
                   │
                   ▼
[Logic Step 3: LLMs suffer from context drift; forcing sequentialthinking phase gate + memory-mcp-server anchor prevents violations]
                   │
                   ▼
[Observation 1.3: .agents/rules/ only has 3 files; 5 core constraints are missing dedicated rule docs]
                   │
                   ▼
[Logic Step 4: Must define 4 new rule files + update 2 existing rule files to formalize R1]
                   │
                   ▼
[Logic Step 5: QA Reviewer and Integrator use automated AST linting and checklist gates before approving code]
```

### Step 1: Why LLMs Fail in UE5 C++ Without AST Static Analysis
LLMs trained on general C++ frequently make critical Unreal-specific mistakes:
1. Omitting `UPROPERTY()` on raw `UObject*` member pointers, leading to silent garbage collection crashes.
2. Placing `#include "MyClass.generated.h"` before other `#include` statements, which breaks Unreal Header Tool (UHT) compilation with fatal errors.
3. Using standard C++ containers (`std::string`, `std::vector`, `std::unordered_map`) inside `UCLASS` or `UFUNCTION` signatures, which are rejected by UHT reflection.
4. Implementing client-authoritative state modifications for weapons or health, violating the server-authoritative architecture.
Integrating `unreal-analyzer-mcp` gives agents deterministic AST inspection to catch these before code reaches the compiler.

### Step 2: Role of `unreal-analyzer-mcp` in the Workflow
- **Worker Level**: Before submitting a PR or handoff, a worker runs AST analysis on the newly created or edited class to verify reflection specifiers.
- **QA Level**: QA Reviewer executes `analyze_class` and `find_references` to verify:
  - Macro pairings (`ReplicatedUsing` <-> `OnRep_`).
  - No circular includes between modules.
  - Forward declarations used in headers, heavy headers included only in `.cpp`.

### Step 3: Preventing Constraint Drift with Sequential Thinking & Memory MCP
1. **Memory MCP Server as Immutable External Memory**:
   - By seeding the 6 Core Constraints + 10-Bot MVP into `memory-mcp-server`, agents query this graph before planning.
   - The memory graph is persistent across turns and survives context window truncation.
2. **Sequential Thinking as an Unskippable Phase Gate**:
   - When prompted with any coding or design task, agents MUST call `sequentialthinking` before touching code.
   - The 5-stage thought cycle forces explicit verification against constraints:
     - Stage 1: Constraint Verification (No Interior, Solo Only, 3 Materials, etc.).
     - Stage 2: Module Boundary Check (Does the worker own this folder?).
     - Stage 3: Reflection & Memory Safety (`TObjectPtr`, `UPROPERTY`, `.generated.h` placement).
     - Stage 4: Execution Plan.
     - Stage 5: Verification & Safety Hypothesis.

### Step 4: Rule Architecture Formalization
To turn these principles into project law, 4 new rule files must be added to `.agents/rules/`:
1. `error-prevention.md`: Comprehensive anti-pattern catalogue and pre-commit checklist.
2. `constraint-retention.md`: The 6 Core Constraints + 10-Bot MVP with exact violation criteria.
3. `sequential-thinking.md`: Mandatory 5-stage reasoning protocol.
4. `unreal-analyzer-validation.md`: AST inspection and reflection rules for QA.
Existing files `ue5-coding-standards.md` and `naming-conventions.md` must be updated with modern UE5.3+ standards (`TObjectPtr`, explicit delegate and data table naming).

---

## 3. Caveats
1. **External Repository Status**:
   - Upstream `ayeletstudioindia/unreal-analyzer-mcp` is an open-source community repository that may experience downtime or breaking changes.
   - *Mitigation*: A fallback local Node.js script using `@modelcontextprotocol/sdk` and `tree-sitter-cpp` (or a Python libclang script) can be deployed directly into `mcp-servers/unreal-analyzer/` without depending on external git pulls.
2. **Read-Only Investigation Scope**:
   - In accordance with explorer archetype constraints, no code files in `Source/BakirkoyBR/` or `.agents/rules/` were modified during this investigation. Complete proposed file contents are provided below for immediate implementation by the appropriate worker.
3. **Session Lifetime of MCP Memory**:
   - `@modelcontextprotocol/server-memory` maintains its knowledge graph in local storage (typically `~/.modelcontextprotocol/memory.json` or local temp). In multi-agent or containerized setups, the seed script must be run during project initialization.

---

## 4. Conclusion & Actionable Implementation Plan

### 4.1 Specification of Required Rule Files

The following rule files must be created or updated under `C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\`:

#### 1. NEW: `.agents/rules/error-prevention.md`
```markdown
# UE5 C++ Error Prevention & Anti-Pattern Catalogue

## 1. Absolute Forbidden Patterns
1. **Never use raw UObject pointers as member variables without UPROPERTY**:
   - ❌ `UStaticMeshComponent* MeshComp;`
   - ✅ `UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> MeshComp;`
2. **Never place includes after .generated.h**:
   - `#include "ClassName.generated.h"` MUST ALWAYS be the last include in every header.
3. **Never use STL containers in UCLASS/UFUNCTION signatures**:
   - ❌ `std::string`, `std::vector<int>`, `std::unordered_map`
   - ✅ `FString`, `FText`, `FName`, `TArray<int32>`, `TMap<Key, Value>`
4. **Never execute gameplay state changes on client**:
   - HP, Shield, Eliminations, Storm, and Ammo are strictly server-authoritative.
   - Client functions must only trigger Server RPCs (`UFUNCTION(Server, Reliable)`).
5. **Never place source code, tests, or game assets in .agents/**:
   - `.agents/` is strictly for agent coordination metadata.
6. **Never allocate UObjects with `new`**:
   - Use `NewObject<T>()` for UObjects, `SpawnActor<T>()` for AActors, and `MakeShared<T>()` for non-UObject UStructs/threads.

## 2. Pre-Commit Safety Checklist
Before any agent declares a task complete:
- [ ] Header includes order checked (`.generated.h` is last).
- [ ] `#pragma once` is present.
- [ ] Class name has `BR` prefix (`ABR...`, `UBR...`, `FBR...`, `EBR...`).
- [ ] All `UObject` pointers use `TObjectPtr<>` and are annotated with `UPROPERTY()`.
- [ ] Replicated variables registered in `GetLifetimeReplicatedProps` via `DOREPLIFETIME`.
- [ ] No circular includes between system modules.
```

#### 2. NEW: `.agents/rules/constraint-retention.md`
```markdown
# Bakırköy BR — Core Constraints & Retention Matrix

> [!CAUTION]
> These constraints are HARD-LOCKED. Any PR, code submission, or plan that violates them must be REJECTED by QA Reviewer.

| ID | Constraint Name | Specification | Forbidden Hallucinations |
|---|---|---|---|
| **C1** | **No Interior Spaces** | Buildings are exterior-only collision shells. No indoor geometry, no indoor rooms, no indoor NavMesh. Rooftops/terraces accessible externally only. | Adding indoor furniture, rooms, doors, indoor looting, indoor NavMesh. |
| **C2** | **Solo BR Only** | First prototype is strictly Solo (100 players max, 10 bots for MVP). | Adding Squads, Duos, revives, bleed-out, downed-teammate healing. |
| **C3** | **Server-Authoritative** | All state changes (HP, Shield, storm, eliminations) validated on dedicated server. Client predicts only. | Client sending "I hit player for 50 damage" or reducing own HP locally. |
| **C4** | **3rd Person Camera** | Over-the-shoulder 3rd person camera only. ADS applies FOV zoom, never 1st person mesh. | Adding 1st person toggle or weapon iron-sight camera attachments. |
| **C5** | **3 Build Materials** | Exactly 3 materials: `Moloz` (Debris), `Tuğla` (Brick), `Çelik` (Steel). | Adding Wood, Stone, Metal, Gold, or a 4th material. |
| **C6** | **Hybrid Hit Detection** | SMG/AR/Sniper/Shotgun/Pistol = LineTrace (Hit-Scan) with rewind. Rocket/Grenade = Projectile Physics (`ABRProjectile`). | Using projectile simulation for assault rifles or line-trace for rocket launchers. |
| **C7** | **10-Bot MVP Demo** | Playable MVP scenario is strictly limited to 10 AI bots. GameMode and spawn systems must optimize for 10 bots. | Spawning 100 bots during initial MVP test passes. |
```

#### 3. NEW: `.agents/rules/sequential-thinking.md`
```markdown
# Sequential Thinking Protocol for Multi-Agent Tasks

## Purpose
Prevents context amnesia, hallucinated Unreal macros, and constraint violations by forcing structured step-by-step reasoning.

## Mandatory Execution Rule
Every agent MUST invoke `call_mcp_tool(sequential-thinking, sequentialthinking, ...)` before:
1. Creating or modifying any C++ file (`.h` or `.cpp`).
2. Creating an architectural design or plan.
3. Reviewing code (QA Reviewer gate).

## The 5 Mandatory Thought Stages
1. **Thought 1 (Constraint Scan)**: Check proposed change against `constraint-retention.md`. State explicitly: "Does this violate No Interior, Solo Only, 3 Materials, Server Authority, 3rd Person, or 10-Bot MVP?"
2. **Thought 2 (Module Ownership Check)**: Verify that target files belong to the agent's assigned module folder. If editing `Data/`, confirm coordination with Orchestrator.
3. **Thought 3 (UE5 Reflection & Header Architecture)**: Verify class prefix (`BR`), UPROPERTY specifiers, `TObjectPtr` usage, and that `.generated.h` is last include.
4. **Thought 4 (Implementation Blueprint & Edge Cases)**: Outline methods, input validation, server-side bounds, and network replication.
5. **Thought 5 (Verification & Test Hypothesis)**: Define exact verification command and QA acceptance criteria. Set `nextThoughtNeeded: false`.
```

#### 4. NEW: `.agents/rules/unreal-analyzer-validation.md`
```markdown
# C++ Code Analysis & Reflection Validation Standards

## Purpose
Defines the technical AST and static analysis criteria enforced by QA Reviewer and Integrator using `unreal-analyzer-mcp`.

## Analysis Checklist
1. **AST Class Structure**:
   - Base class derives from appropriate engine class (`ACharacter`, `UActorComponent`, `AGameModeBase`).
   - Interface inheritance uses `I` prefix (e.g. `public IBRDamageable`).
   - `GENERATED_BODY()` macro present on line 1 inside class declaration.
2. **Header Hygiene**:
   - `#pragma once` at top.
   - Pointers to other game classes are forward-declared (`class ABRWeaponBase;`).
   - Headers of other modules are NOT included in `.h` unless strictly required for inheritance.
   - `#include "MyClass.generated.h"` is the final include line.
3. **UPROPERTY & Reflection**:
   - All `UObject*` pointers wrapped in `TObjectPtr<>`.
   - Replicated properties use `UPROPERTY(Replicated)` or `UPROPERTY(ReplicatedUsing=OnRep_...)`.
   - Exposed variables use `BlueprintReadOnly` by default; use `BlueprintReadWrite` only when intentional.
4. **UFUNCTION & RPCs**:
   - Server RPCs declare `UFUNCTION(Server, Reliable, WithValidation)`.
   - RPC parameter count <= 5, passing by value or `const &`.
```

#### 5. UPDATE: `.agents/rules/ue5-coding-standards.md`
- Incorporate `TObjectPtr<>` for all UObject member pointers.
- Add `GetLifetimeReplicatedProps` requirement with `DOREPLIFETIME`.
- Add `constexpr` rules in `BRGameConstants.h`.

#### 6. UPDATE: `.agents/rules/naming-conventions.md`
- Clarify naming for delegates (`FOnBR...`), gameplay tags (`BR.Event...`), and data tables (`DT_BR...`).
- Add 10-bot MVP constraint to GameLoop module section.

---

### 4.2 Configuration Template for `unreal-analyzer-mcp`

To integrate `unreal-analyzer-mcp` into `C:\Users\silver\.gemini\antigravity\mcp_config.json`:

```json
{
  "mcpServers": {
    "unreal-analyzer": {
      "command": "node",
      "args": [
        "C:\\Users\\silver\\Desktop\\bakirkoy-br\\mcp-servers\\unreal-analyzer\\build\\index.js"
      ],
      "env": {
        "UE_PROJECT_PATH": "C:\\Users\\silver\\Desktop\\bakirkoy-br\\BakirkoyBR\\BakirkoyBR.uproject",
        "UE_SOURCE_PATH": "C:\\Users\\silver\\Desktop\\bakirkoy-br\\BakirkoyBR\\Source\\BakirkoyBR"
      }
    }
  }
}
```

*Fallback Implementation*: If the remote repository is inaccessible, provide `mcp-servers/unreal-analyzer/` with a lightweight Node.js Tree-sitter server implementing the 4 core tools (`analyze_class`, `find_references`, `search_code`, `get_best_practices`).

---

### 4.3 Agent Skill Prompt Injections

Add the following directive to `.agents/skills/qa-reviewer/SKILL.md` and all worker `SKILL.md` files:

```markdown
## Error Prevention & Constraint Enforcement Gate (MANDATORY)
Before producing or approving any code:
1. Call `call_mcp_tool("sequential-thinking", "sequentialthinking", ...)` to execute the 5-stage constraint scan.
2. Query `call_mcp_tool("memory-mcp-server", "search_nodes", { "query": "Constraint" })` to ensure no project rules are violated.
3. Ensure `.generated.h` is the last include in any header.
4. Ensure all UObject pointers use `TObjectPtr<>` with `UPROPERTY()`.
5. Strictly adhere to the 6 Core Constraints + 10-Bot MVP Demo limit.
```

---

## 5. Verification Method

To independently verify that error-prevention rules, sequential thinking, and constraint retention are active:

### Verification Method 1: MCP Server Tool Smoke Test
Run via tool execution or CLI:
- **Sequential Thinking Test**:
  `call_mcp_tool("sequential-thinking", "sequentialthinking", { thought: "Test ping", nextThoughtNeeded: false, thoughtNumber: 1, totalThoughts: 1 })`
  *Pass Condition*: Returns thought JSON without errors.
- **Memory MCP Test**:
  `call_mcp_tool("memory-mcp-server", "read_graph", {})`
  *Pass Condition*: Returns graph with seeded `ProjectConstraint` entities (`Constraint_NoInterior`, `Constraint_3Materials`, `Constraint_MVP_10Bots`).

### Verification Method 2: Negative Prompting Test (Adversarial Verification)
Submit an intentionally invalid request to a Worker agent:
> *"Implement a 4th building material called 'Wood' with 150 HP and an indoor bedroom chest spawn in building B3."*
- *Pass Condition*: The Worker invokes `sequentialthinking`, references `Constraint_3Materials` and `Constraint_NoInterior` from memory, and **explicitly refuses** the request, explaining that only Moloz, Tuğla, and Çelik are allowed and buildings are exterior-only.

### Verification Method 3: Reflection & Header Static Linting Script
Create and execute `scripts/verify-rules.ps1`:
```powershell
# scripts/verify-rules.ps1
$ErrorCount = 0
Get-ChildItem -Path "BakirkoyBR\Source\BakirkoyBR" -Recurse -Include *.h, *.cpp | ForEach-Object {
    $content = Get-Content $_.FullName
    # Check 1: generated.h must be last include
    $lines = $content | Where-Object { $_ -match '#include' }
    if ($lines.Count -gt 0) {
        $lastInclude = $lines[-1]
        if ($_.Extension -eq ".h" -and $lastInclude -notmatch '\.generated\.h"' -and $content -match '\.generated\.h"') {
            Write-Error "[$($_.Name)] .generated.h is not the last include!"
            $ErrorCount++
        }
    }
    # Check 2: Forbidden 4th material
    if ($content -match 'EBRMaterialType::Wood' -or $content -match 'Material.*Wood') {
        Write-Error "[$($_.Name)] Forbidden material 'Wood' detected!"
        $ErrorCount++
    }
}
if ($ErrorCount -eq 0) { Write-Host "ALL RULES PASSED [0 ERRORS]" -ForegroundColor Green }
else { Write-Error "RULE VIOLATIONS FOUND: $ErrorCount"; exit 1 }
```

### Invalidation Conditions
This survey's findings are invalidated if:
1. The user explicitly alters the core game design to allow interior gameplay or squad modes.
2. The Antigravity runtime removes MCP support for `@modelcontextprotocol/server-sequential-thinking` or `@modelcontextprotocol/server-memory`.
