/**
 * Engineering Automation Agent - Build Hooks Integration
 * Provides build system integration for various tools
 */

const fs = require('fs-extra');
const path = require('path');
const { EngineeringAutomationAgent } = require('./index');

class BuildHooksManager {
    constructor(options = {}) {
        this.projectRoot = options.projectRoot || process.cwd();
        this.configFile = options.configFile || path.join(this.projectRoot, '.engineering-agent', 'build-hooks.json');
        this.agent = new EngineeringAutomationAgent(options);
    }

    /**
     * Setup build hooks for different build systems
     */
    async setupBuildHooks(buildSystem = 'npm') {
        const config = await this.loadHooksConfig();
        
        switch (buildSystem.toLowerCase()) {
            case 'npm':
                return await this.setupNpmHooks(config);
            case 'webpack':
                return await this.setupWebpackHooks(config);
            case 'rollup':
                return await this.setupRollupHooks(config);
            case 'vite':
                return await this.setupViteHooks(config);
            case 'parcel':
                return await this.setupParcelHooks(config);
            default:
                throw new Error(`Unsupported build system: ${buildSystem}`);
        }
    }

    /**
     * Setup NPM script hooks
     */
    async setupNpmHooks(config) {
        const packageJsonPath = path.join(this.projectRoot, 'package.json');
        
        if (!(await fs.pathExists(packageJsonPath))) {
            throw new Error('package.json not found');
        }
        
        const packageJson = await fs.readJson(packageJsonPath);
        
        if (!packageJson.scripts) {
            packageJson.scripts = {};
        }
        
        // Add pre/post hooks based on configuration
        const hooks = config.hooks || {};
        
        if (hooks.prebuild?.enabled) {
            packageJson.scripts.prebuild = this.generateNpmScript(hooks.prebuild);
        }
        
        if (hooks.postbuild?.enabled) {
            packageJson.scripts.postbuild = this.generateNpmScript(hooks.postbuild);
        }
        
        if (hooks.pretest?.enabled) {
            packageJson.scripts.pretest = this.generateNpmScript(hooks.pretest);
        }
        
        if (hooks.posttest?.enabled) {
            packageJson.scripts.posttest = this.generateNpmScript(hooks.posttest);
        }
        
        // Add custom engineering scripts
        packageJson.scripts['engineering:lint'] = 'engineering-agent workflow code_quality';
        packageJson.scripts['engineering:audit'] = 'engineering-agent workflow full_analysis';
        packageJson.scripts['engineering:test'] = 'engineering-agent run test_suite';
        packageJson.scripts['engineering:deploy'] = 'engineering-agent workflow deployment';
        
        await fs.writeJson(packageJsonPath, packageJson, { spaces: 2 });
        
        return {
            success: true,
            message: 'NPM hooks configured successfully',
            scripts: Object.keys(packageJson.scripts).filter(s => s.includes('engineering') || s.includes('pre') || s.includes('post'))
        };
    }

    /**
     * Setup Webpack hooks
     */
    async setupWebpackHooks(config) {
        const webpackConfigPath = path.join(this.projectRoot, 'webpack.config.js');
        
        const hookPlugin = `
const { spawn } = require('child_process');

class EngineeringAutomationPlugin {
    constructor(options = {}) {
        this.options = options;
    }
    
    apply(compiler) {
        compiler.hooks.beforeCompile.tapAsync('EngineeringAutomationPlugin', (params, callback) => {
            if (this.options.prebuild) {
                this.runWorkflow(this.options.prebuild.workflow, callback);
            } else {
                callback();
            }
        });
        
        compiler.hooks.afterEmit.tapAsync('EngineeringAutomationPlugin', (compilation, callback) => {
            if (this.options.postbuild) {
                this.runWorkflow(this.options.postbuild.workflow, callback);
            } else {
                callback();
            }
        });
    }
    
    runWorkflow(workflow, callback) {
        const child = spawn('npx', ['engineering-agent', 'workflow', workflow], {
            stdio: 'inherit'
        });
        
        child.on('close', (code) => {
            if (code === 0 || !this.options.failOnError) {
                callback();
            } else {
                callback(new Error(\`Engineering automation failed with code \${code}\`));
            }
        });
    }
}

module.exports = EngineeringAutomationPlugin;
`;

        const pluginPath = path.join(this.projectRoot, 'engineering-automation-webpack-plugin.js');
        await fs.writeFile(pluginPath, hookPlugin);
        
        return {
            success: true,
            message: 'Webpack plugin created',
            pluginPath,
            usage: `
// Add to your webpack.config.js:
const EngineeringAutomationPlugin = require('./engineering-automation-webpack-plugin');

module.exports = {
    // ... your config
    plugins: [
        new EngineeringAutomationPlugin({
            prebuild: { workflow: 'code_quality' },
            postbuild: { workflow: 'reporting' },
            failOnError: false
        })
    ]
};`
        };
    }

    /**
     * Setup Vite hooks
     */
    async setupViteHooks(config) {
        const vitePluginCode = `
import { spawn } from 'child_process';

export function engineeringAutomationPlugin(options = {}) {
    return {
        name: 'engineering-automation',
        buildStart() {
            if (options.prebuild) {
                return this.runWorkflow(options.prebuild.workflow);
            }
        },
        buildEnd() {
            if (options.postbuild) {
                return this.runWorkflow(options.postbuild.workflow);
            }
        },
        runWorkflow(workflow) {
            return new Promise((resolve, reject) => {
                const child = spawn('npx', ['engineering-agent', 'workflow', workflow], {
                    stdio: 'inherit'
                });
                
                child.on('close', (code) => {
                    if (code === 0 || !options.failOnError) {
                        resolve();
                    } else {
                        reject(new Error(\`Engineering automation failed with code \${code}\`));
                    }
                });
            });
        }
    };
}
`;

        const pluginPath = path.join(this.projectRoot, 'engineering-automation-vite-plugin.js');
        await fs.writeFile(pluginPath, vitePluginCode);
        
        return {
            success: true,
            message: 'Vite plugin created',
            pluginPath,
            usage: `
// Add to your vite.config.js:
import { engineeringAutomationPlugin } from './engineering-automation-vite-plugin.js';

export default {
    plugins: [
        engineeringAutomationPlugin({
            prebuild: { workflow: 'code_quality' },
            postbuild: { workflow: 'reporting' },
            failOnError: false
        })
    ]
};`
        };
    }

    /**
     * Generate NPM script command
     */
    generateNpmScript(hookConfig) {
        const workflow = hookConfig.workflow || 'code_quality';
        const failFlag = hookConfig.fail_on_error ? '' : ' || true';
        
        return `engineering-agent workflow ${workflow}${failFlag}`;
    }

    /**
     * Load hooks configuration
     */
    async loadHooksConfig() {
        if (await fs.pathExists(this.configFile)) {
            return await fs.readJson(this.configFile);
        }
        
        // Return default configuration
        return {
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
                reporting: ["test_suite", "confluence"],
                deployment: ["test_suite", "github", "jira"]
            }
        };
    }

    /**
     * Save hooks configuration
     */
    async saveHooksConfig(config) {
        await fs.ensureDir(path.dirname(this.configFile));
        await fs.writeJson(this.configFile, config, { spaces: 2 });
    }

    /**
     * Create GitHub Actions workflow
     */
    async createGitHubActionsWorkflow() {
        const workflowContent = `name: Engineering Automation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  engineering-automation:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
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
      run: npm run engineering:audit
      env:
        GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
        JIRA_API_TOKEN: \${{ secrets.JIRA_API_TOKEN }}
        CONFLUENCE_API_TOKEN: \${{ secrets.CONFLUENCE_API_TOKEN }}
    
    - name: Upload Reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: engineering-reports
        path: .engineering-agent/reports/
`;

        const workflowDir = path.join(this.projectRoot, '.github', 'workflows');
        await fs.ensureDir(workflowDir);
        
        const workflowPath = path.join(workflowDir, 'engineering-automation.yml');
        await fs.writeFile(workflowPath, workflowContent);
        
        return {
            success: true,
            message: 'GitHub Actions workflow created',
            path: workflowPath
        };
    }
}

module.exports = {
    BuildHooksManager
};
