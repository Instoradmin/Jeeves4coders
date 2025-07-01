#!/bin/bash
# Engineering Automation Agent Installation Script
# Installs the agent and sets up the environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AGENT_NAME="engineering-automation-agent"
INSTALL_DIR="${HOME}/.engineering_agent"
VENV_DIR="${INSTALL_DIR}/venv"
CONFIG_DIR="${HOME}/.engineering_agent"

echo -e "${BLUE}🤖 Engineering Automation Agent Installer${NC}"
echo "=================================================="

# Check Python version
echo -e "${YELLOW}📋 Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo -e "${RED}❌ Python 3.8 or higher is required. Found: ${python_version}${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python version: ${python_version}${NC}"

# Create installation directory
echo -e "${YELLOW}📁 Creating installation directory...${NC}"
mkdir -p "${INSTALL_DIR}"
mkdir -p "${CONFIG_DIR}"

# Create virtual environment
echo -e "${YELLOW}🐍 Creating virtual environment...${NC}"
python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

# Upgrade pip
echo -e "${YELLOW}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install the agent
echo -e "${YELLOW}🔧 Installing Engineering Automation Agent...${NC}"

# Check if we're in the source directory
if [ -f "setup.py" ]; then
    echo -e "${BLUE}📍 Installing from source directory...${NC}"
    pip install -e .
else
    echo -e "${BLUE}📍 Installing from current directory...${NC}"
    # Copy source files to installation directory
    cp -r . "${INSTALL_DIR}/source"
    cd "${INSTALL_DIR}/source"
    pip install -e .
fi

# Install dependencies
echo -e "${YELLOW}📚 Installing dependencies...${NC}"
pip install -r requirements.txt

# Create CLI wrapper script
echo -e "${YELLOW}🔗 Creating CLI wrapper...${NC}"
cat > "${INSTALL_DIR}/engineering-agent" << EOF
#!/bin/bash
# Engineering Automation Agent CLI Wrapper
source "${VENV_DIR}/bin/activate"
python -m engineering_automation_agent.cli "\$@"
EOF

chmod +x "${INSTALL_DIR}/engineering-agent"

# Add to PATH
echo -e "${YELLOW}🛤️  Setting up PATH...${NC}"
shell_rc=""
if [ -n "$BASH_VERSION" ]; then
    shell_rc="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    shell_rc="$HOME/.zshrc"
else
    shell_rc="$HOME/.profile"
fi

# Check if PATH is already set
if ! grep -q "${INSTALL_DIR}" "${shell_rc}" 2>/dev/null; then
    echo "" >> "${shell_rc}"
    echo "# Engineering Automation Agent" >> "${shell_rc}"
    echo "export PATH=\"${INSTALL_DIR}:\$PATH\"" >> "${shell_rc}"
    echo -e "${GREEN}✅ Added to PATH in ${shell_rc}${NC}"
else
    echo -e "${BLUE}📍 PATH already configured${NC}"
fi

# Create default configuration
echo -e "${YELLOW}⚙️  Creating default configuration...${NC}"
cat > "${CONFIG_DIR}/global_config.json" << EOF
{
  "version": "1.0.0",
  "default_settings": {
    "test_timeout": 300,
    "test_coverage_threshold": 80.0,
    "code_quality_threshold": 8.0,
    "notifications_enabled": true,
    "auto_deploy_on_success": false
  },
  "integrations": {
    "github": {
      "enabled": true,
      "api_base": "https://api.github.com"
    },
    "jira": {
      "enabled": true,
      "api_version": "3"
    },
    "confluence": {
      "enabled": true,
      "api_version": "latest"
    }
  }
}
EOF

# Create example project configuration
cat > "${CONFIG_DIR}/example_project.json" << EOF
{
  "project_name": "example-project",
  "project_root": ".",
  "project_type": "python",
  "test_enabled": true,
  "test_types": ["unit", "functional", "regression"],
  "code_review_enabled": true,
  "github_enabled": false,
  "jira_enabled": false,
  "confluence_enabled": false
}
EOF

# Test installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"
if "${INSTALL_DIR}/engineering-agent" version > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Installation test passed${NC}"
else
    echo -e "${RED}❌ Installation test failed${NC}"
    exit 1
fi

# Installation complete
echo ""
echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
echo "=================================================="
echo -e "${BLUE}📍 Installation directory: ${INSTALL_DIR}${NC}"
echo -e "${BLUE}⚙️  Configuration directory: ${CONFIG_DIR}${NC}"
echo ""
echo -e "${YELLOW}🚀 Getting Started:${NC}"
echo "1. Restart your shell or run: source ${shell_rc}"
echo "2. Navigate to your project directory"
echo "3. Run: engineering-agent init"
echo "4. Run: engineering-agent workflow full_analysis"
echo ""
echo -e "${YELLOW}📚 Available Commands:${NC}"
echo "• engineering-agent init          - Initialize agent for current project"
echo "• engineering-agent workflow      - Run predefined workflows"
echo "• engineering-agent run           - Run specific modules"
echo "• engineering-agent config        - Manage configurations"
echo "• engineering-agent version       - Show version information"
echo ""
echo -e "${YELLOW}📖 Documentation:${NC}"
echo "• Configuration: ${CONFIG_DIR}/global_config.json"
echo "• Example config: ${CONFIG_DIR}/example_project.json"
echo "• Logs: ${INSTALL_DIR}/engineering_agent.log"
echo ""
echo -e "${GREEN}Happy automating! 🤖${NC}"
