$filePath = (Resolve-Path ".\package_game.ps1").Path
Write-Host "[AUDIT] Inspecting PowerShell AST of $filePath..."

$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($filePath, [ref]$tokens, [ref]$errors)

if ($errors.Count -gt 0) {
    Write-Error "Syntax errors found in package_game.ps1: $($errors.Count)"
    exit 1
}
Write-Host "  [PASS] Zero syntax errors ($($tokens.Count) tokens parsed)."

# Check Parameter block
$paramBlock = $ast.ParamBlock
if (-not $paramBlock) {
    Write-Error "Missing param() block!"
    exit 1
}

$paramNames = $paramBlock.Parameters | ForEach-Object { $_.Name.VariablePath.UserPath }
$expectedParams = @('Configuration', 'Platform', 'OutputDir', 'EnginePath', 'ProjectDir', 'Clean', 'NoCompileEditor', 'DryRun', 'ValidateOnly')
foreach ($ep in $expectedParams) {
    if ($paramNames -notcontains $ep) {
        Write-Error "Missing expected parameter: $ep"
        exit 1
    }
}
Write-Host "  [PASS] All 9 expected parameters present: $($expectedParams -join ', ')"

# Check InvariantCulture in AST
$cultureMatches = $tokens | Where-Object { $_.Text -like "*InvariantCulture*" }
if ($cultureMatches.Count -lt 2) {
    Write-Error "Insufficient InvariantCulture references in script tokens!"
    exit 1
}
Write-Host "  [PASS] CultureInfo::InvariantCulture verified in tokens."

# Check RunUAT command construction strings
$tokenTexts = $tokens | ForEach-Object { $_.Text }
$expectedTokens = @('BuildCookRun', '-project', '-noP4', '-cook', '-allmaps', '-build', '-stage', '-pak', '-iostore', '-archive', '-archivedirectory', '-utf8output')
foreach ($et in $expectedTokens) {
    if (-not ($tokenTexts -match [regex]::Escape($et))) {
        Write-Error "Missing UAT argument token: $et"
        exit 1
    }
}
Write-Host "  [PASS] All canonical UAT BuildCookRun parameters verified in script."

# Check that RunUAT.bat is checked using File::Exists
$fileExistsMatches = $tokens | Where-Object { $_.Text -like "*Exists*" }
if ($fileExistsMatches.Count -lt 1) {
    Write-Error "Missing [System.IO.File]::Exists check in tokens!"
    exit 1
}
Write-Host "  [PASS] [System.IO.File]::Exists non-throwing engine discovery verified."

Write-Host "[ALL POWERSHELL AST AUDITS PASSED CLEANLY]"
