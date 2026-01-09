# Script para rebuild completo do frontend ProspecIA
# Execute este script para reconstruir o container sem cache

Write-Host "=== Rebuild Frontend ProspecIA ===" -ForegroundColor Cyan
Write-Host ""

# Parar o container
Write-Host "1. Parando container frontend..." -ForegroundColor Yellow
docker-compose stop frontend

# Remover o container
Write-Host "2. Removendo container frontend..." -ForegroundColor Yellow
docker-compose rm -f frontend

# Remover a imagem antiga
Write-Host "3. Removendo imagem antiga..." -ForegroundColor Yellow
docker rmi prospecai-frontend -f 2>$null

# Rebuild sem cache
Write-Host "4. Rebuilding frontend (sem cache)..." -ForegroundColor Yellow
docker-compose build --no-cache frontend

# Iniciar o container
Write-Host "5. Iniciando container frontend..." -ForegroundColor Yellow
docker-compose up -d frontend

# Aguardar alguns segundos
Write-Host "6. Aguardando inicialização..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Mostrar logs
Write-Host "7. Logs do container:" -ForegroundColor Yellow
docker-compose logs frontend --tail 50

Write-Host ""
Write-Host "=== Rebuild concluído ===" -ForegroundColor Green
Write-Host "Acesse http://localhost:3000 para ver as alterações" -ForegroundColor Green
