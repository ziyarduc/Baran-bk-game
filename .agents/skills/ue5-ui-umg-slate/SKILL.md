---
name: ue5-ui-umg-slate
description: UE5.6-UE5.8 UI development workflow using UMG and Slate integration. Use when requests involve Widget Blueprint setup, Slate host widgets, lifecycle binding, input and focus handling, tooltip behavior, or viewport clamping logic.
---

# Quick Start
- Identify whether feature belongs to UMG, Slate, or hybrid bridge.
- Define data source component/subsystem and UI binding point.
- Output widget tree intent and runtime binding sequence.

# API Anchors (UE5.6-UE5.8)
- UMG lifecycle and viewport anchors:
  - `UUserWidget::NativeConstruct()`, `UUserWidget::NativeDestruct()`
  - `UUserWidget::AddToViewport(...)`
  - `UWidget::RemoveFromParent()`
  - `UWidget::SetVisibility(...)`
  - `UWidget::SetKeyboardFocus()`
- UMG input mode anchors:
  - `UWidgetBlueprintLibrary::SetInputMode_UIOnlyEx(...)`
  - `UWidgetBlueprintLibrary::SetInputMode_GameAndUIEx(...)`
  - `UWidgetBlueprintLibrary::SetInputMode_GameOnly(...)`
- UMG/Slate bridge anchors:
  - `UWidget::TakeWidget()` for Slate bridge hand-off
  - `SCompoundWidget`, `SLATE_BEGIN_ARGS(...)`
  - `FSlateApplication::SetKeyboardFocus(...)`, `SetUserFocus(...)`
- Viewport geometry anchor:
  - `UGameViewportClient::GetViewportSize(...)`

# UI Stage Contract
- Every UI task must define:
  - UI layer ownership (UMG-only, Slate-only, or hybrid bridge)
  - data source and update trigger (pull, push, event, or mixed)
  - focus and input ownership transition
  - viewport-safe placement behavior for tooltip/popup
  - teardown/cleanup path for unbinds and widget removal
- If any item is missing, the UI implementation is incomplete.

# Workflow
## 1) UI Architecture Decision
- Select UMG for standard game HUD/menu work.
- Select Slate for custom rendering/input behavior that UMG cannot express cleanly.
- Select hybrid when a `UWidget` host needs to embed custom Slate content.

## 2) Construct and Lifetime
- Initialize widget bindings in construct/init path.
- Register event listeners once and store handles when required.
- Define destruct/unregister logic explicitly to avoid stale bindings.

## 3) Data Binding and Refresh
- Bind runtime data from one authoritative source (subsystem/component/view model).
- Use event-driven refresh for high-frequency data where possible.
- Keep display widgets read-only for gameplay state mutation.

## 4) Input and Focus Ownership
- Set input mode deliberately when opening/closing UI contexts.
- Set keyboard/user focus to intended root widget.
- Ensure focus return path back to gameplay on close.

## 5) Tooltip/Popup Viewport Clamp
- Compute desired tooltip position from anchor and cursor/widget geometry.
- Clamp final placement to viewport bounds to avoid off-screen rendering.
- Debounce high-frequency hover updates to avoid flicker.

## 6) Remove and Cleanup
- Remove widget from parent or viewport on close.
- Clear timers/delegates and transient references.
- Confirm no duplicate instances persist after reopen.

# Constraints
- Keep UI rendering and gameplay state mutation separated.
- Avoid direct gameplay writes from passive display widgets.
- Clamp tooltip and popup placement to viewport bounds.
- Prefer deterministic input ownership and focus transitions.
- Keep Slate-only code isolated behind clear bridge boundaries.
- Do not rely on per-frame polling if event-driven updates are available.

# Failure Handling
- Symptom: widget appears but never refreshes.
  - Locate: construct timing, binding registration, source event firing.
  - Fix: bind after source readiness and verify event subscription path.
- Symptom: widget refreshes once then stops.
  - Locate: lost delegate handle or widget recreated without rebind.
  - Fix: rebind on construct and unbind on destruct; prevent duplicate create/destroy churn.
- Symptom: input is swallowed by UI unexpectedly.
  - Locate: current input mode and focused widget path.
  - Fix: enforce intended input mode and set explicit focus target.
- Symptom: keyboard/controller navigation breaks after popup open.
  - Locate: focus transfer and return path.
  - Fix: store previous focus owner and restore on popup close.
- Symptom: tooltip flickers near screen edges.
  - Locate: oscillating clamp output and hover source jitter.
  - Fix: debounce hover updates and clamp with stable viewport metrics.
- Symptom: memory growth after repeated open/close.
  - Locate: stale delegate/timer/reference retention.
  - Fix: clear bindings and transient refs in teardown.

# UE5.6-UE5.8 Compatibility Notes
- UMG lifecycle, input mode, and Slate focus APIs listed above are stable in UE5.6-UE5.8.
- Prefer Enhanced Input + explicit UI input mode ownership across all supported versions.

# Escalation
- Escalate when behavior requires engine-level Slate customization beyond project scope.
- Escalate when UI architecture conflicts with existing CommonUI framework decisions.
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

### Domain Adaptation: UI & HUD
- **Solo BR & FFA HUD**: HUD displays player Health, Shield, weapon ammo, alive player count (out of 11: 1 player + 10 bots), and storm timer / score tracker.
- **No Squad UI**: Do not create teammate status panels, squad markers, or revive indicators.
- **3rd Person Crosshair**: Reticle centered on 3rd person aim point with hit markers and damage numbers.

