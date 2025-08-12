#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-admin-log-viewer",
    version="2.0.0",
    author="Amirhossein Mahmoudi",
    author_email="am.mahmoudi@outlook.com",
    description="A powerful Django app for viewing and monitoring log files in the admin panel with multi-line support, real-time updates, and configurable formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ammahmoudi/django-admin-log-viewer",
    project_urls={
        "Bug Reports": "https://github.com/ammahmoudi/django-admin-log-viewer/issues",
        "Source": "https://github.com/ammahmoudi/django-admin-log-viewer",
        "Documentation": "https://github.com/ammahmoudi/django-admin-log-viewer#readme",
    },
    packages=find_packages(),
    keywords=[
        "django", "admin", "log", "viewer", "monitoring", "debugging", 
        "real-time", "multi-line", "stack-trace", "celery", "nginx", 
        "apache", "log-rotation", "log-parsing", "log-analysis"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-django>=4.0",
            "black>=21.0",
            "flake8>=3.8",
            "isort>=5.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    package_data={
        "log_viewer": [
            "static/log_viewer/css/*.css",
            "static/log_viewer/js/*.js", 
            "templates/log_viewer/*.html",
            "templatetags/*.py",
        ],
    },
)
