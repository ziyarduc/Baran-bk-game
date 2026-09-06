# Rate Limit Resilience & Seamless "Continue" Protocol

## Purpose
This rule ensures that if an API hourly quota, rate limit (HTTP 429 / ResourceExhausted), or token ceiling interrupts any agent or orchestration process, the project state is preserved idempotently. When the user sends a "continue" command (or when quotas reset), execution resumes smoothly from the exact last verified step without duplications, file corruptions, or state regression.

---

## Core Principles

1. **Atomic Checkpointing**:
   - Before starting a multi-file modification or subagent dispatch, log the intent to `.agents/CHECKPOINT.json`.
   - Once a task or sub-task passes validation, mark it as `COMPLETED` in `.agents/CHECKPOINT.json` and `.agents/orchestrator_1/progress.md`.

2. **Zero-Destruction on Interruption**:
   - If an agent is cut off mid-sentence or mid-code-generation, never overwrite existing working files with partial drafts.
   - All code generation must be written to temporary staging (`.tmp_*.h`, `.tmp_*.cpp`) or verified atomically before replacing production code.

3. **Seamless Resume Sequence ("continue")**:
   When a "continue" command is issued after an interruption:
   - **Step 1: Checkpoint Audit**: Read `.agents/CHECKPOINT.json` to identify the active Phase, Milestone, and Task.
   - **Step 2: Subagent Health Check**: Execute `manage_subagents(Action='list')`. If subagents are marked `errored` or `cancelled`, inspect transcripts to extract any completed work before restarting them.
   - **Step 3: Syntax & Integrity Validation**: Run `scripts/verify-rules.ps1` to detect any half-written or corrupted C++ files.
   - **Step 4: Roll Forward, Never Backward**: Do NOT re-execute already completed milestones (e.g., M1, M2, M3). Pick up directly from the first unverified or in-progress task.

---

## State Schema (`.agents/CHECKPOINT.json`)

```json
{
  "last_checkpoint_utc": "2026-09-06T01:45:00Z",
  "active_milestone": "M4",
  "active_task": "T-M4-001-AR-HitScan",
  "active_workers": [
    {
      "role": "WeaponsCombat Worker",
      "assigned_files": ["Source/BakirkoyBR/Weapons/BRWeapon_HitScan.cpp"],
      "status": "IN_PROGRESS",
      "last_verified_step": "Header declared and verified"
    }
  ],
  "completed_milestones": ["M1", "M2", "M3"],
  "recovery_action": "Resume BRWeapon_HitScan.cpp implementation from line 45"
}
```

---

## Handling 429 / Rate Limit Detection

If any agent encounters a quota error:
1. Immediately write the current in-flight state to `.agents/CHECKPOINT.json`.
2. Append a clean freeze notice to `.agents/orchestrator_1/progress.md`:
   `> [PAUSED FOR RATE LIMIT] Checkpoint saved at UTC timestamp. Safe to resume via 'continue'.`
3. Stop spawning further subagents until the window resets.
