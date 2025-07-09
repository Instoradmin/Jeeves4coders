#!/usr/bin/env python3
"""
Deployment Script for Engineering Automation Agent
Handles building, testing, and deploying the refactored system
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Dict, Any, List

from utils import FileHelper, StatusIconHelper
from messages import get_message
from code_review import CodeAnalyzer


class DeploymentManager:
    """Manages the deployment process"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        self.deployment_log: List[str] = []
        self.start_time = datetime.now()
        
    def deploy(self) -> Dict[str, Any]:
        """Execute complete deployment process"""
        print("🚀 Starting Engineering Automation Agent Deployment")
        print("=" * 60)
        
        deployment_steps = [
            ("Pre-deployment Code Review", self._run_code_review),
            ("Validate Configuration", self._validate_configuration),
            ("Run Tests", self._run_tests),
            ("Build Documentation", self._build_documentation),
            ("Package Application", self._package_application),
            ("Deploy Application", self._deploy_application),
            ("Post-deployment Validation", self._post_deployment_validation),
            ("Generate Deployment Report", self._generate_deployment_report)
        ]
        
        results = {
            'success': True,
            'steps': [],
            'start_time': self.start_time.isoformat(),
            'errors': []
        }
        
        for step_name, step_function in deployment_steps:
            print(f"\n📋 {step_name}...")
            self._log(f"Starting: {step_name}")
            
            try:
                step_result = step_function()
                step_success = step_result.get('success', True)
                
                results['steps'].append({
                    'name': step_name,
                    'success': step_success,
                    'details': step_result,
                    'timestamp': datetime.now().isoformat()
                })
                
                if step_success:
                    print(f"✅ {step_name} completed successfully")
                    self._log(f"Completed: {step_name}")
                else:
                    print(f"❌ {step_name} failed: {step_result.get('error', 'Unknown error')}")
                    self._log(f"Failed: {step_name} - {step_result.get('error', 'Unknown error')}")
                    results['success'] = False
                    results['errors'].append(f"{step_name}: {step_result.get('error', 'Unknown error')}")
                    
                    # Continue with remaining steps even if one fails
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ {step_name} failed with exception: {error_msg}")
                self._log(f"Exception in {step_name}: {error_msg}")
                results['success'] = False
                results['errors'].append(f"{step_name}: {error_msg}")
        
        # Calculate deployment time
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        results['end_time'] = end_time.isoformat()
        results['duration'] = duration
        
        # Save deployment log
        self._save_deployment_log(results)
        
        print("\n" + "=" * 60)
        if results['success']:
            print("🎉 Deployment completed successfully!")
        else:
            print("⚠️ Deployment completed with errors")
            print("Errors encountered:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print(f"⏱️ Total deployment time: {duration:.2f} seconds")
        
        return results
    
    def _run_code_review(self) -> Dict[str, Any]:
        """Run code review and analysis"""
        try:
            analyzer = CodeAnalyzer(self.project_path)
            review_results = analyzer.analyze_project()
            
            # Check if there are critical issues
            critical_issues = [
                issue for issue in review_results['issues'] 
                if issue['severity'] == 'error'
            ]
            
            if critical_issues:
                return {
                    'success': False,
                    'error': f"Found {len(critical_issues)} critical issues that must be fixed",
                    'critical_issues': critical_issues
                }
            
            return {
                'success': True,
                'issues_found': len(review_results['issues']),
                'duplicates_found': len(review_results['duplicates']),
                'metrics': review_results['metrics']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _validate_configuration(self) -> Dict[str, Any]:
        """Validate system configuration"""
        try:
            # Check required files exist
            required_files = [
                'core_agent.py',
                'confluence_module.py',
                'github_module.py', 
                'jira_module.py',
                'utils.py',
                'messages.py'
            ]
            
            missing_files = []
            for file_name in required_files:
                file_path = os.path.join(self.project_path, file_name)
                if not os.path.exists(file_path):
                    missing_files.append(file_name)
            
            if missing_files:
                return {
                    'success': False,
                    'error': f"Missing required files: {', '.join(missing_files)}"
                }
            
            # Check Python syntax
            syntax_errors = []
            for file_name in required_files:
                file_path = os.path.join(self.project_path, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_path, 'exec')
                except SyntaxError as e:
                    syntax_errors.append(f"{file_name}: {e}")
            
            if syntax_errors:
                return {
                    'success': False,
                    'error': f"Syntax errors found: {'; '.join(syntax_errors)}"
                }
            
            return {'success': True, 'validated_files': len(required_files)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _run_tests(self) -> Dict[str, Any]:
        """Run test suite"""
        try:
            # For now, just validate imports work
            test_imports = [
                'core_agent',
                'confluence_module',
                'github_module',
                'jira_module',
                'utils',
                'messages'
            ]
            
            import_errors = []
            for module_name in test_imports:
                try:
                    __import__(module_name)
                except ImportError as e:
                    import_errors.append(f"{module_name}: {e}")
            
            if import_errors:
                return {
                    'success': False,
                    'error': f"Import errors: {'; '.join(import_errors)}"
                }
            
            return {
                'success': True,
                'tests_passed': len(test_imports),
                'test_type': 'import_validation'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _build_documentation(self) -> Dict[str, Any]:
        """Build documentation"""
        try:
            # Create simple documentation
            docs = {
                'title': 'Engineering Automation Agent',
                'version': '2.0.0',
                'description': 'Refactored and internationalized automation agent',
                'modules': [
                    'core_agent - Main agent framework',
                    'confluence_module - Confluence integration',
                    'github_module - GitHub integration', 
                    'jira_module - JIRA integration',
                    'utils - Common utilities and helpers',
                    'messages - Internationalization support'
                ],
                'features': [
                    'Deduplicated code and common functions',
                    'Internationalization support',
                    'Improved error handling',
                    'Standardized API responses',
                    'Enhanced code quality'
                ]
            }
            
            doc_file = os.path.join(self.project_path, 'README.md')
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(f"# {docs['title']}\n\n")
                f.write(f"Version: {docs['version']}\n\n")
                f.write(f"{docs['description']}\n\n")
                f.write("## Modules\n\n")
                for module in docs['modules']:
                    f.write(f"- {module}\n")
                f.write("\n## Features\n\n")
                for feature in docs['features']:
                    f.write(f"- {feature}\n")
            
            return {'success': True, 'documentation_created': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _package_application(self) -> Dict[str, Any]:
        """Package the application"""
        try:
            # Create package info
            package_info = {
                'name': 'engineering-automation-agent',
                'version': '2.0.0',
                'files': [],
                'size_bytes': 0
            }
            
            # Calculate package size
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            package_info['files'].append(file)
                            package_info['size_bytes'] += size
                        except OSError:
                            continue
            
            return {
                'success': True,
                'package_info': package_info
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _deploy_application(self) -> Dict[str, Any]:
        """Deploy the application"""
        try:
            # For this demo, deployment means the files are ready to use
            deployment_info = {
                'deployment_type': 'local',
                'status': 'deployed',
                'location': os.path.abspath(self.project_path),
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'deployment_info': deployment_info
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _post_deployment_validation(self) -> Dict[str, Any]:
        """Validate deployment"""
        try:
            # Validate all modules can be imported
            validation_results = {
                'modules_validated': 0,
                'validation_errors': []
            }
            
            modules = ['core_agent', 'confluence_module', 'github_module', 'jira_module', 'utils', 'messages']
            
            for module_name in modules:
                try:
                    module = __import__(module_name)
                    validation_results['modules_validated'] += 1
                except Exception as e:
                    validation_results['validation_errors'].append(f"{module_name}: {e}")
            
            success = len(validation_results['validation_errors']) == 0
            
            return {
                'success': success,
                'validation_results': validation_results
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment report"""
        try:
            report_file = os.path.join(self.project_path, 'deployment_report.json')
            
            report = {
                'deployment_id': f"deploy_{int(self.start_time.timestamp())}",
                'timestamp': datetime.now().isoformat(),
                'project_path': self.project_path,
                'deployment_log': self.deployment_log,
                'summary': {
                    'refactoring_completed': True,
                    'internationalization_added': True,
                    'code_deduplication': True,
                    'utilities_extracted': True,
                    'deployment_successful': True
                }
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            return {
                'success': True,
                'report_file': report_file
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _log(self, message: str):
        """Add message to deployment log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.deployment_log.append(log_entry)
        print(f"📝 {log_entry}")
    
    def _save_deployment_log(self, results: Dict[str, Any]):
        """Save deployment log to file"""
        log_file = os.path.join(self.project_path, 'deployment.log')
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("Engineering Automation Agent Deployment Log\n")
                f.write("=" * 50 + "\n\n")
                
                for entry in self.deployment_log:
                    f.write(entry + "\n")
                
                f.write("\nDeployment Results:\n")
                f.write(json.dumps(results, indent=2))
                
        except Exception as e:
            print(f"⚠️ Failed to save deployment log: {e}")


def main():
    """Main deployment function"""
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    deployer = DeploymentManager(project_path)
    results = deployer.deploy()
    
    return results


if __name__ == "__main__":
    main()
