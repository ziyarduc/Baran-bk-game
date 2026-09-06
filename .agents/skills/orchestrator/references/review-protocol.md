# Review Protocol

## QA Review Process

### Step 1: Worker submits code
Worker sends completed files with a summary of changes.

### Step 2: QA Reviewer checks
QA Reviewer evaluates against this checklist:

#### Code Quality
- [ ] All classes use `BR` prefix
- [ ] `#pragma once` in all headers
- [ ] Forward declarations in headers (not full includes)
- [ ] UPROPERTY/UFUNCTION macros correctly specified
- [ ] No raw `new` / `delete` — use UE5 memory management
- [ ] No `using namespace` in headers

#### UE5 Best Practices
- [ ] Replicated properties have `GetLifetimeReplicatedProps` implementation
- [ ] Server RPCs validate input before state changes
- [ ] No gameplay logic in constructors (use BeginPlay)
- [ ] Timers use `GetWorldTimerManager()` not raw threads
- [ ] Async operations use UE5 delegates, not std::thread

#### STD Alignment
- [ ] Implementation matches the System Design Document specifications
- [ ] No interior space code (no-interior rule)
- [ ] Correct weapon stats, damage values, timing values per STD
- [ ] Solo BR mode only — no squad/duo logic

#### Architecture
- [ ] No circular dependencies between modules
- [ ] Shared types defined in Data/ module only
- [ ] Clear separation of concerns between modules

### Step 3: Verdict
- **APPROVED**: Code passes all checks → forward to Integrator
- **NEEDS_REVISION**: Issues found → return to worker with specific feedback
- **REJECTED**: Fundamental design flaw → escalate to Orchestrator

## Integration Review Process

### Step 1: QA-approved code received
Integrator receives files that passed QA.

### Step 2: Cross-module validation
- Verify all #include paths resolve correctly
- Check that shared types (FBRWeaponData, EBRWeaponType, etc.) are consistent
- Ensure no symbol name collisions across modules
- Validate that the module dependency graph is respected

### Step 3: Compile check (conceptual)
- Walk through the include chain mentally
- Verify forward declarations match actual class hierarchies
- Check that all GENERATED_BODY() classes have matching .generated.h includes

### Step 4: Verdict
- **INTEGRATED**: All checks pass → mark task DONE
- **CONFLICT**: Cross-module issues → return to Orchestrator for resolution
