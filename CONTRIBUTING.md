# Contributing to AgentLens

Thank you for your interest in contributing to AgentLens! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/agentlens.git
   cd agentlens
   ```
3. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a branch for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests:
   ```bash
   pytest
   ```
4. Ensure your code passes linting:
   ```bash
   flake8 agentlens tests
   ```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Push your branch and create a pull request
5. Fill out the pull request template with details about your changes

## Testing

- Write tests for all new functionality
- Aim for high test coverage
- Tests should be in the `tests/` directory with a clear naming structure

## Documentation

- Update documentation for any modified functionality
- Document public APIs clearly
- Include examples where appropriate

## Issue Reporting

When reporting issues, please include:

- A clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Version information
- Any relevant logs or screenshots

## Feature Requests

Feature requests are welcome. Please provide:

- A clear description of the problem your feature solves
- Potential implementation approach if you have one
- Use cases for the feature

## Review Process

- At least one maintainer must approve your PR
- Feedback should be addressed before merging
- Squash commits when merging

## Community Guidelines

- Be respectful
- Provide constructive feedback
- Help others when you can

## License

By contributing to AgentLens, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).