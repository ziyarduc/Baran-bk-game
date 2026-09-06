# Sequential Thinking Protocol for Multi-Agent Tasks

> **Bakırköy BR Project Rule**  
> **Status**: MANDATORY & HARD-LOCKED  
> **Applicable To**: All Agents (Orchestrator, Workers, QA Reviewer, Integrator)  
> **Reference**: Requirement R1 (Sequential Thinking MCP Integration)

---

## 1. Purpose & Core Philosophy

Large Language Models working on complex game development tasks frequently succumb to:
1. **Context Drift / Amnesia**: Forgetting project-specific constraints (e.g. inventing indoor rooms or a 4th building material).
2. **Premature Code Generation**: Writing code before validating module ownership or header include orders.
3. **Engine Macro Hallucinations**: Placing `#include "Class.generated.h"` in the middle of a file or omitting `UPROPERTY()` on raw `UObject*` pointers.

The **Sequential Thinking Protocol** enforces a structured, step-by-step cognitive phase gate. Every agent MUST complete and document the **5 Mandatory Thought Stages** before writing code or making architectural commitments.

---

## 2. Mandatory 5-Stage Reasoning Protocol

Before executing any file write, code refactoring, or architectural review, an agent must execute the following 5 stages:

```
┌────────────────────────────────────────────────────────┐
│  STAGE 1: Constraint & Invariants Scan                 │
│  Validate against 7 Core Constraints + 5 MVP Directives│
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│  STAGE 2: Module Ownership & Write Boundary Check      │
│  Confirm designated folder, minimal change scope       │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│  STAGE 3: Unreal Reflection & Memory Safety Check       │
│  .generated.h last, TObjectPtr, BR prefix, no STL      │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│  STAGE 4: Network Authority & Implementation Blueprint │
│  Server authoritative, RPC validation, edge cases      │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│  STAGE 5: Verification Hypothesis & Acceptance Gate    │
│  Specific test commands, pass criteria, nextThought=F  │
└────────────────────────────────────────────────────────┘
```

---

### Stage 1: Constraint & Invariants Scan (The "Guard Rails" Stage)
- **Objective**: Ensure the proposed action does not violate any project law.
- **Mandatory Questions to Answer**:
  1. *Does this touch buildings?* If yes, are we strictly outside? (Exterior collision shells only, external stairs/ramps, no indoor rooms/NavMesh).
  2. *Does this touch game modes?* Is it Solo BR or FFA Deathmatch? (No squad, duo, DBNO, or revive logic).
  3. *Does this touch state?* Is it server-authoritative? (Server validates; client predicts).
  4. *Does this touch camera?* Is it strictly 3rd person over-the-shoulder?
  5. *Does this touch building materials?* Are there exactly 3 materials (`Moloz`, `Tugla`, `Celik`)?
  6. *Does this touch weapons?* Does it respect the hybrid model (AR = Hit-Scan; Rocket = Projectile splash)?
  7. *Does this touch AI count?* Is it strictly optimized for the 10-Bot MVP scenario?
  8. *Does this touch building mechanics?* Is building paused for Demo 1, relying on natural cover?

---

### Stage 2: Module Ownership & Scope Assessment (The "Discipline" Stage)
- **Objective**: Prevent cross-module contamination and respect agent boundaries.
- **Mandatory Questions to Answer**:
  1. *What is my assigned working module?* (e.g., `Weapons/`, `AI/`, `Core/`, `Character/`, `Building/`).
  2. *Am I modifying files outside my boundary?* If modifying shared headers in `Data/` (`BRTypes.h`, `BRGameConstants.h`), is it coordinated with the Orchestrator?
  3. *Does this change adhere to the Minimal Change Principle?* Make only the necessary edits; no unrelated refactoring.

---

### Stage 3: Unreal Reflection & Header Hygiene (The "Engine Safety" Stage)
- **Objective**: Eliminate all compilation-breaking UE5 syntax errors before writing files.
- **Mandatory Checks**:
  1. *Include Order*: Is `#include "ClassName.generated.h"` placed as the **strictly final include**?
  2. *Header Guard*: Does line 1 have `#pragma once`?
  3. *Naming*: Does the class/struct have the `BR` prefix (`ABR...`, `UBR...`, `FBR...`, `EBR...`)?
  4. *GC Safety*: Are all `UObject*` member pointers wrapped in `TObjectPtr<>` and annotated with `UPROPERTY()`?
  5. *No STL*: Are `std::string`, `std::vector`, `std::map` completely absent in favor of `FString`, `TArray`, `TMap`?
  6. *Forward Declarations*: Are other game classes forward-declared in `.h` rather than included?

---

### Stage 4: Network Authority & Implementation Blueprint (The "Architecture" Stage)
- **Objective**: Plan the logic flow, network replication, and edge cases.
- **Mandatory Checks**:
  1. *Authority*: Are health, ammo, and inventory mutations gated behind `HasAuthority()` on the server?
  2. *Replication*: Are replicated properties declared with `UPROPERTY(Replicated)` / `UPROPERTY(ReplicatedUsing = OnRep_...)` and registered in `GetLifetimeReplicatedProps` via `DOREPLIFETIME`?
  3. *RPC Validation*: Do Server RPCs have `WithValidation` and validate parameters in `_Validate`?
  4. *Edge Cases*: What happens on null pointers, disconnected players, or zero health?

---

### Stage 5: Verification Hypothesis & Acceptance Gate (The "Proof" Stage)
- **Objective**: Define how to independently verify that the implementation works and has no regressions.
- **Mandatory Checks**:
  1. *Build Command*: What is the build target and command?
  2. *Test Command*: What unit test or automated script (`verify-rules.ps1`) verifies the changes?
  3. *Expected Result*: What exact string or exit code indicates success?
  4. *Termination*: Set `nextThoughtNeeded: false`.

---

## 3. Tool Execution Protocol

When the `sequential-thinking` MCP server is active in the environment, agents must call `call_mcp_tool` for each thought:

```json
{
  "ServerName": "sequential-thinking",
  "ToolName": "sequentialthinking",
  "Arguments": {
    "thought": "Stage 1 (Constraint Scan): Checking proposed ABRRocketProjectile. Touches weapons: uses Projectile Physics (Constraint C6). Target AI count is 10 bots (MVP M1). No interior spaces impacted (C1). Server-authoritative damage radius (C3). All constraints satisfied.",
    "thoughtNumber": 1,
    "totalThoughts": 5,
    "nextThoughtNeeded": true
  }
}
```

### Fallback Protocol (Offline / Text Mode)
If the `sequential-thinking` MCP server is not available or encounters network timeout, the agent **MUST** write the 5 thought stages explicitly in its response or in `.agents/<worker_folder>/thought_record.md` before executing any file write tools.

---

## 4. QA Reviewer Enforcement Gate

The QA Reviewer agent must inspect the worker's handoff and verification logs for proof of sequential thinking:
1. Did the worker execute all 5 stages?
2. Did the worker explicitly address the 7 Core Constraints and 5 MVP directives?
3. If any stage was skipped or hand-waved, the QA Reviewer must **reject the handoff** with instructions to execute the sequential thinking protocol.
