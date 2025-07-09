#!/usr/bin/env python3
"""
Engineering Automation Agent - Utilities Module
Common utilities and helper functions for all agent modules
"""

import json
import base64
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import logging


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
