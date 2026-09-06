# Test Suite for package_game.ps1 AST and Logic Verification
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture

$filePath = "C:\Users\silver\Desktop\bakirkoy-br\package_game.ps1"
$raw = Get-Content -Path $filePath -Raw
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseInput($raw, [ref]$tokens, [ref]$errors)

$totalPassed = 0
$totalFailed = 0

function Assert-Check {
    param(
        [string]$Name,
        [bool]$Condition,
        [string]$Message = ""
    )
    if ($Condition) {
        $script:totalPassed++
        Write-Host "  [PASS] $Name" -ForegroundColor Green
    } else {
        $script:totalFailed++
        Write-Host "  [FAIL] $Name - $Message" -ForegroundColor Red
    }
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "AST & Static Validation: package_game.ps1" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Syntax & ParamBlock
Assert-Check -Name "Zero Syntax Errors" -Condition ($errors.Count -eq 0) -Message "Errors count: $($errors.Count)"
Assert-Check -Name "ParamBlock Exists" -Condition ($ast.ParamBlock -ne $null)
Assert-Check -Name "Parameter Count is 9" -Condition ($ast.ParamBlock.Parameters.Count -eq 9) -Message "Count: $($ast.ParamBlock.Parameters.Count)"

$params = @{}
foreach ($p in $ast.ParamBlock.Parameters) {
    $params[$p.Name.VariablePath.UserPath] = $p
}

# 2. Configuration Parameter
Assert-Check -Name "Param 'Configuration' exists" -Condition ($params.ContainsKey('Configuration'))
$cfgParam = $params['Configuration']
$cfgValSet = $cfgParam.Attributes | Where-Object { $_.TypeName.FullName -match 'ValidateSet' }
$cfgValues = $cfgValSet.PositionalArguments | ForEach-Object { $_.Extent.Text.Trim("'", '"') }
Assert-Check -Name "Param 'Configuration' ValidateSet contains Shipping" -Condition ($cfgValues -contains 'Shipping')
Assert-Check -Name "Param 'Configuration' ValidateSet contains Development" -Condition ($cfgValues -contains 'Development')
Assert-Check -Name "Param 'Configuration' default is Shipping" -Condition ($cfgParam.DefaultValue.Extent.Text -match 'Shipping')

# 3. Platform Parameter
Assert-Check -Name "Param 'Platform' exists" -Condition ($params.ContainsKey('Platform'))
$platParam = $params['Platform']
$platValSet = $platParam.Attributes | Where-Object { $_.TypeName.FullName -match 'ValidateSet' }
$platValues = $platValSet.PositionalArguments | ForEach-Object { $_.Extent.Text.Trim("'", '"') }
Assert-Check -Name "Param 'Platform' ValidateSet contains Win64" -Condition ($platValues -contains 'Win64')
Assert-Check -Name "Param 'Platform' default is Win64" -Condition ($platParam.DefaultValue.Extent.Text -match 'Win64')

# 4. OutputDir, EnginePath, ProjectDir
Assert-Check -Name "Param 'OutputDir' exists" -Condition ($params.ContainsKey('OutputDir'))
Assert-Check -Name "Param 'OutputDir' default contains Saved/Packages" -Condition ($params['OutputDir'].DefaultValue.Extent.Text -match 'Saved/Packages')
Assert-Check -Name "Param 'EnginePath' exists" -Condition ($params.ContainsKey('EnginePath'))
Assert-Check -Name "Param 'ProjectDir' exists" -Condition ($params.ContainsKey('ProjectDir'))

# 5. Switch Parameters
Assert-Check -Name "Param 'Clean' is switch" -Condition ($params.ContainsKey('Clean') -and $params['Clean'].StaticType.Name -eq 'SwitchParameter')
Assert-Check -Name "Param 'NoCompileEditor' is switch" -Condition ($params.ContainsKey('NoCompileEditor') -and $params['NoCompileEditor'].StaticType.Name -eq 'SwitchParameter')
Assert-Check -Name "Param 'DryRun' is switch" -Condition ($params.ContainsKey('DryRun') -and $params['DryRun'].StaticType.Name -eq 'SwitchParameter')
Assert-Check -Name "Param 'ValidateOnly' is switch" -Condition ($params.ContainsKey('ValidateOnly') -and $params['ValidateOnly'].StaticType.Name -eq 'SwitchParameter')

# 6. UAT Flags verification
$uatFlags = @(
    "-project=",
    "-noP4",
    "-platform=",
    "-clientconfig=",
    "-serverconfig=",
    "-cook",
    "-allmaps",
    "-build",
    "-stage",
    "-pak",
    "-iostore",
    "-archive",
    "-archivedirectory=",
    "-utf8output",
    "-clean",
    "-nocompileeditor"
)
foreach ($flag in $uatFlags) {
    Assert-Check -Name "UAT Flag present: $flag" -Condition ($raw.Contains($flag))
}

# 7. Safety guards
Assert-Check -Name "Culture Invariance enforced (InvariantCulture)" -Condition ($raw.Contains("InvariantCulture"))
Assert-Check -Name "Safe file existence check ([System.IO.File]::Exists)" -Condition ($raw.Contains("[System.IO.File]::Exists"))
Assert-Check -Name "Multi-tier discovery function defined" -Condition ($raw.Contains("function Resolve-UnrealEngineRoot"))
Assert-Check -Name "Registry probe keys present" -Condition ($raw.Contains("HKLM:\SOFTWARE\EpicGames\Unreal Engine"))
Assert-Check -Name "Environment variables probed" -Condition ($raw.Contains("UE5_PATH") -and $raw.Contains("UNREAL_ENGINE_PATH") -and $raw.Contains("UE_ENGINE_DIR") -and $raw.Contains("UE5_ROOT"))

Write-Host "------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "Total Passed: $totalPassed | Total Failed: $totalFailed" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

if ($totalFailed -gt 0) {
    exit 1
}
exit 0
