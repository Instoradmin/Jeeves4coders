#!/usr/bin/env node
/**
 * Engineering Automation Agent - Pre-uninstall Script
 * Cleans up before package removal
 */

const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');

class PreUninstaller {
    constructor() {
        this.projectRoot = process.cwd();
    }

    async run() {
        console.log(chalk.blue('\n🧹 Engineering Automation Agent - Cleanup'));
        console.log(chalk.blue('=========================================='));

        try {
            await this.promptUserForCleanup();
            await this.cleanupConfiguration();
            await this.showFarewellMessage();
            
        } catch (error) {
            console.error(chalk.red('\n❌ Cleanup failed:'), error.message);
            // Don't exit with error code as this is not critical
        }
    }

    async promptUserForCleanup() {
        console.log(chalk.yellow('\n🤔 What would you like to keep?'));
        console.log(chalk.white('  Configuration files and reports will be preserved by default.'));
        console.log(chalk.white('  You can manually remove .engineering-agent/ directory if needed.'));
    }

    async cleanupConfiguration() {
        console.log(chalk.yellow('\n🧹 Cleaning up temporary files...'));
        
        // Clean up temporary files but preserve configuration
        const tempDirs = [
            path.join(this.projectRoot, '.engineering-agent', 'temp'),
            path.join(this.projectRoot, '.engineering-agent', 'cache'),
            path.join(this.projectRoot, 'node_modules', 'engineering-automation-agent', 'python-agent', 'venv')
        ];
        
        for (const tempDir of tempDirs) {
            if (await fs.pathExists(tempDir)) {
                await fs.remove(tempDir);
                console.log(chalk.green(`  ✅ Removed: ${path.relative(this.projectRoot, tempDir)}`));
            }
        }
        
        // Clean up log files older than 30 days
        const logsDir = path.join(this.projectRoot, '.engineering-agent', 'logs');
        if (await fs.pathExists(logsDir)) {
            const files = await fs.readdir(logsDir);
            const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
            
            for (const file of files) {
                const filePath = path.join(logsDir, file);
                const stats = await fs.stat(filePath);
                
                if (stats.mtime.getTime() < thirtyDaysAgo) {
                    await fs.remove(filePath);
                    console.log(chalk.green(`  ✅ Removed old log: ${file}`));
                }
            }
        }
        
        console.log(chalk.green('✅ Cleanup completed'));
    }

    async showFarewellMessage() {
        console.log(chalk.blue('\n👋 Engineering Automation Agent has been removed'));
        console.log(chalk.yellow('\n📁 Preserved files:'));
        console.log(chalk.white('  .engineering-agent.json           - Main configuration'));
        console.log(chalk.white('  .engineering-agent/               - Local configuration and reports'));
        console.log(chalk.white('  package.json scripts              - Added npm scripts'));
        
        console.log(chalk.yellow('\n🗑️  To completely remove all traces:'));
        console.log(chalk.white('  rm -rf .engineering-agent/'));
        console.log(chalk.white('  rm .engineering-agent.json'));
        console.log(chalk.white('  # Remove engineering-agent scripts from package.json'));
        
        console.log(chalk.blue('\n💙 Thank you for using Engineering Automation Agent!'));
        console.log(chalk.white('  If you have feedback, please visit:'));
        console.log(chalk.white('  https://github.com/Instoradmin/Jeeves4coders/issues'));
    }
}

// Run pre-uninstall if called directly
if (require.main === module) {
    const preUninstaller = new PreUninstaller();
    preUninstaller.run().catch(error => {
        console.error(chalk.red('Pre-uninstall failed:'), error);
        // Don't exit with error code
    });
}

module.exports = PreUninstaller;
