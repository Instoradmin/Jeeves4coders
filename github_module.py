#!/usr/bin/env python3
"""
GitHub Integration Module
GitHub API integration for repository management, commits, PRs, and CI/CD workflows
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .core_agent import AgentModule, AgentConfig

@dataclass
class GitHubCommit:
    """GitHub commit information"""
    sha: str
    message: str
    author: str
    timestamp: str
    url: str

@dataclass
class GitHubPullRequest:
    """GitHub pull request information"""
    number: int
    title: str
    state: str
    author: str
    created_at: str
    updated_at: str
    url: str
    mergeable: bool = False

@dataclass
class GitHubRepository:
    """GitHub repository information"""
    name: str
    full_name: str
    description: str
    private: bool
    default_branch: str
    url: str
    clone_url: str

class GitHubModule(AgentModule):
    """GitHub integration module for repository management and CI/CD"""
    
    def __init__(self, config: AgentConfig, logger):
        super().__init__(config, logger)
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {config.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Engineering-Automation-Agent/1.0"
        }
    
    def validate_config(self) -> bool:
        """Validate GitHub configuration"""
        if not self.config.github_enabled:
            self.log_info("GitHub integration disabled in configuration")
            return False
        
        if not self.config.github_token:
            self.log_error("GitHub token not provided")
            return False
        
        if not self.config.github_repo or not self.config.github_owner:
            self.log_error("GitHub repository or owner not specified")
            return False
        
        # Test API connection
        try:
            response = requests.get(f"{self.api_base}/user", headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.log_error(f"GitHub API authentication failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Failed to connect to GitHub API: {str(e)}")
            return False
        
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub integration tasks"""
        self.log_info("🐙 Starting GitHub integration tasks")
        
        results = {}
        
        # Get repository information
        repo_info = self.get_repository_info()
        results['repository'] = repo_info
        
        # Get recent commits
        commits = self.get_recent_commits(limit=10)
        results['recent_commits'] = commits
        
        # Get pull requests
        pull_requests = self.get_pull_requests()
        results['pull_requests'] = pull_requests
        
        # Check CI/CD status
        ci_status = self.get_ci_status()
        results['ci_status'] = ci_status
        
        # Get repository statistics
        stats = self.get_repository_stats()
        results['statistics'] = stats
        
        # Perform actions based on context
        if context.get('create_commit'):
            commit_result = self.create_commit(context.get('commit_message', 'Automated commit'))
            results['commit_created'] = commit_result
        
        if context.get('create_pr'):
            pr_result = self.create_pull_request(
                title=context.get('pr_title', 'Automated PR'),
                body=context.get('pr_body', 'Automated pull request'),
                head=context.get('pr_head', 'main'),
                base=context.get('pr_base', 'main')
            )
            results['pr_created'] = pr_result
        
        self.log_info("✅ GitHub integration tasks completed")
        return results
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information"""
        try:
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'name': repo_data['name'],
                    'full_name': repo_data['full_name'],
                    'description': repo_data.get('description', ''),
                    'private': repo_data['private'],
                    'default_branch': repo_data['default_branch'],
                    'url': repo_data['html_url'],
                    'clone_url': repo_data['clone_url'],
                    'stars': repo_data['stargazers_count'],
                    'forks': repo_data['forks_count'],
                    'open_issues': repo_data['open_issues_count'],
                    'language': repo_data.get('language', 'Unknown'),
                    'size': repo_data['size'],
                    'created_at': repo_data['created_at'],
                    'updated_at': repo_data['updated_at']
                }
            else:
                self.log_error(f"Failed to get repository info: {response.status_code}")
                return {}
                
        except Exception as e:
            self.log_error(f"Error getting repository info: {str(e)}")
            return {}
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits"""
        try:
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/commits"
            params = {'per_page': limit}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                commits_data = response.json()
                commits = []
                
                for commit_data in commits_data:
                    commit = {
                        'sha': commit_data['sha'][:8],
                        'full_sha': commit_data['sha'],
                        'message': commit_data['commit']['message'].split('\n')[0],  # First line only
                        'author': commit_data['commit']['author']['name'],
                        'author_email': commit_data['commit']['author']['email'],
                        'timestamp': commit_data['commit']['author']['date'],
                        'url': commit_data['html_url']
                    }
                    commits.append(commit)
                
                return commits
            else:
                self.log_error(f"Failed to get commits: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_error(f"Error getting commits: {str(e)}")
            return []
    
    def get_pull_requests(self, state: str = 'open') -> List[Dict[str, Any]]:
        """Get pull requests"""
        try:
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/pulls"
            params = {'state': state, 'per_page': 20}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                prs_data = response.json()
                prs = []
                
                for pr_data in prs_data:
                    pr = {
                        'number': pr_data['number'],
                        'title': pr_data['title'],
                        'state': pr_data['state'],
                        'author': pr_data['user']['login'],
                        'created_at': pr_data['created_at'],
                        'updated_at': pr_data['updated_at'],
                        'url': pr_data['html_url'],
                        'mergeable': pr_data.get('mergeable', False),
                        'head_branch': pr_data['head']['ref'],
                        'base_branch': pr_data['base']['ref'],
                        'draft': pr_data.get('draft', False)
                    }
                    prs.append(pr)
                
                return prs
            else:
                self.log_error(f"Failed to get pull requests: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_error(f"Error getting pull requests: {str(e)}")
            return []
    
    def get_ci_status(self) -> Dict[str, Any]:
        """Get CI/CD status for the latest commit"""
        try:
            # Get latest commit SHA
            commits = self.get_recent_commits(limit=1)
            if not commits:
                return {'status': 'unknown', 'message': 'No commits found'}
            
            latest_sha = commits[0]['full_sha']
            
            # Get status checks
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/commits/{latest_sha}/status"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                return {
                    'state': status_data['state'],
                    'total_count': status_data['total_count'],
                    'statuses': [
                        {
                            'context': status['context'],
                            'state': status['state'],
                            'description': status.get('description', ''),
                            'target_url': status.get('target_url', '')
                        }
                        for status in status_data['statuses']
                    ]
                }
            else:
                return {'status': 'unknown', 'message': f'API error: {response.status_code}'}
                
        except Exception as e:
            self.log_error(f"Error getting CI status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        try:
            stats = {}
            
            # Get contributors
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/contributors"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                contributors = response.json()
                stats['contributors_count'] = len(contributors)
                stats['top_contributors'] = [
                    {
                        'login': contrib['login'],
                        'contributions': contrib['contributions']
                    }
                    for contrib in contributors[:5]
                ]
            
            # Get languages
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/languages"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                languages = response.json()
                total_bytes = sum(languages.values())
                stats['languages'] = {
                    lang: {
                        'bytes': bytes_count,
                        'percentage': round((bytes_count / total_bytes) * 100, 2) if total_bytes > 0 else 0
                    }
                    for lang, bytes_count in languages.items()
                }
            
            # Get release information
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/releases/latest"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                stats['latest_release'] = {
                    'tag_name': release_data['tag_name'],
                    'name': release_data['name'],
                    'published_at': release_data['published_at'],
                    'url': release_data['html_url']
                }
            
            return stats
            
        except Exception as e:
            self.log_error(f"Error getting repository stats: {str(e)}")
            return {}
    
    def create_commit(self, message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a commit with specified files"""
        try:
            # Use git command line for committing
            if files:
                # Add specific files
                for file in files:
                    result = subprocess.run(['git', 'add', file], 
                                          cwd=self.config.project_root, 
                                          capture_output=True, text=True)
                    if result.returncode != 0:
                        self.log_warning(f"Failed to add file {file}: {result.stderr}")
            else:
                # Add all changes
                result = subprocess.run(['git', 'add', '.'], 
                                      cwd=self.config.project_root, 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    return {'success': False, 'error': f"Failed to add files: {result.stderr}"}
            
            # Create commit
            result = subprocess.run(['git', 'commit', '-m', message], 
                                  cwd=self.config.project_root, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get commit SHA
                sha_result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                          cwd=self.config.project_root, 
                                          capture_output=True, text=True)
                commit_sha = sha_result.stdout.strip() if sha_result.returncode == 0 else 'unknown'
                
                return {
                    'success': True,
                    'commit_sha': commit_sha,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            self.log_error(f"Error creating commit: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_pull_request(self, title: str, body: str, head: str, base: str) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/pulls"
            
            data = {
                'title': title,
                'body': body,
                'head': head,
                'base': base
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    'success': True,
                    'number': pr_data['number'],
                    'url': pr_data['html_url'],
                    'title': pr_data['title'],
                    'state': pr_data['state']
                }
            else:
                error_msg = response.json().get('message', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.log_error(f"Error creating pull request: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def push_changes(self, branch: str = None) -> Dict[str, Any]:
        """Push changes to remote repository"""
        try:
            # Get current branch if not specified
            if not branch:
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      cwd=self.config.project_root, 
                                      capture_output=True, text=True)
                branch = result.stdout.strip() if result.returncode == 0 else 'main'
            
            # Push changes
            result = subprocess.run(['git', 'push', 'origin', branch], 
                                  cwd=self.config.project_root, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'branch': branch,
                    'message': 'Changes pushed successfully'
                }
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            self.log_error(f"Error pushing changes: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_workflow_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get GitHub Actions workflow runs"""
        try:
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/actions/runs"
            params = {'per_page': limit}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                runs_data = response.json()
                runs = []
                
                for run_data in runs_data.get('workflow_runs', []):
                    run = {
                        'id': run_data['id'],
                        'name': run_data['name'],
                        'status': run_data['status'],
                        'conclusion': run_data.get('conclusion'),
                        'created_at': run_data['created_at'],
                        'updated_at': run_data['updated_at'],
                        'url': run_data['html_url'],
                        'head_branch': run_data['head_branch'],
                        'head_sha': run_data['head_sha'][:8]
                    }
                    runs.append(run)
                
                return runs
            else:
                self.log_error(f"Failed to get workflow runs: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_error(f"Error getting workflow runs: {str(e)}")
            return []
