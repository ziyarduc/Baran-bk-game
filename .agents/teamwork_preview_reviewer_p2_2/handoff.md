# Handoff Report — Reviewer P2-2: package_game.ps1 Review

## 1. Observation

### 1.1 Source File & Target Metadata
- **File Reviewed**: `C:\Users\silver\Desktop\bakirkoy-br\package_game.ps1` (368 lines, 15,711 bytes)
- **Directives Verified**: Unreal Engine 5 is NOT installed; RunUAT live execution is waived; Static verification via PowerShell Parser / AST and `-DryRun` / `-ValidateOnly` execution required.

### 1.2 AST & Syntax Analysis
AST inspection was performed using `[System.Management.Automation.Language.Parser]::ParseInput`:
```powershell
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseInput($code, [ref]$tokens, [ref]$errors)
# Output:
# AST Parse Errors count: 0
# AST Parse Successful: NO SYNTAX ERRORS
```

### 1.3 Parameter Block & Validation Sets (Lines 38-68)
AST parameter reflection revealed the following parameters and validation sets:
- `Configuration` [String]: Position 0, ValidateSet(`Shipping`, `Development`, `DebugGame`, `Test`, `Debug`), default: `'Shipping'`
- `Platform` [String]: Position 1, ValidateSet(`Win64`, `Linux`, `Mac`, `Android`, `IOS`), default: `'Win64'`
- `OutputDir` [String]: Position 2, default: `'Saved/Packages'`
- `EnginePath` [String]: default: `''`
- `ProjectDir` [String]: default: `''`
- `Clean` [SwitchParameter]
- `NoCompileEditor` [SwitchParameter]
- `DryRun` [SwitchParameter]
- `ValidateOnly` [SwitchParameter]

### 1.4 Cultural Safety (Lines 76-79)
Verbatim code from `package_game.ps1`:
```powershell
76: [System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
77: [System.Globalization.CultureInfo]::DefaultThreadCurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
78: [System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture
79: [System.Globalization.CultureInfo]::DefaultThreadCurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture
```
Tested invocation when session host culture was forced to `tr-TR`:
- Script executed cleanly without `System.NullReferenceException` or case-folding mismatch. Output returned `ExitCode for -ValidateOnly under tr-TR: 0`.

### 1.5 Safe Engine Discovery (Lines 141-247)
The script implements a 4-tier engine discovery function `Resolve-UnrealEngineRoot`:
- Tier 0: Explicit `-EnginePath` parameter
- Tier 1: Environment variables (`UE5_PATH`, `UNREAL_ENGINE_PATH`, `UE_ENGINE_DIR`, `UE5_ROOT`, `UE_${Association}_PATH`)
- Tier 2: Windows Registry (`HKLM:\SOFTWARE\EpicGames\Unreal Engine\...`, `HKCU:\SOFTWARE\Epic Games\Unreal Engine\...`)
- Tier 3: Standard installation paths (`C:\Program Files\Epic Games\UE_5.5`, `D:\...`, `E:\...`)

Lines 152, 157, 174, 179, 203, 221, and 240 strictly use `[System.IO.File]::Exists($uatPath)` and `[System.IO.File]::Exists($uatDirect)` inside `try/catch` blocks.
Verified that probing non-existent drive letters (e.g. `Z:\NonExistentDrive\...`) via `[System.IO.File]::Exists` returns `False` without throwing `DriveNotFoundException`.

### 1.6 UAT BuildCookRun Command Construction (Lines 283-315)
Verbatim array construction from `package_game.ps1`:
```powershell
283: $uatArgs = @(
284:     "BuildCookRun",
285:     "-project=$uprojectPath",
286:     "-noP4",
287:     "-platform=$Platform",
288:     "-clientconfig=$Configuration",
289:     "-serverconfig=$Configuration",
290:     "-cook",
291:     "-allmaps",
292:     "-build",
293:     "-stage",
294:     "-pak",
295:     "-iostore",
296:     "-archive",
297:     "-archivedirectory=$OutputDir",
298:     "-utf8output"
299: )
300: 
301: if ($Clean.IsPresent) {
302:     $uatArgs += "-clean"
303: }
304: 
305: if ($NoCompileEditor.IsPresent) {
306:     $uatArgs += "-nocompileeditor"
307: }
```
When executed with `-DryRun`, the constructed command string emitted is:
`& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun -project=C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR.uproject -noP4 -platform=Win64 -clientconfig=Shipping -serverconfig=Shipping -cook -allmaps -build -stage -pak -iostore -archive -archivedirectory=C:\Users\silver\Desktop\bakirkoy-br\Saved\Packages -utf8output`

### 1.7 Execution, Log Streaming & Exit Codes (Lines 318-367)
- `-DryRun` and `-ValidateOnly` modes exit with code 0 (`exit 0`).
- Missing engine during normal (live) execution prints detailed remediation and terminates with exit code 1 (`exit 1`).
- Live execution pipeline uses `& "$runUatExecutable" $uatArgs 2>&1 | Tee-Object -FilePath $logFile`, preserves `$LASTEXITCODE`, duplicates to `Saved/Logs/Packaging.log`, and exits with `$exitCode`.

---

## 2. Logic Chain

1. **Syntax Integrity**:
   - The PowerShell AST parser produced 0 errors on `package_game.ps1`. Therefore, the script is syntactically sound and parseable by standard PowerShell hosts.

2. **Mandate Compliance**:
   - **Parameter Handling**: Parameter AST inspection confirmed that all 9 required parameters (`-Configuration`, `-Platform`, `-OutputDir`, `-EnginePath`, `-ProjectDir`, `-Clean`, `-NoCompileEditor`, `-DryRun`, `-ValidateOnly`) exist with appropriate types and ValidateSet constraints matching UE5 conventions.
   - **Cultural Invariance**: `[System.Threading.Thread]::CurrentThread.CurrentCulture` and `[System.Globalization.CultureInfo]::DefaultThreadCurrentCulture` are set to `InvariantCulture` before any path manipulation or string evaluation occurs. Direct testing with Turkish locale `tr-TR` confirmed immune execution.
   - **Safe File Probing**: Probing relies on .NET BCL `[System.IO.File]::Exists`, which does not throw `DriveNotFoundException` when scanning unmapped drive letters (`D:`, `E:`).
   - **Command Equivalence**: The 15 core flags required by the canonical BuildCookRun invocation are present in `$uatArgs`, with conditional inclusion of `-clean` and `-nocompileeditor`.
   - **CI & DryRun Grace**: When UE5 is absent, running `-DryRun` or `-ValidateOnly` avoids attempting to invoke `RunUAT.bat` and returns exit code 0.

3. **Integrity Check**:
   - The script contains no dummy facades or hardcoded mock answers that fake build success during a live packaging run. The live execution branch contains a complete invocation, real-time streaming, stopwatch duration tracking, and exit code propagation pipeline.

4. **Adversarial Edge-Case Analysis**:
   - *PowerShell 5.1 NativeCommandError*: Under Windows PowerShell 5.1, if `$ErrorActionPreference = 'Stop'`, piping stderr via `2>&1 | Tee-Object` can promote non-fatal compiler/UAT warning lines into a terminating `RemoteException`. In PowerShell 7+ (pwsh), this does not occur. This is noted as an environment caveat for future live build machines.

---

## 3. Caveats

1. **Waived Live Execution**: Unreal Engine 5 is not installed on the local system. Real-world execution of `RunUAT.bat` with a full build/cook/stage pipeline was waived by project directives and could not be physically executed.
2. **PowerShell Version Variance**: Testing was verified on both PowerShell Core (pwsh 7.x) and Windows PowerShell 5.1. For future live builds on Windows PowerShell 5.1, setting `$ErrorActionPreference = 'Continue'` before invoking external native executables that write diagnostics to stderr is recommended.

---

## 4. Conclusion

**Verdict: APPROVE**

`package_game.ps1` fully satisfies all functional, architectural, cultural safety, and parameter requirements specified in the Review Mandate. It exhibits robust error handling, non-throwing discovery logic, canonical command construction, and clean static validation/dry-run capabilities.

---

## 5. Verification Method

To independently verify this evaluation, execute the following commands in PowerShell from the project root (`C:\Users\silver\Desktop\bakirkoy-br`):

```powershell
# 1. Static AST syntax check
$code = Get-Content -Raw -Path .\package_game.ps1
$ast = [System.Management.Automation.Language.Parser]::ParseInput($code, [ref]$null, [ref]$errors)
Write-Host "Errors: $($errors.Count)"  # Expected: 0

# 2. Static validation mode
.\package_game.ps1 -ValidateOnly
Write-Host "Exit Code: $LASTEXITCODE"   # Expected: 0

# 3. Dry-run mode with Development config and Clean
.\package_game.ps1 -Configuration Development -Clean -NoCompileEditor -DryRun
Write-Host "Exit Code: $LASTEXITCODE"   # Expected: 0

# 4. Invariant culture check under Turkish locale
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::GetCultureInfo('tr-TR')
.\package_game.ps1 -ValidateOnly
Write-Host "Exit Code under tr-TR: $LASTEXITCODE" # Expected: 0

# 5. Invalid parameter rejection
try { .\package_game.ps1 -Configuration InvalidCfg -DryRun } catch { Write-Host "Rejected: $($_.Exception.Message)" }
```

Invalidation conditions:
- Any non-zero exit code returned when running `-ValidateOnly` or `-DryRun`.
- Any syntax errors flagged by `[System.Management.Automation.Language.Parser]`.
- Failure to reject invalid configuration or platform parameters.
