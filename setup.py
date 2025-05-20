#!/usr/bin/env python3
"""安装脚本."""

from setuptools import setup, find_packages

setup(
    name="jira_mcp",
    version="0.1.0",
    description="JIRA MCP for querying JIRA details and lists",
    author="Your Name",
    author_email="your-email@example.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi",
        "uvicorn",
        "jira",
        "pydantic",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "jira-mcp=src.server:main",
            "jira-extract=src.scripts.extract_attachment:main",
            "jira-attachments=src.scripts.download_all_attachments:main",
        ],
    },
    python_requires=">=3.10,<3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
) 