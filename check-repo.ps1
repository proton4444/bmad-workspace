# BMAD Workspace Repository Check Script
# Monitors git status, BMAD version, and upstream alignment

Write-Host "`n====================================="
Write-Host "BMAD Workspace Repository Check"
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Git Status
Write-Host "[1] GIT STATUS" -ForegroundColor Yellow
Write-Host "---------------"
$gitStatus = git status --short
if ($gitStatus) {
    Write-Host $gitStatus
} else {
    Write-Host "[OK] Clean working directory" -ForegroundColor Green
}
Write-Host ""

# 2. Current Branch and Remote
Write-Host "[2] BRANCH AND REMOTE" -ForegroundColor Yellow
Write-Host "----------------------"
$branch = git rev-parse --abbrev-ref HEAD
$commit = git log -1 --pretty=format:%H
$message = git log -1 --pretty=format:%s
Write-Host "Branch: $branch"
Write-Host "Latest Commit: $($commit.Substring(0,7))"
Write-Host "Message: $message"
Write-Host ""

# 3. Check if behind origin
Write-Host "[3] UPSTREAM TRACKING" -ForegroundColor Yellow
Write-Host "---------------------"
git fetch origin --quiet 2>$null
$ahead = (git rev-list --count "origin/master..HEAD").Trim()
$behind = (git rev-list --count "HEAD..origin/master").Trim()

if ($ahead -eq "0" -and $behind -eq "0") {
    Write-Host "Status: [OK] Up to date with origin/master" -ForegroundColor Green
} else {
    if ($ahead -ne "0") { Write-Host "[WARN] Ahead of origin by $ahead commit(s)" -ForegroundColor Yellow }
    if ($behind -ne "0") { Write-Host "[WARN] Behind origin by $behind commit(s)" -ForegroundColor Yellow }
}
Write-Host ""

# 4. BMAD Version Check
Write-Host "[4] BMAD VERSION" -ForegroundColor Yellow
Write-Host "-----------------"
if (Test-Path ".bmad\_cfg\manifest.yaml") {
    $bmadVersion = (Select-String -Path ".bmad\_cfg\manifest.yaml" -Pattern "version:" | Select-Object -First 1).ToString() -replace ".*version:\s+", ""
    Write-Host "Local BMAD version: $bmadVersion"

    # Check upstream
    git fetch upstream --quiet 2>$null
    $upstreamTag = git describe --tags upstream/main --abbrev=0 2>$null
    if ($upstreamTag) {
        Write-Host "Latest BMAD tag: $upstreamTag"
        if ($bmadVersion.Trim() -eq $upstreamTag.Trim()) {
            Write-Host "Status: [OK] Synchronized" -ForegroundColor Green
        } else {
            Write-Host "Status: [WARN] Version mismatch" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[ERROR] BMAD not installed locally" -ForegroundColor Red
}
Write-Host ""

# 5. Project Status
Write-Host "[5] PROJECT STATUS" -ForegroundColor Yellow
Write-Host "-------------------"
if (Test-Path "projects\multi-agent-mvp") {
    $fileCount = (git ls-files "projects/multi-agent-mvp" | Measure-Object -Line).Lines
    Write-Host "multi-agent-mvp: $fileCount files tracked" -ForegroundColor Green
} else {
    Write-Host "[ERROR] multi-agent-mvp directory not found" -ForegroundColor Red
}
Write-Host ""

# 6. Pre-commit Hooks
Write-Host "[6] GIT HOOKS" -ForegroundColor Yellow
Write-Host "--------------"
if (Test-Path ".git\hooks\pre-commit") {
    Write-Host "[OK] Pre-commit hook installed" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Pre-commit hook missing (run: bash setup-hooks.sh)" -ForegroundColor Red
}
Write-Host ""

# 7. Untracked Files Warning
Write-Host "[7] UNTRACKED FILES" -ForegroundColor Yellow
Write-Host "--------------------"
$untracked = (git ls-files --others --exclude-standard | Measure-Object -Line).Lines
if ($untracked -eq 0) {
    Write-Host "[OK] No untracked files" -ForegroundColor Green
} else {
    Write-Host "[WARN] $untracked untracked file(s)" -ForegroundColor Yellow
}
Write-Host ""

# 8. BMAD Method Initialization Check
Write-Host "[8] BMAD METHOD INITIALIZATION" -ForegroundColor Yellow
Write-Host "-------------------------------"
if (Test-Path ".bmad") {
    if ((Test-Path ".bmad\.installed") -or (Test-Path ".bmad\_cfg")) {
        $workflowStatus = $false
        $agentStatus = $false

        # Check for workflow status tracking
        if (Test-Path ".bmad/workflow-status.yaml") {
            Write-Host "[OK] Workflow status tracking initialized" -ForegroundColor Green
            $workflowStatus = $true
        } else {
            Write-Host "[WARN] Workflow status tracking not initialized" -ForegroundColor Yellow
        }

        # Check for agents directory
        if (Test-Path ".bmad/agents") {
            $agentCount = (Get-ChildItem ".bmad/agents" -Recurse -Filter "*.md" | Measure-Object).Count
            if ($agentCount -gt 0) {
                $countMsg = "[OK] BMAD agents initialized (" + $agentCount + " found)"
                Write-Host $countMsg -ForegroundColor Green
                $agentStatus = $true
            } else {
                Write-Host "[WARN] BMAD agents directory exists but is empty" -ForegroundColor Yellow
            }
        } else {
            Write-Host "[WARN] BMAD agents directory not found" -ForegroundColor Yellow
        }

        if ($workflowStatus -and $agentStatus) {
            Write-Host "Status: [OK] BMAD Method fully initialized" -ForegroundColor Green
        } else {
            Write-Host "Status: [WARN] BMAD Method partially initialized - run setup when starting work" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[ERROR] BMAD framework not properly initialized" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] BMAD directory not found" -ForegroundColor Red
}
Write-Host ""

# 9. Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "SUMMARY"
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Repository: bmad-workspace"
Write-Host "Location: $(Get-Location)"
Write-Host "Status: Ready for development" -ForegroundColor Green
Write-Host ""
