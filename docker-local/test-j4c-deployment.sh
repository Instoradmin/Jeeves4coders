#!/bin/bash

# J4C Analytics Dashboard - Deployment Test Script
# Validates that all services are running correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
COMPOSE_FILE="docker-compose.j4c.yml"
BACKEND_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:3001"
NGINX_URL="http://localhost:8080"
DB_ADMIN_URL="http://localhost:8082"
REDIS_ADMIN_URL="http://localhost:8083"

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "🧪 Testing $test_name... "
    
    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

test_docker_services() {
    log_info "Testing Docker services..."
    
    # Test if containers are running
    run_test "Database container" "docker ps | grep j4c-database | grep -q Up"
    run_test "Redis container" "docker ps | grep j4c-redis | grep -q Up"
    run_test "Backend container" "docker ps | grep j4c-backend | grep -q Up"
    run_test "Frontend container" "docker ps | grep j4c-frontend | grep -q Up"
    run_test "Nginx container" "docker ps | grep j4c-nginx | grep -q Up"
    run_test "Adminer container" "docker ps | grep j4c-adminer | grep -q Up"
    run_test "Redis Commander container" "docker ps | grep j4c-redis-commander | grep -q Up"
}

test_database_connectivity() {
    log_info "Testing database connectivity..."
    
    # Test PostgreSQL connection
    run_test "Database connection" "docker exec j4c-database pg_isready -U j4c_user -d j4c_analytics"
    
    # Test if tables exist
    run_test "Database tables" "docker exec j4c-database psql -U j4c_user -d j4c_analytics -c 'SELECT COUNT(*) FROM users;'"
    
    # Test if admin user exists
    run_test "Admin user exists" "docker exec j4c-database psql -U j4c_user -d j4c_analytics -c \"SELECT email FROM users WHERE email='subbu@aurigraph.io'\" | grep -q subbu"
    
    # Test if J4C project exists
    run_test "J4C project exists" "docker exec j4c-database psql -U j4c_user -d j4c_analytics -c \"SELECT project_key FROM projects WHERE project_key='J4C'\" | grep -q J4C"
}

test_redis_connectivity() {
    log_info "Testing Redis connectivity..."
    
    # Test Redis connection
    run_test "Redis connection" "docker exec j4c-redis redis-cli -a j4c_redis_2024 ping | grep -q PONG"
    
    # Test Redis write/read
    run_test "Redis write/read" "docker exec j4c-redis redis-cli -a j4c_redis_2024 set test_key test_value && docker exec j4c-redis redis-cli -a j4c_redis_2024 get test_key | grep -q test_value"
}

test_backend_api() {
    log_info "Testing backend API..."
    
    # Test health endpoint
    run_test "Backend health" "curl -f $BACKEND_URL/health"
    
    # Test API documentation
    run_test "API documentation" "curl -f $BACKEND_URL/docs"
    
    # Test database connection via API
    run_test "API database connection" "curl -f $BACKEND_URL/api/status"
    
    # Test CORS headers
    run_test "CORS headers" "curl -I $BACKEND_URL/health | grep -q 'Access-Control-Allow-Origin'"
}

test_frontend() {
    log_info "Testing frontend..."
    
    # Test frontend health
    run_test "Frontend health" "curl -f $FRONTEND_URL/health"
    
    # Test if React app loads
    run_test "React app loads" "curl -f $FRONTEND_URL/ | grep -q 'J4C Analytics'"
    
    # Test static assets
    run_test "Static assets" "curl -f $FRONTEND_URL/static/js/ || curl -f $FRONTEND_URL/env-config.js"
}

test_nginx_proxy() {
    log_info "Testing Nginx proxy..."
    
    # Test Nginx health
    run_test "Nginx health" "curl -f $NGINX_URL/health"
    
    # Test proxy to frontend
    run_test "Proxy to frontend" "curl -f $NGINX_URL/"
    
    # Test proxy to backend API
    run_test "Proxy to backend API" "curl -f $NGINX_URL/api/health"
    
    # Test security headers
    run_test "Security headers" "curl -I $NGINX_URL/ | grep -q 'X-Frame-Options'"
}

test_admin_interfaces() {
    log_info "Testing admin interfaces..."
    
    # Test Adminer (database admin)
    run_test "Adminer interface" "curl -f $DB_ADMIN_URL"
    
    # Test Redis Commander
    run_test "Redis Commander interface" "curl -f $REDIS_ADMIN_URL"
}

test_data_integrity() {
    log_info "Testing data integrity..."
    
    # Test if sample data exists
    run_test "Sample users exist" "docker exec j4c-database psql -U j4c_user -d j4c_analytics -c 'SELECT COUNT(*) FROM users;' | grep -E '[1-9][0-9]*'"
    
    # Test if roles are configured
    run_test "Roles configured" "docker exec j4c-database psql -U j4c_user -d j4c_analytics -c 'SELECT COUNT(*) FROM roles;' | grep -q '4'"
    
    # Test if sample metrics exist
    run_test "Sample metrics exist" "docker exec j4c-database psql -U j4c_user -d j4c_analytics -c 'SELECT COUNT(*) FROM code_metrics;' | grep -E '[1-9][0-9]*'"
    
    # Test if J4C configuration exists
    run_test "J4C configuration" "docker exec j4c-database psql -U j4c_user -d j4c_analytics -c 'SELECT COUNT(*) FROM j4c_config;' | grep -E '[1-9][0-9]*'"
}

test_performance() {
    log_info "Testing performance..."
    
    # Test API response time (should be under 2 seconds)
    run_test "API response time" "timeout 2 curl -f $BACKEND_URL/health"
    
    # Test frontend load time (should be under 3 seconds)
    run_test "Frontend load time" "timeout 3 curl -f $FRONTEND_URL/"
    
    # Test database query performance
    run_test "Database query performance" "timeout 5 docker exec j4c-database psql -U j4c_user -d j4c_analytics -c 'SELECT COUNT(*) FROM users JOIN roles ON users.role_id = roles.id;'"
}

test_security() {
    log_info "Testing security..."
    
    # Test that sensitive endpoints require authentication
    run_test "API authentication required" "! curl -f $BACKEND_URL/api/users"
    
    # Test HTTPS redirect (if configured)
    run_test "Security headers present" "curl -I $NGINX_URL/ | grep -q 'X-Content-Type-Options'"
    
    # Test that database is not directly accessible
    run_test "Database not directly accessible" "! nc -z localhost 5432"
}

display_test_summary() {
    echo ""
    echo "📊 TEST SUMMARY"
    echo "==============="
    echo "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
    echo -e "Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "🎉 All tests passed! J4C deployment is healthy."
        echo ""
        echo "🚀 Ready to use:"
        echo "• Dashboard: $NGINX_URL"
        echo "• API: $BACKEND_URL"
        echo "• Admin: subbu@aurigraph.io"
        return 0
    else
        log_error "❌ Some tests failed. Please check the deployment."
        echo ""
        echo "🔧 Troubleshooting:"
        echo "• Check logs: docker-compose -f $COMPOSE_FILE logs"
        echo "• Restart: ./deploy-j4c.sh restart"
        echo "• Clean deploy: ./deploy-j4c.sh clean && ./deploy-j4c.sh"
        return 1
    fi
}

# Main test execution
main() {
    echo "🧪 J4C Analytics Dashboard - Deployment Test Suite"
    echo "=================================================="
    echo ""
    
    # Check if services are running
    if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_error "J4C services are not running. Please run ./deploy-j4c.sh first."
        exit 1
    fi
    
    # Run all test suites
    test_docker_services
    test_database_connectivity
    test_redis_connectivity
    test_backend_api
    test_frontend
    test_nginx_proxy
    test_admin_interfaces
    test_data_integrity
    test_performance
    test_security
    
    # Display results
    display_test_summary
}

# Handle command line arguments
case "${1:-}" in
    "quick")
        log_info "Running quick health checks..."
        test_docker_services
        test_backend_api
        test_frontend
        display_test_summary
        ;;
    "db")
        log_info "Running database tests..."
        test_database_connectivity
        test_data_integrity
        display_test_summary
        ;;
    "api")
        log_info "Running API tests..."
        test_backend_api
        display_test_summary
        ;;
    "frontend")
        log_info "Running frontend tests..."
        test_frontend
        display_test_summary
        ;;
    *)
        main
        ;;
esac
