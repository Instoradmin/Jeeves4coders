#!/usr/bin/env python3
"""
Setup script for Jeeves4coders - Engineering Automation Agent
AI automation tool for developers
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), '__init__.py')
    with open(init_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '1.0.0'

# Read long description from README
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "Engineering Automation Agent for comprehensive project automation"

setup(
    name="jeeves4coders",
    version=get_version(),
    author="Instor Engineering Team",
    author_email="engineering@instor.com",
    description="AI automation tool for developers - Comprehensive engineering and housekeeping automation",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Instoradmin/Jeeves4coders",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "PyYAML>=5.4.0",
        "configparser>=5.0.0",
        "dataclasses>=0.6;python_version<'3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=3.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jeeves4coders=engineering_automation_agent.cli:main",
            "engineering-agent=engineering_automation_agent.cli:main",  # Backward compatibility
        ],
    },
    include_package_data=True,
    package_data={
        "engineering_automation_agent": [
            "templates/*.json",
            "templates/*.yaml",
            "config/*.json",
        ],
    },
    zip_safe=False,
)
