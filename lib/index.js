/**
 * Jeeves4coders - Main Library
 * Node.js interface for your intelligent coding assistant
 */

const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('cross-spawn');
const { EventEmitter } = require('events');

class Jeeves4coders extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.options = {
            projectRoot: options.projectRoot || process.cwd(),
            pythonPath: options.pythonPath || null,
            configFile: options.configFile || null,
            silent: options.silent || false,
            ...options
        };
        
        this.packageRoot = path.resolve(__dirname, '..');
        this.pythonAgentPath = path.join(this.packageRoot, 'python-agent');
        this.isWindows = process.platform === 'win32';
        this.pythonCmd = this.isWindows ? 'python' : 'python3';
    }

    /**
     * Initialize the agent for a project
     */
    async init(options = {}) {
        const args = ['init'];
        
        if (options.project) args.push('--project', options.project);
        if (options.root) args.push('--root', options.root);
        if (options.template) args.push('--template', options.template);
        if (options.config) args.push('--config', options.config);
        
        return await this.runPythonAgent(args);
    }

    /**
     * Run a specific workflow
     */
    async runWorkflow(workflowName, options = {}) {
        const args = ['workflow', workflowName];
        
        if (options.project) args.push('--project', options.project);
        if (options.config) args.push('--config', options.config);
        if (options.output) args.push('--output', options.output);
        
        return await this.runPythonAgent(args);
    }

    /**
     * Run a specific module
     */
    async runModule(moduleName, options = {}) {
        const args = ['run', moduleName];
        
        if (options.project) args.push('--project', options.project);
        if (options.config) args.push('--config', options.config);
        if (options.output) args.push('--output', options.output);
        
        return await this.runPythonAgent(args);
    }

    /**
     * Get agent version information
     */
    async getVersion() {
        const result = await this.runPythonAgent(['version'], { capture: true });
        return result.stdout;
    }

    /**
     * Get agent status
     */
    async getStatus() {
        try {
            await this.runPythonAgent(['version'], { capture: true, silent: true });
            return { status: 'healthy', message: 'Agent is working correctly' };
        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    /**
     * Create project configuration
     */
    async createConfig(options = {}) {
        const args = ['config', 'create'];
        
        if (options.project) args.push('--project', options.project);
        if (options.root) args.push('--root', options.root);
        if (options.template) args.push('--template', options.template);
        if (options.output) args.push('--output', options.output);
        
        return await this.runPythonAgent(args);
    }

    /**
     * Load project configuration
     */
    async loadConfig(projectName = null) {
        const configPath = this.options.configFile || 
                          path.join(this.options.projectRoot, '.engineering-agent.json');
        
        if (await fs.pathExists(configPath)) {
            return await fs.readJson(configPath);
        }
        
        return null;
    }

    /**
     * Save project configuration
     */
    async saveConfig(config) {
        const configPath = this.options.configFile || 
                          path.join(this.options.projectRoot, '.engineering-agent.json');
        
        await fs.writeJson(configPath, config, { spaces: 2 });
    }

    /**
     * Get available workflows
     */
    getAvailableWorkflows() {
        return [
            'full_analysis',
            'code_quality',
            'deployment',
            'reporting',
            'ci_cd'
        ];
    }

    /**
     * Get available modules
     */
    getAvailableModules() {
        return [
            'code_review',
            'test_suite',
            'github',
            'jira',
            'confluence'
        ];
    }

    /**
     * Check if agent is properly installed
     */
    async isInstalled() {
        try {
            const coreAgentPath = path.join(this.pythonAgentPath, 'core_agent.py');
            return await fs.pathExists(coreAgentPath);
        } catch (error) {
            return false;
        }
    }

    /**
     * Run the Python agent with specified arguments
     */
    async runPythonAgent(args, options = {}) {
        const opts = { ...this.options, ...options };
        
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
            ENGINEERING_AGENT_PROJECT_ROOT: this.options.projectRoot
        };

        return new Promise((resolve, reject) => {
            const stdio = opts.capture ? 'pipe' : (opts.silent ? 'ignore' : 'inherit');
            
            const child = spawn(command, commandArgs, {
                stdio,
                cwd: this.pythonAgentPath,
                env
            });
            
            let stdout = '';
            let stderr = '';
            
            if (opts.capture) {
                child.stdout?.on('data', (data) => {
                    stdout += data.toString();
                    this.emit('stdout', data.toString());
                });
                
                child.stderr?.on('data', (data) => {
                    stderr += data.toString();
                    this.emit('stderr', data.toString());
                });
            }
            
            child.on('close', (code) => {
                if (code === 0) {
                    resolve(opts.capture ? { stdout, stderr, code } : { code });
                } else {
                    const error = new Error(`Python agent exited with code ${code}`);
                    error.code = code;
                    error.stdout = stdout;
                    error.stderr = stderr;
                    reject(error);
                }
            });
            
            child.on('error', (error) => {
                this.emit('error', error);
                reject(error);
            });
        });
    }
}

/**
 * Convenience function to create and initialize Jeeves4coders
 */
async function createAgent(options = {}) {
    const agent = new Jeeves4coders(options);

    // Check if agent is installed
    if (!(await agent.isInstalled())) {
        throw new Error('Jeeves4coders is not properly installed');
    }

    return agent;
}

/**
 * Quick workflow execution
 */
async function runWorkflow(workflowName, options = {}) {
    const agent = await createAgent(options);
    return await agent.runWorkflow(workflowName, options);
}

/**
 * Quick module execution
 */
async function runModule(moduleName, options = {}) {
    const agent = await createAgent(options);
    return await agent.runModule(moduleName, options);
}

module.exports = {
    Jeeves4coders,
    EngineeringAutomationAgent: Jeeves4coders, // Backward compatibility
    createAgent,
    runWorkflow,
    runModule
};
