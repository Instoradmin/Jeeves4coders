#!/usr/bin/env node
/**
 * Engineering Automation Agent - Test Script
 * Tests the npm package installation and functionality
 */

const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('cross-spawn');
const chalk = require('chalk');

class AgentTester {
    constructor() {
        this.projectRoot = process.cwd();
        this.packageRoot = path.resolve(__dirname, '..');
        this.pythonAgentPath = path.join(this.packageRoot, 'python-agent');
        this.isWindows = process.platform === 'win32';
        this.pythonCmd = this.isWindows ? 'python' : 'python3';
        this.testResults = [];
    }

    async runTests() {
        console.log(chalk.blue('🧪 Engineering Automation Agent - Test Suite'));
        console.log(chalk.blue('=============================================='));

        try {
            await this.testPythonInstallation();
            await this.testAgentInstallation();
            await this.testConfiguration();
            await this.testWorkflows();
            await this.testBuildIntegration();
            
            this.showTestResults();
            
        } catch (error) {
            console.error(chalk.red('\n❌ Test suite failed:'), error.message);
            process.exit(1);
        }
    }

    async testPythonInstallation() {
        console.log(chalk.yellow('\n🐍 Testing Python installation...'));
        
        try {
            const result = await this.runCommand(this.pythonCmd, ['--version']);
            this.addTestResult('Python Installation', true, `Found: ${result.stdout.trim()}`);
        } catch (error) {
            this.addTestResult('Python Installation', false, error.message);
        }
    }

    async testAgentInstallation() {
        console.log(chalk.yellow('\n📦 Testing agent installation...'));
        
        // Test if Python agent files exist
        const requiredFiles = [
            'core_agent.py',
            'cli.py',
            'requirements.txt'
        ];
        
        for (const file of requiredFiles) {
            const filePath = path.join(this.pythonAgentPath, file);
            const exists = await fs.pathExists(filePath);
            this.addTestResult(`Agent File: ${file}`, exists, exists ? 'Found' : 'Missing');
        }
        
        // Test virtual environment
        const venvPath = path.join(this.pythonAgentPath, 'venv');
        const venvExists = await fs.pathExists(venvPath);
        this.addTestResult('Virtual Environment', venvExists, venvExists ? 'Created' : 'Not found');
    }

    async testConfiguration() {
        console.log(chalk.yellow('\n⚙️  Testing configuration...'));
        
        // Test main configuration
        const mainConfigPath = path.join(this.projectRoot, '.engineering-agent.json');
        const mainConfigExists = await fs.pathExists(mainConfigPath);
        this.addTestResult('Main Configuration', mainConfigExists, mainConfigExists ? 'Found' : 'Missing');
        
        // Test build hooks configuration
        const hooksConfigPath = path.join(this.projectRoot, '.engineering-agent', 'build-hooks.json');
        const hooksConfigExists = await fs.pathExists(hooksConfigPath);
        this.addTestResult('Build Hooks Config', hooksConfigExists, hooksConfigExists ? 'Found' : 'Missing');
        
        // Test configuration validity
        if (mainConfigExists) {
            try {
                const config = await fs.readJson(mainConfigPath);
                const hasRequiredFields = config.project_name && config.project_root;
                this.addTestResult('Configuration Validity', hasRequiredFields, hasRequiredFields ? 'Valid' : 'Invalid structure');
            } catch (error) {
                this.addTestResult('Configuration Validity', false, 'Invalid JSON');
            }
        }
    }

    async testWorkflows() {
        console.log(chalk.yellow('\n🔄 Testing workflows...'));
        
        // Test if we can run the agent CLI
        try {
            const venvPath = path.join(this.pythonAgentPath, 'venv');
            const pythonExe = this.isWindows 
                ? path.join(venvPath, 'Scripts', 'python.exe')
                : path.join(venvPath, 'bin', 'python');
                
            const usePython = (await fs.pathExists(pythonExe)) ? pythonExe : this.pythonCmd;
            
            // Test version command
            const result = await this.runCommand(usePython, [
                '-m', 'engineering_automation_agent.cli', 'version'
            ], {
                cwd: this.pythonAgentPath,
                env: {
                    ...process.env,
                    PYTHONPATH: this.pythonAgentPath
                }
            });
            
            this.addTestResult('CLI Version Command', result.code === 0, result.code === 0 ? 'Success' : 'Failed');
            
        } catch (error) {
            this.addTestResult('CLI Version Command', false, error.message);
        }
    }

    async testBuildIntegration() {
        console.log(chalk.yellow('\n🔧 Testing build integration...'));
        
        // Test build hook script
        const buildHookPath = path.join(__dirname, 'build-hook.js');
        const buildHookExists = await fs.pathExists(buildHookPath);
        this.addTestResult('Build Hook Script', buildHookExists, buildHookExists ? 'Found' : 'Missing');
        
        // Test package.json scripts
        const packageJsonPath = path.join(this.projectRoot, 'package.json');
        if (await fs.pathExists(packageJsonPath)) {
            try {
                const packageJson = await fs.readJson(packageJsonPath);
                const hasEngineeringScripts = packageJson.scripts && (
                    packageJson.scripts['lint:engineering'] ||
                    packageJson.scripts['audit:engineering'] ||
                    packageJson.scripts['test:engineering']
                );
                this.addTestResult('Package.json Scripts', hasEngineeringScripts, hasEngineeringScripts ? 'Added' : 'Not added');
            } catch (error) {
                this.addTestResult('Package.json Scripts', false, 'Error reading package.json');
            }
        }
    }

    addTestResult(testName, success, details) {
        this.testResults.push({ testName, success, details });
        const status = success ? chalk.green('✅') : chalk.red('❌');
        console.log(`  ${status} ${testName}: ${details}`);
    }

    showTestResults() {
        console.log(chalk.blue('\n📊 Test Results Summary'));
        console.log(chalk.blue('========================'));
        
        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(r => r.success).length;
        const failedTests = totalTests - passedTests;
        
        console.log(chalk.white(`Total Tests: ${totalTests}`));
        console.log(chalk.green(`Passed: ${passedTests}`));
        console.log(chalk.red(`Failed: ${failedTests}`));
        
        if (failedTests > 0) {
            console.log(chalk.red('\n❌ Failed Tests:'));
            this.testResults
                .filter(r => !r.success)
                .forEach(r => {
                    console.log(chalk.red(`  • ${r.testName}: ${r.details}`));
                });
        }
        
        const successRate = (passedTests / totalTests) * 100;
        console.log(chalk.blue(`\nSuccess Rate: ${successRate.toFixed(1)}%`));
        
        if (successRate >= 80) {
            console.log(chalk.green('\n🎉 Engineering Automation Agent is working correctly!'));
        } else {
            console.log(chalk.yellow('\n⚠️  Some tests failed. Please check the installation.'));
        }
    }

    async runCommand(command, args, options = {}) {
        return new Promise((resolve, reject) => {
            const child = spawn(command, args, {
                stdio: ['inherit', 'pipe', 'pipe'],
                ...options
            });
            
            let stdout = '';
            let stderr = '';
            
            child.stdout?.on('data', (data) => {
                stdout += data.toString();
            });
            
            child.stderr?.on('data', (data) => {
                stderr += data.toString();
            });
            
            child.on('close', (code) => {
                resolve({ stdout, stderr, code });
            });
            
            child.on('error', reject);
        });
    }
}

// Run tests if called directly
if (require.main === module) {
    const tester = new AgentTester();
    tester.runTests().catch(error => {
        console.error(chalk.red('Test suite failed:'), error);
        process.exit(1);
    });
}

module.exports = AgentTester;
