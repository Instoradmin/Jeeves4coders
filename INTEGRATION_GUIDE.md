# 🔗 Jeeves4coders Integration Guide

**How to include Jeeves4coders as an independent dependency in any project**

## 📋 Overview

Jeeves4coders is designed as a reusable, independent automation agent that can be integrated into any development project. This guide shows you how to include it as a dependency and leverage its capabilities across different projects.

## 🚀 Quick Integration

### **Option 1: PyPI Installation (Recommended)**

```bash
# Install from PyPI (when available)
pip install jeeves4coders

# Or install from GitHub
pip install git+https://github.com/Instoradmin/Jeeves4coders.git
```

### **Option 2: Git Submodule**

```bash
# Add as git submodule
git submodule add https://github.com/Instoradmin/Jeeves4coders.git tools/jeeves4coders

# Initialize and update
git submodule init
git submodule update
```

### **Option 3: Direct Clone**

```bash
# Clone into your project
cd your-project/tools
git clone https://github.com/Instoradmin/Jeeves4coders.git jeeves4coders
```

## ⚙️ Project Setup

### **1. Initialize Jeeves4coders in Your Project**

```bash
# Navigate to your project root
cd /path/to/your/project

# Initialize Jeeves4coders
jeeves4coders init

# Or with a specific template
jeeves4coders init --template python_web
```

### **2. Configure for Your Project**

Create a `.jeeves4coders.json` configuration file:

```json
{
  "project_name": "my-awesome-project",
  "project_root": ".",
  "project_type": "python",
  
  "test_enabled": true,
  "test_types": ["unit", "functional", "regression"],
  "test_coverage_threshold": 80.0,
  
  "code_review_enabled": true,
  "code_quality_threshold": 8.0,
  
  "github_enabled": true,
  "github_repo": "my-org/my-repo",
  "github_owner": "my-org",
  
  "jira_enabled": true,
  "jira_project_key": "PROJ",
  
  "confluence_enabled": true,
  "confluence_space_key": "SPACE"
}
```

### **3. Set Environment Variables**

```bash
# GitHub Integration
export GITHUB_TOKEN="your-github-token"

# JIRA Integration
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-jira-token"

# Confluence Integration
export CONFLUENCE_BASE_URL="https://your-company.atlassian.net/wiki"
export CONFLUENCE_EMAIL="your-email@company.com"
export CONFLUENCE_API_TOKEN="your-confluence-token"
```

## 🔄 Integration Patterns

### **Pattern 1: CI/CD Pipeline Integration**

#### **GitHub Actions Example:**

```yaml
# .github/workflows/jeeves4coders.yml
name: Jeeves4coders Automation
on: [push, pull_request]

jobs:
  automation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install Jeeves4coders
        run: pip install git+https://github.com/Instoradmin/Jeeves4coders.git
      
      - name: Run Code Quality Analysis
        run: jeeves4coders workflow code_quality
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
          CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: jeeves4coders-results
          path: jeeves4coders_results.json
```

#### **Jenkins Pipeline Example:**

```groovy
pipeline {
    agent any
    
    environment {
        GITHUB_TOKEN = credentials('github-token')
        JIRA_API_TOKEN = credentials('jira-token')
        CONFLUENCE_API_TOKEN = credentials('confluence-token')
    }
    
    stages {
        stage('Setup Jeeves4coders') {
            steps {
                sh 'pip install git+https://github.com/Instoradmin/Jeeves4coders.git'
            }
        }
        
        stage('Run Automation') {
            steps {
                sh 'jeeves4coders workflow full_analysis'
            }
        }
        
        stage('Publish Results') {
            steps {
                archiveArtifacts artifacts: 'jeeves4coders_results.json'
            }
        }
    }
}
```

### **Pattern 2: Pre-commit Hook Integration**

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Running Jeeves4coders code review..."
jeeves4coders run code_review

if [ $? -ne 0 ]; then
    echo "❌ Code review failed. Please fix issues before committing."
    exit 1
fi

echo "✅ Code review passed!"
```

### **Pattern 3: Make/NPM Script Integration**

#### **Makefile Example:**

```makefile
# Makefile
.PHONY: setup test quality deploy

setup:
	pip install git+https://github.com/Instoradmin/Jeeves4coders.git
	jeeves4coders init

test:
	jeeves4coders run test_suite

quality:
	jeeves4coders workflow code_quality

deploy:
	jeeves4coders workflow deployment
```

#### **package.json Example:**

```json
{
  "scripts": {
    "setup": "pip install git+https://github.com/Instoradmin/Jeeves4coders.git && jeeves4coders init",
    "test": "jeeves4coders run test_suite",
    "quality": "jeeves4coders workflow code_quality",
    "deploy": "jeeves4coders workflow deployment"
  }
}
```

### **Pattern 4: Docker Integration**

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install Jeeves4coders
RUN pip install git+https://github.com/Instoradmin/Jeeves4coders.git

# Copy project files
COPY . /app
WORKDIR /app

# Initialize Jeeves4coders
RUN jeeves4coders init

# Run automation on container start
CMD ["jeeves4coders", "workflow", "full_analysis"]
```

## 🏗️ Project Templates

### **Python Web Application**

```bash
jeeves4coders init --template python_web
```

**Includes:**
- Flask/Django configuration
- Unit and functional testing setup
- Code quality standards for web apps
- Database migration testing
- Security vulnerability scanning

### **Python API Service**

```bash
jeeves4coders init --template python_api
```

**Includes:**
- REST API testing framework
- Performance testing setup
- API documentation generation
- Security testing for APIs
- Load testing configuration

### **JavaScript Web Application**

```bash
jeeves4coders init --template javascript_web
```

**Includes:**
- React/Vue/Angular testing setup
- ESLint and Prettier configuration
- End-to-end testing with Cypress
- Bundle size analysis
- Accessibility testing

### **Java Spring Application**

```bash
jeeves4coders init --template java_spring
```

**Includes:**
- Spring Boot testing configuration
- Maven/Gradle integration
- JUnit and Mockito setup
- Code coverage with JaCoCo
- Security testing with OWASP

## 🔧 Customization

### **Custom Workflows**

Create custom workflows for your specific needs:

```python
# custom_workflow.py
from jeeves4coders import EngineeringAutomationAgent, AgentConfig

def custom_deployment_workflow():
    config = AgentConfig.load_from_file('.jeeves4coders.json')
    agent = EngineeringAutomationAgent(config)
    
    # Custom workflow sequence
    workflow = [
        'code_review',
        'test_suite',
        'security_scan',  # Custom module
        'performance_test',  # Custom module
        'github',
        'jira',
        'confluence'
    ]
    
    results = agent.execute_workflow(workflow)
    return results

if __name__ == "__main__":
    custom_deployment_workflow()
```

### **Custom Modules**

Extend Jeeves4coders with custom modules:

```python
# custom_security_module.py
from jeeves4coders.core_agent import AgentModule

class SecurityScanModule(AgentModule):
    def validate_config(self):
        return self.config.security_enabled
    
    def execute(self, context):
        # Custom security scanning logic
        return {
            "status": "success",
            "vulnerabilities_found": 0,
            "scan_duration": 30.5
        }

# Register with agent
agent.register_module('security_scan', SecurityScanModule(config, logger))
```

## 📊 Monitoring and Reporting

### **Results Collection**

```python
# collect_results.py
from jeeves4coders import quick_start

def collect_automation_results():
    agent = quick_start(".", "my-project")
    
    # Run automation
    results = agent.execute_workflow(['code_quality'])
    
    # Save results
    agent.save_results('automation_results.json')
    
    # Get summary
    summary = agent.get_execution_summary()
    print(f"Success rate: {summary['success_rate']:.1f}%")
    
    return summary
```

### **Dashboard Integration**

```bash
# Send results to monitoring dashboard
jeeves4coders workflow full_analysis --output-format json | \
  curl -X POST -H "Content-Type: application/json" \
       -d @- https://your-dashboard.com/api/automation-results
```

## 🔄 Version Management

### **Pinning Versions**

```bash
# Pin to specific version
pip install git+https://github.com/Instoradmin/Jeeves4coders.git@v1.0.0

# Or in requirements.txt
git+https://github.com/Instoradmin/Jeeves4coders.git@v1.0.0
```

### **Upgrading**

```bash
# Upgrade to latest version
pip install --upgrade git+https://github.com/Instoradmin/Jeeves4coders.git

# Check version
jeeves4coders version
```

## 🚀 Best Practices

### **1. Configuration Management**
- Store configuration in version control
- Use environment variables for sensitive data
- Create project-specific templates
- Document configuration changes

### **2. CI/CD Integration**
- Run Jeeves4coders on every commit
- Fail builds on quality issues
- Archive automation results
- Monitor success rates over time

### **3. Team Adoption**
- Start with basic workflows
- Gradually add more modules
- Train team on usage
- Collect feedback and iterate

### **4. Maintenance**
- Regular updates to latest version
- Monitor for new features
- Review and update configurations
- Clean up old results and logs

## 🆘 Troubleshooting

### **Common Issues**

**Installation Problems:**
```bash
# Clear pip cache
pip cache purge

# Install with verbose output
pip install -v git+https://github.com/Instoradmin/Jeeves4coders.git
```

**Configuration Issues:**
```bash
# Validate configuration
jeeves4coders config show

# Reset configuration
rm .jeeves4coders.json
jeeves4coders init
```

**Permission Issues:**
```bash
# Check API tokens
jeeves4coders run github --validate-only
jeeves4coders run jira --validate-only
```

### **Getting Help**

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check README and examples
- **Community**: Join discussions and get help

---

**Ready to integrate Jeeves4coders into your project? Start automating today!** 🤖✨
