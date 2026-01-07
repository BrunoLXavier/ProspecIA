# ProspecIA - Health Check Script
# Verifies all services are running correctly

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "ProspecIA - Health Check" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="Backend API"; URL="http://localhost:8000/health"; Expected=200},
    @{Name="Frontend"; URL="http://localhost:3000"; Expected=200},
    @{Name="Postgres"; URL="http://localhost:5432"; Expected=-1; SkipHttp=$true},
    @{Name="Neo4j Browser"; URL="http://localhost:7474"; Expected=200},
    @{Name="Keycloak"; URL="http://localhost:8080"; Expected=200},
    @{Name="MinIO Console"; URL="http://localhost:9001"; Expected=200},
    @{Name="MLflow"; URL="http://localhost:5000"; Expected=200},
    @{Name="Prometheus"; URL="http://localhost:9090"; Expected=200},
    @{Name="Grafana"; URL="http://localhost:3001"; Expected=200},
    @{Name="Loki"; URL="http://localhost:3100/ready"; Expected=200}
)

$allHealthy = $true

foreach ($service in $services) {
    Write-Host "Checking $($service.Name)... " -NoNewline
    
    if ($service.SkipHttp) {
        Write-Host "[SKIPPED]" -ForegroundColor Yellow
        continue
    }
    
    try {
        $response = Invoke-WebRequest -Uri $service.URL -Method Get -TimeoutSec 5 -ErrorAction Stop
        
        if ($response.StatusCode -eq $service.Expected) {
            Write-Host "[OK]" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] Status: $($response.StatusCode)" -ForegroundColor Red
            $allHealthy = $false
        }
    }
    catch {
        Write-Host "[FAIL] $_" -ForegroundColor Red
        $allHealthy = $false
    }
    
    Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "All services are healthy!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some services are unhealthy. Check docker-compose logs." -ForegroundColor Red
    exit 1
}
