# Jeeves4coders VS Code Extension

Your intelligent coding assistant integrated directly into VS Code!

## Features

- **🤖 Intelligent Automation**: Comprehensive code analysis, testing, and quality checks
- **🧪 Testing Integration**: Run unit, functional, integration, and regression tests
- **📊 Code Quality**: Automated code review and quality analysis
- **🔗 GitHub Integration**: Seamless GitHub workflow integration
- **🎫 JIRA Integration**: Automatic ticket management and updates
- **📚 Confluence Integration**: Documentation and test results publishing
- **🌍 Multi-language Support**: Internationalization with multiple languages

## Quick Start

1. Install the extension from the VS Code marketplace
2. Open your project in VS Code
3. Use `Ctrl+Shift+P` and search for "Jeeves4coders: Initialize"
4. Follow the setup wizard

## Commands

- **Jeeves4coders: Initialize** - Set up Jeeves4coders for your project
- **Jeeves4coders: Run Workflow** - Execute automation workflows
- **Jeeves4coders: Run Tests** - Run comprehensive test suites
- **Jeeves4coders: Run Code Review** - Analyze code quality
- **Jeeves4coders: Show Status** - View current status and configuration

## Workflows Available

- **Code Quality** - Code review and quality analysis
- **Full Analysis** - Complete project analysis with testing
- **Testing Only** - Comprehensive test execution
- **CI/CD** - Continuous integration workflow
- **Deployment** - Deployment preparation and validation

## Configuration

Configure Jeeves4coders through VS Code settings:

```json
{
  "jeeves4coders.enabled": true,
  "jeeves4coders.autoRun": false,
  "jeeves4coders.defaultWorkflow": "code_quality",
  "jeeves4coders.configFile": ".jeeves4coders.json"
}
```

## Project Configuration

Create a `.jeeves4coders.json` file in your project root:

```json
{
  "project_name": "my-project",
  "test_types": ["unit", "functional", "integration"],
  "github_enabled": true,
  "jira_enabled": true,
  "confluence_enabled": true
}
```

## Usage

### From Command Palette
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Jeeves4coders"
3. Select the desired command

### From Activity Bar
1. Click the Jeeves4coders icon in the activity bar
2. Use the Status, Workflows, and Results panels
3. Click on workflows to execute them

### From Context Menu
- Right-click on files or folders to access Jeeves4coders commands
- Run code review on specific files
- Execute workflows on selected directories

## Status Bar

The Jeeves4coders status bar item shows:
- Current status (ready, running, error)
- Quick access to status panel
- Visual feedback during operations

## Requirements

- VS Code 1.74.0 or higher
- Node.js 14.0.0 or higher
- Python 3.8 or higher (automatically managed)

## Extension Settings

This extension contributes the following settings:

- `jeeves4coders.enabled`: Enable/disable the extension
- `jeeves4coders.autoRun`: Automatically run workflows on file save
- `jeeves4coders.defaultWorkflow`: Default workflow to run
- `jeeves4coders.configFile`: Path to configuration file

## Known Issues

- Initial setup may take a few minutes to install Python dependencies
- Some workflows require additional configuration (GitHub tokens, JIRA credentials)

## Release Notes

### 1.0.0

Initial release of Jeeves4coders VS Code extension:
- Complete integration with Jeeves4coders automation agent
- Command palette integration
- Activity bar panel with status, workflows, and results
- Context menu integration
- Status bar indicator
- Comprehensive configuration options

## Support

- [GitHub Repository](https://github.com/Instoradmin/Jeeves4coders)
- [Documentation](https://github.com/Instoradmin/Jeeves4coders#readme)
- [Issues](https://github.com/Instoradmin/Jeeves4coders/issues)

---

**Enjoy coding with your intelligent assistant!** 🤖
