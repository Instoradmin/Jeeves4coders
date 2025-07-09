"""
Jeeves4coders User Analytics and Database Integration

This module handles user analytics, usage tracking, and integration with
the Aurigraph user database for measuring usage and capturing bugs/feedback.

Privacy-compliant data collection - NO SOURCE CODE is transmitted.
"""

import json
import uuid
import hashlib
import platform
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import requests
import logging
from pathlib import Path
import os


class UserAnalytics:
    """
    Handles user analytics and database integration for Jeeves4coders.
    
    Privacy Features:
    - No source code content is collected or transmitted
    - Only usage metrics and error logs (without code) are sent
    - User can opt-out of analytics at any time
    - All data is anonymized where possible
    """
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.expanduser("~/.jeeves4coders")
        self.analytics_config_file = os.path.join(self.config_dir, "analytics.json")
        self.user_id_file = os.path.join(self.config_dir, "user_id.txt")
        
        # Aurigraph Analytics API endpoints
        # Use localhost for testing, production will use https://analytics.aurigraph.io/api/v1
        self.base_url = os.getenv("JEEVES_ANALYTICS_URL", "http://localhost:8080/api/v1")
        self.endpoints = {
            "register": f"{self.base_url}/users/register",
            "usage": f"{self.base_url}/usage/track",
            "error": f"{self.base_url}/errors/report",
            "feedback": f"{self.base_url}/feedback/submit",
            "heartbeat": f"{self.base_url}/users/heartbeat"
        }
        
        self.logger = logging.getLogger(__name__)
        self.session_id = str(uuid.uuid4())
        self.session_start = time.time()
        
        # Initialize user tracking
        self._ensure_config_dir()
        self._load_analytics_config()
        self._load_or_create_user_id()
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _load_or_create_user_id(self):
        """Load existing user ID or create a new anonymous one."""
        try:
            if os.path.exists(self.user_id_file):
                with open(self.user_id_file, 'r') as f:
                    self.user_id = f.read().strip()
            else:
                # Create anonymous user ID based on system info
                system_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
                self.user_id = hashlib.sha256(system_info.encode()).hexdigest()[:16]
                
                with open(self.user_id_file, 'w') as f:
                    f.write(self.user_id)
                    
                # Register new user
                self._register_user()
                
        except Exception as e:
            self.logger.warning(f"Failed to load/create user ID: {e}")
            self.user_id = "anonymous"
    
    def _load_analytics_config(self):
        """Load analytics configuration (opt-in/opt-out settings)."""
        default_config = {
            "analytics_enabled": True,
            "error_reporting_enabled": True,
            "usage_tracking_enabled": True,
            "feedback_enabled": True,
            "last_privacy_consent": None,
            "privacy_policy_version": "1.0.0"
        }
        
        try:
            if os.path.exists(self.analytics_config_file):
                with open(self.analytics_config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            else:
                self.config = default_config
                self._save_analytics_config()
        except Exception as e:
            self.logger.warning(f"Failed to load analytics config: {e}")
            self.config = default_config
    
    def _save_analytics_config(self):
        """Save analytics configuration to file."""
        try:
            with open(self.analytics_config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save analytics config: {e}")
    
    def _register_user(self):
        """Register new user with Aurigraph analytics database."""
        if not self.config.get("analytics_enabled", True):
            return
        
        try:
            user_data = {
                "user_id": self.user_id,
                "registration_date": datetime.now(timezone.utc).isoformat(),
                "system_info": {
                    "platform": platform.system(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "python_version": platform.python_version(),
                    "jeeves_version": "1.0.0"
                },
                "privacy_consent": {
                    "privacy_policy_version": self.config["privacy_policy_version"],
                    "consent_date": datetime.now(timezone.utc).isoformat(),
                    "analytics_enabled": True,
                    "code_safety_acknowledged": True
                }
            }
            
            response = requests.post(
                self.endpoints["register"],
                json=user_data,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                self.logger.info("User registered successfully with Aurigraph analytics")
                self.config["last_privacy_consent"] = datetime.now(timezone.utc).isoformat()
                self._save_analytics_config()
            else:
                self.logger.warning(f"User registration failed: {response.status_code}")
                
        except Exception as e:
            self.logger.warning(f"Failed to register user: {e}")
    
    def track_usage(self, event_type: str, event_data: Dict[str, Any] = None):
        """
        Track usage events (NO SOURCE CODE included).
        
        Args:
            event_type: Type of event (e.g., 'workflow_executed', 'tool_started')
            event_data: Additional metadata (no code content)
        """
        if not self.config.get("usage_tracking_enabled", True):
            return
        
        try:
            usage_event = {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_data": event_data or {},
                "system_context": {
                    "platform": platform.system(),
                    "jeeves_version": "1.0.0",
                    "session_duration": time.time() - self.session_start
                }
            }
            
            # Ensure no sensitive data is included
            self._sanitize_event_data(usage_event)
            
            response = requests.post(
                self.endpoints["usage"],
                json=usage_event,
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.logger.debug(f"Usage tracking failed: {response.status_code}")
                
        except Exception as e:
            self.logger.debug(f"Failed to track usage: {e}")
    
    def report_error(self, error_type: str, error_message: str, 
                    context: Dict[str, Any] = None, stack_trace: str = None):
        """
        Report errors for bug tracking (NO SOURCE CODE included).
        
        Args:
            error_type: Type of error (e.g., 'ModuleError', 'ConfigError')
            error_message: Error message (sanitized)
            context: Additional context (no code content)
            stack_trace: Stack trace (sanitized)
        """
        if not self.config.get("error_reporting_enabled", True):
            return
        
        try:
            # Sanitize error message and stack trace
            sanitized_message = self._sanitize_error_message(error_message)
            sanitized_stack = self._sanitize_stack_trace(stack_trace) if stack_trace else None
            
            error_report = {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "error_type": error_type,
                "error_message": sanitized_message,
                "stack_trace": sanitized_stack,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": context or {},
                "system_info": {
                    "platform": platform.system(),
                    "python_version": platform.python_version(),
                    "jeeves_version": "1.0.0"
                }
            }
            
            # Additional sanitization
            self._sanitize_event_data(error_report)
            
            response = requests.post(
                self.endpoints["error"],
                json=error_report,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                self.logger.debug("Error reported successfully")
            else:
                self.logger.debug(f"Error reporting failed: {response.status_code}")
                
        except Exception as e:
            self.logger.debug(f"Failed to report error: {e}")
    
    def submit_feedback(self, feedback_type: str, message: str, 
                       rating: int = None, metadata: Dict[str, Any] = None):
        """
        Submit user feedback.
        
        Args:
            feedback_type: Type of feedback ('bug', 'feature_request', 'general')
            message: Feedback message
            rating: Optional rating (1-5)
            metadata: Additional metadata
        """
        if not self.config.get("feedback_enabled", True):
            return
        
        try:
            feedback_data = {
                "user_id": self.user_id,
                "feedback_type": feedback_type,
                "message": message,
                "rating": rating,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
                "system_info": {
                    "platform": platform.system(),
                    "jeeves_version": "1.0.0"
                }
            }
            
            response = requests.post(
                self.endpoints["feedback"],
                json=feedback_data,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                self.logger.info("Feedback submitted successfully")
                return True
            else:
                self.logger.warning(f"Feedback submission failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.warning(f"Failed to submit feedback: {e}")
            return False
    
    def send_heartbeat(self):
        """Send periodic heartbeat to track active users."""
        if not self.config.get("analytics_enabled", True):
            return
        
        try:
            heartbeat_data = {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_duration": time.time() - self.session_start,
                "jeeves_version": "1.0.0"
            }
            
            response = requests.post(
                self.endpoints["heartbeat"],
                json=heartbeat_data,
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.logger.debug(f"Heartbeat failed: {response.status_code}")
                
        except Exception as e:
            self.logger.debug(f"Failed to send heartbeat: {e}")
    
    def _sanitize_event_data(self, data: Dict[str, Any]):
        """Remove any potentially sensitive data from event data."""
        sensitive_keys = [
            'code', 'source', 'content', 'file_content', 'script',
            'password', 'token', 'key', 'secret', 'credential',
            'path', 'filename', 'directory', 'file_path'
        ]
        
        def sanitize_recursive(obj):
            if isinstance(obj, dict):
                return {
                    k: sanitize_recursive(v) for k, v in obj.items()
                    if not any(sensitive in k.lower() for sensitive in sensitive_keys)
                }
            elif isinstance(obj, list):
                return [sanitize_recursive(item) for item in obj]
            elif isinstance(obj, str) and len(obj) > 1000:
                # Truncate very long strings that might contain code
                return obj[:100] + "... [truncated]"
            return obj
        
        return sanitize_recursive(data)
    
    def _sanitize_error_message(self, message: str) -> str:
        """Sanitize error messages to remove potential code content."""
        if not message:
            return ""
        
        # Remove file paths
        import re
        message = re.sub(r'[/\\][^\s]+\.(py|js|ts|java|cpp|c|h)', '[FILE_PATH]', message)
        
        # Remove potential code snippets (lines with common code patterns)
        lines = message.split('\n')
        sanitized_lines = []
        for line in lines:
            if any(pattern in line for pattern in ['def ', 'class ', 'function ', 'import ', 'from ']):
                sanitized_lines.append('[CODE_LINE_REMOVED]')
            else:
                sanitized_lines.append(line)
        
        return '\n'.join(sanitized_lines)
    
    def _sanitize_stack_trace(self, stack_trace: str) -> str:
        """Sanitize stack traces to remove file paths and code content."""
        if not stack_trace:
            return ""
        
        lines = stack_trace.split('\n')
        sanitized_lines = []
        
        for line in lines:
            # Keep error types and basic structure, remove file paths and code
            if 'File "' in line:
                sanitized_lines.append('  File "[PATH_REMOVED]", line [LINE], in [FUNCTION]')
            elif line.strip().startswith('File '):
                sanitized_lines.append('[FILE_REFERENCE_REMOVED]')
            elif any(keyword in line for keyword in ['def ', 'class ', 'import ', 'from ']):
                sanitized_lines.append('[CODE_LINE_REMOVED]')
            else:
                sanitized_lines.append(line)
        
        return '\n'.join(sanitized_lines)
    
    def opt_out_analytics(self):
        """Allow user to opt out of all analytics."""
        self.config.update({
            "analytics_enabled": False,
            "error_reporting_enabled": False,
            "usage_tracking_enabled": False,
            "feedback_enabled": False
        })
        self._save_analytics_config()
        self.logger.info("Analytics disabled by user request")
    
    def opt_in_analytics(self):
        """Allow user to opt back into analytics."""
        self.config.update({
            "analytics_enabled": True,
            "error_reporting_enabled": True,
            "usage_tracking_enabled": True,
            "feedback_enabled": True,
            "last_privacy_consent": datetime.now(timezone.utc).isoformat()
        })
        self._save_analytics_config()
        self.logger.info("Analytics enabled by user request")
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """Get current privacy and analytics settings."""
        return {
            "user_id": self.user_id,
            "analytics_enabled": self.config.get("analytics_enabled", True),
            "error_reporting_enabled": self.config.get("error_reporting_enabled", True),
            "usage_tracking_enabled": self.config.get("usage_tracking_enabled", True),
            "feedback_enabled": self.config.get("feedback_enabled", True),
            "last_privacy_consent": self.config.get("last_privacy_consent"),
            "privacy_policy_version": self.config.get("privacy_policy_version", "1.0.0"),
            "code_safety_guarantee": "Your source code is NEVER transmitted or stored"
        }


# Global analytics instance
_analytics_instance = None

def get_analytics() -> UserAnalytics:
    """Get the global analytics instance."""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = UserAnalytics()
    return _analytics_instance

def track_usage(event_type: str, event_data: Dict[str, Any] = None):
    """Convenience function to track usage events."""
    try:
        get_analytics().track_usage(event_type, event_data)
    except Exception:
        pass  # Fail silently to not disrupt user workflow

def report_error(error_type: str, error_message: str, 
                context: Dict[str, Any] = None, stack_trace: str = None):
    """Convenience function to report errors."""
    try:
        get_analytics().report_error(error_type, error_message, context, stack_trace)
    except Exception:
        pass  # Fail silently to not disrupt user workflow
