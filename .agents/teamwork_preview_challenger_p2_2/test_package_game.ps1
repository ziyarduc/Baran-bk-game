# ==============================================================================
# Adversarial Challenge Test Suite for package_game.ps1
# Agent: Challenger P2-2 (teamwork_preview_challenger_p2_2)
# Date: 2026-09-06
# Target File: C:\Users\silver\Desktop\bakirkoy-br\package_game.ps1
# ==============================================================================

[CmdletBinding()]
param(
    [string]$TargetScript = "C:\Users\silver\Desktop\bakirkoy-br\package_game.ps1",
    [string]$ProjectRoot = "C:\Users\silver\Desktop\bakirkoy-br"
)

$ErrorActionPreference = 'Continue'
$passed = 0
$failed = 0
$total = 0
$failures = @()

function Assert-Condition {
    param(
        [string]$TestId,
        [string]$Description,
        [bool]$Condition,
        [string]$FailureDetails = ""
    )
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] [$TestId] $Description" -ForegroundColor Green
    } else {
        $script:failed++
        Write-Host "  [FAIL] [$TestId] $Description" -ForegroundColor Red
        if ($FailureDetails) {
            Write-Host "         Detail: $FailureDetails" -ForegroundColor Yellow
        }
        $script:failures += "[$TestId] $Description - $FailureDetails"
    }
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Adversarial Challenge Test Suite: package_game.ps1" -ForegroundColor Cyan
Write-Host "  Target: $TargetScript" -ForegroundColor Cyan
Write-Host "  Timestamp: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss UTC'))" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# ------------------------------------------------------------------------------
# SUITE 1: Parser AST Integrity
# ------------------------------------------------------------------------------
Write-Host "`n--- Suite 1: Parser AST Integrity ---" -ForegroundColor Yellow

$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($TargetScript, [ref]$tokens, [ref]$parseErrors)

Assert-Condition -TestId "AST-01" `
    -Description "Script file exists and is accessible" `
    -Condition (Test-Path -Path $TargetScript) `
    -FailureDetails "Target script not found at $TargetScript"

Assert-Condition -TestId "AST-02" `
    -Description "Parser AST syntax error count is 0" `
    -Condition ($parseErrors.Count -eq 0) `
    -FailureDetails "Found $($parseErrors.Count) syntax errors: $(($parseErrors | ForEach-Object { $_.Message }) -join '; ')"

$paramBlock = $ast.ParamBlock
Assert-Condition -TestId "AST-03" `
    -Description "ParamBlock exists in script AST" `
    -Condition ($paramBlock -ne $null) `
    -FailureDetails "ParamBlock is null"

$parameters = $paramBlock.Parameters
Assert-Condition -TestId "AST-04" `
    -Description "Parameter count is exactly 9" `
    -Condition ($parameters.Count -eq 9) `
    -FailureDetails "Expected 9 parameters, found $($parameters.Count)"

$expectedParams = [ordered]@{
    "Configuration"   = "String"
    "Platform"        = "String"
    "OutputDir"       = "String"
    "EnginePath"      = "String"
    "ProjectDir"      = "String"
    "Clean"           = "SwitchParameter"
    "NoCompileEditor" = "SwitchParameter"
    "DryRun"          = "SwitchParameter"
    "ValidateOnly"    = "SwitchParameter"
}

foreach ($entry in $expectedParams.GetEnumerator()) {
    $paramName = $entry.Key
    $expectedType = $entry.Value
    $foundParam = $parameters | Where-Object { $_.Name.VariablePath.UserPath -eq $paramName }
    
    $exists = ($foundParam -ne $null)
    Assert-Condition -TestId "AST-05-$paramName" `
        -Description "Parameter `$$paramName exists with type [$expectedType]" `
        -Condition ($exists -and $foundParam.StaticType.Name -eq $expectedType) `
        -FailureDetails "Param exists: $exists, Type: $($foundParam.StaticType.Name), Expected: $expectedType"
}

# Inspect ValidateSet on Configuration
$configParam = $parameters | Where-Object { $_.Name.VariablePath.UserPath -eq "Configuration" }
$configValidateSet = $null
foreach ($attr in $configParam.Attributes) {
    if ($attr.TypeName.Name -eq "ValidateSet") {
        $configValidateSet = @($attr.PositionalArguments | ForEach-Object { $_.Value })
    }
}
$expectedConfigSet = @('Shipping', 'Development', 'DebugGame', 'Test', 'Debug')
$configMatches = ($configValidateSet -ne $null) -and ((Compare-Object $configValidateSet $expectedConfigSet).Count -eq 0)
Assert-Condition -TestId "AST-06" `
    -Description "Configuration ValidateSet contains ('Shipping', 'Development', 'DebugGame', 'Test', 'Debug')" `
    -Condition $configMatches `
    -FailureDetails "Found ValidateSet: $($configValidateSet -join ', ')"

# Inspect ValidateSet on Platform
$platParam = $parameters | Where-Object { $_.Name.VariablePath.UserPath -eq "Platform" }
$platValidateSet = $null
foreach ($attr in $platParam.Attributes) {
    if ($attr.TypeName.Name -eq "ValidateSet") {
        $platValidateSet = @($attr.PositionalArguments | ForEach-Object { $_.Value })
    }
}
$expectedPlatSet = @('Win64', 'Linux', 'Mac', 'Android', 'IOS')
$platMatches = ($platValidateSet -ne $null) -and ((Compare-Object $platValidateSet $expectedPlatSet).Count -eq 0)
Assert-Condition -TestId "AST-07" `
    -Description "Platform ValidateSet contains ('Win64', 'Linux', 'Mac', 'Android', 'IOS')" `
    -Condition $platMatches `
    -FailureDetails "Found ValidateSet: $($platValidateSet -join ', ')"

# Inspect Default Values in AST
$configDef = ($configParam.DefaultValue.Value -eq "Shipping")
Assert-Condition -TestId "AST-08" `
    -Description "Configuration default value in AST is 'Shipping'" `
    -Condition $configDef `
    -FailureDetails "Default value was $($configParam.DefaultValue.Value)"

$platDef = ($platParam.DefaultValue.Value -eq "Win64")
Assert-Condition -TestId "AST-09" `
    -Description "Platform default value in AST is 'Win64'" `
    -Condition $platDef `
    -FailureDetails "Default value was $($platParam.DefaultValue.Value)"

$outputParam = $parameters | Where-Object { $_.Name.VariablePath.UserPath -eq "OutputDir" }
$outputDef = ($outputParam.DefaultValue.Value -eq "Saved/Packages")
Assert-Condition -TestId "AST-10" `
    -Description "OutputDir default value in AST is 'Saved/Packages'" `
    -Condition $outputDef `
    -FailureDetails "Default value was $($outputParam.DefaultValue.Value)"

# ------------------------------------------------------------------------------
# SUITE 2: ValidateSet Enforcement & Input Validation
# ------------------------------------------------------------------------------
Write-Host "`n--- Suite 2: ValidateSet Enforcement & Input Validation ---" -ForegroundColor Yellow

# Test all valid configurations
foreach ($cfg in @('Shipping', 'Development', 'DebugGame', 'Test', 'Debug')) {
    $out = & pwsh -NoProfile -Command "& '$TargetScript' -Configuration '$cfg' -DryRun" 2>&1
    $exitCode = $LASTEXITCODE
    Assert-Condition -TestId "VAL-01-$cfg" `
        -Description "Valid configuration '$cfg' is accepted (Exit code: 0)" `
        -Condition ($exitCode -eq 0) `
        -FailureDetails "Exit code: $exitCode, Output: $(($out | Out-String).Trim())"
}

# Test case-insensitivity on valid configuration
$outCase = & pwsh -NoProfile -Command "& '$TargetScript' -Configuration 'shipping' -DryRun" 2>&1
$exitCodeCase = $LASTEXITCODE
Assert-Condition -TestId "VAL-02-Case" `
    -Description "Configuration is case-insensitive ('shipping' accepted)" `
    -Condition ($exitCodeCase -eq 0) `
    -FailureDetails "Exit code: $exitCodeCase, Output: $(($outCase | Out-String).Trim())"

# Test invalid configurations
foreach ($badCfg in @('InvalidConfig', 'Production', 'Server', 'ClientOnly')) {
    $err = $null
    try {
        & pwsh -NoProfile -Command "& '$TargetScript' -Configuration '$badCfg' -DryRun" 2>&1 | Out-Null
        $badExit = $LASTEXITCODE
    } catch {
        $badExit = 1
    }
    Assert-Condition -TestId "VAL-03-$badCfg" `
        -Description "Invalid configuration '$badCfg' is rejected with non-zero exit code" `
        -Condition ($badExit -ne 0) `
        -FailureDetails "Script unexpectedly succeeded with exit code $badExit"
}

# Test valid platforms
foreach ($plt in @('Win64', 'Linux', 'Mac', 'Android', 'IOS')) {
    $out = & pwsh -NoProfile -Command "& '$TargetScript' -Platform '$plt' -DryRun" 2>&1
    $exitCode = $LASTEXITCODE
    Assert-Condition -TestId "VAL-04-$plt" `
        -Description "Valid platform '$plt' is accepted (Exit code: 0)" `
        -Condition ($exitCode -eq 0) `
        -FailureDetails "Exit code: $exitCode, Output: $(($out | Out-String).Trim())"
}

# Test invalid platforms
foreach ($badPlat in @('PlayStation5', 'XboxSeriesX', 'Switch', 'Web')) {
    & pwsh -NoProfile -Command "& '$TargetScript' -Platform '$badPlat' -DryRun" 2>&1 | Out-Null
    $badExit = $LASTEXITCODE
    Assert-Condition -TestId "VAL-05-$badPlat" `
        -Description "Invalid platform '$badPlat' is rejected with non-zero exit code" `
        -Condition ($badExit -ne 0) `
        -FailureDetails "Script unexpectedly succeeded with exit code $badExit"
}

# ------------------------------------------------------------------------------
# SUITE 3: Parameter Combinations & Mode Dispatch
# ------------------------------------------------------------------------------
Write-Host "`n--- Suite 3: Parameter Combinations & Mode Dispatch ---" -ForegroundColor Yellow

# Test -DryRun alone
$outDry = & pwsh -NoProfile -Command "& '$TargetScript' -DryRun" 2>&1
$dryCode = $LASTEXITCODE
$dryString = ($outDry | Out-String)
Assert-Condition -TestId "PARAM-01" `
    -Description "-DryRun switch executes static validation mode and exits 0" `
    -Condition ($dryCode -eq 0 -and $dryString -match "Static Validation & DryRun Succeeded") `
    -FailureDetails "Exit code: $dryCode, Text match: $($dryString -match 'Static Validation & DryRun Succeeded')"

# Test -ValidateOnly alone
$outVal = & pwsh -NoProfile -Command "& '$TargetScript' -ValidateOnly" 2>&1
$valCode = $LASTEXITCODE
$valString = ($outVal | Out-String)
Assert-Condition -TestId "PARAM-02" `
    -Description "-ValidateOnly switch executes static validation mode and exits 0" `
    -Condition ($valCode -eq 0 -and $valString -match "Static Validation & DryRun Succeeded") `
    -FailureDetails "Exit code: $valCode, Text match: $($valString -match 'Static Validation & DryRun Succeeded')"

# Test -Clean switch
$outClean = & pwsh -NoProfile -Command "& '$TargetScript' -Clean -DryRun" 2>&1
$cleanString = ($outClean | Out-String)
Assert-Condition -TestId "PARAM-03" `
    -Description "-Clean switch appends -clean to constructed RunUAT command" `
    -Condition ($cleanString -match "-clean") `
    -FailureDetails "Expected '-clean' in command, got: $cleanString"

# Test -NoCompileEditor switch
$outNoEditor = & pwsh -NoProfile -Command "& '$TargetScript' -NoCompileEditor -DryRun" 2>&1
$noEditorString = ($outNoEditor | Out-String)
Assert-Condition -TestId "PARAM-04" `
    -Description "-NoCompileEditor switch appends -nocompileeditor to constructed RunUAT command" `
    -Condition ($noEditorString -match "-nocompileeditor") `
    -FailureDetails "Expected '-nocompileeditor' in command, got: $noEditorString"

# Test both -Clean and -NoCompileEditor
$outBoth = & pwsh -NoProfile -Command "& '$TargetScript' -Clean -NoCompileEditor -DryRun" 2>&1
$bothString = ($outBoth | Out-String)
Assert-Condition -TestId "PARAM-05" `
    -Description "Combined -Clean and -NoCompileEditor appends both flags" `
    -Condition ($bothString -match "-clean" -and $bothString -match "-nocompileeditor") `
    -FailureDetails "Expected both -clean and -nocompileeditor in command"

# Test absence of -Clean and -NoCompileEditor
$outNeither = & pwsh -NoProfile -Command "& '$TargetScript' -DryRun" 2>&1
$neitherString = ($outNeither | Out-String)
$commandLineNeither = ($neitherString -split "`n" | Where-Object { $_ -match "Constructed UAT Command" -or $_ -match "BuildCookRun" }) -join " "
Assert-Condition -TestId "PARAM-06" `
    -Description "Default execution omits -clean and -nocompileeditor" `
    -Condition (-not ($commandLineNeither -match "\s-clean\b") -and -not ($commandLineNeither -match "\s-nocompileeditor\b")) `
    -FailureDetails "Found unexpected clean/nocompileeditor flag in default run: $commandLineNeither"

# Test relative -OutputDir
$outRelDir = & pwsh -NoProfile -Command "& '$TargetScript' -OutputDir 'CustomBuilds/RC1' -DryRun" 2>&1
$relString = ($outRelDir | Out-String)
Assert-Condition -TestId "PARAM-07" `
    -Description "Relative -OutputDir is resolved to absolute path under project root" `
    -Condition ($relString -match [regex]::Escape("CustomBuilds\RC1")) `
    -FailureDetails "Expected CustomBuilds\RC1 in output: $relString"

# Test absolute -OutputDir
$absTarget = "C:\BakirkoyPackages\Release1"
$outAbsDir = & pwsh -NoProfile -Command "& '$TargetScript' -OutputDir '$absTarget' -DryRun" 2>&1
$absString = ($outAbsDir | Out-String)
Assert-Condition -TestId "PARAM-08" `
    -Description "Absolute -OutputDir is preserved as absolute path" `
    -Condition ($absString -match [regex]::Escape($absTarget)) `
    -FailureDetails "Expected $absTarget in output: $absString"

# ------------------------------------------------------------------------------
# SUITE 4: Drive-Letter Robustness & Path Resilience
# ------------------------------------------------------------------------------
Write-Host "`n--- Suite 4: Drive-Letter Robustness & Path Resilience ---" -ForegroundColor Yellow

# Test non-existent drive in -EnginePath
$outDriveX = & pwsh -NoProfile -Command "& '$TargetScript' -EnginePath 'X:\EpicGames\UE_5.5' -DryRun" 2>&1
$codeDriveX = $LASTEXITCODE
$strDriveX = ($outDriveX | Out-String)
$hasDriveNotFoundX = ($strDriveX -match "DriveNotFoundException")
Assert-Condition -TestId "DRV-01" `
    -Description "-EnginePath on non-existent drive (X:\...) throws no DriveNotFoundException and exits 0 in DryRun" `
    -Condition ($codeDriveX -eq 0 -and -not $hasDriveNotFoundX) `
    -FailureDetails "Exit code: $codeDriveX, DriveNotFoundException: $hasDriveNotFoundX"

# Test non-existent drive in -EnginePath fallback
Assert-Condition -TestId "DRV-02" `
    -Description "-EnginePath warning is emitted for non-existent drive without aborting" `
    -Condition ($strDriveX -match "Explicit -EnginePath specified but RunUAT.bat not found" -or $strDriveX -match "Operating in DryRun") `
    -FailureDetails "Output did not indicate graceful fallback: $strDriveX"

# Test non-existent drive in -ProjectDir (Stress check for unhandled DriveNotFoundException)
$outDriveZ = & pwsh -NoProfile -Command "& '$TargetScript' -ProjectDir 'Z:\Projects' -DryRun" 2>&1
$codeDriveZ = $LASTEXITCODE
$strDriveZ = ($outDriveZ | Out-String)
$hasDriveNotFoundZ = ($strDriveZ -match "DriveNotFoundException")
Assert-Condition -TestId "DRV-03" `
    -Description "-ProjectDir on non-existent drive (Z:\...) throws no unhandled DriveNotFoundException" `
    -Condition (-not $hasDriveNotFoundZ) `
    -FailureDetails "DriveNotFoundException was detected: $strDriveZ"

# Test standard directory scanning resilience across missing drives (D:\, E:\)
# In Resolve-UnrealEngineRoot, lines 229-244 scan D:\ and E:\. Verify it doesn't throw.
$outTier3 = & pwsh -NoProfile -Command "& '$TargetScript' -DryRun" 2>&1
$codeTier3 = $LASTEXITCODE
$strTier3 = ($outTier3 | Out-String)
Assert-Condition -TestId "DRV-04" `
    -Description "Standard engine probing scans missing drives (D:\, E:\) without throwing DriveNotFoundException" `
    -Condition ($codeTier3 -eq 0 -and -not ($strTier3 -match "DriveNotFoundException")) `
    -FailureDetails "Exit code: $codeTier3, Output: $strTier3"

# Test missing engine guard without -DryRun
$outNoEngine = & pwsh -NoProfile -Command "& '$TargetScript'" 2>&1
$codeNoEngine = $LASTEXITCODE
$strNoEngine = ($outNoEngine | Out-String)
Assert-Condition -TestId "DRV-05" `
    -Description "Execution without -DryRun on machine without UE5 exits 1 with remediation message (no unhandled exception)" `
    -Condition ($codeNoEngine -eq 1 -and $strNoEngine -match "Unreal Engine 5.5 installation could not be located") `
    -FailureDetails "Exit code: $codeNoEngine, Output: $strNoEngine"

# ------------------------------------------------------------------------------
# SUITE 5: RunUAT Command-Line Synthesis
# ------------------------------------------------------------------------------
Write-Host "`n--- Suite 5: RunUAT Command-Line Synthesis ---" -ForegroundColor Yellow

$testOutputDir = "Saved/Packages"
$synthOutput = & pwsh -NoProfile -Command "& '$TargetScript' -Configuration 'Shipping' -Platform 'Win64' -OutputDir '$testOutputDir' -Clean -NoCompileEditor -DryRun" 2>&1
$synthString = ($synthOutput | Out-String)

# Find the command line line
$cmdLine = ($synthString -split "`n" | Where-Object { $_ -match "BuildCookRun" })
if ($cmdLine -is [array]) { $cmdLine = $cmdLine[0] }

Assert-Condition -TestId "CMD-01" `
    -Description "Command starts with RunUAT executable and BuildCookRun commandlet" `
    -Condition ($cmdLine -match "RunUAT\.bat`"?\s+BuildCookRun") `
    -FailureDetails "Command line: $cmdLine"

$requiredFlags = @(
    @{ Flag = "-project=";             Pattern = "-project=[^ ]+BakirkoyBR\.uproject" }
    @{ Flag = "-platform=Win64";       Pattern = "-platform=Win64" }
    @{ Flag = "-clientconfig=Shipping"; Pattern = "-clientconfig=Shipping" }
    @{ Flag = "-serverconfig=Shipping"; Pattern = "-serverconfig=Shipping" }
    @{ Flag = "-cook";                 Pattern = "\s-cook\b" }
    @{ Flag = "-allmaps";              Pattern = "\s-allmaps\b" }
    @{ Flag = "-build";                Pattern = "\s-build\b" }
    @{ Flag = "-stage";                Pattern = "\s-stage\b" }
    @{ Flag = "-pak";                  Pattern = "\s-pak\b" }
    @{ Flag = "-iostore";              Pattern = "\s-iostore\b" }
    @{ Flag = "-archive";              Pattern = "\s-archive\b" }
    @{ Flag = "-archivedirectory=";    Pattern = "-archivedirectory=[^ ]+" }
    @{ Flag = "-utf8output";           Pattern = "\s-utf8output\b" }
    @{ Flag = "-noP4";                 Pattern = "\s-noP4\b" }
    @{ Flag = "-clean";                Pattern = "\s-clean\b" }
    @{ Flag = "-nocompileeditor";      Pattern = "\s-nocompileeditor\b" }
)

foreach ($rf in $requiredFlags) {
    $flagName = $rf.Flag
    $pattern = $rf.Pattern
    $matched = ($cmdLine -match $pattern)
    Assert-Condition -TestId "CMD-02-$flagName" `
        -Description "Synthesized command contains flag $flagName" `
        -Condition $matched `
        -FailureDetails "Flag $flagName missing or pattern '$pattern' not matched in: $cmdLine"
}

# ------------------------------------------------------------------------------
# SUITE 6: Turkish-I Culture Invariance (tr-TR)
# ------------------------------------------------------------------------------
Write-Host "`n--- Suite 6: Turkish-I Culture Invariance (tr-TR) ---" -ForegroundColor Yellow

$trScript = @"
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::GetCultureInfo('tr-TR')
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::GetCultureInfo('tr-TR')
& '$TargetScript' -Configuration 'Shipping' -DryRun
exit `$LASTEXITCODE
"@
$trOutput = & pwsh -NoProfile -Command $trScript 2>&1
$trExitCode = $LASTEXITCODE
Assert-Condition -TestId "CUL-01" `
    -Description "Script executes successfully under forced tr-TR culture with uppercase 'Shipping' (Exit code: 0)" `
    -Condition ($trExitCode -eq 0) `
    -FailureDetails "Exit code: $trExitCode, Output: $(($trOutput | Out-String).Trim())"

$trScriptLower = @"
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::GetCultureInfo('tr-TR')
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::GetCultureInfo('tr-TR')
& '$TargetScript' -Configuration 'shipping' -DryRun
exit `$LASTEXITCODE
"@
$trLowerOutput = & pwsh -NoProfile -Command $trScriptLower 2>&1
$trLowerExitCode = $LASTEXITCODE
Assert-Condition -TestId "CUL-02" `
    -Description "Script executes successfully under forced tr-TR culture with lowercase 'shipping' (Exit code: 0)" `
    -Condition ($trLowerExitCode -eq 0) `
    -FailureDetails "Exit code: $trLowerExitCode, Output: $(($trLowerOutput | Out-String).Trim())"

$trScriptCombos = @"
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::GetCultureInfo('tr-TR')
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::GetCultureInfo('tr-TR')
& '$TargetScript' -Configuration 'Development' -Clean -NoCompileEditor -ValidateOnly
exit `$LASTEXITCODE
"@
$trComboOutput = & pwsh -NoProfile -Command $trScriptCombos 2>&1
$trComboExitCode = $LASTEXITCODE
Assert-Condition -TestId "CUL-03" `
    -Description "Script executes complex parameters under forced tr-TR culture (Exit code: 0)" `
    -Condition ($trComboExitCode -eq 0) `
    -FailureDetails "Exit code: $trComboExitCode, Output: $(($trComboOutput | Out-String).Trim())"

# Verify culture invariance code exists in script content
$scriptContent = Get-Content -Path $TargetScript -Raw
$hasCultureGuard = ($scriptContent -match "CurrentCulture\s*=\s*\[System\.Globalization\.CultureInfo\]::InvariantCulture" -and `
                    ($scriptContent -match "DefaultThreadCurrentCulture\s*=\s*\[System\.Globalization\.CultureInfo\]::InvariantCulture"))
Assert-Condition -TestId "CUL-04" `
    -Description "Script explicitly sets InvariantCulture on CurrentCulture and DefaultThreadCurrentCulture" `
    -Condition $hasCultureGuard `
    -FailureDetails "Invariant culture guard not found in script lines 71-80"

# ------------------------------------------------------------------------------
# SUITE 7: Empirical Mock RunUAT Execution & Exit Code Propagation
# ------------------------------------------------------------------------------
Write-Host "`n--- Suite 7: Empirical Mock RunUAT Execution & Exit Code Propagation ---" -ForegroundColor Yellow

$tempMockRoot = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), [System.Guid]::NewGuid().ToString())
$mockBatchDir = [System.IO.Path]::Combine($tempMockRoot, "Engine", "Build", "BatchFiles")
New-Item -ItemType Directory -Path $mockBatchDir -Force | Out-Null
$mockUatBat = [System.IO.Path]::Combine($mockBatchDir, "RunUAT.bat")
$mockOutputDir = [System.IO.Path]::Combine($tempMockRoot, "PackagedOutput")

try {
    # Test 7.1: Successful Mock RunUAT execution
    Set-Content -Path $mockUatBat -Value "@echo [Mock RunUAT] BuildCookRun SUCCESS`r`n@exit /b 0"
    
    $mockExecScript = @"
& '$TargetScript' -EnginePath '$tempMockRoot' -OutputDir '$mockOutputDir' -Clean
exit `$LASTEXITCODE
"@
    $mockExecOut = & pwsh -NoProfile -Command $mockExecScript 2>&1
    $mockExecCode = $LASTEXITCODE
    $mockExecStr = ($mockExecOut | Out-String)
    
    Assert-Condition -TestId "MOCK-01" `
        -Description "Empirical Mock RunUAT execution succeeds and propagates exit code 0" `
        -Condition ($mockExecCode -eq 0 -and $mockExecStr -match "\[SUCCESS\] Packaging completed successfully") `
        -FailureDetails "Exit code: $mockExecCode, Output: $mockExecStr"

    Assert-Condition -TestId "MOCK-02" `
        -Description "Output archive directory was created by packaging pipeline" `
        -Condition (Test-Path -Path $mockOutputDir) `
        -FailureDetails "Mock output directory not created at $mockOutputDir"

    $logFile = [System.IO.Path]::Combine($ProjectRoot, "Saved", "Logs", "Packaging.log")
    $logCreated = (Test-Path -Path $logFile)
    $logContent = if ($logCreated) { Get-Content -Path $logFile -Raw } else { "" }
    Assert-Condition -TestId "MOCK-03" `
        -Description "Packaging log file Saved\Logs\Packaging.log was created and captured RunUAT output" `
        -Condition ($logCreated -and ($logContent -match "Mock RunUAT")) `
        -FailureDetails "Log exists: $logCreated, Log content: $logContent"

    # Test 7.2: Failed Mock RunUAT execution (exit code 42)
    Set-Content -Path $mockUatBat -Value "@echo [Mock RunUAT ERROR] Cook error encountered`r`n@exit /b 42"
    
    $mockFailScript = @"
& '$TargetScript' -EnginePath '$tempMockRoot' -OutputDir '$mockOutputDir'
exit `$LASTEXITCODE
"@
    $mockFailOut = & pwsh -NoProfile -Command $mockFailScript 2>&1
    $mockFailCode = $LASTEXITCODE
    $mockFailStr = ($mockFailOut | Out-String)
    
    Assert-Condition -TestId "MOCK-04" `
        -Description "Empirical Mock RunUAT failure propagates non-zero exit code 42" `
        -Condition ($mockFailCode -eq 42 -and $mockFailStr -match "Packaging failed with exit code 42") `
        -FailureDetails "Exit code: $mockFailCode, Output: $mockFailStr"

} finally {
    if (Test-Path -Path $tempMockRoot) {
        Remove-Item -Path $tempMockRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# ------------------------------------------------------------------------------
# Test Summary
# ------------------------------------------------------------------------------
Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "  Adversarial Challenge Summary: package_game.ps1" -ForegroundColor Cyan
Write-Host "  Total Tests Executed : $total" -ForegroundColor Cyan
Write-Host "  Total Passed         : $passed" -ForegroundColor Green
Write-Host "  Total Failed         : $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host "==================================================================" -ForegroundColor Cyan

if ($failed -eq 0) {
    Write-Host "`n>>> ALL ADVERSARIAL TESTS PASSED [100% SUCCESS] <<<`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n>>> ADVERSARIAL FAILURES DETECTED: $failed <<<`n" -ForegroundColor Red
    foreach ($f in $failures) {
        Write-Host "  - $f" -ForegroundColor Red
    }
    exit 1
}
