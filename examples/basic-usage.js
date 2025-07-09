#!/usr/bin/env node
/**
 * Engineering Automation Agent - Basic Usage Example
 * Demonstrates how to use the agent programmatically
 */

const { EngineeringAutomationAgent, runWorkflow, runModule } = require('engineering-automation-agent');

async function basicExample() {
    console.log('🤖 Engineering Automation Agent - Basic Example');
    console.log('===============================================');

    try {
        // Method 1: Quick workflow execution
        console.log('\n📋 Method 1: Quick workflow execution');
        await runWorkflow('code_quality', {
            projectRoot: process.cwd(),
            silent: false
        });

        // Method 2: Using agent instance
        console.log('\n📋 Method 2: Using agent instance');
        const agent = new EngineeringAutomationAgent({
            projectRoot: process.cwd(),
            silent: false
        });

        // Initialize agent
        await agent.init({
            project: 'example-project',
            template: 'default'
        });

        // Run individual modules
        await agent.runModule('code_review');
        
        // Run workflows
        await agent.runWorkflow('code_quality');

        // Get status
        const status = await agent.getStatus();
        console.log('Agent status:', status);

        console.log('\n✅ Example completed successfully!');

    } catch (error) {
        console.error('\n❌ Example failed:', error.message);
        process.exit(1);
    }
}

async function advancedExample() {
    console.log('\n🚀 Advanced Example - Event Handling');
    console.log('====================================');

    const agent = new EngineeringAutomationAgent({
        projectRoot: process.cwd()
    });

    // Listen to events
    agent.on('stdout', (data) => {
        console.log('📤 Agent output:', data.trim());
    });

    agent.on('stderr', (data) => {
        console.error('📥 Agent error:', data.trim());
    });

    agent.on('error', (error) => {
        console.error('💥 Agent error:', error.message);
    });

    try {
        // Load configuration
        const config = await agent.loadConfig();
        console.log('📊 Current config:', config);

        // Run workflow with output capture
        const result = await agent.runWorkflow('code_quality', {
            output: './reports/code-quality.json'
        });

        console.log('📈 Workflow result:', result);

    } catch (error) {
        console.error('❌ Advanced example failed:', error.message);
    }
}

async function configurationExample() {
    console.log('\n⚙️  Configuration Example');
    console.log('========================');

    const agent = new EngineeringAutomationAgent();

    try {
        // Create custom configuration
        const customConfig = {
            version: "1.0.0",
            project_name: "my-custom-project",
            project_root: process.cwd(),
            auto_run_on_build: true,
            default_workflow: "full_analysis",
            modules: {
                code_review: {
                    enabled: true,
                    config: {
                        quality_threshold: 9.0,
                        check_duplicates: true
                    }
                },
                test_suite: {
                    enabled: true,
                    config: {
                        coverage_threshold: 90.0
                    }
                }
            }
        };

        // Save configuration
        await agent.saveConfig(customConfig);
        console.log('✅ Custom configuration saved');

        // Load and verify
        const loadedConfig = await agent.loadConfig();
        console.log('📊 Loaded config:', loadedConfig.project_name);

    } catch (error) {
        console.error('❌ Configuration example failed:', error.message);
    }
}

// Run examples
async function main() {
    const example = process.argv[2] || 'basic';

    switch (example) {
        case 'basic':
            await basicExample();
            break;
        case 'advanced':
            await advancedExample();
            break;
        case 'config':
            await configurationExample();
            break;
        case 'all':
            await basicExample();
            await advancedExample();
            await configurationExample();
            break;
        default:
            console.log('Usage: node basic-usage.js [basic|advanced|config|all]');
            break;
    }
}

if (require.main === module) {
    main().catch(error => {
        console.error('Example failed:', error);
        process.exit(1);
    });
}

module.exports = {
    basicExample,
    advancedExample,
    configurationExample
};
