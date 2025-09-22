# 🤝 Contributing to Beacon MCP Events Fetcher

Thank you for your interest in contributing to Beacon MCP Events Fetcher! This project welcomes contributions from everyone. Here are some guidelines to help you get started.

## 📋 How to Contribute

### 1. 🐛 Reporting Bugs

We use GitHub issues to track public bugs. Report a bug by opening a new issue with the "🐛 Bug Report" template.

**Great Bug Reports** tend to have:
- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### 2. 🚀 Suggesting Features

Feature requests are welcome! Please open an issue with the "🚀 Feature Request" template and provide as much detail as possible.

### 3. 🔧 Code Contributions

#### Fork and Clone
```bash
# Fork the repository
# Clone your fork
git clone https://github.com/yourusername/beacon-mcp-events-fetcher.git
cd beacon-mcp-events-fetcher

# Add the main repository as upstream
git remote add upstream https://github.com/originalowner/beacon-mcp-events-fetcher.git
```

#### Create a Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/your-bug-fix
```

#### Make Your Changes
1. Follow the existing code style
2. Add tests for new functionality
3. Ensure all tests pass
4. Update documentation if needed

#### Commit Your Changes
```bash
git add .
git commit -m "Add: your descriptive commit message"
```

#### Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then, open a pull request on GitHub!

## 🏗️ Development Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/beacon-mcp-events-fetcher.git
cd beacon-mcp-events-fetcher

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio flake8 black
```

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=consolidated_event_scraper --cov-report=html
```

### Code Style
```bash
# Format code
black consolidated_event_scraper.py

# Lint code
flake8 consolidated_event_scraper.py
```

## 📋 Pull Request Process

1. **Ensure CI passes** - All automated tests must pass
2. **Update documentation** - Keep README and docstrings current
3. **Follow naming conventions** - Use descriptive branch names
4. **Write meaningful commit messages** - Follow conventional commits
5. **Reference issues** - Link PR to relevant issues
6. **Be patient** - Reviewers will respond as soon as possible

## 🔧 Code Guidelines

### Style
- Follow PEP 8 guidelines
- Use type hints for function parameters and return types
- Use descriptive variable and function names
- Keep functions small and focused on single responsibility
- Add docstrings to all public functions

### Error Handling
- Use try-except blocks appropriately
- Provide meaningful error messages
- Handle edge cases gracefully
- Log errors with appropriate levels

### Testing
- Write unit tests for new functionality
- Test edge cases and error conditions
- Use descriptive test names
- Mock external dependencies

## 🌟 Recognition

Contributors will be acknowledged in the project documentation and receive credit for their work.

## 📞 Questions?

Feel free to open an issue or discussion for questions about contributing.

---

*Thank you for contributing to make Beacon MCP Events Fetcher better for everyone! 🎉*
