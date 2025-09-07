#!/usr/bin/env python3
"""
Setup script for Vibecoding Configuration Wizard
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Filter out development dependencies
runtime_requirements = []
for req in requirements:
    if not any(dev_pkg in req for dev_pkg in ['pytest', 'mypy', 'black', 'flake8', 'isort', 'sphinx']):
        runtime_requirements.append(req)

setup(
    name="vibecoding-wizard",
    version="1.0.0",
    author="Vibecoding Team",
    author_email="dev@vibecoding.com",
    description="Intelligent MCP Configuration Wizard for LLM Clients",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vibecoding/proyecto-semilla",
    project_urls={
        "Bug Tracker": "https://github.com/vibecoding/proyecto-semilla/issues",
        "Documentation": "https://github.com/vibecoding/proyecto-semilla/blob/main/tools/vibecoding-wizard/README.md",
        "Source Code": "https://github.com/vibecoding/proyecto-semilla/tree/main/tools/vibecoding-wizard",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=runtime_requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0", 
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "mypy>=1.0.0,<2.0.0",
            "black>=22.0.0,<23.0.0",
            "flake8>=5.0.0,<6.0.0",
            "isort>=5.0.0,<6.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0,<6.0.0",
            "sphinx-rtd-theme>=1.0.0,<2.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "vibecoding-wizard=main:main",
            "vibe-wizard=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    zip_safe=False,
    keywords=[
        "mcp", "model-context-protocol", "llm", "ai", "configuration", 
        "wizard", "claude", "anthropic", "automation", "devops"
    ],
    license="MIT",
)