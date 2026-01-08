#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Wave 2 Quick Validation Script - Verify all migrations, seeds, and API endpoints

.DESCRIPTION
    Complete validation suite for Wave 2 implementation. Tests:
    - Database migrations
    - Seed data integrity
    - API endpoint responses
    - Frontend availability

.NOTES
    Prerequisites:
    - Docker containers running (docker-compose up -d)
    - Backend migrations applied (alembic upgrade head)
    - Seed data loaded (python scripts/seed_wave2_data.py)
#>

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Test-HttpEndpoint {
    param(
        [string]$Url,
        [string]$Description,
        [int]$ExpectedCount = 0
    )
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -ErrorAction Stop
        if ($response -is [Array]) {
            $count = $response.Count
        } elseif ($response -is [Object] -and $response.PSObject.Properties['items']) {
            $count = $response.items.Count
        } else {
            $count = 1
        }
        
        if ($ExpectedCount -gt 0 -and $count -ge $ExpectedCount) {
            Write-Success "$Description (found: $count)"
            return $true
        } elseif ($ExpectedCount -eq 0) {
            Write-Success "$Description (status: 200)"
            return $true
        } else {
            Write-Error "$Description (expected ≥$ExpectedCount, got $count)"
            return $false
        }
    } catch {
        Write-Error "$Description - $_"
        return $false
    }
}

# Main validation suite
Write-Header "Wave 2 Validation Suite - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

$baseUrl = "http://localhost:8000"
$results = @()

# 1. Check service health
Write-Host ""
Write-Host "Checking Service Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health/ready" -ErrorAction Stop
    Write-Success "Backend is healthy"
    $results += $true
} catch {
    Write-Error "Backend health check failed - $_"
    $results += $false
}

# 2. Test Funding Sources endpoints
Write-Host ""
Write-Host "Testing Funding Sources..." -ForegroundColor Yellow
$results += (Test-HttpEndpoint -Url "$baseUrl/funding-sources" -Description "GET /funding-sources" -ExpectedCount 5)

# 3. Test Clients endpoints
Write-Host ""
Write-Host "Testing Clients..." -ForegroundColor Yellow
$results += (Test-HttpEndpoint -Url "$baseUrl/clients" -Description "GET /clients" -ExpectedCount 10)

# 4. Test Portfolio endpoints
Write-Host ""
Write-Host "Testing Portfolio..." -ForegroundColor Yellow
$results += (Test-HttpEndpoint -Url "$baseUrl/portfolio/institutes" -Description "GET /portfolio/institutes" -ExpectedCount 3)
$results += (Test-HttpEndpoint -Url "$baseUrl/portfolio/projects" -Description "GET /portfolio/projects" -ExpectedCount 5)

# 5. Test Opportunities endpoints
Write-Host ""
Write-Host "Testing Opportunities..." -ForegroundColor Yellow
$results += (Test-HttpEndpoint -Url "$baseUrl/opportunities" -Description "GET /opportunities" -ExpectedCount 20)

# 6. Test i18n endpoints
Write-Host ""
Write-Host "Testing i18n..." -ForegroundColor Yellow
$results += (Test-HttpEndpoint -Url "$baseUrl/i18n/locales" -Description "GET /i18n/locales")
$results += (Test-HttpEndpoint -Url "$baseUrl/i18n/translations/pt-BR" -Description "GET /i18n/translations/pt-BR")
$results += (Test-HttpEndpoint -Url "$baseUrl/i18n/translations/en-US" -Description "GET /i18n/translations/en-US")

# 7. Test Frontend availability
Write-Host ""
Write-Host "Testing Frontend..." -ForegroundColor Yellow
try {
    $frontendHealth = Invoke-WebRequest -Uri "http://localhost:3000" -ErrorAction Stop
    if ($frontendHealth.StatusCode -eq 200) {
        Write-Success "Frontend is available (http://localhost:3000)"
        $results += $true
    }
} catch {
    Write-Error "Frontend not available - $_"
    $results += $false
}

# 8. Test frontend pages
$pages = @(
    "http://localhost:3000/wave2/funding-sources",
    "http://localhost:3000/wave2/clients",
    "http://localhost:3000/wave2/portfolio",
    "http://localhost:3000/wave2/pipeline"
)

Write-Host ""
Write-Host "Testing Frontend Pages..." -ForegroundColor Yellow
foreach ($page in $pages) {
    try {
        $response = Invoke-WebRequest -Uri $page -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "Page accessible: $page"
            $results += $true
        }
    } catch {
        Write-Error "Page not accessible: $page"
        $results += $false
    }
}

# Summary
Write-Header "Validation Summary"
$passed = ($results | Where-Object { $_ -eq $true }).Count
$total = $results.Count
$percentage = if ($total -gt 0) { [Math]::Round(($passed / $total) * 100) } else { 0 }

Write-Host ""
Write-Host "Results: $passed / $total tests passed ($percentage%)" -ForegroundColor $(if ($percentage -eq 100) { 'Green' } else { 'Yellow' })

if ($percentage -eq 100) {
    Write-Host ""
    Write-Success "All Wave 2 validations passed! ✨"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Review WAVE2_SUMMARY.md for implementation details"
    Write-Host "2. Run seed script if not already done: python scripts/seed_wave2_data.py"
    Write-Host "3. Access UI at http://localhost:3000/wave2/*"
    Write-Host "4. Review API docs at http://localhost:8000/docs"
    Write-Host ""
} else {
    Write-Host ""
    Write-Error "Some validations failed. Please check errors above."
    Write-Host ""
}

exit if ($percentage -eq 100) { 0 } else { 1 }
