# Task Queue Format

## Task Assignment Template

When the Orchestrator assigns a task to a worker, use this format:

```
[TASK]
ID: T-{milestone}-{sequence} (e.g., T-M2-001)
Title: {Brief description}
Priority: P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)
Assignee: {worker agent name}
Module: {target module folder}
Dependencies: {list of TASK_IDs that must complete first, or "None"}

Description:
{Detailed description of what needs to be implemented}

Acceptance Criteria:
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Criterion N}

Relevant STD Section: {Section number and title from STD_v1.md}

Files to Create/Modify:
- {file path 1}
- {file path 2}
[/TASK]
```

## Task Status Values
- `BACKLOG` — Not yet assigned
- `ASSIGNED` — Sent to worker
- `IN_PROGRESS` — Worker is actively working
- `IN_REVIEW` — Submitted to QA Reviewer
- `REVIEW_FAILED` — QA found issues, returned to worker
- `APPROVED` — QA approved
- `INTEGRATING` — Sent to Integrator
- `INTEGRATION_FAILED` — Cross-module issues found
- `DONE` — Fully integrated and verified

## Priority Rules
- P0: Blocks other tasks or is a critical path item
- P1: Important for current milestone
- P2: Can be deferred to next iteration
- P3: Nice-to-have, polish items

## Parallelization Guide
These task groups can run in parallel:
- Group A: Core + Character (Worker 4) ‖ Weapons (Worker 2) ‖ Building (Worker 5)
- Group B: AI (Worker 3) — after Group A completes
- Group C: GameLoop systems (Worker 1) — after Core completes
- Group D: Network (Worker 4) — after all gameplay systems complete
