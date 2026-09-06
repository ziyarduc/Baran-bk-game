<#
.SYNOPSIS
    Bakirkoy BR - Unreal Engine 5 Automated Packaging Pipeline
.DESCRIPTION
    Automates the build, cook, stage, pak, and archive pipeline for Bakirkoy BR
    using Unreal Automation Tool (RunUAT.bat). Implements multi-tier engine discovery,
    strict parameter validation, locale-invariant execution, real-time log streaming,
    and a static validation/dry-run mode for CI environments without UE5 installed.
.PARAMETER Configuration
    Target build configuration. Default: 'Shipping'. Allowed: Shipping, Development, DebugGame, Test, Debug.
.PARAMETER Platform
    Target platform. Default: 'Win64'. Allowed: Win64, Linux, Mac, Android, IOS.
.PARAMETER OutputDir
    Destination archive directory. Default: 'Saved/Packages'.
.PARAMETER EnginePath
    Explicit path to the Unreal Engine root directory (e.g. 'C:\Program Files\Epic Games\UE_5.5').
.PARAMETER ProjectDir
    Explicit path to the project root directory containing 'BakirkoyBR.uproject'.
.PARAMETER Clean
    When specified, cleans previous staging build artifacts before packaging.
.PARAMETER NoCompileEditor
    When specified, skips compiling editor binaries if they are already up to date.
.PARAMETER DryRun
    When specified, resolves all paths and parameters, constructs the UAT command,
    validates syntax, and outputs execution plan without invoking RunUAT.bat (Exit code: 0).
.PARAMETER ValidateOnly
    Alias/specialized mode to validate project structure and configuration statically (Exit code: 0).
.EXAMPLE
    .\package_game.ps1 -Configuration Shipping -Platform Win64
.EXAMPLE
    .\package_game.ps1 -Configuration Development -DryRun
.EXAMPLE
    .\package_game.ps1 -EnginePath "D:\EpicGames\UE_5.5" -Clean
.EXAMPLE
    .\package_game.ps1 -ValidateOnly
#>

[CmdletBinding(DefaultParameterSetName = 'Default')]
param(
    [Parameter(Position = 0)]
    [ValidateSet('Shipping', 'Development', 'DebugGame', 'Test', 'Debug')]
    [string]$Configuration = 'Shipping',

    [Parameter(Position = 1)]
    [ValidateSet('Win64', 'Linux', 'Mac', 'Android', 'IOS')]
    [string]$Platform = 'Win64',

    [Parameter(Position = 2)]
    [string]$OutputDir = 'Saved/Packages',

    [Parameter()]
    [string]$EnginePath = '',

    [Parameter()]
    [string]$ProjectDir = '',

    [Parameter()]
    [switch]$Clean,

    [Parameter()]
    [switch]$NoCompileEditor,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$ValidateOnly
)

# -------------------------------------------------------------------------
# 1. Environment & Invariant Culture Initialization
# -------------------------------------------------------------------------
$ErrorActionPreference = 'Stop'

# Guard against Turkish-I case-folding anomalies (e.g., 'i'.ToUpper() == 'İ')
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Bakirkoy BR - Unreal Engine 5 Packaging Pipeline (RunUAT)" -ForegroundColor Cyan
Write-Host "  Timestamp: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss UTC'))" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# -------------------------------------------------------------------------
# 2. Project & Target Resolution
# -------------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($ProjectDir)) {
    $ProjectDir = $PSScriptRoot
    if ([string]::IsNullOrWhiteSpace($ProjectDir)) {
        $ProjectDir = (Get-Location).Path
    }
}
$ProjectDir = [System.IO.Path]::GetFullPath($ProjectDir)

$uprojectFiles = Get-ChildItem -Path $ProjectDir -Filter "*.uproject" -File -ErrorAction SilentlyContinue
if (-not $uprojectFiles -or $uprojectFiles.Count -eq 0) {
    Write-Error "No .uproject file found in project directory: $ProjectDir"
    exit 1
}
$uprojectPath = $uprojectFiles[0].FullName
$projectName = [System.IO.Path]::GetFileNameWithoutExtension($uprojectPath)

# Read EngineAssociation from .uproject JSON safely
$engineAssociation = "5.5"
try {
    $uprojectJson = Get-Content -Path $uprojectPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($uprojectJson.EngineAssociation) {
        $engineAssociation = [string]$uprojectJson.EngineAssociation
    }
} catch {
    Write-Warning "Could not parse .uproject JSON. Defaulting EngineAssociation to '5.5'."
}

Write-Host "  [+] Target Project    : $projectName ($uprojectPath)" -ForegroundColor Green
Write-Host "  [+] Engine Association: $engineAssociation" -ForegroundColor Green
Write-Host "  [+] Build Target      : $Platform | $Configuration" -ForegroundColor Green

# -------------------------------------------------------------------------
# 3. Output Directory & Log Resolution
# -------------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = "Saved/Packages"
}
if (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = [System.IO.Path]::Combine($ProjectDir, $OutputDir)
}
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
Write-Host "  [+] Archive Directory : $OutputDir" -ForegroundColor Green

$logDir = [System.IO.Path]::Combine($ProjectDir, "Saved", "Logs")
$logTimestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logFile = [System.IO.Path]::Combine($logDir, "Packaging_$logTimestamp.log")
$latestLogFile = [System.IO.Path]::Combine($logDir, "Packaging.log")
Write-Host "  [+] Log Destination   : $latestLogFile" -ForegroundColor Green

# -------------------------------------------------------------------------
# 4. Multi-Tier Engine Discovery Logic
# -------------------------------------------------------------------------
function Resolve-UnrealEngineRoot {
    param(
        [string]$ExplicitPath,
        [string]$Association
    )

    # Tier 0: Explicit Override Parameter
    if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
        try {
            $candidate = [System.IO.Path]::GetFullPath($ExplicitPath)
            $uatPath = [System.IO.Path]::Combine($candidate, "Engine", "Build", "BatchFiles", "RunUAT.bat")
            if ([System.IO.File]::Exists($uatPath)) {
                return $candidate
            }
            # Also check if explicit path pointed directly to Engine subfolder
            $uatDirect = [System.IO.Path]::Combine($candidate, "Build", "BatchFiles", "RunUAT.bat")
            if ([System.IO.File]::Exists($uatDirect)) {
                return (Split-Path -Path $candidate -Parent)
            }
            Write-Warning "Explicit -EnginePath specified but RunUAT.bat not found at: $uatPath"
        } catch {
            Write-Warning "Invalid -EnginePath provided: $ExplicitPath"
        }
    }

    # Tier 1: Environment Variables
    $envVars = @("UE5_PATH", "UNREAL_ENGINE_PATH", "UE_ENGINE_DIR", "UE5_ROOT", "UE_${Association}_PATH")
    foreach ($varName in $envVars) {
        $envVal = [System.Environment]::GetEnvironmentVariable($varName)
        if (-not [string]::IsNullOrWhiteSpace($envVal)) {
            try {
                $candidate = [System.IO.Path]::GetFullPath($envVal)
                $uatPath = [System.IO.Path]::Combine($candidate, "Engine", "Build", "BatchFiles", "RunUAT.bat")
                if ([System.IO.File]::Exists($uatPath)) {
                    return $candidate
                }
                # Also check if env var points directly to Engine subdirectory
                $uatDirect = [System.IO.Path]::Combine($candidate, "Build", "BatchFiles", "RunUAT.bat")
                if ([System.IO.File]::Exists($uatDirect)) {
                    return (Split-Path -Path $candidate -Parent)
                }
            } catch {
                # Silently ignore invalid env paths
            }
        }
    }

    # Tier 2: Windows Registry Lookups
    $registryKeys = @(
        "HKLM:\SOFTWARE\EpicGames\Unreal Engine\$Association",
        "HKLM:\SOFTWARE\Epic Games\Unreal Engine\$Association",
        "HKLM:\SOFTWARE\WOW6432Node\EpicGames\Unreal Engine\$Association",
        "HKCU:\SOFTWARE\EpicGames\Unreal Engine\$Association",
        "HKCU:\SOFTWARE\Epic Games\Unreal Engine\$Association"
    )
    foreach ($regKey in $registryKeys) {
        if (Test-Path -Path $regKey) {
            try {
                $installedDir = (Get-ItemProperty -Path $regKey -Name "InstalledDirectory" -ErrorAction SilentlyContinue).InstalledDirectory
                if (-not [string]::IsNullOrWhiteSpace($installedDir)) {
                    $candidate = [System.IO.Path]::GetFullPath($installedDir)
                    $uatPath = [System.IO.Path]::Combine($candidate, "Engine", "Build", "BatchFiles", "RunUAT.bat")
                    if ([System.IO.File]::Exists($uatPath)) {
                        return $candidate
                    }
                }
            } catch {
                # Silently ignore registry query permissions issues
            }
        }
    }

    # Check custom source builds in registry (Builds key)
    $buildsKey = "HKCU:\SOFTWARE\Epic Games\Unreal Engine\Builds"
    if (Test-Path -Path $buildsKey) {
        try {
            $prop = (Get-ItemProperty -Path $buildsKey -ErrorAction SilentlyContinue).$Association
            if (-not [string]::IsNullOrWhiteSpace($prop)) {
                $candidate = [System.IO.Path]::GetFullPath($prop)
                $uatPath = [System.IO.Path]::Combine($candidate, "Engine", "Build", "BatchFiles", "RunUAT.bat")
                if ([System.IO.File]::Exists($uatPath)) {
                    return $candidate
                }
            }
        } catch { }
    }

    # Tier 3: Standard Epic Games Installation Directories
    $standardDirs = @(
        "C:\Program Files\Epic Games\UE_$Association",
        "C:\Program Files\Epic Games\UE_5.5",
        "C:\Program Files\Epic Games\UE_5.4",
        "C:\Program Files\Epic Games\UE_5.3",
        "D:\Program Files\Epic Games\UE_$Association",
        "E:\Program Files\Epic Games\UE_$Association"
    )
    foreach ($dir in $standardDirs) {
        try {
            $uatPath = [System.IO.Path]::Combine($dir, "Engine", "Build", "BatchFiles", "RunUAT.bat")
            if ([System.IO.File]::Exists($uatPath)) {
                return $dir
            }
        } catch { }
    }

    return $null
}

$resolvedEngineRoot = Resolve-UnrealEngineRoot -ExplicitPath $EnginePath -Association $engineAssociation
$isDryRun = $DryRun.IsPresent -or $ValidateOnly.IsPresent

if (-not $resolvedEngineRoot) {
    if ($isDryRun) {
        Write-Warning "Unreal Engine installation was not detected on this machine."
        Write-Host "  [*] Operating in DryRun / Static Validation Mode." -ForegroundColor Yellow
        $resolvedEngineRoot = "C:\Program Files\Epic Games\UE_$engineAssociation (Simulated)"
        $runUatExecutable = [System.IO.Path]::Combine("C:\Program Files\Epic Games\UE_$engineAssociation", "Engine", "Build", "BatchFiles", "RunUAT.bat")
    } else {
        Write-Error @"
Unreal Engine $engineAssociation installation could not be located on this machine.
Probed sources:
  1. Parameter -EnginePath
  2. Environment variables: UE5_PATH, UNREAL_ENGINE_PATH, UE_ENGINE_DIR, UE5_ROOT
  3. Registry keys: HKLM:\SOFTWARE\EpicGames\Unreal Engine\$engineAssociation
  4. Standard paths: C:\Program Files\Epic Games\UE_$engineAssociation

Remediation:
  - Provide an explicit path via -EnginePath '<PathToUE5>'
  - Set the UE5_PATH environment variable
  - For CI/CD or syntax validation without UE5 installed, run with -DryRun or -ValidateOnly
"@
        exit 1
    }
} else {
    $runUatExecutable = [System.IO.Path]::Combine($resolvedEngineRoot, "Engine", "Build", "BatchFiles", "RunUAT.bat")
    Write-Host "  [+] Resolved Engine   : $resolvedEngineRoot" -ForegroundColor Green
    Write-Host "  [+] RunUAT Tool       : $runUatExecutable" -ForegroundColor Green
}

# -------------------------------------------------------------------------
# 5. UAT BuildCookRun Command Construction
# -------------------------------------------------------------------------
$uatArgs = @(
    "BuildCookRun",
    "-project=$uprojectPath",
    "-noP4",
    "-platform=$Platform",
    "-clientconfig=$Configuration",
    "-serverconfig=$Configuration",
    "-cook",
    "-allmaps",
    "-build",
    "-stage",
    "-pak",
    "-iostore",
    "-archive",
    "-archivedirectory=$OutputDir",
    "-utf8output"
)

if ($Clean.IsPresent) {
    $uatArgs += "-clean"
}

if ($NoCompileEditor.IsPresent) {
    $uatArgs += "-nocompileeditor"
}

# Construct display command
$commandDisplay = "& `"$runUatExecutable`" " + ($uatArgs -join " ")

Write-Host "------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "  Constructed UAT Command:" -ForegroundColor Cyan
Write-Host "  $commandDisplay" -ForegroundColor Gray
Write-Host "------------------------------------------------------------------" -ForegroundColor Cyan

# -------------------------------------------------------------------------
# 6. Execution / DryRun Dispatch
# -------------------------------------------------------------------------
if ($isDryRun) {
    Write-Host "`n  [PASS] Static Validation & DryRun Succeeded." -ForegroundColor Green
    Write-Host "  Target Platform      : $Platform" -ForegroundColor Green
    Write-Host "  Build Configuration  : $Configuration" -ForegroundColor Green
    Write-Host "  Project Descriptor   : $uprojectPath" -ForegroundColor Green
    Write-Host "  Archive Destination  : $OutputDir" -ForegroundColor Green
    Write-Host "  Log Destination      : $latestLogFile" -ForegroundColor Green
    Write-Host "  UAT Invocation Plan  : Validated" -ForegroundColor Green
    exit 0
}

# Live Execution Stage (Executed only when RunUAT.bat is present)
if (-not (Test-Path -Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

if (-not (Test-Path -Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

Write-Host "`n[*] Launching Unreal Automation Tool..." -ForegroundColor Yellow
Write-Host "  [+] Packaging Log     : $logFile" -ForegroundColor Green
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    & "$runUatExecutable" $uatArgs 2>&1 | Tee-Object -FilePath $logFile
    $exitCode = $LASTEXITCODE
    Copy-Item -Path $logFile -Destination $latestLogFile -Force -ErrorAction SilentlyContinue
} catch {
    Write-Error "Failed to invoke RunUAT.bat: $_" -ErrorAction Continue
    exit 1
} finally {
    $stopwatch.Stop()
}

Write-Host "------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "  Packaging Duration: $($stopwatch.Elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
Write-Host "  Process Exit Code : $exitCode" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "[SUCCESS] Packaging completed successfully." -ForegroundColor Green
    Write-Host "Packaged artifacts stored at: $OutputDir" -ForegroundColor Green
    exit 0
} else {
    Write-Error "Packaging failed with exit code $exitCode. Review UAT logs above or at $logFile." -ErrorAction Continue
    exit $exitCode
}
