#!/usr/bin/env python3
"""
Enhanced JIRA Integration Module
Comprehensive JIRA API integration for ticket management, status updates, project tracking,
build integration, exception reporting, and automated bug ticket creation
"""

import json
import base64
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from .core_agent import AgentModule, AgentConfig
    from .utils import (
        format_exception_details,
        sanitize_input,
        validate_email,
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
        format_exception_details,
        sanitize_input,
        validate_email,
        monitor_performance
    )
    from messages import get_message, MessageKeys

class IssueType(Enum):
    """JIRA issue types"""
    BUG = "Bug"
    TASK = "Task"
    STORY = "Story"
    EPIC = "Epic"
    IMPROVEMENT = "Improvement"
    SUB_TASK = "Sub-task"

class IssuePriority(Enum):
    """JIRA issue priorities"""
    HIGHEST = "Highest"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    LOWEST = "Lowest"

class IssueStatus(Enum):
    """Common JIRA issue statuses"""
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    CLOSED = "Closed"
    REOPENED = "Reopened"

@dataclass
class JiraIssue:
    """Enhanced JIRA issue information with build integration"""
    key: str
    summary: str
    description: str
    issue_type: IssueType
    status: IssueStatus
    priority: IssuePriority
    assignee: str
    reporter: str
    created: str
    updated: str
    url: str
    project_key: str = ""
    components: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    fix_versions: List[str] = field(default_factory=list)
    affected_versions: List[str] = field(default_factory=list)
    environment: str = ""
    build_id: str = ""
    commit_hash: str = ""
    test_results: Dict[str, Any] = field(default_factory=dict)
    exception_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JiraProject:
    """Enhanced JIRA project information"""
    key: str
    name: str
    description: str
    lead: str
    url: str
    issue_types: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    versions: List[str] = field(default_factory=list)
    workflows: Dict[str, List[str]] = field(default_factory=dict)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BuildIntegrationResult:
    """Result of build integration with JIRA"""
    tickets_updated: List[str] = field(default_factory=list)
    bug_tickets_created: List[str] = field(default_factory=list)
    failed_updates: List[Dict[str, Any]] = field(default_factory=list)
    build_info: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str = ""

class JiraModule(AgentModule):
    """Enhanced JIRA integration module for comprehensive ticket management and build integration"""

    def __init__(self, config: AgentConfig, logger):
        super().__init__(config, logger)
        self.api_base = f"{config.jira_base_url}/rest/api/3"
        self.project_key = getattr(config, 'jira_project_key', '')
        self.default_assignee = getattr(config, 'jira_default_assignee', '')
        self.build_component = getattr(config, 'jira_build_component', 'Build System')

        # Create authentication header
        auth_string = f"{config.jira_email}:{config.jira_api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Track created tickets for this build
        self.build_tickets = []
        self.exceptions_reported = []
    
    def validate_config(self) -> bool:
        """Validate JIRA configuration"""
        if not self.config.jira_enabled:
            self.log_info("JIRA integration disabled in configuration")
            return False
        
        if not self.config.jira_base_url:
            self.log_error("JIRA base URL not provided")
            return False
        
        if not self.config.jira_email or not self.config.jira_api_token:
            self.log_error("JIRA credentials not provided")
            return False
        
        if not self.config.jira_project_key:
            self.log_error("JIRA project key not specified")
            return False
        
        # Test API connection
        try:
            response = requests.get(f"{self.api_base}/myself", headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.log_error(f"JIRA API authentication failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Failed to connect to JIRA API: {str(e)}")
            return False
        
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive JIRA integration tasks with build integration"""
        self.log_info(get_message(MessageKeys.JIRA_CONNECTION_SUCCESS))

        results = {
            'project_info': None,
            'issues': [],
            'created_issues': [],
            'updated_issues': [],
            'bug_tickets_created': [],
            'build_integration': None,
            'exceptions_reported': [],
            'success': True,
            'error': None
        }
        
        # Get project information
        project_info = self.get_project_info()
        results['project'] = project_info
        
        # Get project issues
        issues = self.get_project_issues()
        results['issues'] = issues
        
        # Get project statistics
        stats = self.get_project_statistics()
        results['statistics'] = stats
        
        # Perform actions based on context
        if context.get('create_ticket'):
            ticket_result = self.create_issue(
                summary=context.get('ticket_summary', 'Automated ticket'),
                description=context.get('ticket_description', 'Automated ticket creation'),
                issue_type=context.get('ticket_type', 'Task'),
                priority=context.get('ticket_priority', 'Medium')
            )
            results['ticket_created'] = ticket_result
        
        if context.get('update_ticket'):
            update_result = self.update_issue(
                issue_key=context.get('ticket_key'),
                fields=context.get('ticket_updates', {})
            )
            results['ticket_updated'] = update_result
        
        if context.get('transition_ticket'):
            transition_result = self.transition_issue(
                issue_key=context.get('ticket_key'),
                transition_name=context.get('transition_name', 'Done')
            )
            results['ticket_transitioned'] = transition_result
        
        self.log_info("✅ JIRA integration tasks completed")
        return results
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        try:
            url = f"{self.api_base}/project/{self.config.jira_project_key}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                project_data = response.json()
                return {
                    'key': project_data['key'],
                    'name': project_data['name'],
                    'description': project_data.get('description', ''),
                    'lead': project_data.get('lead', {}).get('displayName', 'Unknown'),
                    'url': project_data.get('self', ''),
                    'project_type': project_data.get('projectTypeKey', 'Unknown'),
                    'issue_types': [
                        {
                            'id': it['id'],
                            'name': it['name'],
                            'description': it.get('description', '')
                        }
                        for it in project_data.get('issueTypes', [])
                    ]
                }
            else:
                self.log_error(f"Failed to get project info: {response.status_code}")
                return {}
                
        except Exception as e:
            self.log_error(f"Error getting project info: {str(e)}")
            return {}
    
    def get_project_issues(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get project issues"""
        try:
            url = f"{self.api_base}/search"
            
            jql = f"project = {self.config.jira_project_key} ORDER BY updated DESC"
            params = {
                'jql': jql,
                'maxResults': max_results,
                'fields': 'summary,description,issuetype,status,priority,assignee,reporter,created,updated'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                search_data = response.json()
                issues = []
                
                for issue_data in search_data.get('issues', []):
                    fields = issue_data['fields']
                    issue = {
                        'key': issue_data['key'],
                        'summary': fields.get('summary', ''),
                        'description': fields.get('description', ''),
                        'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
                        'status': fields.get('status', {}).get('name', 'Unknown'),
                        'priority': fields.get('priority', {}).get('name', 'Unknown'),
                        'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                        'reporter': fields.get('reporter', {}).get('displayName', 'Unknown'),
                        'created': fields.get('created', ''),
                        'updated': fields.get('updated', ''),
                        'url': f"{self.config.jira_base_url}/browse/{issue_data['key']}"
                    }
                    issues.append(issue)
                
                return issues
            else:
                self.log_error(f"Failed to get project issues: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_error(f"Error getting project issues: {str(e)}")
            return []
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """Get project statistics"""
        try:
            stats = {}
            
            # Get issue counts by status
            url = f"{self.api_base}/search"
            jql = f"project = {self.config.jira_project_key}"
            
            # Get all issues for statistics
            params = {
                'jql': jql,
                'maxResults': 1000,
                'fields': 'status,issuetype,priority,assignee,created,resolved'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                search_data = response.json()
                issues = search_data.get('issues', [])
                
                # Count by status
                status_counts = {}
                type_counts = {}
                priority_counts = {}
                assignee_counts = {}
                
                for issue in issues:
                    fields = issue['fields']
                    
                    # Status counts
                    status = fields.get('status', {}).get('name', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # Type counts
                    issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
                    type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
                    
                    # Priority counts
                    priority = fields.get('priority', {}).get('name', 'Unknown')
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                    
                    # Assignee counts
                    assignee = fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'
                    assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
                
                stats = {
                    'total_issues': len(issues),
                    'status_distribution': status_counts,
                    'type_distribution': type_counts,
                    'priority_distribution': priority_counts,
                    'assignee_distribution': assignee_counts
                }
            
            return stats
            
        except Exception as e:
            self.log_error(f"Error getting project statistics: {str(e)}")
            return {}
    
    def create_issue(self, summary: str, description: str, issue_type: str = "Task", 
                    priority: str = "Medium", assignee: Optional[str] = None) -> Dict[str, Any]:
        """Create a new JIRA issue"""
        try:
            url = f"{self.api_base}/issue"
            
            # Create Atlassian Document Format description
            adf_description = self._create_adf_description(description)
            
            issue_data = {
                "fields": {
                    "project": {"key": self.config.jira_project_key},
                    "summary": summary,
                    "description": adf_description,
                    "issuetype": {"name": issue_type},
                    "priority": {"name": priority}
                }
            }
            
            # Add assignee if specified
            if assignee:
                issue_data["fields"]["assignee"] = {"name": assignee}
            
            response = requests.post(url, headers=self.headers, json=issue_data, timeout=10)
            
            if response.status_code == 201:
                issue_response = response.json()
                issue_key = issue_response['key']
                
                return {
                    'success': True,
                    'key': issue_key,
                    'url': f"{self.config.jira_base_url}/browse/{issue_key}",
                    'summary': summary
                }
            else:
                error_msg = response.json().get('errorMessages', ['Unknown error'])[0] if response.content else f"HTTP {response.status_code}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.log_error(f"Error creating issue: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing JIRA issue"""
        try:
            url = f"{self.api_base}/issue/{issue_key}"
            
            update_data = {"fields": fields}
            
            response = requests.put(url, headers=self.headers, json=update_data, timeout=10)
            
            if response.status_code == 204:
                return {
                    'success': True,
                    'key': issue_key,
                    'message': 'Issue updated successfully'
                }
            else:
                error_msg = response.json().get('errorMessages', ['Unknown error'])[0] if response.content else f"HTTP {response.status_code}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.log_error(f"Error updating issue: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def transition_issue(self, issue_key: str, transition_name: str) -> Dict[str, Any]:
        """Transition an issue to a new status"""
        try:
            # First, get available transitions
            transitions_url = f"{self.api_base}/issue/{issue_key}/transitions"
            response = requests.get(transitions_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {'success': False, 'error': 'Failed to get available transitions'}
            
            transitions_data = response.json()
            transitions = transitions_data.get('transitions', [])
            
            # Find the transition ID
            transition_id = None
            for transition in transitions:
                if transition['name'].lower() == transition_name.lower():
                    transition_id = transition['id']
                    break
            
            if not transition_id:
                available_transitions = [t['name'] for t in transitions]
                return {
                    'success': False, 
                    'error': f"Transition '{transition_name}' not available. Available: {available_transitions}"
                }
            
            # Perform the transition
            transition_data = {
                "transition": {"id": transition_id}
            }
            
            response = requests.post(transitions_url, headers=self.headers, json=transition_data, timeout=10)
            
            if response.status_code == 204:
                return {
                    'success': True,
                    'key': issue_key,
                    'transition': transition_name,
                    'message': f'Issue transitioned to {transition_name}'
                }
            else:
                error_msg = response.json().get('errorMessages', ['Unknown error'])[0] if response.content else f"HTTP {response.status_code}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.log_error(f"Error transitioning issue: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to an issue"""
        try:
            url = f"{self.api_base}/issue/{issue_key}/comment"
            
            # Create Atlassian Document Format comment
            adf_comment = self._create_adf_description(comment)
            
            comment_data = {"body": adf_comment}
            
            response = requests.post(url, headers=self.headers, json=comment_data, timeout=10)
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'key': issue_key,
                    'message': 'Comment added successfully'
                }
            else:
                error_msg = response.json().get('errorMessages', ['Unknown error'])[0] if response.content else f"HTTP {response.status_code}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.log_error(f"Error adding comment: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for issues using JQL"""
        try:
            url = f"{self.api_base}/search"
            
            params = {
                'jql': jql,
                'maxResults': max_results,
                'fields': 'summary,description,issuetype,status,priority,assignee,reporter,created,updated'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                search_data = response.json()
                issues = []
                
                for issue_data in search_data.get('issues', []):
                    fields = issue_data['fields']
                    issue = {
                        'key': issue_data['key'],
                        'summary': fields.get('summary', ''),
                        'status': fields.get('status', {}).get('name', 'Unknown'),
                        'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                        'updated': fields.get('updated', ''),
                        'url': f"{self.config.jira_base_url}/browse/{issue_data['key']}"
                    }
                    issues.append(issue)
                
                return issues
            else:
                self.log_error(f"Failed to search issues: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_error(f"Error searching issues: {str(e)}")
            return []
    
    def get_user_issues(self, username: str = None) -> List[Dict[str, Any]]:
        """Get issues assigned to a specific user"""
        if not username:
            username = "currentUser()"
        else:
            username = f'"{username}"'
        
        jql = f"assignee = {username} AND project = {self.config.jira_project_key} ORDER BY updated DESC"
        return self.search_issues(jql)
    
    def _create_adf_description(self, text: str) -> Dict[str, Any]:
        """Create Atlassian Document Format description"""
        # Add a generic footer for automated content. This should be configurable.
        footer_text = f"This ticket was created automatically by the Jeeves4coders agent on {datetime.now().strftime('%Y-%m-%d')}."
        
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                },
                {
                    "type": "rule"
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text", "text": footer_text, "marks": [{"type": "em"}]
                        }
                    ]
                }
            ]
        }
    
    def create_automation_ticket(self, module_name: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create an automation ticket with results"""
        summary = f"Engineering Automation: {module_name} Results"
        
        # Format results for description
        description = f"Automated {module_name} execution completed.\n\n"
        description += f"Execution Time: {datetime.now().isoformat()}\n"
        description += f"Project: {self.config.project_name}\n\n"
        
        if 'summary' in results:
            description += "Summary:\n"
            for key, value in results['summary'].items():
                description += f"• {key}: {value}\n"
        
        return self.create_issue(
            summary=summary,
            description=description,
            issue_type="Task",
            priority="Medium"
        )

    @monitor_performance
    def integrate_with_build(self, build_context: Dict[str, Any]) -> BuildIntegrationResult:
        """Comprehensive build integration with JIRA"""
        self.log_info(get_message(MessageKeys.BUILD_STARTED, project=self.config.project_name))

        result = BuildIntegrationResult()
        result.build_info = {
            'build_id': build_context.get('build_id', datetime.now().strftime("%Y%m%d_%H%M%S")),
            'project': self.config.project_name,
            'timestamp': datetime.now().isoformat(),
            'environment': build_context.get('environment', 'development'),
            'commit_hash': build_context.get('commit_hash', ''),
            'branch': build_context.get('branch', 'main')
        }

        try:
            # Update existing tickets with build information
            if build_context.get('success', True):
                result.tickets_updated = self._update_tickets_after_successful_build(build_context)
            else:
                result.bug_tickets_created = self._create_bug_tickets_for_failed_build(build_context)

            # Report exceptions if any
            if build_context.get('exceptions'):
                result.bug_tickets_created.extend(
                    self._create_bug_tickets_for_exceptions(build_context['exceptions'])
                )

            # Update test results
            if build_context.get('test_results'):
                self._update_tickets_with_test_results(build_context['test_results'])

            self.log_info(get_message(MessageKeys.BUILD_COMPLETED,
                                    time=build_context.get('execution_time', 0)))

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.failed_updates.append({
                'error': format_exception_details(e),
                'context': 'build_integration'
            })
            self.log_error(get_message(MessageKeys.BUILD_FAILED, error=str(e)))

        return result

    def _update_tickets_after_successful_build(self, build_context: Dict[str, Any]) -> List[str]:
        """Update JIRA tickets after successful build"""
        updated_tickets = []

        try:
            # Find tickets related to this build/project
            jql = f'project = "{self.project_key}" AND status != "Done" AND status != "Closed"'
            if build_context.get('commit_hash'):
                jql += f' AND (description ~ "{build_context["commit_hash"]}" OR comment ~ "{build_context["commit_hash"]}")'

            issues = self.search_issues(jql)

            for issue in issues:
                try:
                    # Add build success comment
                    comment = self._create_build_success_comment(build_context)
                    self.add_comment(issue['key'], comment)

                    # Update custom fields if configured
                    if hasattr(self.config, 'jira_build_field'):
                        self.update_issue(issue['key'], {
                            self.config.jira_build_field: build_context.get('build_id', '')
                        })

                    updated_tickets.append(issue['key'])
                    self.log_info(get_message(MessageKeys.JIRA_TICKET_UPDATED, ticket_id=issue['key']))

                except Exception as e:
                    self.log_error(f"Failed to update ticket {issue['key']}: {str(e)}")

        except Exception as e:
            self.log_error(f"Failed to update tickets after build: {str(e)}")

        return updated_tickets

    def _create_bug_tickets_for_failed_build(self, build_context: Dict[str, Any]) -> List[str]:
        """Create bug tickets for failed build"""
        created_tickets = []

        try:
            # Create main build failure ticket
            summary = f"Build Failed - {self.config.project_name} - {build_context.get('build_id', 'Unknown')}"

            description = self._create_comprehensive_build_failure_description(build_context)

            issue_data = {
                'project': {'key': self.project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': IssueType.BUG.value},
                'priority': {'name': IssuePriority.HIGH.value},
                'components': [{'name': self.build_component}],
                'labels': ['build-failure', 'automated', f"build-{build_context.get('build_id', 'unknown')}"],
                'environment': build_context.get('environment', 'Unknown')
            }

            if self.default_assignee:
                issue_data['assignee'] = {'name': self.default_assignee}

            # Add custom fields for build information
            if hasattr(self.config, 'jira_build_field'):
                issue_data[self.config.jira_build_field] = build_context.get('build_id', '')

            if hasattr(self.config, 'jira_commit_field'):
                issue_data[self.config.jira_commit_field] = build_context.get('commit_hash', '')

            result = self.create_issue(issue_data)
            if result.get('success'):
                created_tickets.append(result['issue']['key'])
                self.log_info(get_message(MessageKeys.JIRA_BUG_TICKET_CREATED,
                                        ticket_id=result['issue']['key'],
                                        component='Build System'))

        except Exception as e:
            self.log_error(f"Failed to create build failure ticket: {str(e)}")

        return created_tickets

    def _create_bug_tickets_for_exceptions(self, exceptions: List[Dict[str, Any]]) -> List[str]:
        """Create bug tickets for exceptions found during build"""
        created_tickets = []

        # Group exceptions by module/component
        exceptions_by_module = {}
        for exc in exceptions:
            module = exc.get('module', 'unknown')
            if module not in exceptions_by_module:
                exceptions_by_module[module] = []
            exceptions_by_module[module].append(exc)

        # Create tickets for each module with exceptions
        for module, module_exceptions in exceptions_by_module.items():
            try:
                summary = f"Exceptions in {module} - {len(module_exceptions)} errors found"

                description = self._create_exception_ticket_description(module, module_exceptions)

                issue_data = {
                    'project': {'key': self.project_key},
                    'summary': summary,
                    'description': description,
                    'issuetype': {'name': IssueType.BUG.value},
                    'priority': {'name': self._determine_priority_from_exceptions(module_exceptions)},
                    'components': [{'name': module}],
                    'labels': ['exception', 'automated', 'error-report'],
                    'environment': f"Module: {module}"
                }

                if self.default_assignee:
                    issue_data['assignee'] = {'name': self.default_assignee}

                result = self.create_issue(issue_data)
                if result.get('success'):
                    created_tickets.append(result['issue']['key'])
                    self.log_info(get_message(MessageKeys.JIRA_BUG_TICKET_CREATED,
                                            ticket_id=result['issue']['key'],
                                            component=module))

            except Exception as e:
                self.log_error(f"Failed to create exception ticket for {module}: {str(e)}")

        return created_tickets

    def _create_build_success_comment(self, build_context: Dict[str, Any]) -> str:
        """Create comprehensive build success comment"""
        comment_parts = [
            f"✅ *Build Successful* - {build_context.get('build_id', 'Unknown')}",
            "",
            f"*Build Information:*",
            f"• Build ID: {build_context.get('build_id', 'N/A')}",
            f"• Timestamp: {datetime.now().isoformat()}",
            f"• Environment: {build_context.get('environment', 'Unknown')}",
            f"• Branch: {build_context.get('branch', 'main')}",
        ]

        if build_context.get('commit_hash'):
            comment_parts.append(f"• Commit: {build_context['commit_hash']}")

        if build_context.get('test_results'):
            test_results = build_context['test_results']
            comment_parts.extend([
                "",
                f"*Test Results:*",
                f"• Total Tests: {test_results.get('total_tests', 0)}",
                f"• Passed: {test_results.get('passed_tests', 0)}",
                f"• Failed: {test_results.get('failed_tests', 0)}",
                f"• Success Rate: {test_results.get('success_rate', 0):.1f}%"
            ])

        comment_parts.extend([
            "",
            "---",
            f"_Automated comment generated by Engineering Automation Agent_"
        ])

        return "\n".join(comment_parts)

    def _create_comprehensive_build_failure_description(self, build_context: Dict[str, Any]) -> str:
        """Create comprehensive build failure description with all relevant information"""
        description_parts = [
            f"# Build Failure Report",
            "",
            f"## Build Information",
            f"* **Build ID:** {build_context.get('build_id', 'Unknown')}",
            f"* **Project:** {self.config.project_name}",
            f"* **Timestamp:** {datetime.now().isoformat()}",
            f"* **Environment:** {build_context.get('environment', 'Unknown')}",
            f"* **Branch:** {build_context.get('branch', 'main')}",
        ]

        if build_context.get('commit_hash'):
            description_parts.append(f"* **Commit Hash:** {build_context['commit_hash']}")

        # Add error information
        if build_context.get('error'):
            description_parts.extend([
                "",
                f"## Error Details",
                f"```",
                f"{build_context['error']}",
                f"```"
            ])

        # Add test results if available
        if build_context.get('test_results'):
            test_results = build_context['test_results']
            description_parts.extend([
                "",
                f"## Test Results",
                f"* **Total Tests:** {test_results.get('total_tests', 0)}",
                f"* **Passed:** {test_results.get('passed_tests', 0)}",
                f"* **Failed:** {test_results.get('failed_tests', 0)}",
                f"* **Success Rate:** {test_results.get('success_rate', 0):.1f}%"
            ])

            # Add failed test details
            if test_results.get('failed_tests', 0) > 0:
                description_parts.extend([
                    "",
                    f"### Failed Tests",
                ])

                for result in test_results.get('results', []):
                    if not result.get('success', True):
                        description_parts.extend([
                            f"* **{result.get('name', 'Unknown Test')}**",
                            f"  * Category: {result.get('category', 'Unknown')}",
                            f"  * Error: {result.get('error_message', 'No error message')}"
                        ])

        # Add exception information
        if build_context.get('exceptions'):
            description_parts.extend([
                "",
                f"## Exceptions ({len(build_context['exceptions'])})",
            ])

            for i, exc in enumerate(build_context['exceptions'][:5], 1):  # Limit to first 5
                description_parts.extend([
                    f"### Exception {i}",
                    f"* **Type:** {exc.get('type', 'Unknown')}",
                    f"* **Module:** {exc.get('module', 'Unknown')}",
                    f"* **Message:** {exc.get('message', 'No message')}",
                    f"* **File:** {exc.get('file_name', 'Unknown')}",
                    f"* **Line:** {exc.get('line_number', 'Unknown')}",
                    ""
                ])

        description_parts.extend([
            "",
            f"## Recommended Actions",
            f"1. Review the error details and logs",
            f"2. Check recent code changes in the commit",
            f"3. Verify test environment configuration",
            f"4. Run tests locally to reproduce the issue",
            f"5. Fix identified issues and trigger a new build",
            "",
            "---",
            f"*This ticket was automatically created by Engineering Automation Agent*",
            f"*Build ID: {build_context.get('build_id', 'Unknown')}*"
        ])

        return "\n".join(description_parts)

    def _create_exception_ticket_description(self, module: str, exceptions: List[Dict[str, Any]]) -> str:
        """Create detailed exception ticket description"""
        description_parts = [
            f"# Exception Report - {module}",
            "",
            f"## Summary",
            f"Multiple exceptions detected in the {module} module during build execution.",
            f"Total exceptions: {len(exceptions)}",
            "",
            f"## Exception Details"
        ]

        for i, exc in enumerate(exceptions, 1):
            description_parts.extend([
                f"### Exception {i}",
                f"* **Type:** {exc.get('type', 'Unknown')}",
                f"* **Message:** {exc.get('message', 'No message available')}",
                f"* **Timestamp:** {exc.get('timestamp', 'Unknown')}",
                f"* **File:** {exc.get('file_name', 'Unknown')}",
                f"* **Line:** {exc.get('line_number', 'Unknown')}",
                "",
                f"**Stack Trace:**",
                f"```",
                f"{exc.get('traceback', 'No traceback available')}",
                f"```",
                ""
            ])

        description_parts.extend([
            f"## Recommended Actions",
            f"1. Review the exception details and stack traces",
            f"2. Check the {module} module for potential issues",
            f"3. Verify input data and configuration",
            f"4. Add error handling and validation",
            f"5. Test the fix thoroughly",
            "",
            "---",
            f"*This ticket was automatically created by Engineering Automation Agent*"
        ])

        return "\n".join(description_parts)

    def _determine_priority_from_exceptions(self, exceptions: List[Dict[str, Any]]) -> str:
        """Determine JIRA priority based on exception severity"""
        critical_exceptions = ['SystemExit', 'KeyboardInterrupt', 'MemoryError']
        high_priority_exceptions = ['ValueError', 'TypeError', 'AttributeError', 'ImportError']

        for exc in exceptions:
            exc_type = exc.get('type', '')
            if exc_type in critical_exceptions:
                return IssuePriority.HIGHEST.value
            elif exc_type in high_priority_exceptions:
                return IssuePriority.HIGH.value

        # Default to medium priority
        return IssuePriority.MEDIUM.value

    def _update_tickets_with_test_results(self, test_results: Dict[str, Any]):
        """Update existing tickets with test results"""
        try:
            # Find tickets that might be related to failed tests
            if test_results.get('failed_tests', 0) > 0:
                jql = f'project = "{self.project_key}" AND status != "Done" AND labels in ("test-failure", "bug")'
                issues = self.search_issues(jql)

                for issue in issues:
                    try:
                        comment = self._create_test_results_comment(test_results)
                        self.add_comment(issue['key'], comment)
                        self.log_info(f"Updated ticket {issue['key']} with test results")
                    except Exception as e:
                        self.log_error(f"Failed to update ticket {issue['key']} with test results: {str(e)}")

        except Exception as e:
            self.log_error(f"Failed to update tickets with test results: {str(e)}")

    def _create_test_results_comment(self, test_results: Dict[str, Any]) -> str:
        """Create test results comment for JIRA tickets"""
        comment_parts = [
            f"📊 *Test Results Update*",
            "",
            f"*Overall Results:*",
            f"• Total Tests: {test_results.get('total_tests', 0)}",
            f"• Passed: {test_results.get('passed_tests', 0)}",
            f"• Failed: {test_results.get('failed_tests', 0)}",
            f"• Success Rate: {test_results.get('success_rate', 0):.1f}%",
            f"• Execution Time: {test_results.get('total_execution_time', 0):.2f}s"
        ]

        # Add coverage information if available
        if test_results.get('coverage_report'):
            coverage = test_results['coverage_report']
            comment_parts.extend([
                "",
                f"*Code Coverage:*",
                f"• Coverage: {coverage.get('coverage_percentage', 0):.1f}%",
                f"• Lines Covered: {coverage.get('covered_lines', 0)}/{coverage.get('total_lines', 0)}"
            ])

        # Add failed test details
        if test_results.get('failed_tests', 0) > 0:
            comment_parts.extend([
                "",
                f"*Failed Tests:*"
            ])

            failed_count = 0
            for result in test_results.get('results', []):
                if not result.get('success', True) and failed_count < 5:  # Limit to 5 failed tests
                    comment_parts.append(f"• {result.get('name', 'Unknown')} ({result.get('category', 'Unknown')})")
                    failed_count += 1

            if test_results.get('failed_tests', 0) > 5:
                comment_parts.append(f"• ... and {test_results['failed_tests'] - 5} more")

        comment_parts.extend([
            "",
            "---",
            f"_Automated test results from Engineering Automation Agent_"
        ])

        return "\n".join(comment_parts)

    def create_comprehensive_ticket_with_build_context(
        self,
        summary: str,
        description: str,
        issue_type: IssueType = IssueType.TASK,
        priority: IssuePriority = IssuePriority.MEDIUM,
        build_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a comprehensive JIRA ticket with full build context and documentation"""

        # Enhance description with build context
        enhanced_description = description

        if build_context:
            enhanced_description += "\n\n## Build Context\n"
            enhanced_description += f"* **Build ID:** {build_context.get('build_id', 'N/A')}\n"
            enhanced_description += f"* **Project:** {self.config.project_name}\n"
            enhanced_description += f"* **Environment:** {build_context.get('environment', 'Unknown')}\n"
            enhanced_description += f"* **Branch:** {build_context.get('branch', 'main')}\n"

            if build_context.get('commit_hash'):
                enhanced_description += f"* **Commit:** {build_context['commit_hash']}\n"

            if build_context.get('test_results'):
                test_results = build_context['test_results']
                enhanced_description += f"\n### Test Results\n"
                enhanced_description += f"* Tests: {test_results.get('passed_tests', 0)}/{test_results.get('total_tests', 0)} passed\n"
                enhanced_description += f"* Success Rate: {test_results.get('success_rate', 0):.1f}%\n"

        # Add comprehensive documentation footer
        enhanced_description += "\n\n---\n"
        enhanced_description += "*This ticket was created with comprehensive documentation and build context.*\n"
        enhanced_description += f"*Generated by Engineering Automation Agent at {datetime.now().isoformat()}*"

        # Create issue with enhanced data
        issue_data = {
            'project': {'key': self.project_key},
            'summary': sanitize_input(summary),
            'description': enhanced_description,
            'issuetype': {'name': issue_type.value},
            'priority': {'name': priority.value},
            'labels': ['automated', 'comprehensive', 'documented']
        }

        # Add build-specific labels
        if build_context:
            issue_data['labels'].extend([
                f"build-{build_context.get('build_id', 'unknown')}",
                f"env-{build_context.get('environment', 'unknown')}"
            ])

        if self.default_assignee:
            issue_data['assignee'] = {'name': self.default_assignee}

        # Add custom fields for build tracking
        if build_context and hasattr(self.config, 'jira_build_field'):
            issue_data[self.config.jira_build_field] = build_context.get('build_id', '')

        if build_context and hasattr(self.config, 'jira_commit_field'):
            issue_data[self.config.jira_commit_field] = build_context.get('commit_hash', '')

        return self.create_issue(issue_data)
