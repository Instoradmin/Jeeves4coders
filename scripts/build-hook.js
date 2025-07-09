#!/usr/bin/env node
/**
 * Engineering Automation Agent - Build Hook Script
 * Integrates with build processes to run automation workflows
 */

const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('cross-spawn');
const chalk = require('chalk');
const { Command } = require('commander');

class BuildHook {
    constructor() {
        this.projectRoot = process.cwd();
        this.agentDir = path.join(this.projectRoot, '.engineering-agent');
        this.packageRoot = path.resolve(__dirname, '..');
        this.pythonAgentPath = path.join(this.packageRoot, 'python-agent');
        this.isWindows = process.platform === 'win32';
        this.pythonCmd = this.isWindows ? 'python' : 'python3';
    }

    async run(options = {}) {
        const {
            workflow = 'code_quality',
            stage = 'build',
            failOnError = false,
            output = null,
            config = null
        } = options;

        console.log(chalk.blue(`\n🔄 Engineering Automation Agent - ${stage.toUpperCase()} Hook`));
        console.log(chalk.blue('='.repeat(50 + stage.length)));

        try {
            // Load configuration
            const config = await this.loadConfiguration();
            
            // Check if automation should run
            if (!this.shouldRun(config, stage, workflow)) {
                console.log(chalk.yellow(`⏭️  Skipping automation for ${stage} stage`));
                return { success: true, skipped: true };
            }

            // Run the workflow
            const result = await this.runWorkflow(workflow, config, output);
            
            // Handle results
            if (result.success) {
                console.log(chalk.green(`\n✅ ${workflow} workflow completed successfully`));
                await this.generateReport(result, workflow, stage);
            } else {
                console.log(chalk.red(`\n❌ ${workflow} workflow failed`));
                
                if (failOnError) {
                    console.log(chalk.red('🚫 Build failed due to automation errors'));
                    process.exit(1);
                } else {
                    console.log(chalk.yellow('⚠️  Continuing build despite automation errors'));
                }
            }

            return result;

        } catch (error) {
            console.error(chalk.red('\n❌ Build hook failed:'), error.message);
            
            if (failOnError) {
                process.exit(1);
            }
            
            return { success: false, error: error.message };
        }
    }

    async loadConfiguration() {
        // Load main configuration
        const mainConfigPath = path.join(this.projectRoot, '.engineering-agent.json');
        let mainConfig = {};
        
        if (await fs.pathExists(mainConfigPath)) {
            mainConfig = await fs.readJson(mainConfigPath);
        }

        // Load build hooks configuration
        const hooksConfigPath = path.join(this.agentDir, 'build-hooks.json');
        let hooksConfig = {};
        
        if (await fs.pathExists(hooksConfigPath)) {
            hooksConfig = await fs.readJson(hooksConfigPath);
        }

        return { ...mainConfig, hooks: hooksConfig.hooks || {}, workflows: hooksConfig.workflows || {} };
    }

    shouldRun(config, stage, workflow) {
        // Check if automation is globally disabled
        if (config.auto_run_on_build === false) {
            return false;
        }

        // Check stage-specific configuration
        const stageConfig = config.hooks[stage];
        if (stageConfig && stageConfig.enabled === false) {
            return false;
        }

        // Check if in CI environment and CI is disabled
        if (process.env.CI && config.ci_enabled === false) {
            return false;
        }

        return true;
    }

    async runWorkflow(workflowName, config, outputFile) {
        console.log(chalk.yellow(`\n🚀 Running workflow: ${workflowName}`));
        
        // Determine Python executable
        const venvPath = path.join(this.pythonAgentPath, 'venv');
        const pythonExe = this.isWindows 
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
            
        const usePython = (await fs.pathExists(pythonExe)) ? pythonExe : this.pythonCmd;
        
        // Prepare command arguments
        const args = [
            '-m', 'engineering_automation_agent.cli',
            'workflow', workflowName
        ];
        
        if (outputFile) {
            args.push('--output', outputFile);
        }
        
        // Set environment variables
        const env = {
            ...process.env,
            PYTHONPATH: this.pythonAgentPath,
            ENGINEERING_AGENT_PROJECT_ROOT: this.projectRoot
        };

        try {
            const result = await this.runCommand(usePython, args, {
                cwd: this.pythonAgentPath,
                env
            });
            
            return {
                success: result.code === 0,
                output: result.stdout,
                error: result.stderr,
                executionTime: result.executionTime
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message,
                executionTime: 0
            };
        }
    }

    async generateReport(result, workflow, stage) {
        console.log(chalk.yellow('\n📊 Generating report...'));
        
        const reportsDir = path.join(this.agentDir, 'reports');
        await fs.ensureDir(reportsDir);
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const reportFile = path.join(reportsDir, `${workflow}-${stage}-${timestamp}.json`);
        
        const report = {
            timestamp: new Date().toISOString(),
            workflow,
            stage,
            project: path.basename(this.projectRoot),
            result,
            environment: {
                node_version: process.version,
                platform: process.platform,
                ci: !!process.env.CI
            }
        };
        
        await fs.writeJson(reportFile, report, { spaces: 2 });
        console.log(chalk.green(`✅ Report saved: ${path.relative(this.projectRoot, reportFile)}`));
        
        // Create latest report symlink
        const latestReportFile = path.join(reportsDir, `${workflow}-latest.json`);
        await fs.writeJson(latestReportFile, report, { spaces: 2 });
    }

    async runCommand(command, args, options = {}) {
        const startTime = Date.now();
        
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
                const executionTime = Date.now() - startTime;
                resolve({ stdout, stderr, code, executionTime });
            });
            
            child.on('error', reject);
        });
    }
}

// CLI interface
async function main() {
    const program = new Command();
    
    program
        .name('build-hook')
        .description('Engineering Automation Agent build integration')
        .version('1.0.0');
    
    program
        .option('-w, --workflow <name>', 'Workflow to run', 'code_quality')
        .option('-s, --stage <name>', 'Build stage', 'build')
        .option('-f, --fail-on-error', 'Fail build on automation errors', false)
        .option('-o, --output <file>', 'Output file for results')
        .option('-c, --config <file>', 'Configuration file');
    
    program.parse();
    
    const options = program.opts();
    const buildHook = new BuildHook();
    
    await buildHook.run(options);
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error(chalk.red('Build hook failed:'), error);
        process.exit(1);
    });
}

module.exports = BuildHook;
