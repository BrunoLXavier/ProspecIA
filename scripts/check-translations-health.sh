#!/bin/bash
# Health Check Script for Admin Translations Feature
# Run this after `docker-compose up -d` to verify everything is working

echo "🔍 ProspecIA Admin Translations - Health Check"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
API_TOKEN="Bearer test-token" # In real scenario, get JWT from Keycloak

# Counter
PASSED=0
FAILED=0

# Test 1: Backend Health
echo "📡 Test 1: Backend Health"
if curl -s "$BACKEND_URL/health/ready" | grep -q "ok"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 2: Frontend Status
echo "🌐 Test 2: Frontend Status"
if curl -s "$FRONTEND_URL" | grep -q "ProspecIA"; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Frontend not accessible${NC}"
    ((FAILED++))
fi
echo ""

# Test 3: Translations API Endpoint
echo "🔗 Test 3: Translations API Endpoint"
TRANS_RESPONSE=$(curl -s "$BACKEND_URL/system/translations")
if echo "$TRANS_RESPONSE" | grep -q "namespace"; then
    echo -e "${GREEN}✓ GET /system/translations works${NC}"
    TRANS_COUNT=$(echo "$TRANS_RESPONSE" | grep -o '"key"' | wc -l)
    echo "  Found $TRANS_COUNT translation keys"
    ((PASSED++))
else
    echo -e "${RED}✗ GET /system/translations failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 4: Admin Page Accessible
echo "🏠 Test 4: Admin Translations Page"
ADMIN_RESPONSE=$(curl -s "$FRONTEND_URL/admin/translations")
if echo "$ADMIN_RESPONSE" | grep -q "translations"; then
    echo -e "${GREEN}✓ Admin page is accessible${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Admin page not accessible${NC}"
    ((FAILED++))
fi
echo ""

# Test 5: Database Check
echo "💾 Test 5: PostgreSQL Connection"
DB_CHECK=$(docker exec prospecai-postgres psql -U prospecai_user -d prospecai -c "SELECT COUNT(*) FROM model_field_configurations;" 2>/dev/null | tail -1)
if [[ ! -z "$DB_CHECK" ]]; then
    echo -e "${GREEN}✓ PostgreSQL is accessible${NC}"
    echo "  Records in model_field_configurations: $DB_CHECK"
    ((PASSED++))
else
    echo -e "${RED}✗ PostgreSQL connection failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 6: Keycloak Status
echo "🔐 Test 6: Keycloak Status"
if curl -s "http://localhost:8080/realms/ProspecAI/.well-known/openid-configuration" | grep -q "issuer"; then
    echo -e "${GREEN}✓ Keycloak is running${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ Keycloak not responding (check if running)${NC}"
    ((FAILED++))
fi
echo ""

# Test 7: Translation Keys Check
echo "📋 Test 7: Translation Keys Verification"
EXPECTED_KEYS=("common:button.save" "admin:button.add_key" "admin:title")
SUCCESS=true
for key in "${EXPECTED_KEYS[@]}"; do
    KEY_ONLY="${key#*:}"
    if echo "$TRANS_RESPONSE" | grep -q "\"key\":\"$KEY_ONLY\""; then
        echo -e "${GREEN}  ✓ Found key: $key${NC}"
    else
        echo -e "${RED}  ✗ Missing key: $key${NC}"
        SUCCESS=false
    fi
done
if [ "$SUCCESS" = true ]; then
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

# Test 8: Docker Containers
echo "🐳 Test 8: Docker Containers Status"
echo "Checking main containers:"
containers=("prospecai-backend" "prospecai-frontend" "prospecai-postgres" "prospecai-keycloak")
all_running=true
for container in "${containers[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo -e "${GREEN}  ✓ $container is running${NC}"
    else
        echo -e "${RED}  ✗ $container is NOT running${NC}"
        all_running=false
    fi
done
if [ "$all_running" = true ]; then
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

# Summary
echo "=============================================="
echo "📊 Summary"
echo "=============================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Admin Translations is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:3000/admin/translations"
    echo "2. Try creating a new translation key"
    echo "3. Edit and delete translations"
    echo "4. Export translations to JSON"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. See details above.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Ensure docker-compose is running: docker-compose ps"
    echo "2. Check backend logs: docker logs prospecai-backend --tail=50"
    echo "3. Check frontend logs: docker logs prospecai-frontend --tail=50"
    echo "4. Verify port availability: netstat -tuln | grep -E '3000|8000'"
    exit 1
fi
