<#
.SYNOPSIS
    Adversarial Challenger MVP Test Suite for Bakırköy BR
.DESCRIPTION
    Executes empirical verification tests and stress-test assertions across
    the new Weapons, AI, and GameModes C++ classes against the 7 Core Constraints.
#>

[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\Users\silver\Desktop\bakirkoy-br"
)

$ErrorActionPreference = "Continue"

[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture

$Passed = 0
$Failed = 0
$Findings = @()

function Test-Assert {
    param(
        [string]$TestName,
        [bool]$Condition,
        [string]$FailureMessage = "Assertion failed",
        [string]$Category = "General"
    )

    if ($Condition) {
        $script:Passed++
        Write-Host "  [PASS] ($Category) $TestName" -ForegroundColor Green
    } else {
        $script:Failed++
        $script:Findings += [PSCustomObject]@{
            Category = $Category
            Test = $TestName
            Message = $FailureMessage
        }
        Write-Host "  [FAIL] ($Category) $TestName - $FailureMessage" -ForegroundColor Red
    }
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Bakirkoy BR - Adversarial Challenger MVP Test Harness" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

$SourceDir = Join-Path $ProjectRoot "BakirkoyBR\Source\BakirkoyBR"

# --- CATEGORY 1: No Interior Spaces (Constraint C1) ---
Write-Host "`n--- Category 1: No Interior Spaces ---" -ForegroundColor Yellow
$aiControllerCpp = Get-Content (Join-Path $SourceDir "AI\BRAIController.cpp") -Raw
$aiControllerH = Get-Content (Join-Path $SourceDir "AI\BRAIController.h") -Raw

Test-Assert -Category "NoInterior" -TestName "IsExteriorLocation declared in BRAIController.h" `
    -Condition ($aiControllerH -match "bool\s+IsExteriorLocation\s*\(\s*const\s+FVector&\s+Location\s*\)")

Test-Assert -Category "NoInterior" -TestName "Vertical upward line trace implemented (150m)" `
    -Condition ($aiControllerCpp -match "(?s)15000\.0f.*LineTraceSingleByChannel")

Test-Assert -Category "NoInterior" -TestName "Indoor ceiling height (<800cm) and downward normal rejected" `
    -Condition ($aiControllerCpp -match "HitResult\.Distance\s*<\s*800\.0f\s*&&\s*HitResult\.ImpactNormal\.Z\s*<\s*-0\.5f")

Test-Assert -Category "NoInterior" -TestName "FindNearestLoot rejects indoor locations" `
    -Condition ($aiControllerCpp -match "if\s*\(!IsExteriorLocation\(LootPos\)\)\s*\{\s*continue;\s*\}")

Test-Assert -Category "NoInterior" -TestName "GetRandomExteriorNavLocation validates candidate exterior points" `
    -Condition ($aiControllerCpp -match "if\s*\(IsExteriorLocation\(RandomNavPoint\.Location\)\)")

Test-Assert -Category "NoInterior" -TestName "FindNaturalCoverLocation filters out interior cover candidates" `
    -Condition ($aiControllerCpp -match "if\s*\(!IsExteriorLocation\(ProjectedPoint\.Location\)\)")

# --- CATEGORY 2: Solo BR Only (Constraint C2) ---
Write-Host "`n--- Category 2: Solo BR Only ---" -ForegroundColor Yellow
$brGmH = Get-Content (Join-Path $SourceDir "GameModes\BRGameMode_BattleRoyale.h") -Raw
$brGmCpp = Get-Content (Join-Path $SourceDir "GameModes\BRGameMode_BattleRoyale.cpp") -Raw

$squadRegex = '\b(Squad|SquadId|Teammate|DBNO|DownButNotOut|Revive|Duo|bIsDownButNotOut)\b'

Test-Assert -Category "SoloBR" -TestName "BRGameMode_BattleRoyale.h has 0 squad/duo/DBNO references" `
    -Condition (-not ($brGmH -match $squadRegex))

Test-Assert -Category "SoloBR" -TestName "BRGameMode_BattleRoyale.cpp has 0 squad/duo/DBNO references" `
    -Condition (-not ($brGmCpp -match $squadRegex))

Test-Assert -Category "SoloBR" -TestName "Elimination directly sets EBRPlayerStatus::Eliminated (no DBNO)" `
    -Condition ($brGmCpp -match "VictimPS->PlayerStatus\s*=\s*EBRPlayerStatus::Eliminated")

Test-Assert -Category "SoloBR" -TestName "Solo Last-Man-Standing win condition implemented" `
    -Condition ($brGmCpp -match "(?s)AliveParticipants\s*<=\s*1.*DeclareWinner\(SoleSurvivor\)")

# --- CATEGORY 3: 3 Materials Only (Constraint C5) ---
Write-Host "`n--- Category 3: Exactly 3 Materials ---" -ForegroundColor Yellow
$typesH = Get-Content (Join-Path $SourceDir "Data\BRTypes.h") -Raw
$forbiddenMatRegex = '\b(Wood|Stone|Metal|Gold|Ahsap|Ahşap|Demir|Beton)\b'

Test-Assert -Category "3Materials" -TestName "BRTypes.h defines Moloz, Tugla, Celik only" `
    -Condition ($typesH -match "(?s)enum\s+class\s+EBRMaterialType.*?Moloz.*?Tugla.*?Celik")

Test-Assert -Category "3Materials" -TestName "No forbidden 4th material in BRTypes.h" `
    -Condition (-not ($typesH -match $forbiddenMatRegex))

# Verify all source files in project for 4th material
$allSourceFiles = Get-ChildItem -Path $SourceDir -Recurse -Include *.h, *.cpp
$found4thMat = $false
foreach ($f in $allSourceFiles) {
    $content = Get-Content $f.FullName -Raw
    if ($content -match $forbiddenMatRegex -and $content -match '(?i)(material|build)') {
        $found4thMat = $true
        break
    }
}
Test-Assert -Category "3Materials" -TestName "All project source files have 0 forbidden 4th materials" `
    -Condition (-not $found4thMat)

# --- CATEGORY 4: Hybrid Hit Detection (Constraint C6 & MVP M2) ---
Write-Host "`n--- Category 4: Hybrid Hit Detection ---" -ForegroundColor Yellow
$hitScanCpp = Get-Content (Join-Path $SourceDir "Weapons\BRWeapon_HitScan.cpp") -Raw
$hitScanH = Get-Content (Join-Path $SourceDir "Weapons\BRWeapon_HitScan.h") -Raw
$projWeaponCpp = Get-Content (Join-Path $SourceDir "Weapons\BRWeapon_Projectile.cpp") -Raw
$projRocketCpp = Get-Content (Join-Path $SourceDir "Weapons\BRProjectileRocket.cpp") -Raw
$projRocketH = Get-Content (Join-Path $SourceDir "Weapons\BRProjectileRocket.h") -Raw
$botCharCpp = Get-Content (Join-Path $SourceDir "AI\BRAIBotCharacter.cpp") -Raw

Test-Assert -Category "HybridHitDetection" -TestName "Assault Rifle weapon type configured" `
    -Condition ($hitScanCpp -match "WeaponType\s*=\s*EBRWeaponType::AssaultRifle")

Test-Assert -Category "HybridHitDetection" -TestName "Assault Rifle uses LineTraceSingleByChannel" `
    -Condition ($hitScanCpp -match "World->LineTraceSingleByChannel")

Test-Assert -Category "HybridHitDetection" -TestName "Assault Rifle applies PointDamage" `
    -Condition ($hitScanCpp -match "UGameplayStatics::ApplyPointDamage")

Test-Assert -Category "HybridHitDetection" -TestName "Assault Rifle calculates linear damage falloff" `
    -Condition ($hitScanCpp -match "CalculateDamageFalloff")

Test-Assert -Category "HybridHitDetection" -TestName "Rocket Launcher weapon type configured" `
    -Condition ($projWeaponCpp -match "WeaponType\s*=\s*EBRWeaponType::RocketLauncher")

Test-Assert -Category "HybridHitDetection" -TestName "Rocket Launcher spawns ABRProjectileRocket" `
    -Condition ($projWeaponCpp -match "World->SpawnActor<ABRProjectileRocket>")

Test-Assert -Category "HybridHitDetection" -TestName "Rocket projectile uses UProjectileMovementComponent" `
    -Condition ($projRocketCpp -match "CreateDefaultSubobject<UProjectileMovementComponent>")

Test-Assert -Category "HybridHitDetection" -TestName "Rocket projectile applies direct PointDamage on hit" `
    -Condition ($projRocketCpp -match "UGameplayStatics::ApplyPointDamage")

Test-Assert -Category "HybridHitDetection" -TestName "Rocket projectile applies RadialDamageWithFalloff" `
    -Condition ($projRocketCpp -match "UGameplayStatics::ApplyRadialDamageWithFalloff")

Test-Assert -Category "HybridHitDetection" -TestName "Bot character has HitScan server firing" `
    -Condition ($botCharCpp -match "(?s)LineTraceSingleByChannel.*ECC_Visibility")

# --- CATEGORY 5: 10-Bot Maximum (MVP M1) ---
Write-Host "`n--- Category 5: 10-Bot Maximum ---" -ForegroundColor Yellow

Test-Assert -Category "10BotMax" -TestName "ABRAIController defines MAX_BOT_COUNT = 10" `
    -Condition ($aiControllerH -match "static\s+constexpr\s+int32\s+MAX_BOT_COUNT\s*=\s*10")

Test-Assert -Category "10BotMax" -TestName "BRGameMode_BattleRoyale defaults RequiredBotCount = 10" `
    -Condition ($brGmCpp -match "RequiredBotCount\s*=\s*10")

$ffaGmCpp = Get-Content (Join-Path $SourceDir "GameModes\BRGameMode_FFA.cpp") -Raw
Test-Assert -Category "10BotMax" -TestName "BRGameMode_FFA defaults RequiredBotCount = 10" `
    -Condition ($ffaGmCpp -match "RequiredBotCount\s*=\s*10")

Test-Assert -Category "10BotMax" -TestName "ABRAIController tracks ActiveBotCount" `
    -Condition ($aiControllerCpp -match "ActiveBotCount\+\+" -and $aiControllerCpp -match "ActiveBotCount--")

# Stress check 5.5: Does GameMode clamp bot count or check CanSpawnBot?
$brBotSpawnLoop = $brGmCpp -match "for\s*\(\s*int32\s+i\s*=\s*0;\s*i\s*<\s*RequiredBotCount"
$hasBotClamp = $brGmCpp -match "Clamp\(RequiredBotCount" -or $brGmCpp -match "CanSpawnBot"
Test-Assert -Category "10BotMax" -TestName "Stress Check: GameMode clamps or checks CanSpawnBot during spawn loop" `
    -Condition $hasBotClamp `
    -FailureMessage "Caveat: BRGameMode spawns RequiredBotCount directly without checking CanSpawnBot() or clamping to 10"

# --- CATEGORY 6: Paused Building (MVP M4) ---
Write-Host "`n--- Category 6: Paused Building ---" -ForegroundColor Yellow

Test-Assert -Category "PausedBuilding" -TestName "AI Controller implements FindNaturalCoverLocation" `
    -Condition ($aiControllerCpp -match "FindNaturalCoverLocation")

Test-Assert -Category "PausedBuilding" -TestName "AI Controller checks line-of-sight occlusion for cover" `
    -Condition ($aiControllerCpp -match "(?s)LineTraceSingleByChannel.*ECC_Visibility")

Test-Assert -Category "PausedBuilding" -TestName "AI Bot character implements SetCoverCrouch" `
    -Condition ($botCharCpp -match "SetCoverCrouch")

# Stress check 6.4: Check BRCharacter.cpp for dangling BRBuildingComponent.h include
$charCpp = Get-Content (Join-Path $SourceDir "Character\BRCharacter.cpp") -Raw
$hasDanglingBuildingHeader = $charCpp -match '#include\s+"Building/BRBuildingComponent\.h"'
$buildingHeaderExists = Test-Path (Join-Path $SourceDir "Building\BRBuildingComponent.h")
Test-Assert -Category "PausedBuilding" -TestName "Stress Check: BRCharacter.cpp has no dangling missing BuildingComponent header" `
    -Condition (-not $hasDanglingBuildingHeader -or $buildingHeaderExists) `
    -FailureMessage "Finding: BRCharacter.cpp includes missing header Building/BRBuildingComponent.h while building is paused"

# --- CATEGORY 7: GameMode 2 Distinct Modes (MVP M3) ---
Write-Host "`n--- Category 7: Two Distinct GameModes ---" -ForegroundColor Yellow
$stormCpp = Get-Content (Join-Path $SourceDir "Storm\BRStormCircle.cpp") -Raw

Test-Assert -Category "GameModes" -TestName "Mode 1: FFA Deathmatch GameMode exists" `
    -Condition (Test-Path (Join-Path $SourceDir "GameModes\BRGameMode_FFA.h"))

Test-Assert -Category "GameModes" -TestName "Mode 1: FFA has ScoreLimit and MatchTimeLimit" `
    -Condition ($ffaGmCpp -match "ScoreLimit" -and $ffaGmCpp -match "MatchTimeLimit")

Test-Assert -Category "GameModes" -TestName "Mode 2: Classic Battle Royale GameMode exists" `
    -Condition (Test-Path (Join-Path $SourceDir "GameModes\BRGameMode_BattleRoyale.h"))

Test-Assert -Category "GameModes" -TestName "Mode 2: Battle Royale integrates StormCircle" `
    -Condition ($brGmCpp -match "ActiveStormCircle" -and $brGmCpp -match "InitializeStormCircle")

Test-Assert -Category "GameModes" -TestName "StormCircle implements 7 progressive phases" `
    -Condition ($stormCpp -match "StormPhases\.Add" -and $stormCpp -match "SetupDefaultPhases")

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "Adversarial Challenger Summary" -ForegroundColor Cyan
Write-Host "Total Tests Passed: $Passed" -ForegroundColor Green
Write-Host "Total Tests Failed: $Failed" -ForegroundColor $(if ($Failed -eq 0) { "Green" } else { "Yellow" })
Write-Host "==================================================================" -ForegroundColor Cyan

if ($Findings.Count -gt 0) {
    Write-Host "`nAdversarial Stress Findings / Caveats ($($Findings.Count)):" -ForegroundColor Yellow
    foreach ($finding in $Findings) {
        Write-Host "  - [$($finding.Category)] $($finding.Test): $($finding.Message)" -ForegroundColor Yellow
    }
}
