# Jeeves4coders - Your Intelligent Coding Assistant

[![npm version](https://badge.fury.io/js/jeeves4coders.svg)](https://badge.fury.io/js/jeeves4coders)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Jeeves4coders - Your intelligent coding assistant for comprehensive automation** - Now available as an NPM package with VS Code extension for seamless integration into JavaScript/Node.js projects!

## 🚀 Quick Start

### Installation

```bash
# Install as a development dependency
npm install --save-dev jeeves4coders

# Or install globally
npm install -g jeeves4coders
```

### Initialize for Your Project

```bash
# Initialize Jeeves4coders for your project
npx jeeves4coders init

# Run code quality checks
npm run jeeves:lint

# Run full analysis
npm run jeeves:audit
```

## 📋 Features

- **🔍 Code Review**: Automated code quality analysis and review
- **🧪 Test Suite**: Comprehensive testing and coverage analysis  
- **🔗 GitHub Integration**: Repository management and CI/CD integration
- **📊 Jira Integration**: Project tracking and issue management
- **📚 Confluence Integration**: Documentation and knowledge management
- **🔄 Build Integration**: Automatic execution during build processes
- **📈 Reporting**: Detailed reports and analytics

## 🛠️ Usage

### Command Line Interface

```bash
# Initialize agent
npx engineering-agent init [options]

# Run workflows
npx engineering-agent workflow <name>
npx engineering-agent workflow code_quality
npx engineering-agent workflow full_analysis

# Run individual modules
npx engineering-agent run <module>
npx engineering-agent run code_review
npx engineering-agent run test_suite

# Configuration management
npx engineering-agent config create --project myproject --root ./
npx engineering-agent config show

# Status and version
npx engineering-agent status
npx engineering-agent version
```

### NPM Scripts Integration

After installation, the following scripts are automatically added to your `package.json`:

```json
{
  "scripts": {
    "lint:engineering": "engineering-agent workflow code_quality",
    "audit:engineering": "engineering-agent workflow full_analysis", 
    "test:engineering": "engineering-agent run test_suite"
  }
}
```

### Programmatic Usage

```javascript
const { EngineeringAutomationAgent, runWorkflow } = require('engineering-automation-agent');

// Create agent instance
const agent = new EngineeringAutomationAgent({
  projectRoot: process.cwd(),
  silent: false
});

// Initialize agent
await agent.init({
  project: 'my-project',
  template: 'react'
});

// Run workflows
await agent.runWorkflow('code_quality');
await agent.runModule('test_suite');

// Quick workflow execution
await runWorkflow('full_analysis', {
  projectRoot: './my-project',
  output: './reports/analysis.json'
});
```

## 🔄 Available Workflows

| Workflow | Modules | Description |
|----------|---------|-------------|
| `code_quality` | code_review | Code quality assessment only |
| `full_analysis` | code_review → test_suite | Complete code and test analysis |
| `deployment` | test_suite → github → jira | Deployment workflow with validation |
| `reporting` | test_suite → confluence | Testing and documentation |
| `ci_cd` | code_review → test_suite → github | Continuous integration workflow |

## 🔧 Build System Integration

### Automatic Build Hooks

The agent automatically integrates with your build process:

```json
{
  "scripts": {
    "prebuild": "engineering-agent workflow code_quality || true",
    "build": "your-build-command",
    "postbuild": "engineering-agent workflow reporting || true",
    "pretest": "engineering-agent run code_review || true"
  }
}
```

### Webpack Integration

```javascript
// webpack.config.js
const EngineeringAutomationPlugin = require('./engineering-automation-webpack-plugin');

module.exports = {
  plugins: [
    new EngineeringAutomationPlugin({
      prebuild: { workflow: 'code_quality' },
      postbuild: { workflow: 'reporting' },
      failOnError: false
    })
  ]
};
```

### Vite Integration

```javascript
// vite.config.js
import { engineeringAutomationPlugin } from './engineering-automation-vite-plugin.js';

export default {
  plugins: [
    engineeringAutomationPlugin({
      prebuild: { workflow: 'code_quality' },
      failOnError: false
    })
  ]
};
```

## ⚙️ Configuration

### Project Configuration (`.engineering-agent.json`)

```json
{
  "version": "1.0.0",
  "project_name": "my-project",
  "project_root": ".",
  "auto_run_on_build": true,
  "default_workflow": "code_quality",
  "modules": {
    "code_review": { "enabled": true },
    "test_suite": { "enabled": true },
    "github": { "enabled": false },
    "jira": { "enabled": false },
    "confluence": { "enabled": false }
  }
}
```

### Build Hooks Configuration (`.engineering-agent/build-hooks.json`)

```json
{
  "hooks": {
    "prebuild": {
      "enabled": true,
      "workflow": "code_quality",
      "fail_on_error": false
    },
    "postbuild": {
      "enabled": false,
      "workflow": "reporting",
      "fail_on_error": false
    }
  }
}
```

## 🔌 CI/CD Integration

### GitHub Actions

```yaml
name: Engineering Automation

on: [push, pull_request]

jobs:
  automation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '16'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: npm ci
      - run: npm run audit:engineering
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps { sh 'npm ci' }
        }
        stage('Engineering Automation') {
            steps { sh 'npm run audit:engineering' }
        }
    }
}
```

## 📊 Reports and Output

Reports are generated in `.engineering-agent/reports/`:

- `code-quality-latest.json` - Latest code quality report
- `full-analysis-latest.json` - Latest full analysis report
- `test-suite-latest.json` - Latest test results

## 🎯 Project Templates

Choose from pre-configured templates:

- `default` - Basic JavaScript project
- `react` - React application with JSX support
- `node` - Node.js backend application
- `typescript` - TypeScript project with strict checking

```bash
npx engineering-agent init --template react
```

## 🔧 Requirements

- **Node.js**: 14.0.0 or higher
- **Python**: 3.8 or higher (automatically managed)
- **NPM**: 6.0.0 or higher

## 📚 Documentation

- [Full Documentation](https://github.com/Instoradmin/Jeeves4coders#readme)
- [API Reference](./docs/api.md)
- [Configuration Guide](./docs/configuration.md)
- [Build Integration Guide](./docs/build-integration.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- [GitHub Issues](https://github.com/Instoradmin/Jeeves4coders/issues)
- [Documentation](https://github.com/Instoradmin/Jeeves4coders#readme)
- Email: engineering@instor.com

---

**Made with ❤️ by the Instor Engineering Team**
