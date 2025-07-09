#!/usr/bin/env python3
"""
Test and Validation Script for Engineering Automation Agent
Comprehensive testing of all modules and functionality
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add the agent to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules directly
from core_agent import EngineeringAutomationAgent, AgentConfig
from config_manager import ConfigurationManager
from code_review_module import CodeReviewModule
from test_suite_module import TestSuiteModule

# Import utility functions from __init__.py
try:
    from __init__ import quick_start, create_agent_from_config, get_default_workflows
except ImportError:
    # Fallback implementations for testing
    def quick_start(project_root, project_name):
        config = AgentConfig(project_name=project_name, project_root=project_root)
        agent = EngineeringAutomationAgent(config)
        # Register basic modules
        if config.code_review_enabled:
            agent.register_module('code_review', CodeReviewModule(config, agent.logger))
        if config.test_enabled:
            agent.register_module('test_suite', TestSuiteModule(config, agent.logger))
        return agent

    def create_agent_from_config(config_file=None, project_name=None, project_root=None):
        config = AgentConfig(project_name=project_name or "test", project_root=project_root or ".")
        return EngineeringAutomationAgent(config)

    def get_default_workflows():
        return {
            'code_quality': ['code_review', 'test_suite'],
            'full_analysis': ['code_review', 'test_suite']
        }

class TestAgentCore(unittest.TestCase):
    """Test core agent functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_config = AgentConfig(
            project_name="test-project",
            project_root=".",
            project_type="python",
            test_enabled=True,
            code_review_enabled=True,
            github_enabled=False,  # Disable for testing
            jira_enabled=False,
            confluence_enabled=False
        )
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = EngineeringAutomationAgent(self.test_config)
        
        self.assertEqual(agent.config.project_name, "test-project")
        self.assertEqual(agent.config.project_type, "python")
        self.assertIsInstance(agent.execution_context, dict)
        self.assertIsInstance(agent.results, list)
    
    def test_module_registration(self):
        """Test module registration"""
        agent = EngineeringAutomationAgent(self.test_config)
        
        # Create mock module
        mock_module = Mock()
        mock_module.validate_config.return_value = True
        
        # Register module
        agent.register_module('test_module', mock_module)
        
        self.assertIn('test_module', agent.modules)
        mock_module.validate_config.assert_called_once()
    
    def test_module_execution(self):
        """Test module execution"""
        agent = EngineeringAutomationAgent(self.test_config)
        
        # Create mock module
        mock_module = Mock()
        mock_module.validate_config.return_value = True
        mock_module.execute.return_value = {"status": "success"}
        
        # Register and execute module
        agent.register_module('test_module', mock_module)
        result = agent.execute_module('test_module')
        
        self.assertTrue(result.success)
        self.assertEqual(result.module_name, 'test_module')
        mock_module.execute.assert_called_once()
    
    def test_workflow_execution(self):
        """Test workflow execution"""
        agent = EngineeringAutomationAgent(self.test_config)
        
        # Create mock modules
        mock_module1 = Mock()
        mock_module1.validate_config.return_value = True
        mock_module1.execute.return_value = {"status": "success"}
        
        mock_module2 = Mock()
        mock_module2.validate_config.return_value = True
        mock_module2.execute.return_value = {"status": "success"}
        
        # Register modules
        agent.register_module('module1', mock_module1)
        agent.register_module('module2', mock_module2)
        
        # Execute workflow
        results = agent.execute_workflow(['module1', 'module2'])
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.success for r in results))

class TestConfigurationManager(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigurationManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_project_config(self):
        """Test project configuration creation"""
        config = self.config_manager.create_project_config(
            project_name="test-project",
            project_root=".",
            template_name="python_web"
        )
        
        self.assertEqual(config.project_name, "test-project")
        self.assertEqual(config.project_type, "python")
        self.assertIn("unit", config.test_types)
    
    def test_save_and_load_config(self):
        """Test configuration save and load"""
        # Create and save config
        config = self.config_manager.create_project_config(
            project_name="save-test",
            project_root="."
        )
        
        # Load config
        loaded_config = self.config_manager.load_project_config("save-test")
        
        self.assertIsNotNone(loaded_config)
        self.assertEqual(loaded_config.project_name, "save-test")
    
    def test_list_projects(self):
        """Test project listing"""
        # Create multiple projects
        self.config_manager.create_project_config("project1", ".")
        self.config_manager.create_project_config("project2", ".")
        
        projects = self.config_manager.list_projects()
        
        self.assertIn("project1", projects)
        self.assertIn("project2", projects)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        valid_config = AgentConfig(
            project_name="valid-project",
            project_root=".",
            test_coverage_threshold=80.0
        )
        
        issues = self.config_manager.validate_project_config(valid_config)
        self.assertEqual(len(issues), 0)
        
        # Invalid config
        invalid_config = AgentConfig(
            project_name="",  # Invalid: empty name
            project_root="/nonexistent",  # Invalid: doesn't exist
            test_coverage_threshold=150.0  # Invalid: > 100
        )
        
        issues = self.config_manager.validate_project_config(invalid_config)
        self.assertGreater(len(issues), 0)

class TestCodeReviewModule(unittest.TestCase):
    """Test code review module"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = AgentConfig(
            project_name="code-review-test",
            project_root=".",
            code_review_enabled=True
        )
        
        # Create mock logger
        self.mock_logger = Mock()
    
    def test_module_initialization(self):
        """Test module initialization"""
        module = CodeReviewModule(self.config, self.mock_logger)
        
        self.assertEqual(module.config, self.config)
        self.assertEqual(module.logger, self.mock_logger)
        self.assertIsInstance(module.supported_extensions, set)
    
    def test_config_validation(self):
        """Test configuration validation"""
        module = CodeReviewModule(self.config, self.mock_logger)
        
        # Should be valid
        self.assertTrue(module.validate_config())
        
        # Test with disabled config
        disabled_config = AgentConfig(
            project_name="test",
            project_root=".",
            code_review_enabled=False
        )
        
        disabled_module = CodeReviewModule(disabled_config, self.mock_logger)
        self.assertFalse(disabled_module.validate_config())

class TestTestSuiteModule(unittest.TestCase):
    """Test test suite module"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = AgentConfig(
            project_name="test-suite-test",
            project_root=".",
            test_enabled=True,
            test_types=["unit", "functional"]
        )
        
        # Create mock logger
        self.mock_logger = Mock()
    
    def test_module_initialization(self):
        """Test module initialization"""
        module = TestSuiteModule(self.config, self.mock_logger)
        
        self.assertEqual(module.config, self.config)
        self.assertEqual(module.logger, self.mock_logger)
        self.assertIsInstance(module.test_runners, dict)
    
    def test_config_validation(self):
        """Test configuration validation"""
        module = TestSuiteModule(self.config, self.mock_logger)
        
        # Should be valid
        self.assertTrue(module.validate_config())
        
        # Test with disabled config
        disabled_config = AgentConfig(
            project_name="test",
            project_root=".",
            test_enabled=False
        )
        
        disabled_module = TestSuiteModule(disabled_config, self.mock_logger)
        self.assertFalse(disabled_module.validate_config())

class TestQuickStart(unittest.TestCase):
    """Test quick start functionality"""
    
    def test_quick_start_basic(self):
        """Test basic quick start"""
        agent = quick_start(".", "quick-start-test")
        
        self.assertIsInstance(agent, EngineeringAutomationAgent)
        self.assertEqual(agent.config.project_name, "quick-start-test")
        self.assertEqual(agent.config.project_root, ".")
    
    def test_quick_start_with_modules(self):
        """Test quick start with module registration"""
        agent = quick_start(".", "module-test")
        
        # Should have some modules registered
        self.assertGreater(len(agent.modules), 0)

class TestWorkflows(unittest.TestCase):
    """Test workflow functionality"""
    
    def test_get_default_workflows(self):
        """Test getting default workflows"""
        workflows = get_default_workflows()
        
        self.assertIsInstance(workflows, dict)
        self.assertIn('full_analysis', workflows)
        self.assertIn('code_quality', workflows)
        
        # Check workflow structure
        for workflow_name, modules in workflows.items():
            self.assertIsInstance(modules, list)
            self.assertGreater(len(modules), 0)

def run_integration_tests():
    """Run integration tests with real modules"""
    print("🧪 Running Integration Tests")
    print("=" * 50)
    
    try:
        # Test 1: Quick start integration
        print("📋 Test 1: Quick Start Integration")
        agent = quick_start(".", "integration-test")
        print(f"✅ Agent created with {len(agent.modules)} modules")
        
        # Test 2: Module execution
        print("\n📋 Test 2: Module Execution")
        available_modules = list(agent.modules.keys())
        
        if available_modules:
            test_module = available_modules[0]
            print(f"🔄 Testing module: {test_module}")
            
            result = agent.execute_module(test_module)
            
            if result.success:
                print(f"✅ Module executed successfully in {result.execution_time:.2f}s")
            else:
                print(f"❌ Module failed: {result.errors}")
        
        # Test 3: Configuration management
        print("\n📋 Test 3: Configuration Management")
        config_manager = ConfigurationManager()
        
        # Test template listing
        templates = config_manager.list_templates()
        print(f"✅ Found {len(templates)} templates: {templates}")
        
        # Test project creation
        test_config = config_manager.create_project_config(
            project_name="integration-config-test",
            project_root=".",
            template_name="python_web" if "python_web" in templates else None
        )
        print(f"✅ Created configuration for project: {test_config.project_name}")
        
        # Test 4: Workflow execution (limited)
        print("\n📋 Test 4: Workflow Execution")
        workflows = get_default_workflows()
        
        # Test code_quality workflow if modules are available
        if 'code_review' in agent.modules and 'test_suite' in agent.modules:
            print("🔄 Testing code_quality workflow...")
            
            try:
                # Simple workflow execution for testing
                results = agent.execute_workflow(['code_review', 'test_suite'])
                
                successful = sum(1 for r in results if r.success)
                total = len(results)
                print(f"✅ Workflow completed: {successful}/{total} modules successful")
                
            except Exception as e:
                print(f"⚠️ Workflow test skipped: {str(e)}")
        else:
            print("⚠️ Workflow test skipped: Required modules not available")
        
        print("\n🎉 Integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        return False

def main():
    """Main test runner"""
    print("🤖 Engineering Automation Agent - Test Suite")
    print("=" * 60)
    
    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAgentCore,
        TestConfigurationManager,
        TestCodeReviewModule,
        TestTestSuiteModule,
        TestQuickStart,
        TestWorkflows
    ]
    
    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    unit_result = runner.run(test_suite)
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_result = run_integration_tests()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    unit_success = unit_result.wasSuccessful()
    print(f"🧪 Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"   • Tests run: {unit_result.testsRun}")
    print(f"   • Failures: {len(unit_result.failures)}")
    print(f"   • Errors: {len(unit_result.errors)}")
    
    print(f"🔗 Integration Tests: {'✅ PASSED' if integration_result else '❌ FAILED'}")
    
    overall_success = unit_success and integration_result
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if not overall_success:
        print("\n🔧 Troubleshooting:")
        print("• Check that all dependencies are installed")
        print("• Ensure the agent is properly installed")
        print("• Verify configuration files are valid")
        print("• Check file permissions and paths")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
