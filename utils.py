#!/usr/bin/env python3
"""
Enhanced Engineering Automation Agent - Utilities Module
Common utilities, helper functions, database connections, and shared functionality for all agent modules
Supports internationalization and comprehensive error handling
"""

import json
import base64
import requests
import os
import sys
import sqlite3
import psycopg2
import mysql.connector
import logging
import traceback
import subprocess
import tempfile
import shutil
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from contextlib import contextmanager
import configparser


# =============================================================================
# DATABASE CONNECTION UTILITIES
# =============================================================================

class DatabaseConnectionManager:
    """Centralized database connection management"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._connections = {}

    @contextmanager
    def get_connection(self, db_type: str = 'default'):
        """Get database connection with context management"""
        connection = None
        try:
            connection = self._create_connection(db_type)
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                connection.close()

    def _create_connection(self, db_type: str):
        """Create database connection based on configuration"""
        db_config = getattr(self.config, f'{db_type}_database', {})

        if not db_config:
            # Try default database configuration
            db_config = getattr(self.config, 'database', {})

        if not db_config:
            # Create SQLite connection as fallback
            db_path = os.path.join(self.config.project_root, 'project.db')
            return sqlite3.connect(db_path)

        db_engine = db_config.get('engine', 'sqlite').lower()

        if db_engine == 'sqlite':
            db_path = db_config.get('path', os.path.join(self.config.project_root, 'project.db'))
            return sqlite3.connect(db_path)

        elif db_engine == 'postgresql':
            return psycopg2.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                database=db_config.get('name'),
                user=db_config.get('user'),
                password=db_config.get('password')
            )

        elif db_engine == 'mysql':
            return mysql.connector.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 3306),
                database=db_config.get('name'),
                user=db_config.get('user'),
                password=db_config.get('password')
            )

        else:
            raise ValueError(f"Unsupported database engine: {db_engine}")

def get_database_connection(config, db_type: str = 'default'):
    """Get database connection - convenience function"""
    manager = DatabaseConnectionManager(config)
    return manager._create_connection(db_type)

def execute_database_query(config, query: str, params: tuple = None, db_type: str = 'default') -> List[Dict[str, Any]]:
    """Execute database query and return results"""
    try:
        with DatabaseConnectionManager(config).get_connection(db_type) as conn:
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch results
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            conn.commit()
            return results

    except Exception as e:
        logging.error(f"Database query failed: {str(e)}")
        raise e

# =============================================================================
# EXCEPTION HANDLING UTILITIES
# =============================================================================

def format_exception_details(exception: Exception) -> Dict[str, Any]:
    """Format exception details for comprehensive reporting"""
    return {
        'type': type(exception).__name__,
        'message': str(exception),
        'traceback': traceback.format_exc(),
        'timestamp': datetime.now().isoformat(),
        'module': getattr(exception, '__module__', 'unknown'),
        'line_number': traceback.extract_tb(exception.__traceback__)[-1].lineno if exception.__traceback__ else None,
        'file_name': traceback.extract_tb(exception.__traceback__)[-1].filename if exception.__traceback__ else None
    }

def collect_and_report_exceptions(exceptions: List[Dict[str, Any]], output_file: str = None) -> Dict[str, Any]:
    """Collect and report all exceptions at the end of build"""
    if not exceptions:
        return {'status': 'success', 'exception_count': 0}

    exception_report = {
        'status': 'failed' if exceptions else 'success',
        'exception_count': len(exceptions),
        'exceptions': exceptions,
        'summary': {
            'total_exceptions': len(exceptions),
            'exception_types': {},
            'affected_modules': set(),
            'timestamp': datetime.now().isoformat()
        }
    }

    # Analyze exceptions
    for exc in exceptions:
        exc_type = exc.get('type', 'Unknown')
        module = exc.get('module', 'unknown')

        # Count exception types
        if exc_type not in exception_report['summary']['exception_types']:
            exception_report['summary']['exception_types'][exc_type] = 0
        exception_report['summary']['exception_types'][exc_type] += 1

        # Track affected modules
        exception_report['summary']['affected_modules'].add(module)

    # Convert set to list for JSON serialization
    exception_report['summary']['affected_modules'] = list(exception_report['summary']['affected_modules'])

    # Save to file if specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(exception_report, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save exception report: {str(e)}")

    return exception_report

# =============================================================================
# COMMAND EXECUTION UTILITIES
# =============================================================================

def run_command_with_timeout(command: List[str], timeout: int = 300, cwd: str = None) -> Dict[str, Any]:
    """Run command with timeout and comprehensive error handling"""
    try:
        result = subprocess.run(
            command,
            timeout=timeout,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )

        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': ' '.join(command),
            'execution_time': None,  # Would need timing wrapper
            'cwd': cwd
        }

    except subprocess.TimeoutExpired as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': e.stdout or '',
            'stderr': e.stderr or '',
            'command': ' '.join(command),
            'error': f"Command timed out after {timeout} seconds",
            'timeout': True,
            'cwd': cwd
        }

    except Exception as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'command': ' '.join(command),
            'error': str(e),
            'exception': format_exception_details(e),
            'cwd': cwd
        }

def setup_logging(log_level: str = 'INFO', log_file: str = None) -> logging.Logger:
    """Setup centralized logging configuration"""
    logger = logging.getLogger('engineering_automation_agent')

    # Clear existing handlers
    logger.handlers.clear()

    # Set log level
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# =============================================================================
# FILE AND PATH UTILITIES
# =============================================================================

def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
    """Validate file path with comprehensive checks"""
    try:
        path = Path(file_path)

        if must_exist and not path.exists():
            return False

        # Check if path is within allowed directories (security check)
        resolved_path = path.resolve()

        # Basic security check - ensure path doesn't contain suspicious patterns
        suspicious_patterns = ['../', '..\\', '/etc/', '/root/', 'C:\\Windows\\']
        path_str = str(resolved_path)

        for pattern in suspicious_patterns:
            if pattern in path_str:
                logging.warning(f"Suspicious path pattern detected: {pattern} in {path_str}")
                return False

        return True

    except Exception as e:
        logging.error(f"Path validation failed for {file_path}: {str(e)}")
        return False

def create_secure_temp_directory() -> str:
    """Create secure temporary directory"""
    temp_dir = tempfile.mkdtemp(prefix='engineering_agent_')
    os.chmod(temp_dir, 0o700)  # Owner read/write/execute only
    return temp_dir

def cleanup_temp_directory(temp_dir: str):
    """Safely cleanup temporary directory"""
    try:
        if os.path.exists(temp_dir) and temp_dir.startswith('/tmp/') or temp_dir.startswith(tempfile.gettempdir()):
            shutil.rmtree(temp_dir)
    except Exception as e:
        logging.error(f"Failed to cleanup temp directory {temp_dir}: {str(e)}")

def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """Calculate file hash for integrity checking"""
    try:
        hash_func = getattr(hashlib, algorithm)()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    except Exception as e:
        logging.error(f"Failed to calculate hash for {file_path}: {str(e)}")
        return ""

class APIClient:
    """Generic API client with common functionality"""
    
    def __init__(self, base_url: str, headers: Dict[str, str], timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.headers = headers
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make GET request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self._make_request('GET', url, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
             json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make POST request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self._make_request('POST', url, data=data, json=json_data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make PUT request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self._make_request('PUT', url, data=data, json=json_data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self._make_request('DELETE', url)
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request failed: {method} {url} - {str(e)}")
            raise


class AuthenticationHelper:
    """Helper class for various authentication methods"""
    
    @staticmethod
    def create_basic_auth_header(email: str, token: str) -> str:
        """Create Basic authentication header"""
        auth_string = f"{email}:{token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return f"Basic {auth_b64}"
    
    @staticmethod
    def create_bearer_token_header(token: str) -> str:
        """Create Bearer token authentication header"""
        return f"Bearer {token}"
    
    @staticmethod
    def create_token_header(token: str) -> str:
        """Create token authentication header"""
        return f"token {token}"


class ResponseParser:
    """Helper class for parsing API responses"""
    
    @staticmethod
    def parse_json_response(response: requests.Response) -> Dict[str, Any]:
        """Parse JSON response with error handling"""
        try:
            if response.content:
                return response.json()
            return {}
        except json.JSONDecodeError as e:
            logging.getLogger(__name__).error(f"Failed to parse JSON response: {str(e)}")
            return {}
    
    @staticmethod
    def extract_error_message(response: requests.Response) -> str:
        """Extract error message from response"""
        if response.content:
            try:
                error_data = response.json()
                # Try common error message fields
                for field in ['message', 'error', 'detail', 'errorMessage']:
                    if field in error_data:
                        return str(error_data[field])
                return f"HTTP {response.status_code}"
            except json.JSONDecodeError:
                return f"HTTP {response.status_code}"
        return f"HTTP {response.status_code}"
    
    @staticmethod
    def create_success_response(data: Any, message: str = "") -> Dict[str, Any]:
        """Create standardized success response"""
        return {
            'success': True,
            'data': data,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def create_error_response(error: str, code: Optional[int] = None) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'success': False,
            'error': error,
            'code': code,
            'timestamp': datetime.now().isoformat()
        }


class ContentFormatter:
    """Helper class for formatting content"""
    
    @staticmethod
    def format_content_with_attribution(content: str, platform: str = "confluence") -> str:
        """Format content with Augment Code attribution"""
        utm_medium = f"{platform}_page" if platform == "confluence" else f"{platform}_content"
        
        if platform == "confluence":
            attribution_html = f'''
<hr/>
<p>
Co-authored by <a href="https://www.augmentcode.com/?utm_source=atlassian&utm_medium={utm_medium}&utm_campaign={platform}">Augment Code</a>
</p>
'''
        else:
            attribution_html = f'''

---
Co-authored by [Augment Code](https://www.augmentcode.com/?utm_source=platform&utm_medium={utm_medium}&utm_campaign={platform})
'''
        
        return content + attribution_html
    
    @staticmethod
    def format_timestamp(timestamp: Optional[str] = None) -> str:
        """Format timestamp for display"""
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                return timestamp
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


class ValidationHelper:
    """Helper class for configuration validation"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        return url.startswith(('http://', 'https://'))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        if not email:
            return False
        return '@' in email and '.' in email.split('@')[1]
    
    @staticmethod
    def validate_required_fields(config: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate required configuration fields"""
        missing_fields = []
        for field in required_fields:
            if not config.get(field):
                missing_fields.append(field)
        return missing_fields


class HTMLTableGenerator:
    """Helper class for generating HTML tables"""
    
    @staticmethod
    def create_table(headers: List[str], rows: List[List[str]], 
                    table_class: str = "") -> str:
        """Create HTML table"""
        class_attr = f' class="{table_class}"' if table_class else ''
        html = f"<table{class_attr}>\n"
        
        # Add headers
        html += "<tr>"
        for header in headers:
            html += f"<th>{header}</th>"
        html += "</tr>\n"
        
        # Add rows
        for row in rows:
            html += "<tr>"
            for cell in row:
                html += f"<td>{cell}</td>"
            html += "</tr>\n"
        
        html += "</table>"
        return html
    
    @staticmethod
    def create_metrics_table(metrics: Dict[str, Any]) -> str:
        """Create metrics table from dictionary"""
        headers = ["Metric", "Value"]
        rows = [[key.replace('_', ' ').title(), str(value)] for key, value in metrics.items()]
        return HTMLTableGenerator.create_table(headers, rows)


class FileHelper:
    """Helper class for file operations"""
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> bool:
        """Ensure directory exists, create if not"""
        import os
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except OSError:
            return False
    
    @staticmethod
    def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
        """Read JSON file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError):
            return None
    
    @staticmethod
    def write_json_file(file_path: str, data: Dict[str, Any]) -> bool:
        """Write JSON file safely"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, TypeError):
            return False


class StatusIconHelper:
    """Helper class for status icons and formatting"""
    
    STATUS_ICONS = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'pending': '⏳',
        'running': '🔄',
        'stopped': '⏹️'
    }
    
    @staticmethod
    def get_status_icon(status: str) -> str:
        """Get status icon for given status"""
        return StatusIconHelper.STATUS_ICONS.get(status.lower(), '❓')
    
    @staticmethod
    def format_status_with_icon(status: str, text: str) -> str:
        """Format text with status icon"""
        icon = StatusIconHelper.get_status_icon(status)
        return f"{icon} {text}"

# =============================================================================
# GITHUB INTEGRATION UTILITIES
# =============================================================================

def create_github_repository_structure(repo_url: str, project_name: str) -> Dict[str, Any]:
    """Create GitHub repository structure for test artifacts"""
    try:
        # Parse repository URL
        if repo_url.startswith('https://github.com/'):
            repo_path = repo_url.replace('https://github.com/', '').rstrip('.git')
        else:
            repo_path = repo_url

        # Create directory structure
        structure = {
            'repository': repo_path,
            'project': project_name,
            'directories': {
                'test_results': f'test_results/{project_name}',
                'test_scripts': f'test_scripts/{project_name}',
                'coverage_reports': f'coverage/{project_name}',
                'artifacts': f'artifacts/{project_name}'
            },
            'timestamp': datetime.now().isoformat()
        }

        return structure

    except Exception as e:
        logging.error(f"Failed to create GitHub repository structure: {str(e)}")
        return {}

def store_test_artifacts_in_github(repo_url: str, file_path: str, content: str) -> str:
    """Store test artifacts in GitHub repository"""
    try:
        # This would integrate with GitHub API to store files
        # For now, return a mock path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        github_path = f"test_artifacts/{timestamp}/{file_path}"

        # In a real implementation, this would:
        # 1. Authenticate with GitHub API
        # 2. Create/update file in repository
        # 3. Return the actual GitHub URL

        logging.info(f"Test artifacts would be stored at: {github_path}")
        return github_path

    except Exception as e:
        logging.error(f"Failed to store test artifacts in GitHub: {str(e)}")
        return ""

def create_github_commit_with_comprehensive_description(
    repo_url: str,
    files: List[str],
    commit_message: str,
    test_results: Dict[str, Any] = None,
    build_info: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create GitHub commit with comprehensive description and comments"""
    try:
        # Generate comprehensive commit description
        description_parts = [commit_message]

        if test_results:
            description_parts.append("\n## Test Results")
            description_parts.append(f"- Total Tests: {test_results.get('total_tests', 0)}")
            description_parts.append(f"- Passed: {test_results.get('passed_tests', 0)}")
            description_parts.append(f"- Failed: {test_results.get('failed_tests', 0)}")
            description_parts.append(f"- Success Rate: {test_results.get('success_rate', 0):.1f}%")

        if build_info:
            description_parts.append("\n## Build Information")
            description_parts.append(f"- Build ID: {build_info.get('build_id', 'N/A')}")
            description_parts.append(f"- Build Time: {build_info.get('build_time', 'N/A')}")
            description_parts.append(f"- Environment: {build_info.get('environment', 'N/A')}")

        description_parts.append(f"\n## Files Modified")
        for file in files:
            description_parts.append(f"- {file}")

        description_parts.append(f"\n---\nGenerated by Engineering Automation Agent at {datetime.now().isoformat()}")

        comprehensive_description = "\n".join(description_parts)

        # Return commit information (in real implementation, this would create the actual commit)
        return {
            'commit_message': commit_message,
            'description': comprehensive_description,
            'files': files,
            'timestamp': datetime.now().isoformat(),
            'repository': repo_url
        }

    except Exception as e:
        logging.error(f"Failed to create GitHub commit: {str(e)}")
        return {}

# =============================================================================
# CONFIGURATION UTILITIES
# =============================================================================

def load_configuration_from_file(config_file: str) -> Dict[str, Any]:
    """Load configuration from various file formats"""
    try:
        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        if config_path.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                return json.load(f)

        elif config_path.suffix.lower() in ['.ini', '.cfg']:
            config = configparser.ConfigParser()
            config.read(config_path)

            # Convert to dictionary
            result = {}
            for section in config.sections():
                result[section] = dict(config[section])
            return result

        elif config_path.suffix.lower() in ['.yml', '.yaml']:
            try:
                import yaml
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML is required for YAML configuration files")

        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")

    except Exception as e:
        logging.error(f"Failed to load configuration from {config_file}: {str(e)}")
        raise e

def merge_configurations(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries"""
    merged = {}

    for config in configs:
        if config:
            merged.update(config)

    return merged

def validate_configuration(config: Dict[str, Any], required_keys: List[str]) -> Tuple[bool, List[str]]:
    """Validate configuration has required keys"""
    missing_keys = []

    for key in required_keys:
        if key not in config:
            missing_keys.append(key)

    return len(missing_keys) == 0, missing_keys

# =============================================================================
# PERFORMANCE MONITORING UTILITIES
# =============================================================================

def monitor_performance(func):
    """Decorator to monitor function performance"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        start_memory = get_memory_usage()

        try:
            result = func(*args, **kwargs)

            end_time = datetime.now()
            end_memory = get_memory_usage()

            execution_time = (end_time - start_time).total_seconds()
            memory_delta = end_memory - start_memory

            logging.info(f"Performance: {func.__name__} - Time: {execution_time:.2f}s, Memory: {memory_delta:.2f}MB")

            return result

        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            logging.error(f"Performance: {func.__name__} failed after {execution_time:.2f}s - {str(e)}")
            raise e

    return wrapper

def get_memory_usage() -> float:
    """Get current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    except ImportError:
        return 0.0
    except Exception:
        return 0.0

# =============================================================================
# SECURITY UTILITIES
# =============================================================================

def sanitize_input(input_string: str) -> str:
    """Sanitize input string to prevent injection attacks"""
    if not isinstance(input_string, str):
        return str(input_string)

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')', '{', '}']
    sanitized = input_string

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    # Limit length
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized.strip()

def validate_email(email: str) -> bool:
    """Validate email address format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_secure_token(length: int = 32) -> str:
    """Generate secure random token"""
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
