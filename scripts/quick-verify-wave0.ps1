Param(
    [string]$BackendBaseUrl = "http://localhost:8000",
    [string]$FrontendUrl = "http://localhost:3000"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Step([string]$Name, [ScriptBlock]$Action) {
    Write-Host "==> $Name"
    try {
        & $Action
        Write-Host ("`u2713 {0}" -f $Name) -ForegroundColor Green
    } catch {
        Write-Host ("`u2717 {0} - {1}" -f $Name, $_.Exception.Message) -ForegroundColor Red
        exit 1
    }
}

function Get-Url([string]$Url, [string]$Method = 'GET', [string]$Body = $null, [string]$ContentType = 'application/json') {
    if ($Method -eq 'GET') {
        Invoke-WebRequest -UseBasicParsing -Uri $Url -Method GET | Out-Null
    } elseif ($Method -eq 'PATCH') {
        Invoke-WebRequest -UseBasicParsing -Uri $Url -Method PATCH -Body $Body -ContentType $ContentType | Out-Null
    } else {
        Invoke-WebRequest -UseBasicParsing -Uri $Url -Method $Method -Body $Body -ContentType $ContentType | Out-Null
    }
}

Invoke-Step "Subir serviços Docker" {
    docker-compose up -d | Out-Null
}

Invoke-Step "Aplicar migrações Alembic" {
    docker exec prospecai-backend alembic upgrade head | Out-Null
}

Invoke-Step "Health do backend (/health/ready)" {
    Get-Url "$BackendBaseUrl/health/ready"
}

Invoke-Step "Métricas Prometheus (/metrics)" {
    Get-Url "$BackendBaseUrl/metrics"
}

Invoke-Step "i18n: listar locales" {
    Get-Url "$BackendBaseUrl/i18n/locales"
}

Invoke-Step "i18n: obter traduções en-US" {
    Get-Url "$BackendBaseUrl/i18n/translations/en-US"
}

Invoke-Step "Model Configs: listar Ingestao" {
    Get-Url "$BackendBaseUrl/system/model-configs/Ingestao"
}

Invoke-Step "Model Configs: PATCH campo 'fonte'" {
    $body = '{"label_key":"fields.source","validators":{"required":true}}'
    Get-Url "$BackendBaseUrl/system/model-configs/Ingestao/fonte" 'PATCH' $body 'application/json'
}

Invoke-Step "ACL: check permitido (admin/update model_configs)" {
    Get-Url "$BackendBaseUrl/system/acl/check?role=admin&resource=system.model_configs&action=update"
}

Invoke-Step "ACL: check negado (viewer/update model_configs)" {
    Get-Url "$BackendBaseUrl/system/acl/check?role=viewer&resource=system.model_configs&action=update"
}

Write-Host "\nAll Wave 0 quick validations passed." -ForegroundColor Green
Write-Host "Frontend (manual): $FrontendUrl"