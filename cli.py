#!/usr/bin/env python3
"""
Command Line Interface for Engineering Automation Agent
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

from . import (
    EngineeringAutomationAgent,
    ConfigurationManager,
    create_agent_from_config,
    quick_start,
    run_workflow,
    get_default_workflows,
    get_version_info
)

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.command == 'init':
            handle_init(args)
        elif args.command == 'run':
            handle_run(args)
        elif args.command == 'config':
            handle_config(args)
        elif args.command == 'workflow':
            handle_workflow(args)
        elif args.command == 'version':
            handle_version(args)
        else:
            parser.print_help()
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Engineering Automation Agent - Comprehensive project automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize agent for current project
  engineering-agent init

  # Run full analysis workflow
  engineering-agent workflow full_analysis

  # Run specific module
  engineering-agent run code_review

  # Create project configuration
  engineering-agent config create --project myproject --root /path/to/project

  # Show version information
  engineering-agent version
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize agent for current project')
    init_parser.add_argument('--project', help='Project name (auto-detected if not provided)')
    init_parser.add_argument('--root', default='.', help='Project root directory (default: current directory)')
    init_parser.add_argument('--template', help='Project template to use')
    init_parser.add_argument('--config', help='Configuration file to use')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run specific module')
    run_parser.add_argument('module', help='Module to run (code_review, test_suite, github, jira, confluence)')
    run_parser.add_argument('--project', help='Project name')
    run_parser.add_argument('--config', help='Configuration file')
    run_parser.add_argument('--output', help='Output file for results')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configurations')
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Configuration actions')
    
    # Config create
    create_parser = config_subparsers.add_parser('create', help='Create new project configuration')
    create_parser.add_argument('--project', required=True, help='Project name')
    create_parser.add_argument('--root', required=True, help='Project root directory')
    create_parser.add_argument('--template', help='Project template')
    create_parser.add_argument('--output', help='Output configuration file')
    
    # Config list
    config_subparsers.add_parser('list', help='List all project configurations')
    
    # Config show
    show_parser = config_subparsers.add_parser('show', help='Show project configuration')
    show_parser.add_argument('project', help='Project name')
    
    # Config delete
    delete_parser = config_subparsers.add_parser('delete', help='Delete project configuration')
    delete_parser.add_argument('project', help='Project name')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run predefined workflows')
    workflow_parser.add_argument('workflow', help='Workflow to run', choices=list(get_default_workflows().keys()))
    workflow_parser.add_argument('--project', help='Project name')
    workflow_parser.add_argument('--config', help='Configuration file')
    workflow_parser.add_argument('--output', help='Output file for results')
    
    # Version command
    subparsers.add_parser('version', help='Show version information')
    
    return parser

def handle_init(args):
    """Handle init command"""
    print("🚀 Initializing Engineering Automation Agent...")
    
    project_root = os.path.abspath(args.root)
    project_name = args.project or os.path.basename(project_root)
    
    print(f"📁 Project: {project_name}")
    print(f"📂 Root: {project_root}")
    
    if args.config:
        # Load from configuration file
        agent = create_agent_from_config(
            config_file=args.config,
            project_name=project_name,
            project_root=project_root
        )
    else:
        # Quick start with auto-detection
        agent = quick_start(project_root, project_name)
    
    print(f"✅ Agent initialized successfully!")
    print(f"📊 Modules loaded: {len(agent.modules)}")
    
    # Show available modules
    if agent.modules:
        print("\n📋 Available modules:")
        for module_name in agent.modules.keys():
            print(f"  • {module_name}")
    
    # Show available workflows
    workflows = get_default_workflows()
    print(f"\n🔄 Available workflows:")
    for workflow_name in workflows.keys():
        print(f"  • {workflow_name}")

def handle_run(args):
    """Handle run command"""
    print(f"🔄 Running module: {args.module}")
    
    # Create agent
    if args.config:
        agent = create_agent_from_config(args.config)
    else:
        project_root = "."
        project_name = args.project or os.path.basename(os.path.abspath(project_root))
        agent = quick_start(project_root, project_name)
    
    # Execute module
    result = agent.execute_module(args.module)
    
    # Show results
    if result.success:
        print(f"✅ Module '{args.module}' completed successfully in {result.execution_time:.2f}s")
    else:
        print(f"❌ Module '{args.module}' failed:")
        for error in result.errors:
            print(f"  • {error}")
    
    # Save results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result.to_dict(), f, indent=2, default=str)
        print(f"💾 Results saved to: {args.output}")

def handle_config(args):
    """Handle config command"""
    config_manager = ConfigurationManager()
    
    if args.config_action == 'create':
        print(f"📝 Creating configuration for project: {args.project}")
        
        config = config_manager.create_project_config(
            project_name=args.project,
            project_root=args.root,
            template_name=args.template
        )
        
        print(f"✅ Configuration created successfully!")
        
        if args.output:
            config_manager.save_config_to_file(config, args.output)
            print(f"💾 Configuration saved to: {args.output}")
    
    elif args.config_action == 'list':
        projects = config_manager.list_projects()
        
        if projects:
            print("📋 Configured projects:")
            for project in projects:
                print(f"  • {project}")
        else:
            print("📋 No projects configured")
    
    elif args.config_action == 'show':
        config = config_manager.load_project_config(args.project)
        
        if config:
            print(f"📊 Configuration for project: {args.project}")
            config_dict = config.__dict__
            for key, value in config_dict.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Project '{args.project}' not found")
    
    elif args.config_action == 'delete':
        success = config_manager.delete_project_config(args.project)
        
        if success:
            print(f"✅ Configuration for project '{args.project}' deleted")
        else:
            print(f"❌ Project '{args.project}' not found")

def handle_workflow(args):
    """Handle workflow command"""
    print(f"🔄 Running workflow: {args.workflow}")
    
    # Create agent
    if args.config:
        agent = create_agent_from_config(args.config)
    else:
        project_root = "."
        project_name = args.project or os.path.basename(os.path.abspath(project_root))
        agent = quick_start(project_root, project_name)
    
    # Execute workflow
    results = run_workflow(agent, args.workflow)
    
    # Show results
    successful_modules = sum(1 for r in results if r.success)
    total_modules = len(results)
    total_time = sum(r.execution_time for r in results)
    
    print(f"\n📊 Workflow Results:")
    print(f"  • Total modules: {total_modules}")
    print(f"  • Successful: {successful_modules}")
    print(f"  • Failed: {total_modules - successful_modules}")
    print(f"  • Total time: {total_time:.2f}s")
    
    # Show individual results
    print(f"\n📋 Module Results:")
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"  {status} {result.module_name} ({result.execution_time:.2f}s)")
        
        if not result.success:
            for error in result.errors:
                print(f"    • {error}")
    
    # Save results if output file specified
    if args.output:
        summary = agent.get_execution_summary()
        with open(args.output, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"💾 Results saved to: {args.output}")

def handle_version(args):
    """Handle version command"""
    version_info = get_version_info()
    
    print(f"🤖 Engineering Automation Agent")
    print(f"Version: {version_info['version']}")
    print(f"Author: {version_info['author']}")
    print(f"Description: {version_info['description']}")
    
    print(f"\n📦 Available Modules:")
    for module in version_info['modules']:
        print(f"  • {module}")
    
    print(f"\n🔄 Available Workflows:")
    workflows = get_default_workflows()
    for workflow_name, modules in workflows.items():
        print(f"  • {workflow_name}: {' -> '.join(modules)}")

if __name__ == '__main__':
    main()
