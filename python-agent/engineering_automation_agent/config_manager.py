#!/usr/bin/env python3
"""
Configuration Management System
Flexible configuration system for different projects and environments
"""

import os
import json
import yaml
import configparser
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    from .core_agent import AgentConfig
except ImportError:
    # Handle relative import for standalone usage
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from core_agent import AgentConfig

@dataclass
class ProjectTemplate:
    """Project template configuration"""
    name: str
    description: str
    project_type: str
    default_config: Dict[str, Any] = field(default_factory=dict)
    required_files: List[str] = field(default_factory=list)
    optional_files: List[str] = field(default_factory=list)

class ConfigurationManager:
    """Manages configuration for different projects and environments"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / ".engineering_agent"
        self.config_dir.mkdir(exist_ok=True)
        
        # Default configuration file paths
        self.global_config_file = self.config_dir / "global_config.json"
        self.projects_config_file = self.config_dir / "projects.json"
        self.templates_config_file = self.config_dir / "templates.json"
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default configuration files if they don't exist"""
        
        # Global configuration
        if not self.global_config_file.exists():
            default_global_config = {
                "version": "1.0.0",
                "default_settings": {
                    "test_timeout": 300,
                    "test_coverage_threshold": 80.0,
                    "code_quality_threshold": 8.0,
                    "notifications_enabled": True,
                    "auto_deploy_on_success": False
                },
                "integrations": {
                    "github": {
                        "enabled": True,
                        "api_base": "https://api.github.com"
                    },
                    "jira": {
                        "enabled": True,
                        "api_version": "3"
                    },
                    "confluence": {
                        "enabled": True,
                        "api_version": "latest"
                    }
                }
            }
            self._save_json_config(self.global_config_file, default_global_config)
        
        # Project templates
        if not self.templates_config_file.exists():
            default_templates = {
                "python_web": {
                    "name": "Python Web Application",
                    "description": "Flask/Django web application template",
                    "project_type": "python",
                    "default_config": {
                        "test_types": ["unit", "functional", "regression"],
                        "test_framework": "pytest",
                        "app_port": 5000
                    },
                    "required_files": ["requirements.txt", "app.py"],
                    "optional_files": ["Dockerfile", "docker-compose.yml", "pytest.ini"]
                },
                "python_api": {
                    "name": "Python API Service",
                    "description": "REST API service template",
                    "project_type": "python",
                    "default_config": {
                        "test_types": ["unit", "functional", "regression", "performance"],
                        "test_framework": "pytest",
                        "app_port": 8000
                    },
                    "required_files": ["requirements.txt", "main.py"],
                    "optional_files": ["Dockerfile", "openapi.yaml"]
                },
                "javascript_web": {
                    "name": "JavaScript Web Application",
                    "description": "React/Vue/Angular web application template",
                    "project_type": "javascript",
                    "default_config": {
                        "test_types": ["unit", "functional", "regression"],
                        "test_framework": "jest",
                        "app_port": 3000
                    },
                    "required_files": ["package.json"],
                    "optional_files": ["Dockerfile", "jest.config.js", "webpack.config.js"]
                },
                "java_spring": {
                    "name": "Java Spring Application",
                    "description": "Spring Boot application template",
                    "project_type": "java",
                    "default_config": {
                        "test_types": ["unit", "functional", "regression"],
                        "test_framework": "junit",
                        "app_port": 8080
                    },
                    "required_files": ["pom.xml", "src/main/java"],
                    "optional_files": ["Dockerfile", "application.properties"]
                }
            }
            self._save_json_config(self.templates_config_file, default_templates)
        
        # Projects configuration (empty initially)
        if not self.projects_config_file.exists():
            self._save_json_config(self.projects_config_file, {})
    
    def create_project_config(self, project_name: str, project_root: str, 
                            template_name: str = None, custom_config: Dict[str, Any] = None) -> AgentConfig:
        """Create configuration for a new project"""
        
        # Load global settings
        global_config = self._load_json_config(self.global_config_file)
        default_settings = global_config.get("default_settings", {})
        
        # Start with default configuration
        config_data = {
            "project_name": project_name,
            "project_root": project_root,
            "project_type": "python"  # Default
        }
        
        # Apply default settings
        config_data.update(default_settings)
        
        # Apply template if specified
        if template_name:
            template_config = self.get_template_config(template_name)
            if template_config:
                config_data.update(template_config.get("default_config", {}))
                config_data["project_type"] = template_config.get("project_type", "python")
        
        # Apply custom configuration
        if custom_config:
            config_data.update(custom_config)
        
        # Auto-detect project type if not specified
        if not template_name:
            detected_type = self._detect_project_type(project_root)
            if detected_type:
                config_data["project_type"] = detected_type
        
        # Create AgentConfig instance
        config = AgentConfig(**config_data)
        
        # Save project configuration
        self.save_project_config(project_name, config)
        
        return config
    
    def load_project_config(self, project_name: str) -> Optional[AgentConfig]:
        """Load configuration for an existing project"""
        projects_config = self._load_json_config(self.projects_config_file)
        
        if project_name not in projects_config:
            return None
        
        project_data = projects_config[project_name]
        return AgentConfig(**project_data)
    
    def save_project_config(self, project_name: str, config: AgentConfig):
        """Save project configuration"""
        projects_config = self._load_json_config(self.projects_config_file)
        projects_config[project_name] = asdict(config)
        self._save_json_config(self.projects_config_file, projects_config)
    
    def list_projects(self) -> List[str]:
        """List all configured projects"""
        projects_config = self._load_json_config(self.projects_config_file)
        return list(projects_config.keys())
    
    def delete_project_config(self, project_name: str) -> bool:
        """Delete project configuration"""
        projects_config = self._load_json_config(self.projects_config_file)
        
        if project_name in projects_config:
            del projects_config[project_name]
            self._save_json_config(self.projects_config_file, projects_config)
            return True
        
        return False
    
    def get_template_config(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template configuration"""
        templates_config = self._load_json_config(self.templates_config_file)
        return templates_config.get(template_name)
    
    def list_templates(self) -> List[str]:
        """List available project templates"""
        templates_config = self._load_json_config(self.templates_config_file)
        return list(templates_config.keys())
    
    def create_template(self, template_name: str, template_data: Dict[str, Any]):
        """Create a new project template"""
        templates_config = self._load_json_config(self.templates_config_file)
        templates_config[template_name] = template_data
        self._save_json_config(self.templates_config_file, templates_config)
    
    def load_config_from_file(self, config_file: str) -> Optional[AgentConfig]:
        """Load configuration from a specific file"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            return None
        
        try:
            if config_path.suffix.lower() == '.json':
                config_data = self._load_json_config(config_path)
            elif config_path.suffix.lower() in ['.yml', '.yaml']:
                config_data = self._load_yaml_config(config_path)
            elif config_path.suffix.lower() in ['.ini', '.cfg']:
                config_data = self._load_ini_config(config_path)
            else:
                return None
            
            return AgentConfig(**config_data)
            
        except Exception as e:
            print(f"Error loading config from {config_file}: {e}")
            return None
    
    def save_config_to_file(self, config: AgentConfig, config_file: str, format: str = "json"):
        """Save configuration to a specific file"""
        config_path = Path(config_file)
        config_data = asdict(config)
        
        try:
            if format.lower() == "json":
                self._save_json_config(config_path, config_data)
            elif format.lower() in ["yml", "yaml"]:
                self._save_yaml_config(config_path, config_data)
            elif format.lower() in ["ini", "cfg"]:
                self._save_ini_config(config_path, config_data)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            print(f"Error saving config to {config_file}: {e}")
    
    def _detect_project_type(self, project_root: str) -> Optional[str]:
        """Auto-detect project type based on files present"""
        project_path = Path(project_root)
        
        # Python project indicators
        if (project_path / "requirements.txt").exists() or \
           (project_path / "setup.py").exists() or \
           (project_path / "pyproject.toml").exists():
            return "python"
        
        # JavaScript/Node.js project indicators
        if (project_path / "package.json").exists():
            return "javascript"
        
        # Java project indicators
        if (project_path / "pom.xml").exists() or \
           (project_path / "build.gradle").exists():
            return "java"
        
        # C# project indicators
        if any(project_path.glob("*.csproj")) or \
           any(project_path.glob("*.sln")):
            return "csharp"
        
        # Go project indicators
        if (project_path / "go.mod").exists():
            return "go"
        
        # Rust project indicators
        if (project_path / "Cargo.toml").exists():
            return "rust"
        
        return None
    
    def _load_json_config(self, config_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json_config(self, config_path: Path, config_data: Dict[str, Any]):
        """Save JSON configuration file"""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, default=str)
    
    def _load_yaml_config(self, config_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except (FileNotFoundError, yaml.YAMLError):
            return {}
    
    def _save_yaml_config(self, config_path: Path, config_data: Dict[str, Any]):
        """Save YAML configuration file"""
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, indent=2, default_flow_style=False)
    
    def _load_ini_config(self, config_path: Path) -> Dict[str, Any]:
        """Load INI configuration file"""
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Convert to nested dictionary
            config_data = {}
            for section_name in config.sections():
                config_data[section_name] = dict(config[section_name])
            
            return config_data
        except (FileNotFoundError, configparser.Error):
            return {}
    
    def _save_ini_config(self, config_path: Path, config_data: Dict[str, Any]):
        """Save INI configuration file"""
        config = configparser.ConfigParser()
        
        for section_name, section_data in config_data.items():
            if isinstance(section_data, dict):
                config[section_name] = section_data
            else:
                # Handle non-dict values
                if 'DEFAULT' not in config:
                    config['DEFAULT'] = {}
                config['DEFAULT'][section_name] = str(section_data)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
    
    def validate_project_config(self, config: AgentConfig) -> List[str]:
        """Validate project configuration and return list of issues"""
        issues = []
        
        # Check required fields
        if not config.project_name:
            issues.append("Project name is required")
        
        if not config.project_root:
            issues.append("Project root is required")
        elif not Path(config.project_root).exists():
            issues.append(f"Project root does not exist: {config.project_root}")
        
        # Check integration configurations
        if config.github_enabled:
            if not config.github_token:
                issues.append("GitHub token is required when GitHub integration is enabled")
            if not config.github_repo or not config.github_owner:
                issues.append("GitHub repository and owner are required when GitHub integration is enabled")
        
        if config.jira_enabled:
            if not config.jira_base_url:
                issues.append("JIRA base URL is required when JIRA integration is enabled")
            if not config.jira_email or not config.jira_api_token:
                issues.append("JIRA credentials are required when JIRA integration is enabled")
            if not config.jira_project_key:
                issues.append("JIRA project key is required when JIRA integration is enabled")
        
        if config.confluence_enabled:
            if not config.confluence_base_url:
                issues.append("Confluence base URL is required when Confluence integration is enabled")
            if not config.confluence_email or not config.confluence_api_token:
                issues.append("Confluence credentials are required when Confluence integration is enabled")
            if not config.confluence_space_key:
                issues.append("Confluence space key is required when Confluence integration is enabled")
        
        # Check threshold values
        if config.test_coverage_threshold < 0 or config.test_coverage_threshold > 100:
            issues.append("Test coverage threshold must be between 0 and 100")
        
        if config.code_quality_threshold < 0 or config.code_quality_threshold > 10:
            issues.append("Code quality threshold must be between 0 and 10")
        
        return issues
    
    def get_environment_config(self, environment: str = "development") -> Dict[str, Any]:
        """Get environment-specific configuration"""
        env_config_file = self.config_dir / f"env_{environment}.json"
        
        if env_config_file.exists():
            return self._load_json_config(env_config_file)
        
        # Return default environment configuration
        return {
            "environment": environment,
            "debug": environment == "development",
            "log_level": "DEBUG" if environment == "development" else "INFO"
        }
    
    def set_environment_config(self, environment: str, config_data: Dict[str, Any]):
        """Set environment-specific configuration"""
        env_config_file = self.config_dir / f"env_{environment}.json"
        self._save_json_config(env_config_file, config_data)
