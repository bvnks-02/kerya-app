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

Examples:
```
feat(auth): add OAuth2 support for Google login
fix(booking): resolve timezone issue in booking dates
docs(api): update authentication endpoint documentation
```

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

## Development Standards

### Code Quality Checklist

- [ ] **Input Validation**: All inputs are validated using Pydantic models
- [ ] **Error Handling**: Comprehensive error handling with proper HTTP status codes
- [ ] **Logging**: Appropriate logging levels and structured logging
- [ ] **Security**: No hardcoded secrets, proper authentication/authorization
- [ ] **Performance**: Efficient database queries, proper caching
- [ ] **Testing**: Unit tests for business logic, integration tests for APIs
- [ ] **Documentation**: Updated docstrings and API documentation

### Security Guidelines

1. **Input Validation**
   - Always validate and sanitize user inputs
   - Use Pydantic models for request validation
   - Implement proper SQL injection prevention

2. **Authentication & Authorization**
   - Use JWT tokens for authentication
   - Implement role-based access control (RBAC)
   - Validate permissions for all endpoints

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement proper session management

4. **Error Handling**
   - Don't expose sensitive information in error messages
   - Log security events appropriately
   - Implement proper rate limiting

### Testing Guidelines

1. **Unit Tests**
   - Test all business logic functions
   - Mock external dependencies
   - Achieve at least 80% code coverage

2. **Integration Tests**
   - Test API endpoints
   - Test database interactions
   - Test external service integrations

3. **Security Tests**
   - Test authentication and authorization
   - Test input validation
   - Test rate limiting

### Documentation Guidelines

1. **Code Documentation**
   - Use Google style docstrings
   - Include type hints for all functions
   - Document complex business logic

2. **API Documentation**
   - Update OpenAPI schema
   - Include request/response examples
   - Document error codes and messages

3. **Architecture Documentation**
   - Update architecture diagrams
   - Document design decisions
   - Keep deployment guides current

## Issue Reporting

### Bug Reports

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and stack traces

### Feature Requests

When requesting features, please include:
- Clear description of the feature
- Use cases and benefits
- Implementation suggestions (if any)
- Priority level

### Security Issues

For security issues:
- **Do not** create public issues
- Email security@kerya.com directly
- Include detailed vulnerability information
- Allow time for assessment and response

## Community Guidelines

### Communication

- Be respectful and inclusive
- Use clear and constructive language
- Provide helpful feedback
- Ask questions when needed

### Collaboration

- Help other contributors
- Share knowledge and best practices
- Review pull requests constructively
- Celebrate contributions and achievements

### Learning

- We welcome contributors of all skill levels
- Don't hesitate to ask for help
- Share your learning experiences
- Help improve our documentation

## Recognition

We appreciate all contributions! Contributors will be:
- Listed in our contributors file
- Recognized in release notes
- Invited to join our community discussions
- Considered for maintainer roles

Thank you for contributing to Kerya App! 🚀 