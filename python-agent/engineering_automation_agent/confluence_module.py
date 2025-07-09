#!/usr/bin/env python3
"""
Confluence Integration Module
Confluence API integration for documentation, reporting, and knowledge management
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

try:
    from .core_agent import AgentModule, AgentConfig
    from .utils import APIClient, AuthenticationHelper, ResponseParser, ContentFormatter, ValidationHelper, HTMLTableGenerator
    from .messages import get_message, Language
except ImportError:
    # Handle relative import for standalone usage
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from core_agent import AgentModule, AgentConfig
    from utils import APIClient, AuthenticationHelper, ResponseParser, ContentFormatter, ValidationHelper, HTMLTableGenerator
    from messages import get_message, Language

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
