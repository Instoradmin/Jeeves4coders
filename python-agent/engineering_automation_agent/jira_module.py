#!/usr/bin/env python3
"""
JIRA Integration Module
JIRA API integration for ticket management, status updates, and project tracking
"""

import json
import base64
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .core_agent import AgentModule, AgentConfig

@dataclass
class JiraIssue:
    """JIRA issue information"""
    key: str
    summary: str
    description: str
    issue_type: str
    status: str
    priority: str
    assignee: str
    reporter: str
    created: str
    updated: str
    url: str

@dataclass
class JiraProject:
    """JIRA project information"""
    key: str
    name: str
    description: str
    lead: str
    url: str
    issue_types: List[str] = field(default_factory=list)

class JiraModule(AgentModule):
    """JIRA integration module for ticket management and project tracking"""
    
    def __init__(self, config: AgentConfig, logger):
        super().__init__(config, logger)
        self.api_base = f"{config.jira_base_url}/rest/api/3"
        
        # Create authentication header
        auth_string = f"{config.jira_email}:{config.jira_api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
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
        """Execute JIRA integration tasks"""
        self.log_info("🎫 Starting JIRA integration tasks")
        
        results = {}
        
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
