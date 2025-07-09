#!/usr/bin/env python3
"""
Enhanced Engineering Automation Agent - Internationalization Messages
Comprehensive message definitions for internationalization support
Includes testing, exception handling, JIRA integration, and GitHub messages
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from enum import Enum
from pathlib import Path


class Language(Enum):
    """Supported languages"""
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    JA = "ja"
    ZH = "zh"
    IT = "it"
    PT = "pt"
    RU = "ru"
    KO = "ko"

class MessageKeys(Enum):
    """Message key constants for type safety"""
    # Common messages
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    LOADING = "loading"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"

    # Configuration messages
    CONFIG_VALIDATION_FAILED = "config_validation_failed"
    CONFIG_MISSING_FIELD = "config_missing_field"
    CONFIG_INVALID_URL = "config_invalid_url"
    CONFIG_INVALID_EMAIL = "config_invalid_email"
    CONFIG_LOADED_SUCCESSFULLY = "config_loaded_successfully"

    # API messages
    API_CONNECTION_FAILED = "api_connection_failed"
    API_AUTHENTICATION_FAILED = "api_authentication_failed"
    API_REQUEST_SUCCESS = "api_request_success"
    API_RATE_LIMIT_EXCEEDED = "api_rate_limit_exceeded"

    # Testing messages
    STARTING_TEST_SUITE = "starting_test_suite"
    TEST_SUITE_COMPLETED = "test_suite_completed"
    TEST_SUITE_FAILED = "test_suite_failed"
    RUNNING_TEST_TYPE = "running_test_type"
    TEST_TYPE_FAILED = "test_type_failed"
    RUNNING_UNIT_TESTS = "running_unit_tests"
    RUNNING_FUNCTIONAL_TESTS = "running_functional_tests"
    RUNNING_INTEGRATION_TESTS = "running_integration_tests"
    RUNNING_REGRESSION_TESTS = "running_regression_tests"
    RUNNING_PERFORMANCE_TESTS = "running_performance_tests"
    RUNNING_SECURITY_TESTS = "running_security_tests"
    RUNNING_E2E_TESTS = "running_e2e_tests"
    TEST_COVERAGE_REPORT = "test_coverage_report"
    TEST_ARTIFACTS_GENERATED = "test_artifacts_generated"

    # Exception handling messages
    EXCEPTION_OCCURRED = "exception_occurred"
    EXCEPTION_REPORT_GENERATED = "exception_report_generated"
    COLLECTING_EXCEPTIONS = "collecting_exceptions"
    EXCEPTION_SUMMARY = "exception_summary"

    # JIRA integration messages
    JIRA_CONNECTION_SUCCESS = "jira_connection_success"
    JIRA_CONNECTION_FAILED = "jira_connection_failed"
    JIRA_TICKET_CREATED = "jira_ticket_created"
    JIRA_TICKET_UPDATED = "jira_ticket_updated"
    JIRA_TICKET_CREATION_FAILED = "jira_ticket_creation_failed"
    JIRA_BUG_TICKET_CREATED = "jira_bug_ticket_created"
    JIRA_PROJECT_NOT_FOUND = "jira_project_not_found"

    # GitHub integration messages
    GITHUB_CONNECTION_SUCCESS = "github_connection_success"
    GITHUB_CONNECTION_FAILED = "github_connection_failed"
    GITHUB_COMMIT_CREATED = "github_commit_created"
    GITHUB_COMMIT_FAILED = "github_commit_failed"
    GITHUB_ARTIFACTS_STORED = "github_artifacts_stored"
    GITHUB_REPOSITORY_NOT_FOUND = "github_repository_not_found"

    # Build process messages
    BUILD_STARTED = "build_started"
    BUILD_COMPLETED = "build_completed"
    BUILD_FAILED = "build_failed"
    BUILD_ARTIFACTS_GENERATED = "build_artifacts_generated"
    PRE_COMMIT_CHECKS = "pre_commit_checks"
    POST_BUILD_ACTIONS = "post_build_actions"

    # Code review messages
    CODE_REVIEW_STARTED = "code_review_started"
    CODE_REVIEW_COMPLETED = "code_review_completed"
    CODE_QUALITY_ISSUES_FOUND = "code_quality_issues_found"
    CODE_DOCUMENTATION_MISSING = "code_documentation_missing"


class Messages:
    """Enhanced centralized message definitions with comprehensive internationalization support"""

    # Default language
    DEFAULT_LANGUAGE = Language.EN

    # Current language (can be changed at runtime)
    _current_language = Language.EN

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
            "config_loaded_successfully": "Configuration loaded successfully from {file}",

            # API messages
            "api_connection_failed": "Failed to connect to API: {error}",
            "api_authentication_failed": "API authentication failed: {status_code}",
            "api_request_success": "API request successful: {endpoint}",
            "api_rate_limit_exceeded": "API rate limit exceeded. Please try again later",

            # Testing messages
            "starting_test_suite": "🧪 Starting comprehensive test suite execution",
            "test_suite_completed": "✅ Test suite completed: {passed}/{total} tests passed ({rate:.1f}%)",
            "test_suite_failed": "❌ Test suite execution failed: {error}",
            "running_test_type": "🔄 Running {test_type} tests...",
            "test_type_failed": "❌ Failed to run {test_type} tests: {error}",
            "running_unit_tests": "🧪 Running unit tests...",
            "running_functional_tests": "⚙️ Running functional tests...",
            "running_integration_tests": "🔗 Running integration tests...",
            "running_regression_tests": "🔄 Running regression tests...",
            "running_performance_tests": "⚡ Running performance tests...",
            "running_security_tests": "🔒 Running security tests...",
            "running_e2e_tests": "🎯 Running end-to-end tests...",
            "test_coverage_report": "📊 Test coverage: {coverage:.1f}% ({covered}/{total} lines)",
            "test_artifacts_generated": "📁 Test artifacts generated: {path}",

            # Exception handling messages
            "exception_occurred": "⚠️ Exception occurred in {module}: {error}",
            "exception_report_generated": "📋 Exception report generated: {count} exceptions found",
            "collecting_exceptions": "🔍 Collecting exceptions for final report...",
            "exception_summary": "📊 Exception Summary: {count} exceptions in {modules} modules",

            # JIRA integration messages
            "jira_connection_success": "✅ Connected to JIRA successfully",
            "jira_connection_failed": "❌ Failed to connect to JIRA: {error}",
            "jira_ticket_created": "🎫 JIRA ticket created: {ticket_id} - {summary}",
            "jira_ticket_updated": "📝 JIRA ticket updated: {ticket_id}",
            "jira_ticket_creation_failed": "❌ Failed to create JIRA ticket: {error}",
            "jira_bug_ticket_created": "🐛 Bug ticket created: {ticket_id} for {component}",
            "jira_project_not_found": "❌ JIRA project not found: {project}",

            # GitHub integration messages
            "github_connection_success": "✅ Connected to GitHub successfully",
            "github_connection_failed": "❌ Failed to connect to GitHub: {error}",
            "github_commit_created": "📝 GitHub commit created: {commit_hash}",
            "github_commit_failed": "❌ Failed to create GitHub commit: {error}",
            "github_artifacts_stored": "📦 Test artifacts stored in GitHub: {path}",
            "github_repository_not_found": "❌ GitHub repository not found: {repo}",

            # Build process messages
            "build_started": "🚀 Build process started for {project}",
            "build_completed": "✅ Build completed successfully in {time:.2f}s",
            "build_failed": "❌ Build failed: {error}",
            "build_artifacts_generated": "📦 Build artifacts generated: {path}",
            "pre_commit_checks": "🔍 Running pre-commit checks...",
            "post_build_actions": "🔄 Executing post-build actions...",

            # Code review messages
            "code_review_started": "🔍 Starting code review analysis...",
            "code_review_completed": "✅ Code review completed: {issues} issues found",
            "code_quality_issues_found": "⚠️ Code quality issues found: {count} in {files} files",
            "code_documentation_missing": "📝 Missing documentation in {files} files",
        },

        Language.ES: {
            # Common messages
            "success": "Éxito",
            "error": "Error",
            "warning": "Advertencia",
            "info": "Información",
            "loading": "Cargando...",
            "completed": "Completado",
            "failed": "Falló",
            "pending": "Pendiente",
            "running": "Ejecutando",
            "stopped": "Detenido",

            # Configuration messages
            "config_validation_failed": "Falló la validación de configuración",
            "config_missing_field": "Campo de configuración requerido faltante: {field}",
            "config_invalid_url": "Formato de URL inválido: {url}",
            "config_invalid_email": "Formato de email inválido: {email}",
            "config_loaded_successfully": "Configuración cargada exitosamente desde {file}",

            # Testing messages
            "starting_test_suite": "🧪 Iniciando ejecución de suite de pruebas integral",
            "test_suite_completed": "✅ Suite de pruebas completada: {passed}/{total} pruebas pasaron ({rate:.1f}%)",
            "test_suite_failed": "❌ Falló la ejecución de la suite de pruebas: {error}",
            "running_test_type": "🔄 Ejecutando pruebas de {test_type}...",
            "test_type_failed": "❌ Falló al ejecutar pruebas de {test_type}: {error}",
            "running_unit_tests": "🧪 Ejecutando pruebas unitarias...",
            "running_functional_tests": "⚙️ Ejecutando pruebas funcionales...",
            "running_integration_tests": "🔗 Ejecutando pruebas de integración...",
            "running_regression_tests": "🔄 Ejecutando pruebas de regresión...",
            "running_performance_tests": "⚡ Ejecutando pruebas de rendimiento...",
            "running_security_tests": "🔒 Ejecutando pruebas de seguridad...",
            "running_e2e_tests": "🎯 Ejecutando pruebas de extremo a extremo...",

            # JIRA integration messages
            "jira_connection_success": "✅ Conectado a JIRA exitosamente",
            "jira_connection_failed": "❌ Falló la conexión a JIRA: {error}",
            "jira_ticket_created": "🎫 Ticket de JIRA creado: {ticket_id} - {summary}",
            "jira_ticket_updated": "📝 Ticket de JIRA actualizado: {ticket_id}",
            "jira_bug_ticket_created": "🐛 Ticket de bug creado: {ticket_id} para {component}",

            # GitHub integration messages
            "github_connection_success": "✅ Conectado a GitHub exitosamente",
            "github_connection_failed": "❌ Falló la conexión a GitHub: {error}",
            "github_commit_created": "📝 Commit de GitHub creado: {commit_hash}",
            "github_artifacts_stored": "📦 Artefactos de prueba almacenados en GitHub: {path}",

            # Build process messages
            "build_started": "🚀 Proceso de construcción iniciado para {project}",
            "build_completed": "✅ Construcción completada exitosamente en {time:.2f}s",
            "build_failed": "❌ Falló la construcción: {error}",
            "code_review_started": "🔍 Iniciando análisis de revisión de código...",
            "code_review_completed": "✅ Revisión de código completada: {issues} problemas encontrados",
        },

        Language.FR: {
            # Common messages
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

            # Testing messages
            "starting_test_suite": "🧪 Démarrage de l'exécution de la suite de tests complète",
            "test_suite_completed": "✅ Suite de tests terminée: {passed}/{total} tests réussis ({rate:.1f}%)",
            "running_unit_tests": "🧪 Exécution des tests unitaires...",
            "running_integration_tests": "🔗 Exécution des tests d'intégration...",
            "running_performance_tests": "⚡ Exécution des tests de performance...",

            # JIRA integration messages
            "jira_connection_success": "✅ Connecté à JIRA avec succès",
            "jira_ticket_created": "🎫 Ticket JIRA créé: {ticket_id} - {summary}",
            "jira_bug_ticket_created": "🐛 Ticket de bug créé: {ticket_id} pour {component}",

            # GitHub integration messages
            "github_connection_success": "✅ Connecté à GitHub avec succès",
            "github_commit_created": "📝 Commit GitHub créé: {commit_hash}",

            # Build process messages
            "build_started": "🚀 Processus de construction démarré pour {project}",
            "build_completed": "✅ Construction terminée avec succès en {time:.2f}s",
            "code_review_started": "🔍 Démarrage de l'analyse de révision de code...",
        },

        Language.DE: {
            # Common messages
            "success": "Erfolg",
            "error": "Fehler",
            "warning": "Warnung",
            "info": "Information",
            "loading": "Laden...",
            "completed": "Abgeschlossen",
            "failed": "Fehlgeschlagen",
            "pending": "Ausstehend",
            "running": "Läuft",
            "stopped": "Gestoppt",

            # Testing messages
            "starting_test_suite": "🧪 Starte umfassende Testsuite-Ausführung",
            "test_suite_completed": "✅ Testsuite abgeschlossen: {passed}/{total} Tests bestanden ({rate:.1f}%)",
            "running_unit_tests": "🧪 Führe Unit-Tests aus...",
            "running_integration_tests": "🔗 Führe Integrationstests aus...",

            # JIRA integration messages
            "jira_connection_success": "✅ Erfolgreich mit JIRA verbunden",
            "jira_ticket_created": "🎫 JIRA-Ticket erstellt: {ticket_id} - {summary}",

            # Build process messages
            "build_started": "🚀 Build-Prozess gestartet für {project}",
            "build_completed": "✅ Build erfolgreich abgeschlossen in {time:.2f}s",
        }
    }

    @classmethod
    def set_language(cls, language: Language):
        """Set the current language for messages"""
        cls._current_language = language
        logging.info(f"Language set to: {language.value}")

    @classmethod
    def get_current_language(cls) -> Language:
        """Get the current language"""
        return cls._current_language

    @classmethod
    def load_from_properties_file(cls, file_path: str, language: Language):
        """Load messages from properties file"""
        try:
            properties = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        properties[key.strip()] = value.strip()

            if language not in cls.MESSAGES:
                cls.MESSAGES[language] = {}

            cls.MESSAGES[language].update(properties)
            logging.info(f"Loaded {len(properties)} messages from {file_path} for language {language.value}")

        except Exception as e:
            logging.error(f"Failed to load properties file {file_path}: {str(e)}")

    @classmethod
    def save_to_properties_file(cls, file_path: str, language: Language):
        """Save messages to properties file"""
        try:
            messages = cls.MESSAGES.get(language, {})

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Messages for language: {language.value}\n")
                f.write(f"# Generated on: {datetime.now().isoformat()}\n\n")

                for key, value in sorted(messages.items()):
                    f.write(f"{key}={value}\n")

            logging.info(f"Saved {len(messages)} messages to {file_path} for language {language.value}")

        except Exception as e:
            logging.error(f"Failed to save properties file {file_path}: {str(e)}")

    @classmethod
    def get_message(cls, key: str, language: Optional[Language] = None, **kwargs) -> str:
        """Get localized message with parameter substitution"""
        if language is None:
            language = cls._current_language

        # Get message from specified language
        messages = cls.MESSAGES.get(language, {})
        message = messages.get(key)

        # Fallback to English if message not found
        if message is None and language != cls.DEFAULT_LANGUAGE:
            messages = cls.MESSAGES.get(cls.DEFAULT_LANGUAGE, {})
            message = messages.get(key)

        # Fallback to key if still not found
        if message is None:
            message = key
            logging.warning(f"Message not found for key: {key} in language: {language.value}")

        # Substitute parameters
        try:
            return message.format(**kwargs)
        except KeyError as e:
            logging.warning(f"Missing parameter {e} for message key: {key}")
            return message
        except Exception as e:
            logging.error(f"Error formatting message {key}: {str(e)}")
            return message

# Global message management functions
def get_message(key: MessageKeys, language: Optional[Language] = None, **kwargs) -> str:
    """Get localized message using MessageKeys enum"""
    return Messages.get_message(key.value, language, **kwargs)

def set_language(language: Language):
    """Set the global language for messages"""
    Messages.set_language(language)

def load_messages_from_directory(directory: str):
    """Load all message files from a directory"""
    try:
        directory_path = Path(directory)
        if not directory_path.exists():
            logging.warning(f"Messages directory not found: {directory}")
            return

        for file_path in directory_path.glob("*.properties"):
            # Extract language from filename (e.g., messages_es.properties -> es)
            filename = file_path.stem
            if '_' in filename:
                lang_code = filename.split('_')[-1]
                try:
                    language = Language(lang_code)
                    Messages.load_from_properties_file(str(file_path), language)
                except ValueError:
                    logging.warning(f"Unknown language code in filename: {lang_code}")
            else:
                # Default to English for files without language suffix
                Messages.load_from_properties_file(str(file_path), Language.EN)

    except Exception as e:
        logging.error(f"Failed to load messages from directory {directory}: {str(e)}")

def create_properties_files(output_directory: str):
    """Create properties files for all supported languages"""
    try:
        output_path = Path(output_directory)
        output_path.mkdir(exist_ok=True)

        for language in Language:
            filename = f"messages_{language.value}.properties"
            file_path = output_path / filename
            Messages.save_to_properties_file(str(file_path), language)

        logging.info(f"Created properties files in {output_directory}")

    except Exception as e:
        logging.error(f"Failed to create properties files: {str(e)}")

# Initialize message system
def initialize_message_system(config_dir: str = None, language: Language = None):
    """Initialize the message system with optional configuration"""
    try:
        # Set language if provided
        if language:
            set_language(language)

        # Load messages from configuration directory if provided
        if config_dir:
            messages_dir = Path(config_dir) / "messages"
            if messages_dir.exists():
                load_messages_from_directory(str(messages_dir))

        logging.info("Message system initialized successfully")

    except Exception as e:
        logging.error(f"Failed to initialize message system: {str(e)}")

# Legacy support - maintain backward compatibility
def get_localized_message(key: str, **kwargs) -> str:
    """Legacy function for backward compatibility"""
    return Messages.get_message(key, **kwargs)
