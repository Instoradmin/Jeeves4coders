#!/bin/sh

# Engineering Automation Agent - Frontend Docker Entrypoint
# Uses runtime configuration injection technique for React environment variables

set -e

# Function to generate runtime environment configuration
generate_runtime_config() {
    echo "🔧 Generating runtime configuration..."

    # Create environment configuration as JSON
    cat > /usr/share/nginx/html/env-config.js << EOF
window._env_ = {
  REACT_APP_API_BASE_URL: "${REACT_APP_API_BASE_URL:-http://localhost:8000/api}",
  REACT_APP_WEBSOCKET_URL: "${REACT_APP_WEBSOCKET_URL:-ws://localhost:8000/ws}",
  REACT_APP_GOOGLE_CLIENT_ID: "${REACT_APP_GOOGLE_CLIENT_ID:-}",
  REACT_APP_GITHUB_CLIENT_ID: "${REACT_APP_GITHUB_CLIENT_ID:-}",
  REACT_APP_ENVIRONMENT: "${REACT_APP_ENVIRONMENT:-development}",
  REACT_APP_VERSION: "${REACT_APP_VERSION:-1.0.0}",
  REACT_APP_ADMIN_EMAIL: "${REACT_APP_ADMIN_EMAIL:-admin@example.com}",
  REACT_APP_ENABLE_AI_INSIGHTS: "${REACT_APP_ENABLE_AI_INSIGHTS:-true}",
  REACT_APP_ENABLE_REAL_TIME: "${REACT_APP_ENABLE_REAL_TIME:-true}",
  REACT_APP_ENABLE_EXPORT: "${REACT_APP_ENABLE_EXPORT:-true}",
  REACT_APP_THEME_MODE: "${REACT_APP_THEME_MODE:-light}",
  REACT_APP_PRIMARY_COLOR: "${REACT_APP_PRIMARY_COLOR:-#1976d2}",
  REACT_APP_SECONDARY_COLOR: "${REACT_APP_SECONDARY_COLOR:-#dc004e}",
  REACT_APP_REFRESH_INTERVAL: "${REACT_APP_REFRESH_INTERVAL:-30000}",
  REACT_APP_CACHE_DURATION: "${REACT_APP_CACHE_DURATION:-300000}",
  REACT_APP_API_TIMEOUT: "${REACT_APP_API_TIMEOUT:-30000}",
  REACT_APP_MAX_RETRIES: "${REACT_APP_MAX_RETRIES:-3}",
  REACT_APP_JIRA_BASE_URL: "${REACT_APP_JIRA_BASE_URL:-https://instor.atlassian.net}",
  REACT_APP_JIRA_PROJECT_KEY: "${REACT_APP_JIRA_PROJECT_KEY:-J4C}",
  REACT_APP_GITHUB_ORG: "${REACT_APP_GITHUB_ORG:-Instoradmin}",
  REACT_APP_GITHUB_REPO: "${REACT_APP_GITHUB_REPO:-Jeeves4coders}",
  REACT_APP_COMPANY_NAME: "${REACT_APP_COMPANY_NAME:-Aurigraph}",
  REACT_APP_APP_NAME: "${REACT_APP_APP_NAME:-Engineering Automation Agent}",
  REACT_APP_SUPPORT_EMAIL: "${REACT_APP_SUPPORT_EMAIL:-support@aurigraph.io}",
  REACT_APP_BUILD_DATE: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
};
EOF

    echo "✅ Runtime configuration generated"
}

# Function to inject configuration into index.html
inject_config_into_html() {
    echo "📝 Injecting configuration into HTML..."

    # Check if index.html exists
    if [ ! -f "/usr/share/nginx/html/index.html" ]; then
        echo "❌ Error: index.html not found"
        exit 1
    fi

    # Create a temporary file with the script injection
    cat > /tmp/config-script.html << 'EOF'
    <script src="/env-config.js"></script>
EOF

    # Inject the script tag before the closing </head> tag
    sed -i '/<\/head>/i\    <script src="/env-config.js"></script>' /usr/share/nginx/html/index.html

    echo "✅ Configuration injected into HTML"
}

# Function to create nginx configuration for serving config file
setup_nginx_config() {
    echo "🌐 Setting up Nginx configuration for config file..."

    # Ensure the config file is served with correct MIME type
    cat >> /etc/nginx/conf.d/default.conf << 'EOF'

# Serve environment configuration
location /env-config.js {
    add_header Content-Type application/javascript;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    add_header Pragma "no-cache";
    add_header Expires "0";
}
EOF

    echo "✅ Nginx configuration updated"
}

# Function to validate the setup
validate_setup() {
    echo "🔍 Validating setup..."

    # Check if config file was created
    if [ ! -f "/usr/share/nginx/html/env-config.js" ]; then
        echo "❌ Error: env-config.js not created"
        exit 1
    fi

    # Check if index.html was modified
    if ! grep -q "env-config.js" /usr/share/nginx/html/index.html; then
        echo "❌ Error: Configuration not injected into index.html"
        exit 1
    fi

    # Check if static assets exist
    if [ ! -d "/usr/share/nginx/html/static" ]; then
        echo "❌ Warning: static assets directory not found"
    fi

    echo "✅ Setup validation passed"
}

# Function to set proper permissions
set_permissions() {
    echo "🔐 Setting file permissions..."

    # Ensure nginx can read all files
    find /usr/share/nginx/html -type f -exec chmod 644 {} \;
    find /usr/share/nginx/html -type d -exec chmod 755 {} \;

    # Make config file readable
    chmod 644 /usr/share/nginx/html/env-config.js

    echo "✅ Permissions set successfully"
}

# Function to display configuration summary
display_config_summary() {
    echo "📋 Configuration Summary:"
    echo "========================"
    echo "API Base URL: ${REACT_APP_API_BASE_URL:-http://localhost:8000/api}"
    echo "WebSocket URL: ${REACT_APP_WEBSOCKET_URL:-ws://localhost:8000/ws}"
    echo "Environment: ${REACT_APP_ENVIRONMENT:-development}"
    echo "Admin Email: ${REACT_APP_ADMIN_EMAIL:-admin@example.com}"
    echo "Google Client ID: ${REACT_APP_GOOGLE_CLIENT_ID:-[Not Set]}"
    echo "GitHub Client ID: ${REACT_APP_GITHUB_CLIENT_ID:-[Not Set]}"
    echo "========================"
}

# Main execution function
main() {
    echo "🚀 Starting Engineering Automation Agent Frontend..."
    echo "=================================================="

    # Display current configuration
    display_config_summary

    # Run setup steps
    generate_runtime_config
    inject_config_into_html
    validate_setup
    set_permissions

    echo "🎉 Frontend configuration completed successfully!"
    echo "Starting Nginx server..."

    # Execute the main command (nginx)
    exec "$@"
}

# Run main function with all arguments
main "$@"
