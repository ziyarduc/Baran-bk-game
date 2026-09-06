<#
.SYNOPSIS
    BakirkoyBR Checkpoint & Resume Manager
.DESCRIPTION
    Saves and restores project state to prevent loss during rate limits or interruptions.
#>

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("Save", "Resume", "Status")]
    [string]$Action = "Status",

    [string]$Milestone = "Current",
    [string]$Task = "Current",
    [string]$Details = ""
)

$CheckpointPath = Join-Path $PSScriptRoot "..\.agents\CHECKPOINT.json"
$AgentsPath = Join-Path $PSScriptRoot "..\.agents"

function Save-Checkpoint {
    param([string]$m, [string]$t, [string]$d)
    
    $data = @{
        TimestampUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        ActiveMilestone = $m
        ActiveTask = $t
        RecoveryDetails = $d
        GitStatus = (git status --porcelain 2>&1 | Out-String)
    }

    $json = $data | ConvertTo-Json -Depth 5
    Set-Content -Path $CheckpointPath -Value $json -Encoding utf8
    Write-Host "[CHECKPOINT] State successfully saved to $CheckpointPath" -ForegroundColor Green
}

function Resume-Checkpoint {
    if (-not (Test-Path $CheckpointPath)) {
        Write-Warning "[CHECKPOINT] No checkpoint file found at $CheckpointPath."
        return
    }

    $raw = Get-Content -Path $CheckpointPath -Raw -Encoding utf8
    $data = $raw | ConvertFrom-Json
    
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "RESUMING FROM CHECKPOINT" -ForegroundColor Cyan
    Write-Host "Timestamp (UTC) : $($data.TimestampUtc)"
    Write-Host "Milestone       : $($data.ActiveMilestone)"
    Write-Host "Active Task     : $($data.ActiveTask)"
    Write-Host "Recovery Details: $($data.RecoveryDetails)"
    Write-Host "==========================================" -ForegroundColor Cyan

    # Integrity verification
    $verifyScript = Join-Path $PSScriptRoot "verify-rules.ps1"
    if (Test-Path $verifyScript) {
        Write-Host "[INTEGRITY] Running rule validation on modified files..." -ForegroundColor Yellow
        & $verifyScript
    }
}

function Show-Status {
    if (Test-Path $CheckpointPath) {
        Get-Content -Path $CheckpointPath -Raw | Write-Output
    } else {
        Write-Host "No active checkpoint found. Initializing baseline..."
        Save-Checkpoint -m "M1-M3" -t "Gate-Verification-Remediation" -d "Initial gate remediation underway"
    }
}

switch ($Action) {
    "Save"   { Save-Checkpoint -m $Milestone -t $Task -d $Details }
    "Resume" { Resume-Checkpoint }
    "Status" { Show-Status }
}
