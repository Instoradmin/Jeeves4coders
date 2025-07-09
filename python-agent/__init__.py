#!/usr/bin/env python3
"""
Engineering Automation Agent Package
Comprehensive automation agent for engineering and housekeeping activities
"""

# Import version information
from .version import __version__, __version_info__, RELEASE_NAME, get_version, get_release_info

__author__ = "Engineering Automation Team"
__description__ = "Comprehensive automation agent for engineering and housekeeping activities"

# Core imports
from .core_agent import EngineeringAutomationAgent, AgentConfig, AgentModule, ExecutionResult
from .config_manager import ConfigurationManager

# Module imports
from .code_review_module import CodeReviewModule
from .test_suite_module import TestSuiteModule
from .github_module import GitHubModule
from .jira_module import JiraModule
from .confluence_module import ConfluenceModule

# Utility functions
from .core_agent import load_config_from_file, create_default_config

__all__ = [
    # Core classes
    'EngineeringAutomationAgent',
    'AgentConfig',
    'AgentModule',
    'ExecutionResult',
    'ConfigurationManager',
    
    # Module classes
    'CodeReviewModule',
    'TestSuiteModule',
    'GitHubModule',
    'JiraModule',
    'ConfluenceModule',
    
    # Utility functions
    'load_config_from_file',
    'create_default_config',
    
    # Package metadata
    '__version__',
    '__author__',
    '__description__'
]

def create_agent_from_config(config_file: str = None, project_name: str = None, project_root: str = None) -> EngineeringAutomationAgent:
    """
    Create an Engineering Automation Agent from configuration
    
    Args:
        config_file: Path to configuration file (optional)
        project_name: Name of the project (optional)
        project_root: Root directory of the project (optional)
    
    Returns:
        EngineeringAutomationAgent: Configured agent instance
    """
    if config_file:
        config = load_config_from_file(config_file)
        if not config:
            raise ValueError(f"Failed to load configuration from {config_file}")
    else:
        # Create default configuration
        config = create_default_config(
            project_root or ".",
            project_name or "default-project"
        )
    
    # Create agent
    agent = EngineeringAutomationAgent(config)
    
    # Register modules
    register_default_modules(agent)
    
    return agent

def register_default_modules(agent: EngineeringAutomationAgent):
    """
    Register default modules with the agent
    
    Args:
        agent: EngineeringAutomationAgent instance
    """
    # Register code review module
    if agent.config.code_review_enabled:
        code_review_module = CodeReviewModule(agent.config, agent.logger)
        agent.register_module('code_review', code_review_module)
    
    # Register test suite module
    if agent.config.test_enabled:
        test_suite_module = TestSuiteModule(agent.config, agent.logger)
        agent.register_module('test_suite', test_suite_module)
    
    # Register GitHub module
    if agent.config.github_enabled:
        github_module = GitHubModule(agent.config, agent.logger)
        agent.register_module('github', github_module)
    
    # Register JIRA module
    if agent.config.jira_enabled:
        jira_module = JiraModule(agent.config, agent.logger)
        agent.register_module('jira', jira_module)
    
    # Register Confluence module
    if agent.config.confluence_enabled:
        confluence_module = ConfluenceModule(agent.config, agent.logger)
        agent.register_module('confluence', confluence_module)

def get_default_workflows() -> dict:
    """
    Get predefined workflows for common engineering tasks
    
    Returns:
        dict: Dictionary of workflow names and their module sequences
    """
    return {
        'full_analysis': [
            'code_review',
            'test_suite',
            'github',
            'jira',
            'confluence'
        ],
        'code_quality': [
            'code_review',
            'test_suite'
        ],
        'deployment': [
            'test_suite',
            'github',
            'jira'
        ],
        'reporting': [
            'test_suite',
            'confluence'
        ],
        'ci_cd': [
            'code_review',
            'test_suite',
            'github'
        ]
    }

def run_workflow(agent: EngineeringAutomationAgent, workflow_name: str, context: dict = None) -> list:
    """
    Run a predefined workflow
    
    Args:
        agent: EngineeringAutomationAgent instance
        workflow_name: Name of the workflow to run
        context: Additional context for the workflow
    
    Returns:
        list: List of execution results
    """
    workflows = get_default_workflows()
    
    if workflow_name not in workflows:
        raise ValueError(f"Unknown workflow: {workflow_name}. Available workflows: {list(workflows.keys())}")
    
    workflow_modules = workflows[workflow_name]
    
    # Add workflow context
    if context is None:
        context = {}
    
    context['workflow_name'] = workflow_name
    context['workflow_modules'] = workflow_modules
    
    # Update agent execution context
    agent.execution_context.update(context)
    
    # Execute workflow
    return agent.execute_workflow(workflow_modules)

# Version information
def get_version_info() -> dict:
    """Get detailed version information"""
    return {
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'modules': [
            'CodeReviewModule',
            'TestSuiteModule',
            'GitHubModule',
            'JiraModule',
            'ConfluenceModule'
        ]
    }

# Quick start function
def quick_start(project_root: str = ".", project_name: str = None) -> EngineeringAutomationAgent:
    """
    Quick start function to create and configure an agent with minimal setup
    
    Args:
        project_root: Root directory of the project
        project_name: Name of the project (auto-detected if not provided)
    
    Returns:
        EngineeringAutomationAgent: Ready-to-use agent instance
    """
    import os
    
    # Auto-detect project name if not provided
    if not project_name:
        project_name = os.path.basename(os.path.abspath(project_root))
    
    # Create configuration manager
    config_manager = ConfigurationManager()
    
    # Try to load existing configuration
    config = config_manager.load_project_config(project_name)
    
    if not config:
        # Create new configuration with auto-detection
        config = config_manager.create_project_config(
            project_name=project_name,
            project_root=project_root
        )
    
    # Create and configure agent
    agent = EngineeringAutomationAgent(config)
    register_default_modules(agent)
    
    return agent
