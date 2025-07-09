#!/usr/bin/env python3
"""
Enhanced Engineering Automation Agent - Core Framework
Comprehensive automation agent for engineering and housekeeping activities with:
- Unit, functional, integration, and regression testing
- GitHub test script storage and comprehensive commit descriptions
- Common functions and database connections in utils.py
- Internationalization support with properties files
- Exception reporting and collection before commits
- JIRA ticket updates and bug ticket creation
- Comprehensive code documentation and comments
"""

import os
import sys
import json
import logging
import importlib
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path

try:
    from .utils import (
        setup_logging,
        collect_and_report_exceptions,
        format_exception_details,
        get_database_connection,
        monitor_performance
    )
    from .messages import get_message, MessageKeys, initialize_message_system
except ImportError:
    # Handle relative import for standalone usage
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from utils import (
        setup_logging,
        collect_and_report_exceptions,
        format_exception_details,
        get_database_connection,
        monitor_performance
    )
    from messages import get_message, MessageKeys, initialize_message_system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('engineering_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

@dataclass
class AgentConfig:
    """Configuration for the Engineering Automation Agent"""
    
    # Project Configuration
    project_name: str = ""
    project_root: str = ""
    project_type: str = "python"  # python, javascript, java, etc.
    
    # GitHub Configuration
    github_enabled: bool = True
    github_token: str = ""
    github_repo: str = ""
    github_owner: str = ""
    
    # JIRA Configuration
    jira_enabled: bool = True
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = ""
    
    # Confluence Configuration
    confluence_enabled: bool = True
    confluence_base_url: str = ""
    confluence_email: str = ""
    confluence_api_token: str = ""
    confluence_space_key: str = ""
    
    # Enhanced Testing Configuration
    test_enabled: bool = True
    test_types: List[str] = field(default_factory=lambda: ["unit", "functional", "integration", "regression", "performance", "security", "end_to_end"])
    test_timeout: int = 300
    test_coverage_threshold: float = 80.0
    github_test_repository: str = ""  # Repository for storing test scripts
    test_artifacts_retention_days: int = 30

    # Code Review Configuration
    code_review_enabled: bool = True
    deduplication_enabled: bool = True
    code_quality_threshold: float = 8.0
    comprehensive_documentation: bool = True
    auto_add_comments: bool = True

    # Build Integration Configuration
    build_integration_enabled: bool = True
    pre_commit_checks: bool = True
    exception_reporting_enabled: bool = True
    auto_create_bug_tickets: bool = True
    build_artifacts_storage: str = "github"  # github, local, s3

    # JIRA Integration Enhancement
    jira_default_assignee: str = ""
    jira_build_component: str = "Build System"
    jira_build_field: str = ""  # Custom field for build ID
    jira_commit_field: str = ""  # Custom field for commit hash

    # GitHub Integration Enhancement
    github_base_url: str = "https://api.github.com"
    github_test_repository: str = ""  # Separate repo for test artifacts
    comprehensive_commit_descriptions: bool = True
    auto_create_pull_requests: bool = False

    # Database Configuration
    database: Dict[str, Any] = field(default_factory=dict)

    # Internationalization Configuration
    language: str = "en"
    messages_directory: str = ""

    # Exception Handling Configuration
    exception_collection_enabled: bool = True
    exception_report_file: str = "exceptions_report.json"
    fail_build_on_exceptions: bool = False

    # Deployment Configuration
    deployment_enabled: bool = True
    deployment_environment: str = "staging"
    auto_deploy_on_success: bool = False

    # Notification Configuration
    notifications_enabled: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["confluence", "jira"])

class AgentModule(ABC):
    """Abstract base class for agent modules"""
    
    def __init__(self, config: AgentConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.name = self.__class__.__name__
        
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module's main functionality"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate module configuration"""
        pass
    
    def log_info(self, message: str):
        """Log info message with module name"""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        """Log error message with module name"""
        self.logger.error(f"[{self.name}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message with module name"""
        self.logger.warning(f"[{self.name}] {message}")

@dataclass
class ExecutionResult:
    """Result of module execution"""
    success: bool
    module_name: str
    execution_time: float
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'success': self.success,
            'module_name': self.module_name,
            'execution_time': self.execution_time,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings
        }

class EngineeringAutomationAgent:
    """Main Engineering Automation Agent"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = setup_logging(log_file='engineering_agent.log')
        self.modules: Dict[str, AgentModule] = {}
        self.execution_context: Dict[str, Any] = {}
        self.results: List[ExecutionResult] = []
        self.exceptions_collector = []
        self.build_context = {}

        # Initialize internationalization
        try:
            initialize_message_system(config.messages_directory, config.language)
        except Exception as e:
            self.logger.warning(f"Failed to initialize message system: {str(e)}")

        # Initialize database connection if configured
        self.db_connection = None
        if hasattr(config, 'database') and config.database:
            try:
                self.db_connection = get_database_connection(config)
            except Exception as e:
                self.logger.warning(f"Failed to initialize database connection: {str(e)}")

        # Initialize agent
        self._initialize_agent()

        self.logger.info(get_message(MessageKeys.SUCCESS))
    
    def _initialize_agent(self):
        """Initialize the agent and load modules"""
        self.logger.info("🚀 Initializing Engineering Automation Agent")
        self.logger.info(f"📁 Project: {self.config.project_name}")
        self.logger.info(f"📂 Root: {self.config.project_root}")
        
        # Set up execution context
        self.execution_context = {
            'project_name': self.config.project_name,
            'project_root': self.config.project_root,
            'project_type': self.config.project_type,
            'timestamp': datetime.now().isoformat(),
            'agent_version': '1.0.0'
        }
        
        # Load available modules
        self._load_modules()
    
    def _load_modules(self):
        """Load all available agent modules"""
        self.logger.info("📦 Loading agent modules...")
        
        # Module loading will be implemented in subsequent steps
        # For now, we'll register module types
        module_types = [
            'CodeReviewModule',
            'TestSuiteModule', 
            'GitHubModule',
            'JiraModule',
            'ConfluenceModule',
            'DeploymentModule'
        ]
        
        for module_type in module_types:
            self.logger.info(f"  📋 Registered module type: {module_type}")
    
    def register_module(self, name: str, module: AgentModule):
        """Register a module with the agent"""
        if module.validate_config():
            self.modules[name] = module
            self.logger.info(f"✅ Registered module: {name}")
        else:
            self.logger.error(f"❌ Failed to register module: {name} (config validation failed)")
    
    def execute_module(self, module_name: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """Execute a specific module"""
        if module_name not in self.modules:
            error_msg = f"Module '{module_name}' not found"
            self.logger.error(error_msg)
            return ExecutionResult(
                success=False,
                module_name=module_name,
                execution_time=0.0,
                errors=[error_msg]
            )
        
        module = self.modules[module_name]
        execution_context = {**self.execution_context, **(context or {})}
        
        self.logger.info(f"🔄 Executing module: {module_name}")
        start_time = datetime.now()
        
        try:
            result_data = module.execute(execution_context)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = ExecutionResult(
                success=True,
                module_name=module_name,
                execution_time=execution_time,
                data=result_data
            )
            
            self.logger.info(f"✅ Module '{module_name}' completed successfully in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Module execution failed: {str(e)}"
            self.logger.error(error_msg)
            
            result = ExecutionResult(
                success=False,
                module_name=module_name,
                execution_time=execution_time,
                errors=[error_msg]
            )
        
        self.results.append(result)
        return result
    
    def execute_workflow(self, workflow: List[str]) -> List[ExecutionResult]:
        """Execute a workflow of modules in sequence"""
        self.logger.info(f"🔄 Executing workflow: {' -> '.join(workflow)}")
        workflow_results = []
        
        for module_name in workflow:
            result = self.execute_module(module_name)
            workflow_results.append(result)
            
            # Stop workflow if module fails (unless configured otherwise)
            if not result.success:
                self.logger.error(f"❌ Workflow stopped due to module failure: {module_name}")
                break
        
        return workflow_results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all executions"""
        total_modules = len(self.results)
        successful_modules = sum(1 for r in self.results if r.success)
        total_time = sum(r.execution_time for r in self.results)
        
        return {
            'total_modules': total_modules,
            'successful_modules': successful_modules,
            'failed_modules': total_modules - successful_modules,
            'success_rate': (successful_modules / total_modules * 100) if total_modules > 0 else 0,
            'total_execution_time': total_time,
            'results': [r.to_dict() for r in self.results]
        }
    
    def save_results(self, filepath: str):
        """Save execution results to file"""
        summary = self.get_execution_summary()
        summary['config'] = self.config.__dict__
        summary['context'] = self.execution_context
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"💾 Results saved to: {filepath}")

    @monitor_performance
    def execute_comprehensive_build(self, build_id: str = None) -> Dict[str, Any]:
        """Execute comprehensive build with exception reporting and JIRA/GitHub integration"""

        build_id = build_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.build_context = {
            'build_id': build_id,
            'project': self.config.project_name,
            'timestamp': datetime.now().isoformat(),
            'environment': getattr(self.config, 'deployment_environment', 'development'),
            'success': True,
            'exceptions': [],
            'test_results': {},
            'code_review_results': {},
            'artifacts': []
        }

        self.logger.info(get_message(MessageKeys.BUILD_STARTED, project=self.config.project_name))

        try:
            # Pre-commit checks
            if self.config.pre_commit_checks:
                self._run_pre_commit_checks()

            # Execute all workflows
            workflow_results = self.execute_all_workflows()

            # Collect results
            self.build_context['test_results'] = workflow_results.get('test_suite', {})
            self.build_context['code_review_results'] = workflow_results.get('code_review', {})

            # Check for failures
            if any(not result.success for result in self.results):
                self.build_context['success'] = False

            # Collect exceptions
            self.build_context['exceptions'] = self.exceptions_collector

            # Report exceptions before commit
            if self.config.exception_reporting_enabled and self.exceptions_collector:
                exception_report = collect_and_report_exceptions(
                    self.exceptions_collector,
                    self.config.exception_report_file
                )
                self.logger.warning(get_message(MessageKeys.EXCEPTION_REPORT_GENERATED,
                                              count=len(self.exceptions_collector)))

                # Fail build if configured
                if self.config.fail_build_on_exceptions:
                    self.build_context['success'] = False

            # Update JIRA tickets
            if 'jira' in self.modules and self.build_context['success']:
                jira_result = self.modules['jira'].integrate_with_build(self.build_context)
                self.build_context['jira_integration'] = jira_result.__dict__

            # Post test results to Confluence
            if 'confluence' in self.modules and self.build_context.get('test_results'):
                confluence_result = self.modules['confluence'].post_test_results_to_confluence(
                    self.build_context['test_results'],
                    self.build_context
                )
                self.build_context['confluence_test_results'] = confluence_result.__dict__

                # Also create comprehensive build report
                build_report_result = self.modules['confluence'].create_build_report_page(
                    self.build_context,
                    self.build_context['test_results'],
                    self.build_context['code_review_results']
                )
                self.build_context['confluence_build_report'] = build_report_result

            # Create comprehensive GitHub commit
            if 'github' in self.modules and self.build_context['success']:
                commit_files = self._get_modified_files()
                if commit_files:
                    github_result = self.modules['github'].create_comprehensive_commit(
                        commit_files,
                        f"Build {build_id} - Comprehensive automation results",
                        self.build_context,
                        self.build_context['test_results'],
                        self.build_context['code_review_results']
                    )
                    self.build_context['github_commit'] = github_result

            # Store test artifacts in GitHub
            if 'github' in self.modules and self.build_context.get('test_results'):
                artifacts_result = self.modules['github'].store_test_artifacts_in_repository(
                    {
                        'test_results': self.build_context['test_results'],
                        'exceptions': self.exceptions_collector,
                        'build_context': self.build_context
                    },
                    build_id
                )
                self.build_context['artifacts'] = artifacts_result.get('stored_files', [])

            # Post-build actions
            self._run_post_build_actions()

            if self.build_context['success']:
                self.logger.info(get_message(MessageKeys.BUILD_COMPLETED,
                                           time=self.build_context.get('execution_time', 0)))
            else:
                self.logger.error(get_message(MessageKeys.BUILD_FAILED,
                                            error="Build failed due to errors or exceptions"))

            return self.build_context

        except Exception as e:
            # Collect top-level exception
            exception_details = format_exception_details(e)
            self.exceptions_collector.append({
                'component': 'build_execution',
                'error': exception_details,
                'timestamp': datetime.now().isoformat()
            })

            self.build_context['success'] = False
            self.build_context['error'] = str(e)
            self.build_context['exceptions'] = self.exceptions_collector

            self.logger.error(get_message(MessageKeys.BUILD_FAILED, error=str(e)))

            # Create bug ticket for build failure
            if 'jira' in self.modules and self.config.auto_create_bug_tickets:
                try:
                    self.modules['jira'].integrate_with_build(self.build_context)
                except Exception as jira_error:
                    self.logger.error(f"Failed to create JIRA bug ticket: {str(jira_error)}")

            return self.build_context

    def _run_pre_commit_checks(self):
        """Run pre-commit checks"""
        self.logger.info(get_message(MessageKeys.PRE_COMMIT_CHECKS))

        try:
            # Run code review first
            if 'code_review' in self.modules:
                code_review_result = self.modules['code_review'].execute(self.execution_context)
                if not code_review_result.get('success', True):
                    self.exceptions_collector.append({
                        'component': 'pre_commit_code_review',
                        'error': code_review_result.get('error', 'Code review failed'),
                        'timestamp': datetime.now().isoformat()
                    })

            # Run basic tests
            if 'test_suite' in self.modules:
                # Run only unit tests for pre-commit
                original_test_types = self.config.test_types
                self.config.test_types = ['unit']

                test_result = self.modules['test_suite'].execute(self.execution_context)

                # Restore original test types
                self.config.test_types = original_test_types

                if not test_result.get('success', True):
                    self.exceptions_collector.append({
                        'component': 'pre_commit_tests',
                        'error': test_result.get('error', 'Pre-commit tests failed'),
                        'timestamp': datetime.now().isoformat()
                    })

        except Exception as e:
            exception_details = format_exception_details(e)
            self.exceptions_collector.append({
                'component': 'pre_commit_checks',
                'error': exception_details,
                'timestamp': datetime.now().isoformat()
            })

    def _run_post_build_actions(self):
        """Run post-build actions"""
        self.logger.info(get_message(MessageKeys.POST_BUILD_ACTIONS))

        try:
            # Generate comprehensive documentation
            if self.config.comprehensive_documentation:
                self._generate_comprehensive_documentation()

            # Add comprehensive comments to code
            if self.config.auto_add_comments and 'github' in self.modules:
                self._add_comprehensive_code_comments()

        except Exception as e:
            exception_details = format_exception_details(e)
            self.exceptions_collector.append({
                'component': 'post_build_actions',
                'error': exception_details,
                'timestamp': datetime.now().isoformat()
            })

    def _get_modified_files(self) -> List[str]:
        """Get list of modified files for commit"""
        try:
            import subprocess
            result = subprocess.run(['git', 'diff', '--name-only', '--cached'],
                                  cwd=self.config.project_root,
                                  capture_output=True, text=True)

            if result.returncode == 0:
                return [f.strip() for f in result.stdout.split('\n') if f.strip()]
            else:
                # If no staged files, get all modified files
                result = subprocess.run(['git', 'diff', '--name-only'],
                                      cwd=self.config.project_root,
                                      capture_output=True, text=True)
                return [f.strip() for f in result.stdout.split('\n') if f.strip()]

        except Exception as e:
            self.logger.error(f"Failed to get modified files: {str(e)}")
            return []

    def _generate_comprehensive_documentation(self):
        """Generate comprehensive documentation for the project"""
        try:
            # This would generate comprehensive documentation
            # Implementation depends on project type and requirements
            self.logger.info("Generating comprehensive documentation...")

            # Create documentation structure
            docs_dir = Path(self.config.project_root) / "docs"
            docs_dir.mkdir(exist_ok=True)

            # Generate build report
            build_report = {
                'build_id': self.build_context.get('build_id'),
                'timestamp': datetime.now().isoformat(),
                'project': self.config.project_name,
                'results': [result.__dict__ for result in self.results],
                'exceptions': self.exceptions_collector,
                'test_results': self.build_context.get('test_results', {}),
                'code_review_results': self.build_context.get('code_review_results', {})
            }

            report_file = docs_dir / f"build_report_{self.build_context.get('build_id', 'unknown')}.json"
            with open(report_file, 'w') as f:
                json.dump(build_report, f, indent=2, default=str)

            self.logger.info(f"Build report generated: {report_file}")

        except Exception as e:
            self.logger.error(f"Failed to generate comprehensive documentation: {str(e)}")

    def _add_comprehensive_code_comments(self):
        """Add comprehensive comments to code files"""
        try:
            # This would analyze code and add comprehensive comments
            # Implementation would depend on the programming language and code analysis
            self.logger.info("Adding comprehensive code comments...")

            # Example: Add comments to Python files
            python_files = list(Path(self.config.project_root).glob("**/*.py"))

            for py_file in python_files[:5]:  # Limit to 5 files for example
                if 'github' in self.modules:
                    comments = [
                        {
                            'line': 1,
                            'comment': f'Enhanced by Engineering Automation Agent - Build {self.build_context.get("build_id")}',
                            'type': 'single'
                        }
                    ]

                    self.modules['github'].add_comprehensive_code_comments(
                        str(py_file.relative_to(self.config.project_root)),
                        comments
                    )

        except Exception as e:
            self.logger.error(f"Failed to add comprehensive code comments: {str(e)}")

def load_config_from_file(config_path: str) -> AgentConfig:
    """Load agent configuration from JSON file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    return AgentConfig(**config_data)

def create_default_config(project_root: str, project_name: str) -> AgentConfig:
    """Create default configuration for a project"""
    return AgentConfig(
        project_name=project_name,
        project_root=project_root,
        project_type="python"
    )

if __name__ == "__main__":
    # Example usage
    config = create_default_config(".", "example-project")
    agent = EngineeringAutomationAgent(config)
    
    print("🤖 Engineering Automation Agent initialized successfully!")
    print(f"📊 Agent ready with {len(agent.modules)} modules loaded")
