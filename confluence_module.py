#!/usr/bin/env python3
"""
Enhanced Confluence Integration Module
Comprehensive Confluence API integration for documentation, reporting, knowledge management,
and automated test results posting to connected Confluence pages
"""

import json
import logging
import base64
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

try:
    from .core_agent import AgentModule, AgentConfig
    from .utils import (
        APIClient,
        AuthenticationHelper,
        ResponseParser,
        ContentFormatter,
        ValidationHelper,
        HTMLTableGenerator,
        format_exception_details,
        monitor_performance
    )
    from .messages import get_message, MessageKeys
except ImportError:
    # Handle relative import for standalone usage
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from core_agent import AgentModule, AgentConfig
    from utils import (
        APIClient,
        AuthenticationHelper,
        ResponseParser,
        ContentFormatter,
        ValidationHelper,
        HTMLTableGenerator,
        format_exception_details,
        monitor_performance
    )
    from messages import get_message, MessageKeys

@dataclass
class ConfluencePage:
    """Enhanced Confluence page information with test results integration"""
    id: str
    title: str
    space_key: str
    content: str
    version: int
    url: str
    created: str
    updated: str
    test_results_section: str = ""
    build_info_section: str = ""
    last_test_update: str = ""

@dataclass
class ConfluenceSpace:
    """Enhanced Confluence space information"""
    key: str
    name: str
    description: str
    homepage_id: str
    url: str
    test_results_page_id: str = ""
    build_reports_page_id: str = ""

@dataclass
class TestResultsPost:
    """Test results posting configuration and result"""
    page_id: str
    page_title: str
    test_results: Dict[str, Any]
    build_context: Dict[str, Any]
    success: bool = True
    error_message: str = ""
    confluence_url: str = ""

class ConfluenceModule(AgentModule):
    """Enhanced Confluence integration module for documentation, reporting, and test results posting"""

    def __init__(self, config: AgentConfig, logger):
        super().__init__(config, logger)
        self.api_base = f"{config.confluence_base_url}/rest/api"
        self.space_key = getattr(config, 'confluence_space_key', '')
        self.test_results_page_title = getattr(config, 'confluence_test_results_page', 'Test Results Dashboard')
        self.build_reports_page_title = getattr(config, 'confluence_build_reports_page', 'Build Reports')

        # Create authentication header using utility
        auth_header = AuthenticationHelper.create_basic_auth_header(
            config.confluence_email,
            config.confluence_api_token
        )

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Initialize API client
        self.api_client = APIClient(self.api_base, headers)

        # Track test results postings
        self.test_results_posts = []
    
    def validate_config(self) -> bool:
        """Validate Confluence configuration"""
        if not self.config.confluence_enabled:
            self.log_info(get_message("module_disabled", module="Confluence"))
            return False

        # Validate required fields
        required_fields = [
            'confluence_base_url',
            'confluence_email',
            'confluence_api_token',
            'confluence_space_key'
        ]

        missing_fields = ValidationHelper.validate_required_fields(
            self.config.__dict__, required_fields
        )

        if missing_fields:
            for field in missing_fields:
                self.log_error(get_message("config_missing_field", field=field))
            return False

        # Validate URL format
        if not ValidationHelper.validate_url(self.config.confluence_base_url):
            self.log_error(get_message("config_invalid_url", url=self.config.confluence_base_url))
            return False

        # Validate email format
        if not ValidationHelper.validate_email(self.config.confluence_email):
            self.log_error(get_message("config_invalid_email", email=self.config.confluence_email))
            return False

        # Test API connection
        try:
            response = self.api_client.get("/user/current")
            if response.status_code != 200:
                self.log_error(get_message("api_authentication_failed", status_code=response.status_code))
                return False
        except Exception as e:
            self.log_error(get_message("api_connection_failed", error=str(e)))
            return False

        self.log_info(get_message("module_validation_passed", module="Confluence"))
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Confluence integration tasks"""
        self.log_info(get_message("module_starting", module="Confluence"))

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

        if context.get('update_page') and context.get('page_id'):
            update_result = self.update_page(
                page_id=str(context.get('page_id')),
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

        self.log_info(get_message("module_completed", module="Confluence"))
        return results
    
    def get_space_info(self) -> Optional[ConfluenceSpace]:
        """Get space information"""
        try:
            endpoint = f"/space/{self.config.confluence_space_key}"
            response = self.api_client.get(endpoint, params={'expand': 'description,homepage'})

            if response.status_code == 200:
                space_data = ResponseParser.parse_json_response(response)
                self.log_info(get_message("confluence_space_info_retrieved"))
                return ConfluenceSpace(
                    key=space_data['key'],
                    name=space_data['name'],
                    description=space_data.get('description', {}).get('plain', {}).get('value', ''),
                    homepage_id=space_data.get('homepage', {}).get('id', ''),
                    url=f"{self.config.confluence_base_url}/spaces/{space_data['key']}"
                )
            else:
                error_msg = ResponseParser.extract_error_message(response)
                self.log_error(get_message("confluence_space_info_failed") + f": {error_msg}")
                return None

        except Exception as e:
            self.log_error(get_message("confluence_space_info_failed") + f": {str(e)}")
            return None
    
    def get_recent_pages(self, limit: int = 20) -> List[ConfluencePage]:
        """Get recent pages from the space"""
        try:
            params = {
                'spaceKey': self.config.confluence_space_key,
                'type': 'page',
                'limit': limit,
                'expand': 'version,space,body.storage,history',
                'orderby': 'lastModified'
            }

            response = self.api_client.get("/content", params=params)

            if response.status_code == 200:
                response_data = ResponseParser.parse_json_response(response)
                results_data = response_data.get('results', [])
                pages = []

                for page_data in results_data:
                    pages.append(ConfluencePage(
                        id=page_data['id'],
                        title=page_data['title'],
                        space_key=page_data['space']['key'],
                        content=page_data.get('body', {}).get('storage', {}).get('value', ''),
                        version=page_data['version']['number'],
                        url=f"{self.config.confluence_base_url}{page_data['_links']['webui']}",
                        created=page_data.get('history', {}).get('createdDate', ''),
                        updated=page_data['version']['when']
                    ))

                self.log_info(f"Retrieved {len(pages)} recent pages")
                return pages
            else:
                error_msg = ResponseParser.extract_error_message(response)
                self.log_error(f"Failed to get recent pages: {error_msg}")
                return []

        except Exception as e:
            self.log_error(f"Error getting recent pages: {str(e)}")
            return []
    
    def create_page(self, title: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Confluence page"""
        try:
            # Format content with attribution
            formatted_content = ContentFormatter.format_content_with_attribution(content, "confluence")

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

            response = self.api_client.post("/content", json_data=page_data)

            if response.status_code == 200:
                page_response = ResponseParser.parse_json_response(response)
                page_id = page_response['id']
                page_url = f"{self.config.confluence_base_url}{page_response['_links']['webui']}"

                self.log_info(get_message("confluence_page_created", title=title))
                return ResponseParser.create_success_response({
                    'id': page_id,
                    'title': title,
                    'url': page_url
                })
            else:
                error_msg = ResponseParser.extract_error_message(response)
                self.log_error(get_message("confluence_page_creation_failed", error=error_msg))
                return ResponseParser.create_error_response(error_msg, response.status_code)

        except Exception as e:
            error_msg = str(e)
            self.log_error(get_message("confluence_page_creation_failed", error=error_msg))
            return ResponseParser.create_error_response(error_msg)
    
    def update_page(self, page_id: str, title: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing Confluence page"""
        try:
            # First, get current page info
            response = self.api_client.get(f"/content/{page_id}", params={'expand': 'version,body.storage'})

            if response.status_code != 200:
                error_msg = ResponseParser.extract_error_message(response)
                self.log_error(f"Failed to get current page info: {error_msg}")
                return ResponseParser.create_error_response("Failed to get current page info", response.status_code)

            current_page = ResponseParser.parse_json_response(response)
            current_version = current_page['version']['number']

            # Prepare update data
            update_data = {
                "version": {"number": current_version + 1},
                "type": "page",
                "title": title or current_page['title']
            }

            if content:
                formatted_content = ContentFormatter.format_content_with_attribution(content, "confluence")
                update_data["body"] = {
                    "storage": {
                        "value": formatted_content,
                        "representation": "storage"
                    }
                }

            response = self.api_client.put(f"/content/{page_id}", json_data=update_data)

            if response.status_code == 200:
                page_response = ResponseParser.parse_json_response(response)
                page_url = f"{self.config.confluence_base_url}{page_response['_links']['webui']}"

                self.log_info(get_message("confluence_page_updated", title=page_response['title']))
                return ResponseParser.create_success_response({
                    'id': page_id,
                    'title': page_response['title'],
                    'version': page_response['version']['number'],
                    'url': page_url
                })
            else:
                error_msg = ResponseParser.extract_error_message(response)
                self.log_error(get_message("confluence_page_update_failed", error=error_msg))
                return ResponseParser.create_error_response(error_msg, response.status_code)

        except Exception as e:
            error_msg = str(e)
            self.log_error(get_message("confluence_page_update_failed", error=error_msg))
            return ResponseParser.create_error_response(error_msg)
    
    def search_pages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for pages in the space"""
        try:
            params = {
                'cql': f'space = {self.config.confluence_space_key} AND text ~ "{query}"',
                'limit': limit,
                'expand': 'version'
            }

            response = self.api_client.get("/content/search", params=params)

            if response.status_code == 200:
                search_data = ResponseParser.parse_json_response(response)
                pages = []

                for result in search_data.get('results', []):
                    page = {
                        'id': result['id'],
                        'title': result['title'],
                        'type': result['type'],
                        'url': f"{self.config.confluence_base_url}{result['_links']['webui']}"
                    }
                    pages.append(page)

                self.log_info(get_message("confluence_search_completed", count=len(pages)))
                return pages
            else:
                error_msg = ResponseParser.extract_error_message(response)
                self.log_error(f"Failed to search pages: {error_msg}")
                return []

        except Exception as e:
            self.log_error(f"Error searching pages: {str(e)}")
            return []
    
    def publish_automation_report(self, report_data: Dict[str, Any], report_type: str = "general") -> Dict[str, Any]:
        """Publish an automation report to Confluence"""
        try:
            timestamp = ContentFormatter.format_timestamp()
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

            if result.get('success') and result.get('data', {}).get('url'):
                report_url = result['data']['url']
                self.log_info(get_message("confluence_report_published",
                                        report_type=report_type, url=report_url))

            return result

        except Exception as e:
            error_msg = str(e)
            self.log_error(f"Error publishing automation report: {error_msg}")
            return ResponseParser.create_error_response(error_msg)
    
    def _generate_test_results_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for test results report"""
        suite_results = report_data.get('suite_results', {})

        # Create summary metrics table
        summary_metrics = {
            'total_tests': suite_results.get('total_tests', 0),
            'passed_tests': suite_results.get('passed_tests', 0),
            'failed_tests': suite_results.get('failed_tests', 0),
            'success_rate': f"{suite_results.get('success_rate', 0):.1f}%",
            'total_execution_time': f"{suite_results.get('total_execution_time', 0):.2f}s"
        }

        summary_table = HTMLTableGenerator.create_metrics_table(summary_metrics)

        html = f"""
<h1>🧪 {get_message("summary")} - Test Suite Results</h1>
<p><strong>{get_message("execution_time")}:</strong> {ContentFormatter.format_timestamp()}</p>
<p><strong>Project:</strong> {self.config.project_name}</p>

<h2>📊 {get_message("summary")}</h2>
{summary_table}

<h2>📋 Test Categories</h2>
"""

        categories = suite_results.get('categories', {})
        for category, stats in categories.items():
            html += f"""
<h3>{category.title()} Tests</h3>
<ul>
<li>{get_message("count")}: {stats.get('total', 0)}</li>
<li>Passed: {stats.get('passed', 0)}</li>
<li>Failed: {stats.get('failed', 0)}</li>
</ul>
"""

        # Add detailed results
        html += f"<h2>🔍 {get_message('details')}</h2>"
        results = suite_results.get('results', [])

        for result in results:
            status_icon = "✅" if result.get('success') else "❌"
            html += f"""
<h4>{status_icon} {result.get('name', 'Unknown Test')}</h4>
<p><strong>{get_message("category")}:</strong> {result.get('category', 'Unknown')}</p>
<p><strong>{get_message("execution_time")}:</strong> {result.get('execution_time', 0):.3f}s</p>
"""
            if result.get('error_message'):
                html += f"<p><strong>Error:</strong> <code>{result['error_message']}</code></p>"

            if result.get('details'):
                html += f"<p><strong>{get_message('details')}:</strong> {result['details']}</p>"

        return html
    
    def _generate_code_review_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for code review report"""
        metrics = report_data.get('metrics', {})
        issues = report_data.get('issues', [])
        duplicates = report_data.get('duplicates', [])

        # Create metrics table
        code_metrics = {
            'total_files': metrics.get('total_files', 0),
            'total_lines': metrics.get('total_lines', 0),
            'duplicate_lines': metrics.get('duplicate_lines', 0),
            'maintainability_index': f"{metrics.get('maintainability_index', 0):.1f}"
        }

        metrics_table = HTMLTableGenerator.create_metrics_table(code_metrics)

        html = f"""
<h1>🔍 Code Review and Quality Analysis</h1>
<p><strong>{get_message("timestamp")}:</strong> {ContentFormatter.format_timestamp()}</p>
<p><strong>Project:</strong> {self.config.project_name}</p>

<h2>📊 Code {get_message("metrics")}</h2>
{metrics_table}

<h2>🐛 {get_message("issues")} Found</h2>
<p>Total {get_message("issues")}: {len(issues)}</p>
"""

        # Group issues by type
        issue_types: Dict[str, List[Dict[str, Any]]] = {}
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)

        for issue_type, type_issues in issue_types.items():
            html += f"<h3>{issue_type.title()} {get_message('issues')} ({len(type_issues)})</h3><ul>"
            for issue in type_issues[:10]:  # Limit to first 10 issues per type
                file_path = issue.get('file_path', 'Unknown')
                line_number = issue.get('line_number', 0)
                description = issue.get('description', 'No description')
                html += f"<li><strong>{file_path}:{line_number}</strong> - {description}</li>"
            html += "</ul>"

        # Add duplicates section
        html += f"<h2>🔄 Duplicate Code Blocks</h2><p>Found {len(duplicates)} duplicate code blocks</p>"

        return html
    
    def _generate_deployment_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for deployment report"""
        html = f"""
<h1>🚀 Deployment Report</h1>
<p><strong>{get_message("timestamp")}:</strong> {ContentFormatter.format_timestamp()}</p>
<p><strong>Project:</strong> {self.config.project_name}</p>

<h2>📊 Deployment {get_message("summary")}</h2>
<p>Deployment completed successfully with automated validation.</p>
"""

        # Add any specific deployment data
        if 'github' in report_data:
            github_data = report_data['github']
            repo_name = github_data.get('repository', {}).get('full_name', 'Unknown')
            recent_commits = github_data.get('recent_commits', [])
            latest_commit = recent_commits[0].get('sha', 'Unknown') if recent_commits else 'Unknown'

            html += f"""
<h3>GitHub Integration</h3>
<ul>
<li>Repository: {repo_name}</li>
<li>Latest Commit: {latest_commit}</li>
</ul>
"""

        return html
    
    def _generate_general_report_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for general automation report"""
        html = f"""
<h1>🤖 Engineering Automation Report</h1>
<p><strong>{get_message("execution_time")}:</strong> {ContentFormatter.format_timestamp()}</p>
<p><strong>Project:</strong> {self.config.project_name}</p>

<h2>📊 Automation {get_message("summary")}</h2>
<p>Automated engineering tasks completed successfully.</p>

<h2>📋 Execution {get_message("details")}</h2>
<pre><code>{json.dumps(report_data, indent=2)}</code></pre>
"""

        return html

    @monitor_performance
    def post_test_results_to_confluence(
        self,
        test_results: Dict[str, Any],
        build_context: Dict[str, Any] = None
    ) -> TestResultsPost:
        """Post comprehensive test results to connected Confluence page"""

        self.log_info(get_message(MessageKeys.CONFLUENCE_CONNECTION_SUCCESS))

        result = TestResultsPost(
            page_id="",
            page_title=self.test_results_page_title,
            test_results=test_results,
            build_context=build_context or {}
        )

        try:
            # Find or create test results page
            page_info = self._find_or_create_test_results_page()
            result.page_id = page_info['id']
            result.confluence_url = page_info['url']

            # Generate comprehensive test results content
            test_content = self._generate_comprehensive_test_results_content(
                test_results, build_context
            )

            # Update the page with new test results
            update_result = self._update_page_with_test_results(
                page_info['id'],
                page_info['version'],
                test_content
            )

            if update_result['success']:
                result.success = True
                self.test_results_posts.append(result)
                self.log_info(f"Test results posted to Confluence page: {result.confluence_url}")
            else:
                result.success = False
                result.error_message = update_result.get('error', 'Unknown error')

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            self.log_error(f"Failed to post test results to Confluence: {str(e)}")

        return result

    def _find_or_create_test_results_page(self) -> Dict[str, Any]:
        """Find existing test results page or create a new one"""

        try:
            # Search for existing test results page
            search_url = f"{self.api_base}/content"
            params = {
                'spaceKey': self.space_key,
                'title': self.test_results_page_title,
                'expand': 'version,space'
            }

            response = requests.get(search_url, headers=self.api_client.headers, params=params, timeout=30)

            if response.status_code == 200:
                results = response.json()
                if results['results']:
                    # Page exists, return its info
                    page = results['results'][0]
                    return {
                        'id': page['id'],
                        'version': page['version']['number'],
                        'url': f"{self.config.confluence_base_url}/pages/viewpage.action?pageId={page['id']}"
                    }

            # Page doesn't exist, create it
            return self._create_test_results_page()

        except Exception as e:
            self.log_error(f"Failed to find or create test results page: {str(e)}")
            raise e

    def _create_test_results_page(self) -> Dict[str, Any]:
        """Create a new test results page"""

        initial_content = self._generate_initial_test_results_page_content()

        page_data = {
            'type': 'page',
            'title': self.test_results_page_title,
            'space': {'key': self.space_key},
            'body': {
                'storage': {
                    'value': initial_content,
                    'representation': 'storage'
                }
            }
        }

        create_url = f"{self.api_base}/content"
        response = requests.post(create_url, headers=self.api_client.headers, json=page_data, timeout=30)

        if response.status_code == 200:
            page = response.json()
            return {
                'id': page['id'],
                'version': page['version']['number'],
                'url': f"{self.config.confluence_base_url}/pages/viewpage.action?pageId={page['id']}"
            }
        else:
            raise Exception(f"Failed to create test results page: {response.status_code} - {response.text}")

    def _generate_initial_test_results_page_content(self) -> str:
        """Generate initial content for test results page"""

        return f"""
<h1>🧪 Test Results Dashboard - {self.config.project_name}</h1>

<p>This page contains automated test results for the <strong>{self.config.project_name}</strong> project.</p>

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p>This page is automatically updated by Jeeves4coders after each test run.</p>
</ac:rich-text-body>
</ac:structured-macro>

<h2>📊 Latest Test Results</h2>
<p><em>No test results available yet. Results will appear here after the first test run.</em></p>

<h2>📈 Test History</h2>
<p><em>Test history will be maintained here.</em></p>

<hr/>
<p><small>Last updated: {datetime.now().isoformat()} | Generated by Jeeves4coders</small></p>
"""

    def _generate_comprehensive_test_results_content(
        self,
        test_results: Dict[str, Any],
        build_context: Dict[str, Any] = None
    ) -> str:
        """Generate comprehensive HTML content for test results"""

        timestamp = datetime.now().isoformat()
        build_id = build_context.get('build_id', 'Unknown') if build_context else 'Unknown'

        # Generate test summary
        total_tests = test_results.get('total_tests', 0)
        passed_tests = test_results.get('passed_tests', 0)
        failed_tests = test_results.get('failed_tests', 0)
        success_rate = test_results.get('success_rate', 0)
        execution_time = test_results.get('total_execution_time', 0)

        # Determine status color and icon
        if success_rate >= 90:
            status_color = "green"
            status_icon = "✅"
        elif success_rate >= 70:
            status_color = "yellow"
            status_icon = "⚠️"
        else:
            status_color = "red"
            status_icon = "❌"

        content = f"""
<h1>🧪 Test Results Dashboard - {self.config.project_name}</h1>

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p>This page is automatically updated by Jeeves4coders after each test run.</p>
</ac:rich-text-body>
</ac:structured-macro>

<h2>📊 Latest Test Results</h2>

<ac:structured-macro ac:name="status">
<ac:parameter ac:name="colour">{status_color}</ac:parameter>
<ac:parameter ac:name="title">Build {build_id} - {status_icon} {success_rate:.1f}% Success Rate</ac:parameter>
</ac:structured-macro>

<p><strong>Execution Time:</strong> {timestamp}</p>
<p><strong>Build ID:</strong> {build_id}</p>

<h3>📈 Test Summary</h3>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Total Tests</td><td>{total_tests}</td></tr>
<tr><td>Passed Tests</td><td style="color: green;">{passed_tests}</td></tr>
<tr><td>Failed Tests</td><td style="color: red;">{failed_tests}</td></tr>
<tr><td>Success Rate</td><td>{success_rate:.1f}%</td></tr>
<tr><td>Execution Time</td><td>{execution_time:.2f}s</td></tr>
</table>
"""

        # Add test results by category
        if test_results.get('results'):
            content += self._generate_test_results_by_category(test_results['results'])

        # Add coverage information
        if test_results.get('coverage_report'):
            content += self._generate_coverage_section(test_results['coverage_report'])

        # Add build context information
        if build_context:
            content += self._generate_build_context_section(build_context)

        # Add failed tests details
        if failed_tests > 0:
            content += self._generate_failed_tests_section(test_results.get('results', []))

        # Add test history section
        content += self._generate_test_history_section()

        content += f"""
<hr/>
<p><small>Last updated: {timestamp} | Generated by Jeeves4coders | Build: {build_id}</small></p>
"""

        return content

    def _generate_test_results_by_category(self, results: List[Dict[str, Any]]) -> str:
        """Generate test results breakdown by category"""

        # Group results by category
        categories = {}
        for result in results:
            category = result.get('category', 'Unknown')
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'total': 0}

            categories[category]['total'] += 1
            if result.get('success', False):
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1

        content = """
<h3>📋 Test Results by Category</h3>
<table>
<tr><th>Category</th><th>Total</th><th>Passed</th><th>Failed</th><th>Success Rate</th></tr>
"""

        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            color = "green" if success_rate >= 90 else "yellow" if success_rate >= 70 else "red"

            content += f"""
<tr>
<td><strong>{category.title()}</strong></td>
<td>{stats['total']}</td>
<td style="color: green;">{stats['passed']}</td>
<td style="color: red;">{stats['failed']}</td>
<td style="color: {color};">{success_rate:.1f}%</td>
</tr>
"""

        content += "</table>"
        return content

    def _generate_coverage_section(self, coverage_report: Dict[str, Any]) -> str:
        """Generate code coverage section"""

        coverage_percentage = coverage_report.get('coverage_percentage', 0)
        covered_lines = coverage_report.get('covered_lines', 0)
        total_lines = coverage_report.get('total_lines', 0)

        color = "green" if coverage_percentage >= 80 else "yellow" if coverage_percentage >= 60 else "red"

        return f"""
<h3>📊 Code Coverage</h3>
<ac:structured-macro ac:name="status">
<ac:parameter ac:name="colour">{color}</ac:parameter>
<ac:parameter ac:name="title">Coverage: {coverage_percentage:.1f}%</ac:parameter>
</ac:structured-macro>

<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Coverage Percentage</td><td style="color: {color};">{coverage_percentage:.1f}%</td></tr>
<tr><td>Lines Covered</td><td>{covered_lines}</td></tr>
<tr><td>Total Lines</td><td>{total_lines}</td></tr>
<tr><td>Uncovered Lines</td><td>{total_lines - covered_lines}</td></tr>
</table>
"""

    def _generate_build_context_section(self, build_context: Dict[str, Any]) -> str:
        """Generate build context information section"""

        return f"""
<h3>🚀 Build Information</h3>
<table>
<tr><th>Property</th><th>Value</th></tr>
<tr><td>Build ID</td><td><code>{build_context.get('build_id', 'Unknown')}</code></td></tr>
<tr><td>Environment</td><td>{build_context.get('environment', 'Unknown')}</td></tr>
<tr><td>Branch</td><td>{build_context.get('branch', 'main')}</td></tr>
<tr><td>Commit Hash</td><td><code>{build_context.get('commit_hash', 'N/A')}</code></td></tr>
<tr><td>Build Status</td><td>{'✅ Success' if build_context.get('success') else '❌ Failed'}</td></tr>
</table>
"""

    def _generate_failed_tests_section(self, results: List[Dict[str, Any]]) -> str:
        """Generate failed tests details section"""

        failed_tests = [r for r in results if not r.get('success', True)]

        if not failed_tests:
            return ""

        content = """
<h3>❌ Failed Tests Details</h3>
<ac:structured-macro ac:name="expand">
<ac:parameter ac:name="title">Click to view failed test details</ac:parameter>
<ac:rich-text-body>
<table>
<tr><th>Test Name</th><th>Category</th><th>Error Message</th><th>Execution Time</th></tr>
"""

        for test in failed_tests[:10]:  # Limit to first 10 failed tests
            content += f"""
<tr>
<td><code>{test.get('name', 'Unknown')}</code></td>
<td>{test.get('category', 'Unknown')}</td>
<td style="color: red;">{test.get('error_message', 'No error message')[:100]}...</td>
<td>{test.get('execution_time', 0):.2f}s</td>
</tr>
"""

        if len(failed_tests) > 10:
            content += f"""
<tr>
<td colspan="4"><em>... and {len(failed_tests) - 10} more failed tests</em></td>
</tr>
"""

        content += """
</table>
</ac:rich-text-body>
</ac:structured-macro>
"""

        return content

    def _generate_test_history_section(self) -> str:
        """Generate test history section"""

        return """
<h3>📈 Test History</h3>
<p><em>Test history tracking will be implemented in future versions.</em></p>
<p>This section will show:</p>
<ul>
<li>Test success rate trends</li>
<li>Performance metrics over time</li>
<li>Coverage trends</li>
<li>Build comparison data</li>
</ul>
"""

    def _update_page_with_test_results(
        self,
        page_id: str,
        current_version: int,
        new_content: str
    ) -> Dict[str, Any]:
        """Update Confluence page with new test results content"""

        try:
            update_data = {
                'version': {
                    'number': current_version + 1
                },
                'title': self.test_results_page_title,
                'type': 'page',
                'body': {
                    'storage': {
                        'value': new_content,
                        'representation': 'storage'
                    }
                }
            }

            update_url = f"{self.api_base}/content/{page_id}"
            response = requests.put(update_url, headers=self.api_client.headers, json=update_data, timeout=30)

            if response.status_code == 200:
                return {'success': True, 'page': response.json()}
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_build_report_page(
        self,
        build_context: Dict[str, Any],
        test_results: Dict[str, Any] = None,
        code_review_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a comprehensive build report page in Confluence"""

        try:
            build_id = build_context.get('build_id', datetime.now().strftime("%Y%m%d_%H%M%S"))
            page_title = f"Build Report - {build_id} - {self.config.project_name}"

            # Generate comprehensive build report content
            content = self._generate_comprehensive_build_report_content(
                build_context, test_results, code_review_results
            )

            page_data = {
                'type': 'page',
                'title': page_title,
                'space': {'key': self.space_key},
                'body': {
                    'storage': {
                        'value': content,
                        'representation': 'storage'
                    }
                }
            }

            create_url = f"{self.api_base}/content"
            response = requests.post(create_url, headers=self.api_client.headers, json=page_data, timeout=30)

            if response.status_code == 200:
                page = response.json()
                page_url = f"{self.config.confluence_base_url}/pages/viewpage.action?pageId={page['id']}"

                self.log_info(f"Build report page created: {page_url}")

                return {
                    'success': True,
                    'page_id': page['id'],
                    'page_url': page_url,
                    'title': page_title
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            error_details = format_exception_details(e)
            self.log_error(f"Failed to create build report page: {str(e)}")
            return {'success': False, 'error': str(e), 'exception': error_details}

    def _generate_comprehensive_build_report_content(
        self,
        build_context: Dict[str, Any],
        test_results: Dict[str, Any] = None,
        code_review_results: Dict[str, Any] = None
    ) -> str:
        """Generate comprehensive build report content"""

        build_id = build_context.get('build_id', 'Unknown')
        timestamp = datetime.now().isoformat()
        success = build_context.get('success', False)

        status_color = "green" if success else "red"
        status_icon = "✅" if success else "❌"

        content = f"""
<h1>🚀 Build Report - {build_id}</h1>

<ac:structured-macro ac:name="status">
<ac:parameter ac:name="colour">{status_color}</ac:parameter>
<ac:parameter ac:name="title">{status_icon} Build {build_id} - {'Success' if success else 'Failed'}</ac:parameter>
</ac:structured-macro>

<p><strong>Project:</strong> {self.config.project_name}</p>
<p><strong>Build Time:</strong> {timestamp}</p>
<p><strong>Environment:</strong> {build_context.get('environment', 'Unknown')}</p>

<h2>📊 Build Summary</h2>
<table>
<tr><th>Property</th><th>Value</th></tr>
<tr><td>Build ID</td><td><code>{build_id}</code></td></tr>
<tr><td>Status</td><td style="color: {status_color};">{'Success' if success else 'Failed'}</td></tr>
<tr><td>Environment</td><td>{build_context.get('environment', 'Unknown')}</td></tr>
<tr><td>Branch</td><td>{build_context.get('branch', 'main')}</td></tr>
<tr><td>Commit Hash</td><td><code>{build_context.get('commit_hash', 'N/A')}</code></td></tr>
</table>
"""

        # Add test results section
        if test_results:
            content += f"""
<h2>🧪 Test Results</h2>
{self._generate_test_results_summary_for_build_report(test_results)}
"""

        # Add code review section
        if code_review_results:
            content += f"""
<h2>🔍 Code Review Results</h2>
{self._generate_code_review_summary_for_build_report(code_review_results)}
"""

        # Add exceptions section
        if build_context.get('exceptions'):
            content += f"""
<h2>⚠️ Exceptions and Issues</h2>
{self._generate_exceptions_summary_for_build_report(build_context['exceptions'])}
"""

        content += f"""
<hr/>
<p><small>Generated by Jeeves4coders | {timestamp}</small></p>
"""

        return content

    def _generate_test_results_summary_for_build_report(self, test_results: Dict[str, Any]) -> str:
        """Generate test results summary for build report"""

        total_tests = test_results.get('total_tests', 0)
        passed_tests = test_results.get('passed_tests', 0)
        failed_tests = test_results.get('failed_tests', 0)
        success_rate = test_results.get('success_rate', 0)

        color = "green" if success_rate >= 90 else "yellow" if success_rate >= 70 else "red"

        return f"""
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Total Tests</td><td>{total_tests}</td></tr>
<tr><td>Passed</td><td style="color: green;">{passed_tests}</td></tr>
<tr><td>Failed</td><td style="color: red;">{failed_tests}</td></tr>
<tr><td>Success Rate</td><td style="color: {color};">{success_rate:.1f}%</td></tr>
</table>

<p><a href="{self.config.confluence_base_url}/pages/viewpage.action?pageId={self.test_results_page_title}">View Detailed Test Results</a></p>
"""

    def _generate_code_review_summary_for_build_report(self, code_review_results: Dict[str, Any]) -> str:
        """Generate code review summary for build report"""

        quality_score = code_review_results.get('quality_score', 0)
        issues_count = code_review_results.get('issues_count', 0)

        color = "green" if quality_score >= 8 else "yellow" if quality_score >= 6 else "red"

        return f"""
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Quality Score</td><td style="color: {color};">{quality_score:.1f}/10</td></tr>
<tr><td>Issues Found</td><td>{issues_count}</td></tr>
<tr><td>Duplicates</td><td>{code_review_results.get('duplicates_count', 0)}</td></tr>
<tr><td>Complexity Score</td><td>{code_review_results.get('complexity_score', 0):.1f}</td></tr>
</table>
"""

    def _generate_exceptions_summary_for_build_report(self, exceptions: List[Dict[str, Any]]) -> str:
        """Generate exceptions summary for build report"""

        if not exceptions:
            return "<p>No exceptions reported during this build.</p>"

        content = f"""
<ac:structured-macro ac:name="warning">
<ac:rich-text-body>
<p>{len(exceptions)} exceptions were reported during this build.</p>
</ac:rich-text-body>
</ac:structured-macro>

<table>
<tr><th>Module</th><th>Exception Type</th><th>Message</th><th>Timestamp</th></tr>
"""

        for exc in exceptions[:5]:  # Show first 5 exceptions
            content += f"""
<tr>
<td>{exc.get('module', 'Unknown')}</td>
<td><code>{exc.get('error', {}).get('type', 'Unknown')}</code></td>
<td>{exc.get('error', {}).get('message', 'No message')[:100]}...</td>
<td>{exc.get('timestamp', 'Unknown')}</td>
</tr>
"""

        if len(exceptions) > 5:
            content += f"""
<tr>
<td colspan="4"><em>... and {len(exceptions) - 5} more exceptions</em></td>
</tr>
"""

        content += "</table>"
        return content
