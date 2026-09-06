<#
.SYNOPSIS
    Bakirkoy BR Project Rules and AST Validation Script
.DESCRIPTION
    Validates rule file existence, constraint retention, sequential thinking definitions,
    and applies AST/regex validation rules against both the project codebase and synthetic test patterns.
.NOTES
    Author: Worker M2 (Error-Prevention and Rules Worker)
    Reference: Milestone 2 and Requirement R1
#>

[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\Users\silver\Desktop\bakirkoy-br",
    [switch]$VerboseOutput = $false
)

$ErrorActionPreference = "Continue"

# Force InvariantCulture to prevent Turkish-I ("I" -> "ı") case-folding bugs in regex ranges on Turkish Windows locales
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture

$Global:TotalPassed = 0
$Global:TotalFailed = 0
$Global:TestResults = @()

function Assert-Test {
    param(
        [string]$TestName,
        [bool]$Condition,
        [string]$FailureMessage = "Test condition evaluated to false."
    )

    if ($Condition) {
        $Global:TotalPassed++
        $Global:TestResults += [PSCustomObject]@{
            Test = $TestName
            Status = "PASS"
            Details = "Passed"
        }
        Write-Host "  [PASS] $TestName" -ForegroundColor Green
    } else {
        $Global:TotalFailed++
        $Global:TestResults += [PSCustomObject]@{
            Test = $TestName
            Status = "FAIL"
            Details = $FailureMessage
        }
        Write-Host "  [FAIL] $TestName - $FailureMessage" -ForegroundColor Red
    }
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Bakirkoy BR - Rules and AST Validation Suite" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# -------------------------------------------------------------------------
# SUITE 1: Rule Files Existence and Integrity
# -------------------------------------------------------------------------
Write-Host "`n--- Suite 1: Rule Files Existence and Integrity ---" -ForegroundColor Yellow

$RequiredRuleFiles = @(
    ".agents\rules\error-prevention.md",
    ".agents\rules\constraint-retention.md",
    ".agents\rules\sequential-thinking.md",
    ".agents\rules\unreal-analyzer-validation.md",
    ".agents\rules\no-interior.md",
    ".agents\rules\naming-conventions.md",
    ".agents\rules\ue5-coding-standards.md",
    ".agents\AGENTS.md"
)

foreach ($relPath in $RequiredRuleFiles) {
    $fullPath = Join-Path $ProjectRoot $relPath
    $exists = Test-Path $fullPath
    $size = 0
    if ($exists) {
        $size = (Get-Item $fullPath).Length
    }
    Assert-Test -TestName "Rule File Exists: $relPath" -Condition ($exists -and $size -gt 200) -FailureMessage "File missing or under 200 bytes (size: $size bytes)"
}

# -------------------------------------------------------------------------
# SUITE 2: Core Constraints and MVP Directives Specification
# -------------------------------------------------------------------------
Write-Host "`n--- Suite 2: Core Constraints and MVP Directives Specification ---" -ForegroundColor Yellow

$ConstraintFile = Join-Path $ProjectRoot ".agents\rules\constraint-retention.md"
$AgentsFile = Join-Path $ProjectRoot ".agents\AGENTS.md"

$ConstraintContent = if (Test-Path $ConstraintFile) { Get-Content $ConstraintFile -Raw -Encoding UTF8 } else { "" }
$AgentsContent = if (Test-Path $AgentsFile) { Get-Content $AgentsFile -Raw -Encoding UTF8 } else { "" }

$CoreConstraints = @(
    @{ Name = "C1: No Interior Spaces (Exterior-only)"; Pattern = "(?i)(no\s+interior|exterior-only)" },
    @{ Name = "C2: Solo BR Only (No Squad/Duo)"; Pattern = "(?i)solo(\s+br|\s+only)" },
    @{ Name = "C3: Server-Authoritative Architecture"; Pattern = "(?i)server-authoritative" },
    @{ Name = "C4: 3rd Person Camera Perspective Only"; Pattern = "(?i)3rd\s+person" },
    @{ Name = "C5: Exactly 3 Build Materials (Moloz, Tugla, Celik)"; Pattern = "(?i)(moloz.*tu.*elik|3\s+build\s+materials)" },
    @{ Name = "C6: Hybrid Hit Detection (HitScan AR + Projectile Rocket)"; Pattern = "(?i)(hybrid\s+hit\s+detection|hit-scan.*projectile)" },
    @{ Name = "C7: Mandatory BR Prefix"; Pattern = "(?i)(br\s+prefix|ABR|UBR)" }
)

foreach ($c in $CoreConstraints) {
    $cName = $c["Name"]
    $cPattern = $c["Pattern"]
    $inConstraintDoc = $ConstraintContent -match $cPattern
    $inAgentsDoc = $AgentsContent -match $cPattern
    Assert-Test -TestName "Constraint Specified: $cName" -Condition ($inConstraintDoc -and $inAgentsDoc) -FailureMessage "Constraint pattern '$cPattern' not matched in both constraint-retention.md and AGENTS.md"
}

$MvpDirectives = @(
    @{ Name = "MVP 1: 10-Bot Test Scenario"; Pattern = "(?i)10[\s-]bot" },
    @{ Name = "MVP 2: 2 Weapon Prototypes (AR + Rocket Launcher)"; Pattern = "(?i)(2\s+weapon\s+prototypes|assault\s+rifle.*rocket\s+launcher)" },
    @{ Name = "MVP 3: 2 Distinct GameModes (FFA + Classic BR)"; Pattern = "(?i)(free-for-all|ffa).*classic\s+br" },
    @{ Name = "MVP 4: Building Paused for Demo 1 (Natural Cover)"; Pattern = "(?i)(building.*paused|natural.*cover)" },
    @{ Name = "MVP 5: Exterior Vertical Navigation and Rooftop NavMesh"; Pattern = "(?i)(rooftop.*navmesh|exterior.*vertical)" }
)

foreach ($m in $MvpDirectives) {
    $mName = $m["Name"]
    $mPattern = $m["Pattern"]
    $inConstraintDoc = $ConstraintContent -match $mPattern
    $inAgentsDoc = $AgentsContent -match $mPattern
    Assert-Test -TestName "MVP Directive Specified: $mName" -Condition ($inConstraintDoc -and $inAgentsDoc) -FailureMessage "MVP pattern '$mPattern' not matched in both constraint-retention.md and AGENTS.md"
}

# -------------------------------------------------------------------------
# SUITE 3: Sequential Thinking Protocol Stages
# -------------------------------------------------------------------------
Write-Host "`n--- Suite 3: Sequential Thinking Protocol Stages ---" -ForegroundColor Yellow

$SeqFile = Join-Path $ProjectRoot ".agents\rules\sequential-thinking.md"
$SeqContent = if (Test-Path $SeqFile) { Get-Content $SeqFile -Raw -Encoding UTF8 } else { "" }

$SeqStages = @(
    "Stage 1",
    "Stage 2",
    "Stage 3",
    "Stage 4",
    "Stage 5"
)

foreach ($stage in $SeqStages) {
    $matched = $SeqContent -match "(?i)$stage"
    Assert-Test -TestName "Sequential Thinking Defines: $stage" -Condition $matched -FailureMessage "Stage '$stage' missing from sequential-thinking.md"
}

# -------------------------------------------------------------------------
# SUITE 4: Source Codebase Static AST and Header Hygiene
# -------------------------------------------------------------------------
Write-Host "`n--- Suite 4: Source Codebase Static AST and Header Hygiene ---" -ForegroundColor Yellow

$SourceDir = Join-Path $ProjectRoot "BakirkoyBR\Source\BakirkoyBR"
if (Test-Path $SourceDir) {
    $HeaderFiles = Get-ChildItem -Path $SourceDir -Recurse -Filter "*.h"
    $CppFiles = Get-ChildItem -Path $SourceDir -Recurse -Filter "*.cpp"

    Write-Host "  Found $($HeaderFiles.Count) header files and $($CppFiles.Count) source files in $SourceDir." -ForegroundColor DarkGray

    # Regex patterns
    $RawPointerRegex = '(?:^|[{;])\s*(?:UPROPERTY\(.*?\)\s*)?(?:[UAF][A-Z][a-zA-Z0-9_]*)\s*\*\s*([a-zA-Z0-9_]+)\s*(?:=\s*[^;]+)?\s*;'
    $StlRegex = '\bstd::(vector|string|map|unordered_map|set|shared_ptr|unique_ptr|wstring|array|deque|list|unordered_set)\b'
    $ForbiddenMaterialRegex = '\b(Wood|Stone|Metal|Gold|Ahsap|Ahşap|Demir|Beton)\b'
    $MaterialContextRegex = '(?i)(enum\s+class\s+\w*Material|struct\s+\w*Material|EBRMaterialType|EBRMaterial|BuildMaterial|BuildPiece)'
    $SquadLogicRegex = '\b(bIsDownButNotOut|ReviveTeammate|FSquadInfo|ASquadState|Squad|SquadId|Teammate|DBNO|DownButNotOut|Revive|Duo)\b'

    foreach ($header in $HeaderFiles) {
        $lines = Get-Content $header.FullName
        $content = $lines -join "`n"

        # Check 4.1: #pragma once
        $hasPragma = $lines | Where-Object { $_ -match '^\s*#pragma\s+once' }
        Assert-Test -TestName "Header Guard [#pragma once]: $($header.Name)" -Condition ($null -ne $hasPragma -and $hasPragma.Count -gt 0) -FailureMessage "Missing #pragma once"

        # Check 4.2: .generated.h strictly last include
        if ($content -match '\.generated\.h["\>]') {
            $includeLines = @()
            for ($i = 0; $i -lt $lines.Count; $i++) {
                if ($lines[$i] -match '^\s*#include\s+["<]([^">]+)[">]') {
                    $includeLines += [PSCustomObject]@{
                        LineNumber = $i + 1
                        IncludeFile = $matches[1]
                        Raw = $lines[$i]
                    }
                }
            }

            if ($includeLines.Count -gt 0) {
                $lastInclude = $includeLines[-1]
                $isLastGenerated = $lastInclude.IncludeFile -match '\.generated\.h$'
                Assert-Test -TestName "Generated Header Is Last Include: $($header.Name)" -Condition $isLastGenerated -FailureMessage "Last include is '$($lastInclude.IncludeFile)', expected .generated.h"
            }
        }

        # Check 4.3: Ban on std:: containers in headers
        $hasStl = $content -match $StlRegex
        Assert-Test -TestName "No Standard Library STL in Header: $($header.Name)" -Condition (-not $hasStl) -FailureMessage "Found forbidden std:: container usage in $($header.Name)"

        # Check 4.4: Rule C - No raw UObject member pointers (TObjectPtr enforced)
        $hasRawPointer = $false
        $rawPointerLine = ""
        foreach ($line in $lines) {
            if ($line -match $RawPointerRegex -and $line -notmatch 'TObjectPtr' -and $line -notmatch 'TWeakObjectPtr') {
                $hasRawPointer = $true
                $rawPointerLine = $line.Trim()
                break
            }
        }
        Assert-Test -TestName "No Raw UObject Pointer (TObjectPtr Enforced): $($header.Name)" -Condition (-not $hasRawPointer) -FailureMessage "Found raw UObject pointer member without TObjectPtr: '$rawPointerLine'"

        # Check 4.5: Rule E - ReplicatedUsing callback has UFUNCTION()
        $missingOnRepUFunction = $false
        $failedCallback = ""
        $repMatches = [regex]::Matches($content, 'ReplicatedUsing\s*=\s*([a-zA-Z0-9_]+)')
        foreach ($rm in $repMatches) {
            $callbackName = $rm.Groups[1].Value
            $onRepPattern = "UFUNCTION\s*\([^\)]*\)\s*(?:virtual\s+)?void\s+$callbackName"
            if ($content -notmatch $onRepPattern) {
                $missingOnRepUFunction = $true
                $failedCallback = $callbackName
                break
            }
        }
        Assert-Test -TestName "OnRep Callback Has UFUNCTION(): $($header.Name)" -Condition (-not $missingOnRepUFunction) -FailureMessage "ReplicatedUsing callback '$failedCallback' is missing UFUNCTION() macro"

        # Check 4.6: No forbidden materials like Wood, Stone, Metal, Gold, Ahsap, Ahşap
        $hasForbiddenMaterial = ($content -match $ForbiddenMaterialRegex) -and ($content -match $MaterialContextRegex)
        Assert-Test -TestName "No Forbidden 4th Material in Header: $($header.Name)" -Condition (-not $hasForbiddenMaterial) -FailureMessage "Forbidden building material detected in $($header.Name)"

        # Check 4.7: No forbidden Squad/Duo/DBNO constructs in headers
        $hasSquadLogic = $content -match $SquadLogicRegex
        Assert-Test -TestName "No Forbidden Squad/Duo/DBNO Logic in Header: $($header.Name)" -Condition (-not $hasSquadLogic) -FailureMessage "Forbidden squad/duo/DBNO construct detected in $($header.Name)"
    }

    foreach ($cpp in $CppFiles) {
        $lines = Get-Content $cpp.FullName
        $content = $lines -join "`n"

        # Check 4.8: Ban on std:: containers in source files (.cpp)
        $hasStl = $content -match $StlRegex
        Assert-Test -TestName "No Standard Library STL in Source: $($cpp.Name)" -Condition (-not $hasStl) -FailureMessage "Found forbidden std:: container usage in $($cpp.Name)"

        # Check 4.9: No forbidden materials in source files (.cpp)
        $hasForbiddenMaterial = ($content -match $ForbiddenMaterialRegex) -and ($content -match $MaterialContextRegex)
        Assert-Test -TestName "No Forbidden 4th Material in Source: $($cpp.Name)" -Condition (-not $hasForbiddenMaterial) -FailureMessage "Forbidden building material detected in $($cpp.Name)"

        # Check 4.10: No forbidden Squad/Duo/DBNO constructs in source files (.cpp)
        $hasSquadLogic = $content -match $SquadLogicRegex
        Assert-Test -TestName "No Forbidden Squad/Duo/DBNO Logic in Source: $($cpp.Name)" -Condition (-not $hasSquadLogic) -FailureMessage "Forbidden squad/duo/DBNO construct detected in $($cpp.Name)"
    }
} else {
    Write-Host "  [WARN] Source directory not found: $SourceDir" -ForegroundColor Yellow
}

# -------------------------------------------------------------------------
# SUITE 5: AST / Regex Validation Engine Self-Tests (Positive and Negative)
# -------------------------------------------------------------------------
Write-Host "`n--- Suite 5: AST / Regex Engine Self-Tests (Positive and Negative) ---" -ForegroundColor Yellow

function Test-AstSnippet {
    param([string]$CodeSnippet, [string]$FileType = ".h")

    $Violations = @()
    $lines = $CodeSnippet -split "`r?`n"

    # Rule A: #pragma once in header
    if ($FileType -eq ".h") {
        $hasPragma = $lines | Where-Object { $_ -match '^\s*#pragma\s+once' }
        if (-not $hasPragma) {
            $Violations += "ERR_MISSING_PRAGMA_ONCE"
        }
    }

    # Rule B: .generated.h strictly last
    if ($CodeSnippet -match '\.generated\.h["\>]') {
        $includeLines = @()
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match '^\s*#include\s+["<]([^">]+)[">]') {
                $includeLines += $matches[1]
            }
        }
        if ($includeLines.Count -gt 0 -and $includeLines[-1] -notmatch '\.generated\.h$') {
            $Violations += "ERR_GENERATED_HEADER_NOT_LAST"
        }
    }

    # Rule C: Raw pointer member inside class without TObjectPtr (including initialized pointers = nullptr;)
    foreach ($line in $lines) {
        if ($line -match '(?:^|[{;])\s*(?:UPROPERTY\(.*?\)\s*)?(?:[UAF][A-Z][a-zA-Z0-9_]*)\s*\*\s*([a-zA-Z0-9_]+)\s*(?:=\s*[^;]+)?\s*;' -and $line -notmatch 'TObjectPtr' -and $line -notmatch 'TWeakObjectPtr') {
            $Violations += "ERR_RAW_UOBJECT_POINTER"
            break
        }
    }

    # Rule D: STL usage
    if ($CodeSnippet -match '\bstd::(vector|string|map|unordered_map|set|shared_ptr|unique_ptr|wstring|array|deque|list|unordered_set)\b') {
        $Violations += "ERR_FORBIDDEN_STL_TYPE"
    }

    # Rule E: ReplicatedUsing callback without UFUNCTION()
    $repMatches = [regex]::Matches($CodeSnippet, 'ReplicatedUsing\s*=\s*([a-zA-Z0-9_]+)')
    foreach ($rm in $repMatches) {
        $callback = $rm.Groups[1].Value
        $pattern = "UFUNCTION\s*\([^\)]*\)\s*(?:virtual\s+)?void\s+$callback"
        if ($CodeSnippet -notmatch $pattern) {
            $Violations += "ERR_ONREP_WITHOUT_UFUNCTION"
            break
        }
    }

    # Rule F: Forbidden material in enum or struct
    if ($CodeSnippet -match '(?i)(enum\s+class\s+\w*Material|struct\s+\w*Material|EBRMaterialType|EBRMaterial|BuildMaterial|BuildPiece)' -and $CodeSnippet -match '\b(Wood|Stone|Metal|Gold|Ahsap|Ahşap|Demir|Beton)\b') {
        $Violations += "ERR_FORBIDDEN_MATERIAL"
    }

    # Rule G: Forbidden Squad / Duo / DBNO constructs
    if ($CodeSnippet -match '\b(bIsDownButNotOut|ReviveTeammate|FSquadInfo|ASquadState|Squad|SquadId|Teammate|DBNO|DownButNotOut|Revive|Duo)\b') {
        $Violations += "ERR_FORBIDDEN_SQUAD_LOGIC"
    }

    return $Violations
}

# Test 5.1 (Negative): Include order violation
$BadIncludeSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include "BRCharacter.generated.h"
#include "Weapons/BRWeaponBase.h"

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter {
    GENERATED_BODY()
};
"@
$v1 = Test-AstSnippet -CodeSnippet $BadIncludeSnippet
Assert-Test -TestName "Engine Catches: .generated.h Not Last" -Condition ($v1 -contains "ERR_GENERATED_HEADER_NOT_LAST") -FailureMessage "Failed to catch .generated.h include order violation"

# Test 5.2 (Negative): Raw pointer member violation
$BadPointerSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include "BRCharacter.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter {
    GENERATED_BODY()
private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* MeshComp;
};
"@
$v2 = Test-AstSnippet -CodeSnippet $BadPointerSnippet
Assert-Test -TestName "Engine Catches: Raw UObject* Pointer (Missing TObjectPtr)" -Condition ($v2 -contains "ERR_RAW_UOBJECT_POINTER") -FailureMessage "Failed to catch raw pointer member"

# Test 5.3 (Negative): STL container violation
$BadStlSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include <vector>
#include "BRCharacter.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter {
    GENERATED_BODY()
public:
    std::vector<int> Scores;
};
"@
$v3 = Test-AstSnippet -CodeSnippet $BadStlSnippet
Assert-Test -TestName "Engine Catches: Forbidden std::vector STL Type" -Condition ($v3 -contains "ERR_FORBIDDEN_STL_TYPE") -FailureMessage "Failed to catch STL container"

# Test 5.4 (Negative): OnRep callback lacking UFUNCTION()
$BadOnRepSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include "BRCharacter.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter {
    GENERATED_BODY()
protected:
    UPROPERTY(ReplicatedUsing = OnRep_Health)
    float CurrentHealth;

    void OnRep_Health();
};
"@
$v4 = Test-AstSnippet -CodeSnippet $BadOnRepSnippet
Assert-Test -TestName "Engine Catches: ReplicatedUsing OnRep Without UFUNCTION()" -Condition ($v4 -contains "ERR_ONREP_WITHOUT_UFUNCTION") -FailureMessage "Failed to catch missing UFUNCTION() on OnRep callback"

# Test 5.5 (Negative): Forbidden material
$BadMaterialSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include "BRTypes.generated.h"

UENUM(BlueprintType)
enum class EBRMaterialType : uint8 {
    Moloz,
    Tugla,
    Celik,
    Wood
};
"@
$v5 = Test-AstSnippet -CodeSnippet $BadMaterialSnippet
Assert-Test -TestName "Engine Catches: Forbidden Material (Wood)" -Condition ($v5 -contains "ERR_FORBIDDEN_MATERIAL") -FailureMessage "Failed to catch forbidden material Wood"

# Test 5.6 (Positive): Fully compliant UE5 pattern
$GoodSnippet = @"
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
class UStaticMeshComponent;
#include "BRCharacter.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter {
    GENERATED_BODY()

public:
    ABRCharacter();

protected:
    UPROPERTY(ReplicatedUsing = OnRep_Health, BlueprintReadOnly, Category = "Health")
    float CurrentHealth = 100.0f;

    UFUNCTION()
    virtual void OnRep_Health();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UStaticMeshComponent> CharacterMesh;
};
"@
$vGood = Test-AstSnippet -CodeSnippet $GoodSnippet
Assert-Test -TestName "Engine Passes: Fully Compliant UE5 Header" -Condition ($vGood.Count -eq 0) -FailureMessage "Compliant snippet had unexpected violations: $($vGood -join ', ')"

# Test 5.7 (Negative): Angle bracket .generated.h include order violation
$BadAngleIncludeSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include <BRCharacter.generated.h>
#include "Weapons/BRWeaponBase.h"

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter {
    GENERATED_BODY()
};
"@
$v7 = Test-AstSnippet -CodeSnippet $BadAngleIncludeSnippet
Assert-Test -TestName "Engine Catches: Angle Bracket .generated.h Not Last" -Condition ($v7 -contains "ERR_GENERATED_HEADER_NOT_LAST") -FailureMessage "Failed to catch angle bracket .generated.h include order violation"

# Test 5.8 (Negative): Initialized raw pointer member violation (= nullptr;)
$BadInitializedPointerSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include "BRCharacter.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter {
    GENERATED_BODY()
private:
    UPROPERTY(BlueprintReadOnly)
    AActor* Instigator = nullptr;
};
"@
$v8 = Test-AstSnippet -CodeSnippet $BadInitializedPointerSnippet
Assert-Test -TestName "Engine Catches: Initialized Raw Pointer (= nullptr;)" -Condition ($v8 -contains "ERR_RAW_UOBJECT_POINTER") -FailureMessage "Failed to catch initialized raw pointer member"

# Test 5.9 (Negative): Turkish forbidden material (Ahsap / Ahşap)
$BadTurkishMaterialSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include "BRTypes.generated.h"

UENUM(BlueprintType)
enum class EBRMaterialType : uint8 {
    Moloz,
    Tugla,
    Celik,
    Ahsap
};
"@
$v9 = Test-AstSnippet -CodeSnippet $BadTurkishMaterialSnippet
Assert-Test -TestName "Engine Catches: Turkish Forbidden Material (Ahsap)" -Condition ($v9 -contains "ERR_FORBIDDEN_MATERIAL") -FailureMessage "Failed to catch Turkish forbidden material Ahsap"

# Test 5.10 (Negative): Forbidden Squad/Duo/DBNO constructs
$BadSquadSnippet = @"
#pragma once
#include "CoreMinimal.h"
#include "BRCharacter.generated.h"

struct FSquadInfo {
    int32 SquadId;
};

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter {
    GENERATED_BODY()
public:
    bool bIsDownButNotOut;
    void ReviveTeammate(int32 PlayerId);
};
"@
$v10 = Test-AstSnippet -CodeSnippet $BadSquadSnippet
Assert-Test -TestName "Engine Catches: Forbidden Squad/Duo/DBNO Logic" -Condition ($v10 -contains "ERR_FORBIDDEN_SQUAD_LOGIC") -FailureMessage "Failed to catch squad/duo/DBNO constructs"


# -------------------------------------------------------------------------
# FINAL REPORT
# -------------------------------------------------------------------------
Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "Total Passed: $Global:TotalPassed" -ForegroundColor Green
Write-Host "Total Failed: $Global:TotalFailed" -ForegroundColor $(if ($Global:TotalFailed -eq 0) { "Green" } else { "Red" })
Write-Host "==================================================================" -ForegroundColor Cyan

if ($Global:TotalFailed -eq 0) {
    Write-Host "`n>>> ALL CHECKS PASSED [0 ERRORS] <<<" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n>>> VALIDATION FAILED WITH $Global:TotalFailed ERROR(S) <<<" -ForegroundColor Red
    exit 1
}
