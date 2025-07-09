#!/usr/bin/env node
/**
 * Jeeves4coders - CLI Wrapper
 * Your intelligent coding assistant - Node.js CLI that interfaces with the Python agent
 */

const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('cross-spawn');
const chalk = require('chalk');
const { Command } = require('commander');
const which = require('which');

class Jeeves4codersCLI {
    constructor() {
        this.packageRoot = path.resolve(__dirname, '..');
        this.pythonAgentPath = path.join(this.packageRoot, 'python-agent');
        this.projectRoot = process.cwd();
        this.isWindows = process.platform === 'win32';
        this.pythonCmd = this.isWindows ? 'python' : 'python3';
    }

    async run() {
        const program = new Command();
        
        program
            .name('jeeves4coders')
            .description('Jeeves4coders - Your intelligent coding assistant for comprehensive project automation')
            .version('1.0.0');

        // Init command
        program
            .command('init')
            .description('Initialize agent for current project')
            .option('-p, --project <name>', 'Project name (auto-detected if not provided)')
            .option('-r, --root <path>', 'Project root directory', '.')
            .option('-t, --template <name>', 'Project template to use')
            .option('-c, --config <file>', 'Configuration file to use')
            .action(async (options) => {
                await this.handleInit(options);
            });

        // Workflow command
        program
            .command('workflow <name>')
            .description('Run predefined workflows')
            .option('-p, --project <name>', 'Project name')
            .option('-c, --config <file>', 'Configuration file')
            .option('-o, --output <file>', 'Output file for results')
            .action(async (workflowName, options) => {
                await this.handleWorkflow(workflowName, options);
            });

        // Run command
        program
            .command('run <module>')
            .description('Run specific module')
            .option('-p, --project <name>', 'Project name')
            .option('-c, --config <file>', 'Configuration file')
            .option('-o, --output <file>', 'Output file for results')
            .action(async (moduleName, options) => {
                await this.handleRun(moduleName, options);
            });

        // Config command
        const configCmd = program
            .command('config')
            .description('Manage configurations');

        configCmd
            .command('create')
            .description('Create new project configuration')
            .requiredOption('-p, --project <name>', 'Project name')
            .requiredOption('-r, --root <path>', 'Project root directory')
            .option('-t, --template <name>', 'Project template')
            .option('-o, --output <file>', 'Output configuration file')
            .action(async (options) => {
                await this.handleConfigCreate(options);
            });

        configCmd
            .command('show [project]')
            .description('Show project configuration')
            .action(async (project) => {
                await this.handleConfigShow(project);
            });

        // Version command
        program
            .command('version')
            .description('Show version information')
            .action(async () => {
                await this.handleVersion();
            });

        // Status command
        program
            .command('status')
            .description('Show agent status and health check')
            .action(async () => {
                await this.handleStatus();
            });

        await program.parseAsync();
    }

    async handleInit(options) {
        console.log(chalk.blue('🚀 Initializing Engineering Automation Agent...'));
        
        try {
            await this.ensureAgentSetup();
            
            const args = ['init'];
            if (options.project) args.push('--project', options.project);
            if (options.root) args.push('--root', options.root);
            if (options.template) args.push('--template', options.template);
            if (options.config) args.push('--config', options.config);
            
            await this.runPythonAgent(args);
            
        } catch (error) {
            console.error(chalk.red('❌ Initialization failed:'), error.message);
            process.exit(1);
        }
    }

    async handleWorkflow(workflowName, options) {
        console.log(chalk.blue(`🔄 Running workflow: ${workflowName}`));
        
        try {
            await this.ensureAgentSetup();
            
            const args = ['workflow', workflowName];
            if (options.project) args.push('--project', options.project);
            if (options.config) args.push('--config', options.config);
            if (options.output) args.push('--output', options.output);
            
            await this.runPythonAgent(args);
            
        } catch (error) {
            console.error(chalk.red('❌ Workflow failed:'), error.message);
            process.exit(1);
        }
    }

    async handleRun(moduleName, options) {
        console.log(chalk.blue(`🔄 Running module: ${moduleName}`));
        
        try {
            await this.ensureAgentSetup();
            
            const args = ['run', moduleName];
            if (options.project) args.push('--project', options.project);
            if (options.config) args.push('--config', options.config);
            if (options.output) args.push('--output', options.output);
            
            await this.runPythonAgent(args);
            
        } catch (error) {
            console.error(chalk.red('❌ Module execution failed:'), error.message);
            process.exit(1);
        }
    }

    async handleConfigCreate(options) {
        console.log(chalk.blue('📝 Creating configuration...'));
        
        try {
            await this.ensureAgentSetup();
            
            const args = ['config', 'create'];
            args.push('--project', options.project);
            args.push('--root', options.root);
            if (options.template) args.push('--template', options.template);
            if (options.output) args.push('--output', options.output);
            
            await this.runPythonAgent(args);
            
        } catch (error) {
            console.error(chalk.red('❌ Configuration creation failed:'), error.message);
            process.exit(1);
        }
    }

    async handleConfigShow(project) {
        console.log(chalk.blue('📊 Showing configuration...'));
        
        try {
            await this.ensureAgentSetup();
            
            const args = ['config', 'show'];
            if (project) args.push(project);
            
            await this.runPythonAgent(args);
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to show configuration:'), error.message);
            process.exit(1);
        }
    }

    async handleVersion() {
        console.log(chalk.blue('🤖 Jeeves4coders - Your Intelligent Coding Assistant'));
        console.log(chalk.blue('==================================================='));
        
        // Show npm package version
        const packageJsonPath = path.join(this.packageRoot, 'package.json');
        if (await fs.pathExists(packageJsonPath)) {
            const packageJson = await fs.readJson(packageJsonPath);
            console.log(chalk.white(`NPM Package Version: ${packageJson.version}`));
        }
        
        try {
            await this.ensureAgentSetup();
            await this.runPythonAgent(['version']);
        } catch (error) {
            console.error(chalk.red('❌ Failed to get Python agent version:'), error.message);
        }
    }

    async handleStatus() {
        console.log(chalk.blue('🔍 Jeeves4coders - Status Check'));
        console.log(chalk.blue('==============================='));
        
        try {
            // Check Python installation
            console.log(chalk.yellow('\n🐍 Python Environment:'));
            const pythonVersion = await this.checkPython();
            console.log(chalk.green(`  ✅ Python: ${pythonVersion}`));
            
            // Check agent installation
            console.log(chalk.yellow('\n📦 Agent Installation:'));
            const agentInstalled = await this.checkAgentInstallation();
            console.log(agentInstalled ? chalk.green('  ✅ Agent: Installed') : chalk.red('  ❌ Agent: Not installed'));
            
            // Check configuration
            console.log(chalk.yellow('\n⚙️  Configuration:'));
            const configExists = await this.checkConfiguration();
            console.log(configExists ? chalk.green('  ✅ Config: Found') : chalk.yellow('  ⚠️  Config: Not found (run init)'));
            
            // Check Python agent
            if (agentInstalled) {
                console.log(chalk.yellow('\n🤖 Python Agent:'));
                try {
                    await this.runPythonAgent(['version'], { silent: true });
                    console.log(chalk.green('  ✅ Python Agent: Working'));
                } catch (error) {
                    console.log(chalk.red('  ❌ Python Agent: Error'));
                }
            }
            
        } catch (error) {
            console.error(chalk.red('❌ Status check failed:'), error.message);
        }
    }

    async ensureAgentSetup() {
        // Check if Python agent is installed
        if (!(await fs.pathExists(this.pythonAgentPath))) {
            throw new Error('Python agent not found. Please reinstall the package.');
        }
        
        // Check if Python is available
        try {
            await which(this.pythonCmd);
        } catch (error) {
            throw new Error('Python not found. Please install Python 3.8+ and ensure it\'s in your PATH.');
        }
    }

    async runPythonAgent(args, options = {}) {
        // Determine Python executable
        const venvPath = path.join(this.pythonAgentPath, 'venv');
        const pythonExe = this.isWindows 
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
            
        const usePython = (await fs.pathExists(pythonExe)) ? pythonExe : this.pythonCmd;
        
        // Prepare command
        const command = usePython;
        const commandArgs = ['-m', 'engineering_automation_agent.cli', ...args];
        
        // Set environment
        const env = {
            ...process.env,
            PYTHONPATH: this.pythonAgentPath,
            ENGINEERING_AGENT_PROJECT_ROOT: this.projectRoot
        };

        return new Promise((resolve, reject) => {
            const child = spawn(command, commandArgs, {
                stdio: options.silent ? 'pipe' : 'inherit',
                cwd: this.pythonAgentPath,
                env
            });
            
            child.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Python agent exited with code ${code}`));
                }
            });
            
            child.on('error', reject);
        });
    }

    async checkPython() {
        const result = await this.runCommand(this.pythonCmd, ['--version']);
        return result.stdout.trim();
    }

    async checkAgentInstallation() {
        return await fs.pathExists(path.join(this.pythonAgentPath, 'core_agent.py'));
    }

    async checkConfiguration() {
        return await fs.pathExists(path.join(this.projectRoot, '.engineering-agent.json'));
    }

    async runCommand(command, args) {
        return new Promise((resolve, reject) => {
            const child = spawn(command, args, { stdio: 'pipe' });
            
            let stdout = '';
            let stderr = '';
            
            child.stdout.on('data', (data) => stdout += data.toString());
            child.stderr.on('data', (data) => stderr += data.toString());
            
            child.on('close', (code) => {
                if (code === 0) {
                    resolve({ stdout, stderr });
                } else {
                    reject(new Error(stderr || `Command failed with code ${code}`));
                }
            });
            
            child.on('error', reject);
        });
    }
}

// Run CLI if called directly
if (require.main === module) {
    const cli = new Jeeves4codersCLI();
    cli.run().catch(error => {
        console.error(chalk.red('CLI error:'), error);
        process.exit(1);
    });
}

module.exports = Jeeves4codersCLI;
