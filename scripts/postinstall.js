#!/usr/bin/env node
/**
 * Engineering Automation Agent - Post-installation Script
 * Runs after npm install to finalize setup
 */

const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');

class PostInstaller {
    constructor() {
        this.packageRoot = path.resolve(__dirname, '..');
        this.projectRoot = process.cwd();
    }

    async run() {
        console.log(chalk.blue('\n🔧 Engineering Automation Agent - Post-installation'));
        console.log(chalk.blue('===================================================='));

        try {
            await this.setupProjectIntegration();
            await this.createBuildHooks();
            await this.showWelcomeMessage();
            
        } catch (error) {
            console.error(chalk.red('\n❌ Post-installation failed:'), error.message);
            // Don't exit with error code as this is not critical
        }
    }

    async setupProjectIntegration() {
        console.log(chalk.yellow('\n🔗 Setting up project integration...'));
        
        // Check if this is being installed in a project (not globally)
        const packageJsonPath = path.join(this.projectRoot, 'package.json');
        
        if (await fs.pathExists(packageJsonPath)) {
            const packageJson = await fs.readJson(packageJsonPath);
            
            // Add engineering-agent scripts if they don't exist
            if (!packageJson.scripts) {
                packageJson.scripts = {};
            }
            
            const scriptsToAdd = {
                'lint:engineering': 'engineering-agent workflow code_quality',
                'audit:engineering': 'engineering-agent workflow full_analysis',
                'test:engineering': 'engineering-agent run test_suite'
            };
            
            let scriptsAdded = false;
            for (const [scriptName, scriptCommand] of Object.entries(scriptsToAdd)) {
                if (!packageJson.scripts[scriptName]) {
                    packageJson.scripts[scriptName] = scriptCommand;
                    scriptsAdded = true;
                    console.log(chalk.green(`  ✅ Added script: ${scriptName}`));
                }
            }
            
            if (scriptsAdded) {
                await fs.writeJson(packageJsonPath, packageJson, { spaces: 2 });
                console.log(chalk.green('✅ Updated package.json with engineering-agent scripts'));
            } else {
                console.log(chalk.green('✅ Scripts already configured'));
            }
        }
    }

    async createBuildHooks() {
        console.log(chalk.yellow('\n🪝 Creating build hooks...'));
        
        // Create .engineering-agent directory for local configuration
        const agentDir = path.join(this.projectRoot, '.engineering-agent');
        await fs.ensureDir(agentDir);
        
        // Create build hook configuration
        const buildHookConfig = {
            version: "1.0.0",
            hooks: {
                prebuild: {
                    enabled: true,
                    workflow: "code_quality",
                    fail_on_error: false
                },
                postbuild: {
                    enabled: false,
                    workflow: "reporting",
                    fail_on_error: false
                },
                pretest: {
                    enabled: true,
                    workflow: "test_suite",
                    fail_on_error: true
                }
            },
            workflows: {
                code_quality: ["code_review"],
                full_analysis: ["code_review", "test_suite"],
                reporting: ["test_suite", "confluence"]
            }
        };
        
        const hookConfigPath = path.join(agentDir, 'build-hooks.json');
        if (!(await fs.pathExists(hookConfigPath))) {
            await fs.writeJson(hookConfigPath, buildHookConfig, { spaces: 2 });
            console.log(chalk.green(`✅ Created build hooks configuration: ${hookConfigPath}`));
        }
        
        // Create example configuration files
        await this.createExampleConfigs(agentDir);
    }

    async createExampleConfigs(agentDir) {
        // GitHub Actions workflow example
        const githubWorkflow = `name: Engineering Automation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  engineering-automation:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
        cache: 'npm'
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run Engineering Automation
      run: npm run audit:engineering
      env:
        GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
        JIRA_API_TOKEN: \${{ secrets.JIRA_API_TOKEN }}
        CONFLUENCE_API_TOKEN: \${{ secrets.CONFLUENCE_API_TOKEN }}
`;

        const examplesDir = path.join(agentDir, 'examples');
        await fs.ensureDir(examplesDir);
        
        await fs.writeFile(
            path.join(examplesDir, 'github-actions.yml'), 
            githubWorkflow
        );
        
        // Jenkins pipeline example
        const jenkinsPipeline = `pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Engineering Automation') {
            steps {
                sh 'npm run audit:engineering'
            }
            post {
                always {
                    archiveArtifacts artifacts: '.engineering-agent/reports/**/*', allowEmptyArchive: true
                }
            }
        }
    }
}`;

        await fs.writeFile(
            path.join(examplesDir, 'Jenkinsfile'), 
            jenkinsPipeline
        );
        
        console.log(chalk.green('✅ Created example CI/CD configurations'));
    }

    async showWelcomeMessage() {
        console.log(chalk.green('\n🎉 Engineering Automation Agent installed successfully!'));
        console.log(chalk.blue('\n📋 Available Commands:'));
        console.log(chalk.white('  npx engineering-agent init          - Initialize agent for your project'));
        console.log(chalk.white('  npx engineering-agent workflow <name> - Run a specific workflow'));
        console.log(chalk.white('  npm run lint:engineering           - Run code quality checks'));
        console.log(chalk.white('  npm run audit:engineering          - Run full analysis'));
        console.log(chalk.white('  npm run test:engineering           - Run test suite'));
        
        console.log(chalk.blue('\n🔄 Available Workflows:'));
        console.log(chalk.white('  code_quality    - Code review and quality analysis'));
        console.log(chalk.white('  full_analysis   - Complete project analysis'));
        console.log(chalk.white('  deployment      - Deployment workflow'));
        console.log(chalk.white('  reporting       - Generate reports'));
        console.log(chalk.white('  ci_cd          - Continuous integration workflow'));
        
        console.log(chalk.blue('\n📁 Configuration Files:'));
        console.log(chalk.white('  .engineering-agent.json           - Main configuration'));
        console.log(chalk.white('  .engineering-agent/build-hooks.json - Build integration settings'));
        console.log(chalk.white('  .engineering-agent/examples/       - CI/CD examples'));
        
        console.log(chalk.yellow('\n💡 Next Steps:'));
        console.log(chalk.white('  1. Run: npx engineering-agent init'));
        console.log(chalk.white('  2. Configure your integrations (GitHub, Jira, Confluence)'));
        console.log(chalk.white('  3. Run: npm run lint:engineering'));
        console.log(chalk.white('  4. Check the generated reports in .engineering-agent/reports/'));
        
        console.log(chalk.blue('\n📖 Documentation: https://github.com/Instoradmin/Jeeves4coders#readme'));
    }
}

// Run post-installation if called directly
if (require.main === module) {
    const postInstaller = new PostInstaller();
    postInstaller.run().catch(error => {
        console.error(chalk.red('Post-installation failed:'), error);
        // Don't exit with error code
    });
}

module.exports = PostInstaller;
