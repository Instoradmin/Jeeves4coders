#!/usr/bin/env python3
"""
Engineering Automation Agent - Internationalization Messages
Centralized message definitions for internationalization support
"""

from typing import Dict, Any
from enum import Enum


class Language(Enum):
    """Supported languages"""
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    JA = "ja"
    ZH = "zh"


class Messages:
    """Centralized message definitions with internationalization support"""
    
    # Default language
    DEFAULT_LANGUAGE = Language.EN
    
    # Message definitions by language
    MESSAGES = {
        Language.EN: {
            # Common messages
            "success": "Success",
            "error": "Error",
            "warning": "Warning",
            "info": "Information",
            "loading": "Loading...",
            "completed": "Completed",
            "failed": "Failed",
            "pending": "Pending",
            "running": "Running",
            "stopped": "Stopped",
            
            # Configuration messages
            "config_validation_failed": "Configuration validation failed",
            "config_missing_field": "Missing required configuration field: {field}",
            "config_invalid_url": "Invalid URL format: {url}",
            "config_invalid_email": "Invalid email format: {email}",
            
            # API messages
            "api_connection_failed": "Failed to connect to API: {error}",
            "api_authentication_failed": "API authentication failed: {status_code}",
            "api_request_failed": "API request failed: {method} {url} - {error}",
            "api_response_parse_failed": "Failed to parse API response: {error}",
            
            # Module messages
            "module_starting": "Starting {module} integration tasks",
            "module_completed": "Completed {module} integration tasks",
            "module_disabled": "{module} integration disabled in configuration",
            "module_validation_passed": "{module} configuration validation passed",
            "module_validation_failed": "{module} configuration validation failed",
            
            # Confluence messages
            "confluence_page_created": "Confluence page created: {title}",
            "confluence_page_updated": "Confluence page updated: {title}",
            "confluence_page_creation_failed": "Failed to create Confluence page: {error}",
            "confluence_page_update_failed": "Failed to update Confluence page: {error}",
            "confluence_space_info_retrieved": "Retrieved Confluence space information",
            "confluence_space_info_failed": "Failed to retrieve Confluence space information",
            "confluence_report_published": "Published {report_type} report: {url}",
            "confluence_search_completed": "Search completed, found {count} pages",
            
            # GitHub messages
            "github_repo_info_retrieved": "Retrieved GitHub repository information",
            "github_repo_info_failed": "Failed to retrieve GitHub repository information",
            "github_commits_retrieved": "Retrieved {count} recent commits",
            "github_commits_failed": "Failed to retrieve recent commits",
            "github_pr_created": "Pull request created: {title}",
            "github_pr_creation_failed": "Failed to create pull request: {error}",
            "github_issue_created": "GitHub issue created: {title}",
            "github_issue_creation_failed": "Failed to create GitHub issue: {error}",
            
            # JIRA messages
            "jira_project_info_retrieved": "Retrieved JIRA project information",
            "jira_project_info_failed": "Failed to retrieve JIRA project information",
            "jira_issues_retrieved": "Retrieved {count} JIRA issues",
            "jira_issues_failed": "Failed to retrieve JIRA issues",
            "jira_issue_created": "JIRA issue created: {key}",
            "jira_issue_creation_failed": "Failed to create JIRA issue: {error}",
            "jira_issue_updated": "JIRA issue updated: {key}",
            "jira_issue_update_failed": "Failed to update JIRA issue: {error}",
            
            # Test messages
            "test_suite_starting": "Starting comprehensive test suite",
            "test_suite_completed": "Test suite completed successfully",
            "test_suite_failed": "Test suite execution failed",
            "test_category_starting": "Starting {category} tests",
            "test_category_completed": "Completed {category} tests: {passed}/{total} passed",
            "test_execution_time": "Test execution time: {time:.2f}s",
            "test_coverage_report": "Test coverage: {coverage:.1f}%",
            
            # Code review messages
            "code_review_starting": "Starting code review and quality analysis",
            "code_review_completed": "Code review completed",
            "code_review_issues_found": "Found {count} code quality issues",
            "code_review_duplicates_found": "Found {count} duplicate code blocks",
            "code_review_metrics_calculated": "Code metrics calculated",
            "deduplication_starting": "Starting code deduplication",
            "deduplication_completed": "Code deduplication completed",
            
            # Report messages
            "report_generating": "Generating {report_type} report",
            "report_generated": "Report generated successfully",
            "report_generation_failed": "Failed to generate report: {error}",
            "report_publishing": "Publishing report to {platform}",
            "report_published": "Report published successfully",
            "report_publishing_failed": "Failed to publish report: {error}",
            
            # File operation messages
            "file_read_success": "Successfully read file: {file_path}",
            "file_read_failed": "Failed to read file: {file_path}",
            "file_write_success": "Successfully wrote file: {file_path}",
            "file_write_failed": "Failed to write file: {file_path}",
            "directory_created": "Created directory: {directory}",
            "directory_creation_failed": "Failed to create directory: {directory}",
            
            # Validation messages
            "validation_passed": "Validation passed",
            "validation_failed": "Validation failed",
            "required_field_missing": "Required field missing: {field}",
            "invalid_format": "Invalid format for {field}",
            
            # Attribution messages
            "co_authored_by": "Co-authored by",
            "augment_code": "Augment Code",
            
            # Status messages
            "status_healthy": "Healthy",
            "status_unhealthy": "Unhealthy",
            "status_unknown": "Unknown",
            "status_active": "Active",
            "status_inactive": "Inactive",
            
            # Time and date messages
            "execution_time": "Execution Time",
            "created_at": "Created At",
            "updated_at": "Updated At",
            "timestamp": "Timestamp",
            
            # Report section headers
            "summary": "Summary",
            "details": "Details",
            "metrics": "Metrics",
            "results": "Results",
            "issues": "Issues",
            "recommendations": "Recommendations",
            "conclusion": "Conclusion",
            
            # Table headers
            "name": "Name",
            "type": "Type",
            "status": "Status",
            "description": "Description",
            "value": "Value",
            "count": "Count",
            "percentage": "Percentage",
            "category": "Category",
            "priority": "Priority",
            "assignee": "Assignee",
            "reporter": "Reporter",
            "author": "Author",
            "url": "URL",
            "version": "Version",
        },
        
        # Spanish translations (partial example)
        Language.ES: {
            "success": "Éxito",
            "error": "Error",
            "warning": "Advertencia",
            "info": "Información",
            "loading": "Cargando...",
            "completed": "Completado",
            "failed": "Fallido",
            "pending": "Pendiente",
            "running": "Ejecutándose",
            "stopped": "Detenido",
            "summary": "Resumen",
            "details": "Detalles",
            "metrics": "Métricas",
            "results": "Resultados",
            "issues": "Problemas",
            "recommendations": "Recomendaciones",
            "conclusion": "Conclusión",
        },
        
        # French translations (partial example)
        Language.FR: {
            "success": "Succès",
            "error": "Erreur",
            "warning": "Avertissement",
            "info": "Information",
            "loading": "Chargement...",
            "completed": "Terminé",
            "failed": "Échoué",
            "pending": "En attente",
            "running": "En cours",
            "stopped": "Arrêté",
            "summary": "Résumé",
            "details": "Détails",
            "metrics": "Métriques",
            "results": "Résultats",
            "issues": "Problèmes",
            "recommendations": "Recommandations",
            "conclusion": "Conclusion",
        }
    }
    
    @classmethod
    def get(cls, key: str, language: Language = None, **kwargs) -> str:
        """Get localized message"""
        if language is None:
            language = cls.DEFAULT_LANGUAGE
        
        # Get message from specified language, fallback to English
        messages = cls.MESSAGES.get(language, cls.MESSAGES[Language.EN])
        message = messages.get(key, cls.MESSAGES[Language.EN].get(key, key))
        
        # Format message with provided kwargs
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message
    
    @classmethod
    def set_default_language(cls, language: Language):
        """Set default language"""
        cls.DEFAULT_LANGUAGE = language
    
    @classmethod
    def get_available_languages(cls) -> list:
        """Get list of available languages"""
        return list(cls.MESSAGES.keys())


# Convenience function for getting messages
def get_message(key: str, language: Language = None, **kwargs) -> str:
    """Convenience function to get localized message"""
    return Messages.get(key, language, **kwargs)
