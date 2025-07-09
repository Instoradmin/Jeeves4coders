#!/usr/bin/env node
/**
 * Engineering Automation Agent - NPM Installation Script
 * Installs Python dependencies and sets up the agent environment
 */

const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('cross-spawn');
const chalk = require('chalk');
const which = require('which');

class AgentInstaller {
    constructor() {
        this.packageRoot = path.resolve(__dirname, '..');
        this.pythonAgentPath = path.join(this.packageRoot, 'python-agent');
        this.isWindows = process.platform === 'win32';
        this.pythonCmd = this.isWindows ? 'python' : 'python3';
    }

    async install() {
        console.log(chalk.blue('🤖 Engineering Automation Agent - Installation'));
        console.log(chalk.blue('================================================'));

        try {
            await this.checkPython();
            await this.copyPythonAgent();
            await this.installPythonDependencies();
            await this.createVirtualEnvironment();
            await this.setupConfiguration();
            
            console.log(chalk.green('\n✅ Installation completed successfully!'));
            console.log(chalk.yellow('\n📋 Next steps:'));
            console.log(chalk.white('  1. Run: npx engineering-agent init'));
            console.log(chalk.white('  2. Configure your project settings'));
            console.log(chalk.white('  3. Run: npm run lint (for code quality check)'));
            
        } catch (error) {
            console.error(chalk.red('\n❌ Installation failed:'), error.message);
            process.exit(1);
        }
    }

    async checkPython() {
        console.log(chalk.yellow('\n📋 Checking Python installation...'));
        
        try {
            // Try to find Python
            const pythonPath = await which(this.pythonCmd);
            console.log(chalk.green(`✅ Found Python: ${pythonPath}`));
            
            // Check Python version
            const versionResult = await this.runCommand(this.pythonCmd, ['--version']);
            const version = versionResult.stdout.trim();
            console.log(chalk.green(`✅ Python version: ${version}`));
            
            // Verify minimum version (3.8+)
            const versionMatch = version.match(/Python (\d+)\.(\d+)/);
            if (versionMatch) {
                const major = parseInt(versionMatch[1]);
                const minor = parseInt(versionMatch[2]);
                
                if (major < 3 || (major === 3 && minor < 8)) {
                    throw new Error(`Python 3.8+ required, found ${version}`);
                }
            }
            
        } catch (error) {
            if (error.code === 'ENOENT') {
                throw new Error('Python not found. Please install Python 3.8+ and ensure it\'s in your PATH');
            }
            throw error;
        }
    }

    async copyPythonAgent() {
        console.log(chalk.yellow('\n📁 Setting up Python agent...'));
        
        // Ensure python-agent directory exists
        await fs.ensureDir(this.pythonAgentPath);
        
        // Copy Python source files
        const sourceFiles = [
            '__init__.py',
            'cli.py', 
            'core_agent.py',
            'config_manager.py',
            'code_review_module.py',
            'test_suite_module.py',
            'github_module.py',
            'jira_module.py',
            'confluence_module.py',
            'utils.py',
            'messages.py',
            'version.py',
            'requirements.txt',
            'setup.py'
        ];
        
        for (const file of sourceFiles) {
            const sourcePath = path.join(this.packageRoot, file);
            const destPath = path.join(this.pythonAgentPath, file);
            
            if (await fs.pathExists(sourcePath)) {
                await fs.copy(sourcePath, destPath);
                console.log(chalk.green(`  ✅ Copied: ${file}`));
            } else {
                console.log(chalk.yellow(`  ⚠️  Skipped: ${file} (not found)`));
            }
        }
    }

    async installPythonDependencies() {
        console.log(chalk.yellow('\n📦 Installing Python dependencies...'));
        
        const requirementsPath = path.join(this.pythonAgentPath, 'requirements.txt');
        
        if (await fs.pathExists(requirementsPath)) {
            await this.runCommand(this.pythonCmd, ['-m', 'pip', 'install', '-r', requirementsPath], {
                cwd: this.pythonAgentPath
            });
            console.log(chalk.green('✅ Python dependencies installed'));
        } else {
            console.log(chalk.yellow('⚠️  No requirements.txt found, skipping dependency installation'));
        }
    }

    async createVirtualEnvironment() {
        console.log(chalk.yellow('\n🐍 Setting up virtual environment...'));
        
        const venvPath = path.join(this.pythonAgentPath, 'venv');
        
        try {
            // Create virtual environment
            await this.runCommand(this.pythonCmd, ['-m', 'venv', venvPath]);
            console.log(chalk.green('✅ Virtual environment created'));
            
            // Install agent in development mode
            const activateScript = this.isWindows 
                ? path.join(venvPath, 'Scripts', 'python.exe')
                : path.join(venvPath, 'bin', 'python');
                
            if (await fs.pathExists(activateScript)) {
                await this.runCommand(activateScript, ['-m', 'pip', 'install', '-e', '.'], {
                    cwd: this.pythonAgentPath
                });
                console.log(chalk.green('✅ Agent installed in virtual environment'));
            }
            
        } catch (error) {
            console.log(chalk.yellow('⚠️  Virtual environment setup failed, using global Python'));
        }
    }

    async setupConfiguration() {
        console.log(chalk.yellow('\n⚙️  Setting up configuration...'));
        
        const configPath = path.join(process.cwd(), '.engineering-agent.json');
        
        if (!(await fs.pathExists(configPath))) {
            const defaultConfig = {
                version: "1.0.0",
                project_name: path.basename(process.cwd()),
                project_root: process.cwd(),
                auto_run_on_build: true,
                default_workflow: "code_quality",
                modules: {
                    code_review: { enabled: true },
                    test_suite: { enabled: true },
                    github: { enabled: false },
                    jira: { enabled: false },
                    confluence: { enabled: false }
                }
            };
            
            await fs.writeJson(configPath, defaultConfig, { spaces: 2 });
            console.log(chalk.green(`✅ Created configuration: ${configPath}`));
        } else {
            console.log(chalk.green('✅ Configuration already exists'));
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
                process.stdout.write(data);
            });
            
            child.stderr?.on('data', (data) => {
                stderr += data.toString();
                process.stderr.write(data);
            });
            
            child.on('close', (code) => {
                if (code === 0) {
                    resolve({ stdout, stderr, code });
                } else {
                    reject(new Error(`Command failed with code ${code}: ${stderr}`));
                }
            });
            
            child.on('error', reject);
        });
    }
}

// Run installation if called directly
if (require.main === module) {
    const installer = new AgentInstaller();
    installer.install().catch(error => {
        console.error(chalk.red('Installation failed:'), error);
        process.exit(1);
    });
}

module.exports = AgentInstaller;
