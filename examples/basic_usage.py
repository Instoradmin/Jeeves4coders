#!/usr/bin/env python3
"""
Basic Usage Examples for Engineering Automation Agent
Demonstrates common usage patterns and workflows
"""

import os
import sys
import json
from pathlib import Path

# Add the agent to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engineering_automation_agent import (
    EngineeringAutomationAgent,
    AgentConfig,
    quick_start,
    run_workflow,
    get_default_workflows,
    ConfigurationManager
)

def example_quick_start():
    """Example: Quick start with auto-detection"""
    print("🚀 Example: Quick Start")
    print("=" * 50)
    
    # Quick start - automatically detects project type and creates configuration
    project_root = "."
    project_name = "example-project"
    
    agent = quick_start(project_root, project_name)
    
    print(f"✅ Agent initialized for project: {project_name}")
    print(f"📦 Modules loaded: {list(agent.modules.keys())}")
    print(f"🔧 Project type: {agent.config.project_type}")
    print()

def example_custom_configuration():
    """Example: Custom configuration"""
    print("⚙️ Example: Custom Configuration")
    print("=" * 50)
    
    # Create custom configuration
    config = AgentConfig(
        project_name="custom-project",
        project_root=".",
        project_type="python",
        
        # Enable specific modules
        test_enabled=True,
        test_types=["unit", "functional"],
        test_coverage_threshold=85.0,
        
        code_review_enabled=True,
        code_quality_threshold=8.5,
        
        # Disable integrations for this example
        github_enabled=False,
        jira_enabled=False,
        confluence_enabled=False,
        
        # Notification settings
        notifications_enabled=True,
        notification_channels=["console"]
    )
    
    # Create agent with custom configuration
    agent = EngineeringAutomationAgent(config)
    
    # Register modules manually (since we're using custom config)
    from engineering_automation_agent import CodeReviewModule, TestSuiteModule
    
    if config.code_review_enabled:
        agent.register_module('code_review', CodeReviewModule(config, agent.logger))
    
    if config.test_enabled:
        agent.register_module('test_suite', TestSuiteModule(config, agent.logger))
    
    print(f"✅ Agent created with custom configuration")
    print(f"📦 Modules: {list(agent.modules.keys())}")
    print()

def example_run_individual_modules():
    """Example: Run individual modules"""
    print("🔧 Example: Run Individual Modules")
    print("=" * 50)
    
    # Create agent
    agent = quick_start(".", "module-example")
    
    # Run code review module
    if 'code_review' in agent.modules:
        print("🔍 Running code review...")
        result = agent.execute_module('code_review')
        
        if result.success:
            print(f"✅ Code review completed in {result.execution_time:.2f}s")
            
            # Show some results
            if 'summary' in result.data:
                summary = result.data['summary']
                print(f"📊 Quality grade: {summary.get('quality_grade', 'N/A')}")
                print(f"🐛 Total issues: {summary.get('total_issues', 0)}")
        else:
            print(f"❌ Code review failed: {result.errors}")
    
    # Run test suite module
    if 'test_suite' in agent.modules:
        print("\n🧪 Running test suite...")
        result = agent.execute_module('test_suite')
        
        if result.success:
            print(f"✅ Test suite completed in {result.execution_time:.2f}s")
            
            # Show test results
            if 'suite_results' in result.data:
                suite = result.data['suite_results']
                print(f"📊 Success rate: {suite.get('success_rate', 0):.1f}%")
                print(f"🧪 Tests: {suite.get('passed_tests', 0)}/{suite.get('total_tests', 0)}")
        else:
            print(f"❌ Test suite failed: {result.errors}")
    
    print()

def example_run_workflows():
    """Example: Run predefined workflows"""
    print("🔄 Example: Run Workflows")
    print("=" * 50)
    
    # Create agent
    agent = quick_start(".", "workflow-example")
    
    # Show available workflows
    workflows = get_default_workflows()
    print("📋 Available workflows:")
    for name, modules in workflows.items():
        print(f"  • {name}: {' → '.join(modules)}")
    
    # Run code quality workflow
    print("\n🔄 Running code quality workflow...")
    try:
        results = run_workflow(agent, 'code_quality')
        
        # Show workflow results
        successful = sum(1 for r in results if r.success)
        total = len(results)
        total_time = sum(r.execution_time for r in results)
        
        print(f"📊 Workflow completed: {successful}/{total} modules successful")
        print(f"⏱️ Total time: {total_time:.2f}s")
        
        # Show individual results
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.module_name} ({result.execution_time:.2f}s)")
    
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
    
    print()

def example_configuration_management():
    """Example: Configuration management"""
    print("⚙️ Example: Configuration Management")
    print("=" * 50)
    
    # Create configuration manager
    config_manager = ConfigurationManager()
    
    # List available templates
    templates = config_manager.list_templates()
    print("📋 Available templates:")
    for template in templates:
        template_info = config_manager.get_template_config(template)
        print(f"  • {template}: {template_info.get('description', 'No description')}")
    
    # Create project configuration using template
    print("\n📝 Creating project configuration...")
    config = config_manager.create_project_config(
        project_name="template-example",
        project_root=".",
        template_name="python_web"
    )
    
    print(f"✅ Configuration created for project: {config.project_name}")
    print(f"🏗️ Project type: {config.project_type}")
    print(f"🧪 Test types: {config.test_types}")
    
    # List configured projects
    projects = config_manager.list_projects()
    print(f"\n📋 Configured projects: {projects}")
    
    print()

def example_save_and_load_results():
    """Example: Save and load execution results"""
    print("💾 Example: Save and Load Results")
    print("=" * 50)
    
    # Create agent and run some modules
    agent = quick_start(".", "results-example")
    
    # Execute a workflow
    if agent.modules:
        # Run available modules
        for module_name in list(agent.modules.keys())[:2]:  # Run first 2 modules
            result = agent.execute_module(module_name)
            print(f"📊 Executed {module_name}: {'✅' if result.success else '❌'}")
    
    # Get execution summary
    summary = agent.get_execution_summary()
    
    # Save results to file
    results_file = "agent_results.json"
    agent.save_results(results_file)
    print(f"💾 Results saved to: {results_file}")
    
    # Load and display results
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            loaded_results = json.load(f)
        
        print(f"📊 Loaded results:")
        print(f"  • Total modules: {loaded_results['total_modules']}")
        print(f"  • Success rate: {loaded_results['success_rate']:.1f}%")
        print(f"  • Total time: {loaded_results['total_execution_time']:.2f}s")
        
        # Clean up
        os.remove(results_file)
        print(f"🗑️ Cleaned up results file")
    
    print()

def example_error_handling():
    """Example: Error handling and validation"""
    print("🛡️ Example: Error Handling")
    print("=" * 50)
    
    # Example of handling configuration errors
    try:
        # Create invalid configuration
        invalid_config = AgentConfig(
            project_name="",  # Invalid: empty name
            project_root="/nonexistent/path",  # Invalid: doesn't exist
            test_coverage_threshold=150.0  # Invalid: > 100
        )
        
        # Validate configuration
        config_manager = ConfigurationManager()
        issues = config_manager.validate_project_config(invalid_config)
        
        if issues:
            print("❌ Configuration validation failed:")
            for issue in issues:
                print(f"  • {issue}")
        else:
            print("✅ Configuration is valid")
    
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
    
    # Example of handling module execution errors
    try:
        # Create agent with minimal config
        config = AgentConfig(
            project_name="error-example",
            project_root=".",
            test_enabled=True
        )
        
        agent = EngineeringAutomationAgent(config)
        
        # Try to execute non-existent module
        result = agent.execute_module('nonexistent_module')
        
        if not result.success:
            print(f"❌ Module execution failed: {result.errors[0]}")
    
    except Exception as e:
        print(f"❌ Execution error: {str(e)}")
    
    print()

def main():
    """Run all examples"""
    print("🤖 Engineering Automation Agent - Basic Usage Examples")
    print("=" * 60)
    print()
    
    # Run examples
    example_quick_start()
    example_custom_configuration()
    example_run_individual_modules()
    example_run_workflows()
    example_configuration_management()
    example_save_and_load_results()
    example_error_handling()
    
    print("🎉 All examples completed!")
    print("=" * 60)
    print()
    print("📚 Next steps:")
    print("• Explore the CLI: engineering-agent --help")
    print("• Create your own configuration")
    print("• Customize workflows for your project")
    print("• Integrate with your CI/CD pipeline")

if __name__ == "__main__":
    main()
