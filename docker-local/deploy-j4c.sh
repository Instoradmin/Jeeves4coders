#!/bin/bash

# J4C (Jeeves4coders) Local Docker Deployment Script
# Deploys the complete J4C Analytics Dashboard locally using Docker

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="J4C Analytics Dashboard"
COMPOSE_FILE="docker-compose.j4c.yml"
ENV_FILE=".env.j4c"

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

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    J4C Analytics Dashboard                   ║"
    echo "║              Local Docker Deployment Script                  ║"
    echo "║                                                              ║"
    echo "║  🚀 Engineering Automation Agent for Jeeves4coders          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check available disk space (minimum 2GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 2097152 ]; then  # 2GB in KB
        log_warning "Low disk space detected. At least 2GB recommended."
    fi
    
    log_success "Prerequisites check passed"
}

create_environment_file() {
    log_info "Creating environment configuration..."
    
    cat > $ENV_FILE << EOF
# J4C Analytics Dashboard - Local Environment Configuration
# Generated on $(date)

# ============================================================================
# GOOGLE SERVICES (Optional - for AI and OAuth)
# ============================================================================
J4C_GOOGLE_CLIENT_ID=
J4C_GOOGLE_CLIENT_SECRET=
J4C_GOOGLE_AI_API_KEY=

# ============================================================================
# GITHUB INTEGRATION (Optional)
# ============================================================================
J4C_GITHUB_CLIENT_ID=
J4C_GITHUB_CLIENT_SECRET=
J4C_GITHUB_TOKEN=

# ============================================================================
# JIRA INTEGRATION
# ============================================================================
J4C_JIRA_API_TOKEN=ATATT3xFfGF02M-uwYL27Q-lc-OdO8bb5WSSEFk8QPFOMo_tTdWQZ_qjDX6HhFMYdd2Nh8CN7e1adhBZbg3ERZMq_IJV8KP3fEW5u8G2K4dxGaLevRfNUnVprTFSJGYY03ex2Rr3X_H2yb5ax-0JYGGOfbjiPXJ5tT9EtfgpdhbgFq45k9HgL9g=D139BE86

# ============================================================================
# DEVELOPMENT SETTINGS
# ============================================================================
J4C_DEBUG=true
J4C_LOG_LEVEL=info
J4C_ENVIRONMENT=development

EOF
    
    log_success "Environment file created: $ENV_FILE"
    log_warning "Please update $ENV_FILE with your actual API keys and tokens"
}

setup_directories() {
    log_info "Setting up required directories..."
    
    # Create necessary directories
    mkdir -p database/backups
    mkdir -p nginx/ssl
    mkdir -p logs
    mkdir -p data
    
    # Create SSL certificates for development (self-signed)
    if [ ! -f "nginx/ssl/j4c.crt" ]; then
        log_info "Generating self-signed SSL certificates for development..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/j4c.key \
            -out nginx/ssl/j4c.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=j4c.local" \
            2>/dev/null || log_warning "OpenSSL not available, skipping SSL setup"
    fi
    
    log_success "Directories and certificates set up"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build images using Docker Compose
    if command -v docker-compose &> /dev/null; then
        docker-compose -f $COMPOSE_FILE build --no-cache
    else
        docker compose -f $COMPOSE_FILE build --no-cache
    fi
    
    log_success "Docker images built successfully"
}

start_services() {
    log_info "Starting J4C services..."
    
    # Start services in the correct order
    if command -v docker-compose &> /dev/null; then
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
    else
        docker compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
    fi
    
    log_success "J4C services started"
}

wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for database
    log_info "Waiting for database..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker exec j4c-database pg_isready -U j4c_user -d j4c_analytics &>/dev/null; then
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Database failed to start within 60 seconds"
        return 1
    fi
    
    # Wait for backend
    log_info "Waiting for backend API..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8001/health &>/dev/null; then
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Backend API failed to start within 60 seconds"
        return 1
    fi
    
    # Wait for frontend
    log_info "Waiting for frontend..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:3001/health &>/dev/null; then
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Frontend failed to start within 60 seconds"
        return 1
    fi
    
    log_success "All services are ready!"
}

run_health_checks() {
    log_info "Running health checks..."
    
    # Check database
    if docker exec j4c-database pg_isready -U j4c_user -d j4c_analytics &>/dev/null; then
        log_success "✅ Database is healthy"
    else
        log_error "❌ Database health check failed"
    fi
    
    # Check Redis
    if docker exec j4c-redis redis-cli -a j4c_redis_2024 ping &>/dev/null; then
        log_success "✅ Redis is healthy"
    else
        log_error "❌ Redis health check failed"
    fi
    
    # Check backend API
    if curl -f http://localhost:8001/health &>/dev/null; then
        log_success "✅ Backend API is healthy"
    else
        log_error "❌ Backend API health check failed"
    fi
    
    # Check frontend
    if curl -f http://localhost:3001/health &>/dev/null; then
        log_success "✅ Frontend is healthy"
    else
        log_error "❌ Frontend health check failed"
    fi
    
    # Check Nginx proxy
    if curl -f http://localhost:8080/health &>/dev/null; then
        log_success "✅ Nginx proxy is healthy"
    else
        log_error "❌ Nginx proxy health check failed"
    fi
}

display_service_info() {
    log_header "🎉 J4C Analytics Dashboard is now running!"
    echo ""
    echo "📋 Service Information:"
    echo "======================="
    echo "🌐 Main Dashboard:     http://localhost:8080"
    echo "🔗 Direct Frontend:    http://localhost:3001"
    echo "📡 Backend API:        http://localhost:8001"
    echo "📚 API Documentation:  http://localhost:8001/docs"
    echo "🗄️  Database Admin:     http://localhost:8082"
    echo "🔴 Redis Commander:    http://localhost:8083"
    echo ""
    echo "🔐 Default Admin Login:"
    echo "======================="
    echo "Email: subbu@aurigraph.io"
    echo "Note: Admin user will be created on first login"
    echo ""
    echo "🛠️  Management Commands:"
    echo "========================"
    echo "View logs:     docker-compose -f $COMPOSE_FILE logs -f"
    echo "Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "Restart:       docker-compose -f $COMPOSE_FILE restart"
    echo "Clean up:      docker-compose -f $COMPOSE_FILE down -v"
    echo ""
    echo "📊 Database Connection:"
    echo "======================"
    echo "Host: localhost"
    echo "Port: 5433"
    echo "Database: j4c_analytics"
    echo "Username: j4c_user"
    echo "Password: j4c_secure_password_2024"
    echo ""
    echo "🎯 Next Steps:"
    echo "=============="
    echo "1. Open http://localhost:8080 in your browser"
    echo "2. Register or login with Google/GitHub OAuth"
    echo "3. Explore the analytics dashboard"
    echo "4. Check JIRA integration in the dashboard"
    echo "5. Generate AI insights (if Google AI API key is configured)"
    echo ""
}

cleanup_on_error() {
    log_error "Deployment failed. Cleaning up..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
    else
        docker compose -f $COMPOSE_FILE down 2>/dev/null || true
    fi
}

# Main deployment function
main() {
    print_banner
    
    # Set up error handling
    trap cleanup_on_error ERR
    
    log_header "Starting J4C Analytics Dashboard deployment..."
    echo ""
    
    check_prerequisites
    create_environment_file
    setup_directories
    build_images
    start_services
    wait_for_services
    run_health_checks
    display_service_info
    
    log_success "🚀 J4C Analytics Dashboard deployed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    "stop")
        log_info "Stopping J4C services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f $COMPOSE_FILE down
        else
            docker compose -f $COMPOSE_FILE down
        fi
        log_success "J4C services stopped"
        ;;
    "restart")
        log_info "Restarting J4C services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f $COMPOSE_FILE restart
        else
            docker compose -f $COMPOSE_FILE restart
        fi
        log_success "J4C services restarted"
        ;;
    "logs")
        if command -v docker-compose &> /dev/null; then
            docker-compose -f $COMPOSE_FILE logs -f
        else
            docker compose -f $COMPOSE_FILE logs -f
        fi
        ;;
    "clean")
        log_warning "This will remove all J4C containers and volumes. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if command -v docker-compose &> /dev/null; then
                docker-compose -f $COMPOSE_FILE down -v --remove-orphans
            else
                docker compose -f $COMPOSE_FILE down -v --remove-orphans
            fi
            log_success "J4C environment cleaned up"
        fi
        ;;
    "status")
        if command -v docker-compose &> /dev/null; then
            docker-compose -f $COMPOSE_FILE ps
        else
            docker compose -f $COMPOSE_FILE ps
        fi
        ;;
    *)
        main
        ;;
esac
