#!/usr/bin/env node
/**
 * Engineering Automation Agent - Publish Check Script
 * Validates the package before publishing to npm
 */

const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('cross-spawn');
const chalk = require('chalk');

class PublishChecker {
    constructor() {
        this.packageRoot = path.resolve(__dirname, '..');
        this.errors = [];
        this.warnings = [];
    }

    async runChecks() {
        console.log(chalk.blue('📦 Engineering Automation Agent - Publish Check'));
        console.log(chalk.blue('================================================'));

        try {
            await this.checkPackageJson();
            await this.checkRequiredFiles();
            await this.checkDirectoryStructure();
            await this.checkScripts();
            await this.checkDependencies();
            await this.checkLicense();
            await this.checkReadme();
            await this.runTests();
            
            this.showResults();
            
        } catch (error) {
            console.error(chalk.red('\n❌ Publish check failed:'), error.message);
            process.exit(1);
        }
    }

    async checkPackageJson() {
        console.log(chalk.yellow('\n📋 Checking package.json...'));
        
        const packageJsonPath = path.join(this.packageRoot, 'package.json');
        
        if (!(await fs.pathExists(packageJsonPath))) {
            this.addError('package.json not found');
            return;
        }
        
        const packageJson = await fs.readJson(packageJsonPath);
        
        // Check required fields
        const requiredFields = ['name', 'version', 'description', 'main', 'bin', 'author', 'license'];
        for (const field of requiredFields) {
            if (!packageJson[field]) {
                this.addError(`package.json missing required field: ${field}`);
            }
        }
        
        // Check scripts
        const requiredScripts = ['install', 'postinstall', 'test'];
        for (const script of requiredScripts) {
            if (!packageJson.scripts || !packageJson.scripts[script]) {
                this.addWarning(`package.json missing recommended script: ${script}`);
            }
        }
        
        // Check dependencies
        if (!packageJson.dependencies || Object.keys(packageJson.dependencies).length === 0) {
            this.addWarning('No dependencies specified');
        }
        
        console.log(chalk.green('  ✅ package.json structure valid'));
    }

    async checkRequiredFiles() {
        console.log(chalk.yellow('\n📁 Checking required files...'));
        
        const requiredFiles = [
            'README-npm.md',
            'LICENSE',
            'bin/engineering-agent.js',
            'lib/index.js',
            'scripts/install.js',
            'scripts/postinstall.js',
            'scripts/build-hook.js'
        ];
        
        for (const file of requiredFiles) {
            const filePath = path.join(this.packageRoot, file);
            if (await fs.pathExists(filePath)) {
                console.log(chalk.green(`  ✅ ${file}`));
            } else {
                this.addError(`Required file missing: ${file}`);
            }
        }
    }

    async checkDirectoryStructure() {
        console.log(chalk.yellow('\n📂 Checking directory structure...'));
        
        const requiredDirs = [
            'bin',
            'lib', 
            'scripts',
            'python-agent'
        ];
        
        for (const dir of requiredDirs) {
            const dirPath = path.join(this.packageRoot, dir);
            if (await fs.pathExists(dirPath)) {
                console.log(chalk.green(`  ✅ ${dir}/`));
            } else {
                this.addError(`Required directory missing: ${dir}/`);
            }
        }
        
        // Check python-agent has required files
        const pythonFiles = [
            'python-agent/__init__.py',
            'python-agent/core_agent.py',
            'python-agent/cli.py'
        ];
        
        for (const file of pythonFiles) {
            const filePath = path.join(this.packageRoot, file);
            if (await fs.pathExists(filePath)) {
                console.log(chalk.green(`  ✅ ${file}`));
            } else {
                this.addWarning(`Python agent file missing: ${file}`);
            }
        }
    }

    async checkScripts() {
        console.log(chalk.yellow('\n🔧 Checking executable scripts...'));
        
        const scripts = [
            'bin/engineering-agent.js',
            'scripts/install.js',
            'scripts/postinstall.js',
            'scripts/build-hook.js'
        ];
        
        for (const script of scripts) {
            const scriptPath = path.join(this.packageRoot, script);
            
            if (await fs.pathExists(scriptPath)) {
                const content = await fs.readFile(scriptPath, 'utf8');
                
                // Check shebang
                if (!content.startsWith('#!/usr/bin/env node')) {
                    this.addWarning(`Script ${script} missing shebang`);
                }
                
                console.log(chalk.green(`  ✅ ${script}`));
            }
        }
    }

    async checkDependencies() {
        console.log(chalk.yellow('\n📦 Checking dependencies...'));
        
        try {
            // Check if node_modules exists and has required packages
            const nodeModulesPath = path.join(this.packageRoot, 'node_modules');
            
            if (await fs.pathExists(nodeModulesPath)) {
                console.log(chalk.green('  ✅ node_modules exists'));
            } else {
                this.addWarning('node_modules not found - run npm install');
            }
            
            // Try to require main dependencies
            const requiredDeps = ['cross-spawn', 'chalk', 'commander', 'fs-extra'];
            
            for (const dep of requiredDeps) {
                try {
                    require(dep);
                    console.log(chalk.green(`  ✅ ${dep} available`));
                } catch (error) {
                    this.addError(`Dependency ${dep} not available`);
                }
            }
            
        } catch (error) {
            this.addWarning('Could not check dependencies');
        }
    }

    async checkLicense() {
        console.log(chalk.yellow('\n📄 Checking license...'));
        
        const licensePath = path.join(this.packageRoot, 'LICENSE');
        
        if (await fs.pathExists(licensePath)) {
            const license = await fs.readFile(licensePath, 'utf8');
            
            if (license.includes('MIT License')) {
                console.log(chalk.green('  ✅ MIT License found'));
            } else {
                this.addWarning('License file exists but may not be MIT');
            }
        } else {
            this.addError('LICENSE file missing');
        }
    }

    async checkReadme() {
        console.log(chalk.yellow('\n📖 Checking README...'));
        
        const readmePath = path.join(this.packageRoot, 'README-npm.md');
        
        if (await fs.pathExists(readmePath)) {
            const readme = await fs.readFile(readmePath, 'utf8');
            
            const requiredSections = [
                '# Engineering Automation Agent',
                '## Installation',
                '## Usage',
                '## Features'
            ];
            
            for (const section of requiredSections) {
                if (readme.includes(section)) {
                    console.log(chalk.green(`  ✅ ${section} section found`));
                } else {
                    this.addWarning(`README missing section: ${section}`);
                }
            }
        } else {
            this.addError('README-npm.md file missing');
        }
    }

    async runTests() {
        console.log(chalk.yellow('\n🧪 Running tests...'));
        
        try {
            const testScript = path.join(this.packageRoot, 'scripts', 'test.js');
            
            if (await fs.pathExists(testScript)) {
                await this.runCommand('node', [testScript]);
                console.log(chalk.green('  ✅ Tests passed'));
            } else {
                this.addWarning('Test script not found');
            }
            
        } catch (error) {
            this.addError(`Tests failed: ${error.message}`);
        }
    }

    addError(message) {
        this.errors.push(message);
        console.log(chalk.red(`  ❌ ${message}`));
    }

    addWarning(message) {
        this.warnings.push(message);
        console.log(chalk.yellow(`  ⚠️  ${message}`));
    }

    showResults() {
        console.log(chalk.blue('\n📊 Publish Check Results'));
        console.log(chalk.blue('========================='));
        
        console.log(chalk.white(`Errors: ${this.errors.length}`));
        console.log(chalk.white(`Warnings: ${this.warnings.length}`));
        
        if (this.errors.length > 0) {
            console.log(chalk.red('\n❌ Errors that must be fixed:'));
            this.errors.forEach(error => {
                console.log(chalk.red(`  • ${error}`));
            });
        }
        
        if (this.warnings.length > 0) {
            console.log(chalk.yellow('\n⚠️  Warnings (recommended to fix):'));
            this.warnings.forEach(warning => {
                console.log(chalk.yellow(`  • ${warning}`));
            });
        }
        
        if (this.errors.length === 0) {
            console.log(chalk.green('\n🎉 Package is ready for publishing!'));
            console.log(chalk.blue('\n📋 Next steps:'));
            console.log(chalk.white('  1. npm pack (to create tarball)'));
            console.log(chalk.white('  2. npm publish --dry-run (to test)'));
            console.log(chalk.white('  3. npm publish (to publish)'));
        } else {
            console.log(chalk.red('\n🚫 Package is not ready for publishing'));
            console.log(chalk.yellow('Please fix the errors above before publishing'));
            process.exit(1);
        }
    }

    async runCommand(command, args) {
        return new Promise((resolve, reject) => {
            const child = spawn(command, args, {
                stdio: 'pipe',
                cwd: this.packageRoot
            });
            
            child.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Command failed with code ${code}`));
                }
            });
            
            child.on('error', reject);
        });
    }
}

// Run publish check if called directly
if (require.main === module) {
    const checker = new PublishChecker();
    checker.runChecks().catch(error => {
        console.error(chalk.red('Publish check failed:'), error);
        process.exit(1);
    });
}

module.exports = PublishChecker;
