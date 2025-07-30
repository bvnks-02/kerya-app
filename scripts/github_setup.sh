#!/bin/bash

# Kerya App GitHub Repository Setup Script
# This script helps initialize and set up the GitHub repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if git is installed
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install git first."
        exit 1
    fi
    print_status "Git is installed"
}

# Check if GitHub CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_warning "GitHub CLI is not installed. You'll need to create the repository manually."
        return 1
    fi
    print_status "GitHub CLI is installed"
    return 0
}

# Initialize git repository
init_git_repo() {
    print_header "Initializing Git Repository"
    
    if [ -d ".git" ]; then
        print_warning "Git repository already exists"
        return
    fi
    
    git init
    print_status "Git repository initialized"
}

# Create .gitignore file
create_gitignore() {
    print_header "Creating .gitignore"
    
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/

# VS Code
.vscode/

# Docker
.dockerignore

# Kubernetes
*.kubeconfig

# Logs
logs/
*.log

# Temporary files
*.tmp
*.temp

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Backup files
*.bak
*.backup

# Database files
*.db
*.sqlite

# Redis dump
dump.rdb

# Elasticsearch data
data/

# RabbitMQ data
rabbitmq_data/

# AWS credentials
.aws/

# SSL certificates
*.pem
*.key
*.crt

# Terraform
*.tfstate
*.tfstate.*
.terraform/

# Ansible
*.retry

# Local development
local/
dev/
EOF

    print_status ".gitignore created"
}

# Create GitHub repository
create_github_repo() {
    print_header "Creating GitHub Repository"
    
    if check_gh_cli; then
        read -p "Enter repository name (default: kerya-app): " repo_name
        repo_name=${repo_name:-kerya-app}
        
        read -p "Enter repository description: " repo_description
        repo_description=${repo_description:-"Kerya App - Property Rental Platform Backend"}
        
        read -p "Make repository private? (y/N): " is_private
        is_private=${is_private:-N}
        
        if [[ $is_private =~ ^[Yy]$ ]]; then
            gh repo create "$repo_name" --description "$repo_description" --private
        else
            gh repo create "$repo_name" --description "$repo_description" --public
        fi
        
        print_status "GitHub repository created: $repo_name"
    else
        print_warning "Please create the GitHub repository manually and then run:"
        print_warning "git remote add origin https://github.com/YOUR_USERNAME/kerya-app.git"
    fi
}

# Add files to git
add_files_to_git() {
    print_header "Adding Files to Git"
    
    # Add all files
    git add .
    
    # Create initial commit
    git commit -m "Initial commit: Kerya App Backend

- Microservices architecture with FastAPI
- User authentication and authorization
- Property management system
- Booking and reservation system
- Notification service
- Review and rating system
- Post management for client requests
- API Gateway with rate limiting
- Docker and Kubernetes deployment
- Comprehensive monitoring and logging
- Security best practices implementation"
    
    print_status "Initial commit created"
}

# Set up branch protection (if GitHub CLI is available)
setup_branch_protection() {
    if check_gh_cli; then
        print_header "Setting up Branch Protection"
        
        # Get repository name
        repo_name=$(basename $(git remote get-url origin 2>/dev/null || echo "kerya-app"))
        
        # Set up branch protection rules
        gh api repos/:owner/:repo/branches/main/protection \
            --method PUT \
            --field required_status_checks='{"strict":true,"contexts":["ci/tests","ci/security-scan"]}' \
            --field enforce_admins=true \
            --field required_pull_request_reviews='{"required_approving_review_count":2,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
            --field restrictions=null
        
        print_status "Branch protection rules configured"
    else
        print_warning "GitHub CLI not available. Please set up branch protection manually."
    fi
}

# Create GitHub Actions workflow
create_github_actions() {
    print_header "Creating GitHub Actions Workflow"
    
    mkdir -p .github/workflows
    
    cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: kerya_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy bandit
    
    - name: Run linting
      run: |
        black --check .
        isort --check-only .
        flake8 .
        mypy .
    
    - name: Run security scan
      run: |
        bandit -r . -f json -o bandit-report.json || true
    
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'kerya/user-service:latest'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push Docker images
      run: |
        docker build -t kerya/user-service:latest ./user_service/
        docker build -t kerya/api-gateway:latest ./api_gateway/
        docker push kerya/user-service:latest
        docker push kerya/api-gateway:latest

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add your staging deployment commands here

  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # Add your production deployment commands here
EOF

    print_status "GitHub Actions workflow created"
}

# Create issue templates
create_issue_templates() {
    print_header "Creating Issue Templates"
    
    mkdir -p .github/ISSUE_TEMPLATE
    
    # Bug report template
    cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: ['bug']
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Ubuntu 20.04]
 - Python Version: [e.g. 3.11]
 - Docker Version: [e.g. 20.10]
 - Browser: [e.g. chrome, safari]

**Additional context**
Add any other context about the problem here.
EOF

    # Feature request template
    cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: ['enhancement']
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
EOF

    print_status "Issue templates created"
}

# Create pull request template
create_pr_template() {
    print_header "Creating Pull Request Template"
    
    cat > .github/pull_request_template.md << 'EOF'
## Description
Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context.

Fixes # (issue)

## Type of change
Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

## How Has This Been Tested?
Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration.

- [ ] Test A
- [ ] Test B

## Checklist:
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules

## Security Considerations
- [ ] I have considered the security implications of this change
- [ ] I have validated all inputs and outputs
- [ ] I have ensured proper authentication and authorization
- [ ] I have followed secure coding practices
EOF

    print_status "Pull request template created"
}

# Create CODE_OF_CONDUCT.md
create_code_of_conduct() {
    print_header "Creating Code of Conduct"
    
    cat > CODE_OF_CONDUCT.md << 'EOF'
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the
  overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or
  advances of any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email
  address, without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
[INSERT CONTACT METHOD].
All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series
of actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interactions in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or
permanent ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior,  harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.0, available at
https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.

Community Impact Guidelines were inspired by [Mozilla's code of conduct
enforcement ladder][Mozilla CoC].

For answers to common questions about this code of conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.

[homepage]: https://www.contributor-covenant.org
[Mozilla CoC]: https://github.com/mozilla/diversity
[v2.0]: https://www.contributor-covenant.org/version/2/0/code_of_conduct.html
EOF

    print_status "Code of Conduct created"
}

# Create CONTRIBUTING.md
create_contributing() {
    print_header "Creating Contributing Guidelines"
    
    cat > CONTRIBUTING.md << 'EOF'
# Contributing to Kerya App

Thank you for your interest in contributing to Kerya App! This document provides guidelines and information for contributors.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/YOUR_USERNAME/kerya-app.git`
3. **Create a feature branch**: `git checkout -b feature/amazing-feature`
4. **Set up development environment**: Follow the setup instructions in `docs/DEVELOPMENT.md`

## Development Workflow

### 1. Code Style

We follow PEP 8 with some modifications:
- Line length: 88 characters (Black default)
- Use type hints for all functions
- Follow Google style docstrings

### 2. Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### 3. Testing

Write tests for all new functionality:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py
```

### 4. Code Quality

Before submitting a PR, ensure:
- [ ] Code passes all linting checks (`black`, `isort`, `flake8`, `mypy`)
- [ ] All tests pass
- [ ] Code coverage is maintained or improved
- [ ] Documentation is updated

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Submit pull request** with clear description

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate

## Commit Message Format

Use conventional commits format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

## Security

- Follow secure coding practices
- Validate all inputs
- Use parameterized queries
- Implement proper authentication/authorization
- Report security issues privately to security@kerya.com

## Getting Help

- Check existing issues and discussions
- Join our community chat
- Contact maintainers for guidance

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
EOF

    print_status "Contributing guidelines created"
}

# Create CHANGELOG.md
create_changelog() {
    print_header "Creating Changelog"
    
    cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup
- Microservices architecture
- User authentication and authorization
- Property management system
- Booking and reservation system
- Notification service
- Review and rating system
- Post management for client requests
- API Gateway with rate limiting
- Docker and Kubernetes deployment
- Comprehensive monitoring and logging
- Security best practices implementation

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.0.0] - 2024-01-15

### Added
- Initial release of Kerya App backend
- Complete microservices architecture
- Full API documentation
- Deployment guides
- Security documentation
- Development guidelines

[Unreleased]: https://github.com/your-org/kerya-app/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/kerya-app/releases/tag/v1.0.0
EOF

    print_status "Changelog created"
}

# Main execution
main() {
    print_header "Kerya App GitHub Repository Setup"
    
    # Check prerequisites
    check_git
    
    # Initialize repository
    init_git_repo
    create_gitignore
    
    # Create GitHub repository
    create_github_repo
    
    # Add files to git
    add_files_to_git
    
    # Set up GitHub features
    create_github_actions
    create_issue_templates
    create_pr_template
    create_code_of_conduct
    create_contributing
    create_changelog
    
    # Set up branch protection
    setup_branch_protection
    
    print_header "Setup Complete!"
    print_status "Your Kerya App repository has been set up successfully!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Push your code: git push -u origin main"
    print_status "2. Set up branch protection rules in GitHub"
    print_status "3. Configure GitHub Actions secrets"
    print_status "4. Set up monitoring and alerting"
    print_status "5. Review and update documentation"
    print_status ""
    print_status "Happy coding! 🚀"
}

# Run main function
main "$@" 