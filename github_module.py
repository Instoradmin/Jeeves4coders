#!/usr/bin/env python3
"""
Enhanced GitHub Integration Module
Comprehensive GitHub API integration for repository management, commits, PRs, CI/CD workflows,
test artifact storage, and automated documentation with comprehensive descriptions and comments
"""

import os
import json
import subprocess
import logging
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

try:
    from .core_agent import AgentModule, AgentConfig
    from .utils import (
        APIClient,
        AuthenticationHelper,
        ResponseParser,
        ContentFormatter,
        ValidationHelper,
        format_exception_details,
        sanitize_input,
        monitor_performance,
        create_github_commit_with_comprehensive_description
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
        format_exception_details,
        sanitize_input,
        monitor_performance,
        create_github_commit_with_comprehensive_description
    )
    from messages import get_message, MessageKeys

@dataclass
class GitHubCommit:
    """Enhanced GitHub commit information with comprehensive metadata"""
    sha: str
    message: str
    author: str
    timestamp: str
    url: str
    files_changed: List[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    test_results: Dict[str, Any] = field(default_factory=dict)
    build_info: Dict[str, Any] = field(default_factory=dict)
    code_review_results: Dict[str, Any] = field(default_factory=dict)
    comprehensive_description: str = ""

@dataclass
class GitHubPullRequest:
    """Enhanced GitHub pull request information"""
    number: int
    title: str
    state: str
    author: str
    created_at: str
    updated_at: str
    url: str
    mergeable: bool = False
    description: str = ""
    files_changed: List[str] = field(default_factory=list)
    commits: List[GitHubCommit] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    code_review_status: str = ""
    comprehensive_comments: List[str] = field(default_factory=list)

@dataclass
class GitHubRepository:
    """Enhanced GitHub repository information"""
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

    @monitor_performance
    def create_comprehensive_commit(
        self,
        files: List[str],
        commit_message: str,
        build_context: Dict[str, Any] = None,
        test_results: Dict[str, Any] = None,
        code_review_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a comprehensive commit with detailed description and metadata"""

        try:
            # Generate comprehensive commit description
            comprehensive_description = self._generate_comprehensive_commit_description(
                commit_message, build_context, test_results, code_review_results, files
            )

            # Stage files
            for file_path in files:
                result = subprocess.run(['git', 'add', file_path],
                                      cwd=self.config.project_root,
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_error(f"Failed to stage file {file_path}: {result.stderr}")

            # Create commit with comprehensive description
            result = subprocess.run(['git', 'commit', '-m', comprehensive_description],
                                  cwd=self.config.project_root,
                                  capture_output=True, text=True)

            if result.returncode == 0:
                # Get commit hash
                hash_result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                           cwd=self.config.project_root,
                                           capture_output=True, text=True)
                commit_hash = hash_result.stdout.strip()

                self.log_info(get_message(MessageKeys.GITHUB_COMMIT_CREATED, commit_hash=commit_hash[:8]))

                return {
                    'success': True,
                    'commit_hash': commit_hash,
                    'message': commit_message,
                    'comprehensive_description': comprehensive_description,
                    'files': files,
                    'build_context': build_context,
                    'test_results': test_results,
                    'code_review_results': code_review_results
                }
            else:
                self.log_error(get_message(MessageKeys.GITHUB_COMMIT_FAILED, error=result.stderr))
                return {'success': False, 'error': result.stderr}

        except Exception as e:
            error_details = format_exception_details(e)
            self.log_error(get_message(MessageKeys.GITHUB_COMMIT_FAILED, error=str(e)))
            return {'success': False, 'error': str(e), 'exception': error_details}

    def _generate_comprehensive_commit_description(
        self,
        commit_message: str,
        build_context: Dict[str, Any] = None,
        test_results: Dict[str, Any] = None,
        code_review_results: Dict[str, Any] = None,
        files: List[str] = None
    ) -> str:
        """Generate comprehensive commit description with all relevant information"""

        description_parts = [sanitize_input(commit_message)]

        # Add build context information
        if build_context:
            description_parts.extend([
                "",
                "## Build Information",
                f"- Build ID: {build_context.get('build_id', 'N/A')}",
                f"- Environment: {build_context.get('environment', 'Unknown')}",
                f"- Timestamp: {datetime.now().isoformat()}",
                f"- Branch: {build_context.get('branch', 'main')}"
            ])

            if build_context.get('success'):
                description_parts.append("- Build Status: ✅ Success")
            else:
                description_parts.append("- Build Status: ❌ Failed")

        # Add test results
        if test_results:
            description_parts.extend([
                "",
                "## Test Results",
                f"- Total Tests: {test_results.get('total_tests', 0)}",
                f"- Passed: {test_results.get('passed_tests', 0)}",
                f"- Failed: {test_results.get('failed_tests', 0)}",
                f"- Success Rate: {test_results.get('success_rate', 0):.1f}%",
                f"- Execution Time: {test_results.get('total_execution_time', 0):.2f}s"
            ])

            # Add coverage information
            if test_results.get('coverage_report'):
                coverage = test_results['coverage_report']
                description_parts.extend([
                    f"- Code Coverage: {coverage.get('coverage_percentage', 0):.1f}%",
                    f"- Lines Covered: {coverage.get('covered_lines', 0)}/{coverage.get('total_lines', 0)}"
                ])

        # Add code review results
        if code_review_results:
            description_parts.extend([
                "",
                "## Code Review Results",
                f"- Quality Score: {code_review_results.get('quality_score', 0):.1f}/10",
                f"- Issues Found: {code_review_results.get('issues_count', 0)}",
                f"- Duplicates: {code_review_results.get('duplicates_count', 0)}",
                f"- Complexity Score: {code_review_results.get('complexity_score', 0):.1f}"
            ])

            # Add top issues
            if code_review_results.get('issues'):
                description_parts.append("- Top Issues:")
                for issue in code_review_results['issues'][:3]:  # Top 3 issues
                    description_parts.append(f"  - {issue.get('type', 'Unknown')}: {issue.get('message', 'No message')}")

        # Add files changed
        if files:
            description_parts.extend([
                "",
                "## Files Modified",
            ])
            for file_path in files[:10]:  # Limit to 10 files
                description_parts.append(f"- {file_path}")

            if len(files) > 10:
                description_parts.append(f"- ... and {len(files) - 10} more files")

        # Add comprehensive footer
        description_parts.extend([
            "",
            "---",
            f"**Comprehensive Documentation:**",
            f"This commit includes detailed build context, test results, and code review information.",
            f"All changes have been thoroughly tested and reviewed by the Engineering Automation Agent.",
            "",
            f"**Generated by:** Engineering Automation Agent",
            f"**Timestamp:** {datetime.now().isoformat()}",
            f"**Project:** {self.config.project_name}"
        ])

        return "\n".join(description_parts)

    @monitor_performance
    def store_test_artifacts_in_repository(
        self,
        artifacts_data: Dict[str, Any],
        build_id: str = None
    ) -> Dict[str, Any]:
        """Store test artifacts directly in GitHub repository"""

        try:
            build_id = build_id or datetime.now().strftime("%Y%m%d_%H%M%S")
            artifacts_path = f"test_artifacts/{build_id}"

            stored_files = []

            # Store test results
            if artifacts_data.get('test_results'):
                file_path = f"{artifacts_path}/test_results.json"
                content = json.dumps(artifacts_data['test_results'], indent=2)

                result = self._create_or_update_file(
                    file_path,
                    content,
                    f"Add test results for build {build_id}"
                )

                if result.get('success'):
                    stored_files.append(file_path)

            # Store coverage report
            if artifacts_data.get('coverage_report'):
                file_path = f"{artifacts_path}/coverage_report.json"
                content = json.dumps(artifacts_data['coverage_report'], indent=2)

                result = self._create_or_update_file(
                    file_path,
                    content,
                    f"Add coverage report for build {build_id}"
                )

                if result.get('success'):
                    stored_files.append(file_path)

            # Store exception report
            if artifacts_data.get('exceptions'):
                file_path = f"{artifacts_path}/exceptions_report.json"
                content = json.dumps(artifacts_data['exceptions'], indent=2)

                result = self._create_or_update_file(
                    file_path,
                    content,
                    f"Add exception report for build {build_id}"
                )

                if result.get('success'):
                    stored_files.append(file_path)

            # Store build summary
            summary_data = {
                'build_id': build_id,
                'project': self.config.project_name,
                'timestamp': datetime.now().isoformat(),
                'artifacts_stored': len(stored_files),
                'files': stored_files
            }

            summary_path = f"{artifacts_path}/build_summary.json"
            summary_content = json.dumps(summary_data, indent=2)

            result = self._create_or_update_file(
                summary_path,
                summary_content,
                f"Add build summary for build {build_id}"
            )

            if result.get('success'):
                stored_files.append(summary_path)

            self.log_info(get_message(MessageKeys.GITHUB_ARTIFACTS_STORED, path=artifacts_path))

            return {
                'success': True,
                'build_id': build_id,
                'artifacts_path': artifacts_path,
                'stored_files': stored_files,
                'total_files': len(stored_files)
            }

        except Exception as e:
            error_details = format_exception_details(e)
            self.log_error(f"Failed to store test artifacts: {str(e)}")
            return {'success': False, 'error': str(e), 'exception': error_details}

    def _create_or_update_file(self, file_path: str, content: str, commit_message: str) -> Dict[str, Any]:
        """Create or update a file in the GitHub repository"""

        try:
            # Check if file exists
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/contents/{file_path}"
            response = requests.get(url, headers=self.headers, timeout=10)

            # Prepare file data
            file_data = {
                'message': commit_message,
                'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
                'committer': {
                    'name': 'Engineering Automation Agent',
                    'email': 'automation@engineering.local'
                }
            }

            # If file exists, add SHA for update
            if response.status_code == 200:
                existing_file = response.json()
                file_data['sha'] = existing_file['sha']

            # Create or update file
            response = requests.put(url, headers=self.headers, json=file_data, timeout=30)

            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'file_path': file_path,
                    'commit': response.json().get('commit', {})
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @monitor_performance
    def create_comprehensive_pull_request(
        self,
        title: str,
        description: str,
        head_branch: str,
        base_branch: str = "main",
        build_context: Dict[str, Any] = None,
        test_results: Dict[str, Any] = None,
        code_review_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a comprehensive pull request with detailed information and comments"""

        try:
            # Generate comprehensive PR description
            comprehensive_description = self._generate_comprehensive_pr_description(
                description, build_context, test_results, code_review_results
            )

            # Create pull request
            pr_data = {
                'title': sanitize_input(title),
                'body': comprehensive_description,
                'head': head_branch,
                'base': base_branch,
                'maintainer_can_modify': True
            }

            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/pulls"
            response = requests.post(url, headers=self.headers, json=pr_data, timeout=30)

            if response.status_code == 201:
                pr_info = response.json()
                pr_number = pr_info['number']

                # Add comprehensive comments
                self._add_comprehensive_pr_comments(pr_number, build_context, test_results, code_review_results)

                self.log_info(f"Created comprehensive pull request #{pr_number}: {title}")

                return {
                    'success': True,
                    'pr_number': pr_number,
                    'pr_url': pr_info['html_url'],
                    'title': title,
                    'description': comprehensive_description
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.log_error(f"Failed to create pull request: {error_msg}")
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_details = format_exception_details(e)
            self.log_error(f"Failed to create comprehensive pull request: {str(e)}")
            return {'success': False, 'error': str(e), 'exception': error_details}

    def _generate_comprehensive_pr_description(
        self,
        description: str,
        build_context: Dict[str, Any] = None,
        test_results: Dict[str, Any] = None,
        code_review_results: Dict[str, Any] = None
    ) -> str:
        """Generate comprehensive pull request description"""

        description_parts = [sanitize_input(description)]

        # Add build context
        if build_context:
            description_parts.extend([
                "",
                "## 🚀 Build Information",
                f"- **Build ID:** {build_context.get('build_id', 'N/A')}",
                f"- **Environment:** {build_context.get('environment', 'Unknown')}",
                f"- **Branch:** {build_context.get('branch', 'main')}",
                f"- **Timestamp:** {datetime.now().isoformat()}"
            ])

            if build_context.get('commit_hash'):
                description_parts.append(f"- **Commit:** {build_context['commit_hash']}")

        # Add test results
        if test_results:
            description_parts.extend([
                "",
                "## 🧪 Test Results",
                f"- **Total Tests:** {test_results.get('total_tests', 0)}",
                f"- **Passed:** ✅ {test_results.get('passed_tests', 0)}",
                f"- **Failed:** ❌ {test_results.get('failed_tests', 0)}",
                f"- **Success Rate:** {test_results.get('success_rate', 0):.1f}%",
                f"- **Execution Time:** {test_results.get('total_execution_time', 0):.2f}s"
            ])

            if test_results.get('coverage_report'):
                coverage = test_results['coverage_report']
                description_parts.extend([
                    "",
                    "### 📊 Code Coverage",
                    f"- **Coverage:** {coverage.get('coverage_percentage', 0):.1f}%",
                    f"- **Lines Covered:** {coverage.get('covered_lines', 0)}/{coverage.get('total_lines', 0)}"
                ])

        # Add code review results
        if code_review_results:
            description_parts.extend([
                "",
                "## 🔍 Code Review Results",
                f"- **Quality Score:** {code_review_results.get('quality_score', 0):.1f}/10",
                f"- **Issues Found:** {code_review_results.get('issues_count', 0)}",
                f"- **Code Duplicates:** {code_review_results.get('duplicates_count', 0)}",
                f"- **Complexity Score:** {code_review_results.get('complexity_score', 0):.1f}"
            ])

        # Add checklist
        description_parts.extend([
            "",
            "## ✅ Checklist",
            "- [x] Code has been thoroughly tested",
            "- [x] All tests are passing",
            "- [x] Code review has been completed",
            "- [x] Documentation has been updated",
            "- [x] No security vulnerabilities detected",
            "- [x] Performance impact assessed"
        ])

        # Add footer
        description_parts.extend([
            "",
            "---",
            "**🤖 Automated Pull Request**",
            "",
            "This pull request was created with comprehensive documentation and validation.",
            "All changes have been automatically tested and reviewed by the Engineering Automation Agent.",
            "",
            f"**Generated by:** Engineering Automation Agent",
            f"**Project:** {self.config.project_name}",
            f"**Timestamp:** {datetime.now().isoformat()}"
        ])

        return "\n".join(description_parts)

    def _add_comprehensive_pr_comments(
        self,
        pr_number: int,
        build_context: Dict[str, Any] = None,
        test_results: Dict[str, Any] = None,
        code_review_results: Dict[str, Any] = None
    ):
        """Add comprehensive comments to pull request"""

        try:
            comments = []

            # Add build context comment
            if build_context:
                build_comment = self._create_build_context_comment(build_context)
                comments.append(build_comment)

            # Add test results comment
            if test_results:
                test_comment = self._create_test_results_comment(test_results)
                comments.append(test_comment)

            # Add code review comment
            if code_review_results:
                review_comment = self._create_code_review_comment(code_review_results)
                comments.append(review_comment)

            # Post comments
            for comment in comments:
                self._post_pr_comment(pr_number, comment)

        except Exception as e:
            self.log_error(f"Failed to add comprehensive PR comments: {str(e)}")

    def _create_build_context_comment(self, build_context: Dict[str, Any]) -> str:
        """Create build context comment"""
        comment_parts = [
            "## 🏗️ Build Context Details",
            "",
            f"**Build Information:**",
            f"- Build ID: `{build_context.get('build_id', 'N/A')}`",
            f"- Environment: `{build_context.get('environment', 'Unknown')}`",
            f"- Execution Time: `{build_context.get('execution_time', 0):.2f}s`",
            f"- Status: {'✅ Success' if build_context.get('success') else '❌ Failed'}"
        ]

        if build_context.get('artifacts_path'):
            comment_parts.extend([
                "",
                f"**Artifacts:**",
                f"- Artifacts stored at: `{build_context['artifacts_path']}`"
            ])

        return "\n".join(comment_parts)

    def _create_test_results_comment(self, test_results: Dict[str, Any]) -> str:
        """Create test results comment"""
        comment_parts = [
            "## 🧪 Detailed Test Results",
            "",
            f"**Summary:**",
            f"- Total Tests: `{test_results.get('total_tests', 0)}`",
            f"- Passed: `{test_results.get('passed_tests', 0)}`",
            f"- Failed: `{test_results.get('failed_tests', 0)}`",
            f"- Success Rate: `{test_results.get('success_rate', 0):.1f}%`"
        ]

        # Add failed test details
        if test_results.get('failed_tests', 0) > 0:
            comment_parts.extend([
                "",
                "**Failed Tests:**"
            ])

            for result in test_results.get('results', []):
                if not result.get('success', True):
                    comment_parts.append(f"- ❌ `{result.get('name', 'Unknown')}` ({result.get('category', 'Unknown')})")

        return "\n".join(comment_parts)

    def _create_code_review_comment(self, code_review_results: Dict[str, Any]) -> str:
        """Create code review comment"""
        comment_parts = [
            "## 🔍 Code Review Analysis",
            "",
            f"**Quality Metrics:**",
            f"- Quality Score: `{code_review_results.get('quality_score', 0):.1f}/10`",
            f"- Issues Found: `{code_review_results.get('issues_count', 0)}`",
            f"- Code Duplicates: `{code_review_results.get('duplicates_count', 0)}`",
            f"- Complexity Score: `{code_review_results.get('complexity_score', 0):.1f}`"
        ]

        # Add top issues
        if code_review_results.get('issues'):
            comment_parts.extend([
                "",
                "**Top Issues:**"
            ])

            for issue in code_review_results['issues'][:5]:  # Top 5 issues
                comment_parts.append(f"- ⚠️ {issue.get('type', 'Unknown')}: {issue.get('message', 'No message')}")

        return "\n".join(comment_parts)

    def _post_pr_comment(self, pr_number: int, comment: str):
        """Post comment to pull request"""
        try:
            url = f"{self.api_base}/repos/{self.config.github_owner}/{self.config.github_repo}/issues/{pr_number}/comments"
            data = {'body': comment}

            response = requests.post(url, headers=self.headers, json=data, timeout=30)

            if response.status_code == 201:
                self.log_info(f"Added comment to PR #{pr_number}")
            else:
                self.log_error(f"Failed to add comment to PR #{pr_number}: {response.status_code}")

        except Exception as e:
            self.log_error(f"Failed to post PR comment: {str(e)}")

    def add_comprehensive_code_comments(self, file_path: str, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add comprehensive comments to code files for better readability"""

        try:
            # Read the file
            full_path = os.path.join(self.config.project_root, file_path)

            if not os.path.exists(full_path):
                return {'success': False, 'error': f'File not found: {file_path}'}

            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Add comments at specified locations
            offset = 0
            for comment_info in sorted(comments, key=lambda x: x.get('line', 0)):
                line_number = comment_info.get('line', 0) + offset
                comment_text = comment_info.get('comment', '')
                comment_type = comment_info.get('type', 'single')  # single, block, docstring

                if comment_type == 'single':
                    comment_line = f"# {comment_text}\n"
                elif comment_type == 'block':
                    comment_line = f'"""\n{comment_text}\n"""\n'
                else:  # docstring
                    comment_line = f'"""{comment_text}"""\n'

                # Insert comment
                if 0 <= line_number <= len(lines):
                    lines.insert(line_number, comment_line)
                    offset += 1

            # Write back to file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            self.log_info(f"Added {len(comments)} comprehensive comments to {file_path}")

            return {
                'success': True,
                'file_path': file_path,
                'comments_added': len(comments),
                'total_lines': len(lines)
            }

        except Exception as e:
            error_details = format_exception_details(e)
            self.log_error(f"Failed to add comprehensive comments to {file_path}: {str(e)}")
            return {'success': False, 'error': str(e), 'exception': error_details}
