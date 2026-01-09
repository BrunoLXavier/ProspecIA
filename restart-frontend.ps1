# Script para reiniciar o frontend ProspecIA (com rebuild rápido)
# Execute este script para rebuild com cache (mais rápido)

Write-Host "=== Restart Frontend ProspecIA ===" -ForegroundColor Cyan
Write-Host ""

# Parar e remover container
Write-Host "1. Parando e removendo container..." -ForegroundColor Yellow
docker-compose stop frontend
docker-compose rm -f frontend

# Rebuild com cache
Write-Host "2. Rebuilding frontend (com cache)..." -ForegroundColor Yellow
docker-compose build frontend

# Iniciar
Write-Host "3. Iniciando container..." -ForegroundColor Yellow
docker-compose up -d frontend

# Aguardar
Write-Host "4. Aguardando inicialização..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Mostrar status
Write-Host "5. Status:" -ForegroundColor Yellow
docker-compose ps frontend

Write-Host ""
Write-Host "=== Restart concluído ===" -ForegroundColor Green
Write-Host "Acesse http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Para ver logs em tempo real execute:" -ForegroundColor Cyan
Write-Host "docker-compose logs -f frontend" -ForegroundColor White
