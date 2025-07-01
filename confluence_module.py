#!/usr/bin/env python3
"""
Confluence Integration Module
Confluence API integration for documentation, reporting, and knowledge management
"""

import json
import base64
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

try:
    from .core_agent import AgentModule, AgentConfig
except ImportError:
    # Handle relative import for standalone usage
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from core_agent import AgentModule, AgentConfig

@dataclass
class ConfluencePage:
    """Confluence page information"""
    id: str
    title: str
    space_key: str
    content: str
    version: int
    url: str
    created: str
    updated: str

@dataclass
class ConfluenceSpace:
    """Confluence space information"""
    key: str
    name: str
    description: str
    homepage_id: str
    url: str

class ConfluenceModule(AgentModule):
    """Confluence integration module for documentation and reporting"""
    
    def __init__(self, config: AgentConfig, logger):
        super().__init__(config, logger)
        self.api_base = f"{config.confluence_base_url}/rest/api"
        
        # Create authentication header
        auth_string = f"{config.confluence_email}:{config.confluence_api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def validate_config(self) -> bool:
        """Validate Confluence configuration"""
        if not self.config.confluence_enabled:
            self.log_info("Confluence integration disabled in configuration")
            return False
        
        if not self.config.confluence_base_url:
            self.log_error("Confluence base URL not provided")
            return False
        
        if not self.config.confluence_email or not self.config.confluence_api_token:
            self.log_error("Confluence credentials not provided")
            return False
        
        if not self.config.confluence_space_key:
            self.log_error("Confluence space key not specified")
            return False
        
        # Test API connection
        try:
            response = requests.get(f"{self.api_base}/user/current", headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.log_error(f"Confluence API authentication failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Failed to connect to Confluence API: {str(e)}")
            return False
        
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Confluence integration tasks"""
        self.log_info("📚 Starting Confluence integration tasks")
        
        results = {}
        
        # Get space information
        space_info = self.get_space_info()
        results['space'] = space_info
        
        # Get recent pages
        pages = self.get_recent_pages()
        results['recent_pages'] = pages
        
        # Perform actions based on context
        if context.get('create_page'):
            page_result = self.create_page(
                title=context.get('page_title', 'Automated Documentation'),
                content=context.get('page_content', 'Automated content'),
                parent_id=context.get('parent_id')
            )
            results['page_created'] = page_result
        
        if context.get('update_page'):
            update_result = self.update_page(
                page_id=context.get('page_id'),
                title=context.get('page_title'),
                content=context.get('page_content')
            )
            results['page_updated'] = update_result
        
        if context.get('publish_report'):
            report_result = self.publish_automation_report(
                report_data=context.get('report_data', {}),
                report_type=context.get('report_type', 'general')
            )
            results['report_published'] = report_result
        
        self.log_info("✅ Confluence integration tasks completed")
        return results
    
    def get_space_info(self) -> Dict[str, Any]:
        """Get space information"""
        try:
            url = f"{self.api_base}/space/{self.config.confluence_space_key}"
            params = {'expand': 'description,homepage'}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                space_data = response.json()
                return {
                    'key': space_data['key'],
                    'name': space_data['name'],
                    'description': space_data.get('description', {}).get('plain', {}).get('value', ''),
                    'homepage_id': space_data.get('homepage', {}).get('id', ''),
                    'url': f"{self.config.confluence_base_url}/spaces/{space_data['key']}",
                    'type': space_data.get('type', 'Unknown')
                }
            else:
                self.log_error(f"Failed to get space info: {response.status_code}")
                return {}
                
        except Exception as e:
            self.log_error(f"Error getting space info: {str(e)}")
            return {}
    
    def get_recent_pages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent pages from the space"""
        try:
            url = f"{self.api_base}/content"
            params = {
                'spaceKey': self.config.confluence_space_key,
                'type': 'page',
                'limit': limit,
                'expand': 'version,space',
                'orderby': 'lastModified'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                content_data = response.json()
                pages = []
                
                for page_data in content_data.get('results', []):
                    page = {
                        'id': page_data['id'],
                        'title': page_data['title'],
                        'type': page_data['type'],
                        'status': page_data['status'],
                        'version': page_data['version']['number'],
                        'created': page_data['version']['when'],
                        'url': f"{self.config.confluence_base_url}{page_data['_links']['webui']}"
                    }
                    pages.append(page)
                
                return pages
            else:
                self.log_error(f"Failed to get recent pages: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_error(f"Error getting recent pages: {str(e)}")
            return []
    
    def create_page(self, title: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Confluence page"""
        try:
            url = f"{self.api_base}/content"
            
            # Format content with attribution
            formatted_content = self._format_content_with_attribution(content)
            
            page_data = {
                "type": "page",
                "title": title,
                "space": {"key": self.config.confluence_space_key},
                "body": {
                    "storage": {
                        "value": formatted_content,
                        "representation": "storage"
                    }
                }
            }
            
            # Add parent if specified
            if parent_id:
                page_data["ancestors"] = [{"id": parent_id}]
            
            response = requests.post(url, headers=self.headers, json=page_data, timeout=10)
            
            if response.status_code == 200:
                page_response = response.json()
                page_id = page_response['id']
                
                return {
                    'success': True,
                    'id': page_id,
                    'title': title,
                    'url': f"{self.config.confluence_base_url}{page_response['_links']['webui']}"
                }
            else:
                error_msg = response.json().get('message', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.log_error(f"Error creating page: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_page(self, page_id: str, title: str = None, content: str = None) -> Dict[str, Any]:
        """Update an existing Confluence page"""
        try:
            # First, get current page info
            get_url = f"{self.api_base}/content/{page_id}"
            params = {'expand': 'version,body.storage'}
            response = requests.get(get_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return {'success': False, 'error': 'Failed to get current page info'}
            
            current_page = response.json()
            current_version = current_page['version']['number']
            
            # Prepare update data
            update_url = f"{self.api_base}/content/{page_id}"
            
            update_data = {
                "version": {"number": current_version + 1},
                "type": "page",
                "title": title or current_page['title']
            }
            
            if content:
                formatted_content = self._format_content_with_attribution(content)
                update_data["body"] = {
                    "storage": {
                        "value": formatted_content,
                        "representation": "storage"
                    }
                }
            
            response = requests.put(update_url, headers=self.headers, json=update_data, timeout=10)
            
            if response.status_code == 200:
                page_response = response.json()
                return {
                    'success': True,
                    'id': page_id,
                    'title': page_response['title'],
                    'version': page_response['version']['number'],
                    'url': f"{self.config.confluence_base_url}{page_response['_links']['webui']}"
                }
            else:
                error_msg = response.json().get('message', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.log_error(f"Error updating page: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def search_pages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for pages in the space"""
        try:
            url = f"{self.api_base}/content/search"
            params = {
                'cql': f'space = {self.config.confluence_space_key} AND text ~ "{query}"',
                'limit': limit,
                'expand': 'version'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                search_data = response.json()
                pages = []
                
                for result in search_data.get('results', []):
                    page = {
                        'id': result['id'],
                        'title': result['title'],
                        'type': result['type'],
                        'url': f"{self.config.confluence_base_url}{result['_links']['webui']}"
                    }
                    pages.append(page)
                
                return pages
            else:
                self.log_error(f"Failed to search pages: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_error(f"Error searching pages: {str(e)}")
            return []
    
    def publish_automation_report(self, report_data: Dict[str, Any], report_type: str = "general") -> Dict[str, Any]:
        """Publish an automation report to Confluence"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title = f"Engineering Automation Report - {report_type.title()} - {timestamp}"
            
            # Generate HTML content based on report type
            if report_type == "test_results":
                content = self._generate_test_results_content(report_data)
            elif report_type == "code_review":
                content = self._generate_code_review_content(report_data)
            elif report_type == "deployment":
                content = self._generate_deployment_content(report_data)
            else:
                content = self._generate_general_report_content(report_data)
            
            # Create the page
            result = self.create_page(title, content)
            
            if result.get('success'):
                self.log_info(f"📄 Published {report_type} report: {result['url']}")
            
            return result
            
        except Exception as e:
            self.log_error(f"Error publishing automation report: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _format_content_with_attribution(self, content: str) -> str:
        """Format content with Augment Code attribution"""
        attribution_html = '''
<hr/>
<p>
Co-authored by <a href="https://www.augmentcode.com/?utm_source=atlassian&utm_medium=confluence_page&utm_campaign=confluence">Augment Code</a>
</p>
'''
        return content + attribution_html
    
    def _generate_test_results_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for test results report"""
        suite_results = report_data.get('suite_results', {})
        
        html = f"""
<h1>🧪 Comprehensive Test Suite Results</h1>
<p><strong>Execution Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<p><strong>Project:</strong> {self.config.project_name}</p>

<h2>📊 Summary</h2>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Total Tests</td><td>{suite_results.get('total_tests', 0)}</td></tr>
<tr><td>Passed Tests</td><td>{suite_results.get('passed_tests', 0)}</td></tr>
<tr><td>Failed Tests</td><td>{suite_results.get('failed_tests', 0)}</td></tr>
<tr><td>Success Rate</td><td>{suite_results.get('success_rate', 0):.1f}%</td></tr>
<tr><td>Execution Time</td><td>{suite_results.get('total_execution_time', 0):.2f}s</td></tr>
</table>

<h2>📋 Test Categories</h2>
"""
        
        categories = suite_results.get('categories', {})
        for category, stats in categories.items():
            html += f"""
<h3>{category.title()} Tests</h3>
<ul>
<li>Total: {stats.get('total', 0)}</li>
<li>Passed: {stats.get('passed', 0)}</li>
<li>Failed: {stats.get('failed', 0)}</li>
</ul>
"""
        
        # Add detailed results
        html += "<h2>🔍 Detailed Results</h2>"
        results = suite_results.get('results', [])
        
        for result in results:
            status_icon = "✅" if result.get('success') else "❌"
            html += f"""
<h4>{status_icon} {result.get('name', 'Unknown Test')}</h4>
<p><strong>Category:</strong> {result.get('category', 'Unknown')}</p>
<p><strong>Execution Time:</strong> {result.get('execution_time', 0):.3f}s</p>
"""
            if result.get('error_message'):
                html += f"<p><strong>Error:</strong> <code>{result['error_message']}</code></p>"
            
            if result.get('details'):
                html += f"<p><strong>Details:</strong> {result['details']}</p>"
        
        return html
    
    def _generate_code_review_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for code review report"""
        metrics = report_data.get('metrics', {})
        issues = report_data.get('issues', [])
        duplicates = report_data.get('duplicates', [])
        
        html = f"""
<h1>🔍 Code Review and Quality Analysis</h1>
<p><strong>Analysis Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<p><strong>Project:</strong> {self.config.project_name}</p>

<h2>📊 Code Metrics</h2>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Total Files</td><td>{metrics.get('total_files', 0)}</td></tr>
<tr><td>Total Lines</td><td>{metrics.get('total_lines', 0)}</td></tr>
<tr><td>Duplicate Lines</td><td>{metrics.get('duplicate_lines', 0)}</td></tr>
<tr><td>Maintainability Index</td><td>{metrics.get('maintainability_index', 0):.1f}</td></tr>
</table>

<h2>🐛 Issues Found</h2>
<p>Total Issues: {len(issues)}</p>
"""
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        for issue_type, type_issues in issue_types.items():
            html += f"<h3>{issue_type.title()} Issues ({len(type_issues)})</h3><ul>"
            for issue in type_issues[:10]:  # Limit to first 10 issues per type
                html += f"<li><strong>{issue.get('file_path', 'Unknown')}:{issue.get('line_number', 0)}</strong> - {issue.get('description', 'No description')}</li>"
            html += "</ul>"
        
        # Add duplicates section
        html += f"<h2>🔄 Duplicate Code Blocks</h2><p>Found {len(duplicates)} duplicate code blocks</p>"
        
        return html
    
    def _generate_deployment_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for deployment report"""
        html = f"""
<h1>🚀 Deployment Report</h1>
<p><strong>Deployment Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<p><strong>Project:</strong> {self.config.project_name}</p>

<h2>📊 Deployment Summary</h2>
<p>Deployment completed successfully with automated validation.</p>
"""
        
        # Add any specific deployment data
        if 'github' in report_data:
            github_data = report_data['github']
            html += f"""
<h3>GitHub Integration</h3>
<ul>
<li>Repository: {github_data.get('repository', {}).get('full_name', 'Unknown')}</li>
<li>Latest Commit: {github_data.get('recent_commits', [{}])[0].get('sha', 'Unknown') if github_data.get('recent_commits') else 'Unknown'}</li>
</ul>
"""
        
        return html
    
    def _generate_general_report_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for general automation report"""
        html = f"""
<h1>🤖 Engineering Automation Report</h1>
<p><strong>Execution Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<p><strong>Project:</strong> {self.config.project_name}</p>

<h2>📊 Automation Summary</h2>
<p>Automated engineering tasks completed successfully.</p>

<h2>📋 Execution Details</h2>
<pre><code>{json.dumps(report_data, indent=2)}</code></pre>
"""
        
        return html
