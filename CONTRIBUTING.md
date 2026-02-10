# Contributing to Sentinel

First off, thank you for considering contributing to Sentinel! 🎉

This document provides guidelines for contributing to the project. Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open source project.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- **Be respectful** - Different viewpoints and experiences are valuable
- **Be collaborative** - Work together towards common goals
- **Be patient** - Not everyone has the same level of experience
- **Be constructive** - Provide helpful feedback and suggestions

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Great bug reports include:**

- A clear, descriptive title
- Detailed steps to reproduce
- Expected vs. actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, etc.)
- Error messages and stack traces

**Use this template:**

```markdown
**Environment:**
- OS: macOS 14.2
- Python: 3.11.5
- Sentinel: 0.2.0

**Steps to Reproduce:**
1. Run `sentinel clean-pc scan ~/Downloads`
2. Click "Execute Plan"
3. Observe error

**Expected:** Plan executes successfully
**Actual:** Error: "Permission denied"

**Error Log:**
[Paste error here]
```

### Suggesting Features

Feature suggestions are welcome! Please:

1. **Check existing issues** to avoid duplicates
2. **Explain the use case** - Why is this needed?
3. **Describe the solution** - How should it work?
4. **Consider alternatives** - What other approaches did you consider?

### Pull Requests

#### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/sentinel.git
cd sentinel

# Backend setup
cd sentinel-core
poetry install
poetry shell

# Frontend setup
cd ../sentinel-web
npm install

# Pre-commit hooks
cd ..
pre-commit install
```

#### Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guide
   - Add tests for new functionality
   - Update documentation if needed

3. **Run quality checks**
   ```bash
   # Python
   cd sentinel-core
   poetry run ruff check .
   poetry run black .
   poetry run mypy sentinel_core
   poetry run pytest
   
   # TypeScript
   cd sentinel-web
   npm run lint
   npm run type-check
   npm run build
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation only
   - `style:` - Code style (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

#### PR Checklist

Before submitting, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest` and `npm test`)
- [ ] New functionality has tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts

## Code Style

### Python

We use:
- **Ruff** - Fast linting
- **Black** - Automatic formatting (100 char line length)
- **Mypy** - Type checking

```bash
# Auto-fix most issues
poetry run ruff check --fix .
poetry run black .

# Check types
poetry run mypy sentinel_core
```

**Key conventions:**
- Type hints on all functions
- Docstrings (Google style) on public APIs
- Maximum complexity: 10 (enforced by Ruff)

**Example:**
```python
from typing import List

def classify_files(files: List[FileMetadata]) -> List[FileClassification]:
    """
    Classify a list of files based on heuristics.
    
    Args:
        files: List of file metadata objects to classify
        
    Returns:
        List of file classifications with suggested actions
        
    Example:
        >>> files = scanner.scan()
        >>> classifications = classify_files(files)
    """
    return [_classify_file(f) for f in files]
```

### TypeScript/React

We use:
- **ESLint** - Linting
- **Prettier** - Formatting (via ESLint)

```bash
# Run linter
npm run lint

# Type check
npm run type-check
```

**Key conventions:**
- Functional components with hooks
- TypeScript for all new code
- Props interfaces for components

**Example:**
```typescript
interface TaskCardProps {
  task: Task;
  onExecute: (taskId: string) => void;
}

export function TaskCard({ task, onExecute }: TaskCardProps) {
  return (
    <div className="task-card">
      <h3>{task.name}</h3>
      <button onClick={() => onExecute(task.id)}>Execute</button>
    </div>
  );
}
```

## Testing

### Writing Tests

**Test structure:**
```python
class TestFeatureName:
    """Tests for feature X."""
    
    def test_basic_case(self, mock_fs):
        """Test description."""
        # Arrange
        setup_data()
        
        # Act
        result = do_something()
        
        # Assert
        assert result == expected
```

**Coverage requirements:**
- New features: > 90% coverage
- Bug fixes: Include regression test
- Critical paths: 100% coverage

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_scanner.py

# With coverage
pytest --cov=sentinel_core --cov-report=html
```

## Documentation

Update documentation when:
- Adding new features
- Changing APIs
- Fixing bugs that affect usage

**Documentation locations:**
- API docs: Code docstrings
- User guides: `docs/` folder
- README: High-level overview
- TESTING.md: Test documentation

## Areas Needing Help

We especially welcome contributions in:

### 🎨 Frontend/UI
- Dashboard improvements
- Responsive design
- Accessibility features
- Animation polish

### 🧪 Testing
- Additional test coverage
- Integration tests
- Performance benchmarks
- Cross-platform testing

### 📝 Documentation
- Tutorials and guides
- API documentation
- Video walkthroughs
- Translation

### 🔌 Features
- New file classifiers
- Organization rules
- Plugin system
- Advanced analytics

## Getting Help

Stuck? We're here to help!

- 💬 [GitHub Discussions](https://github.com/mystic/sentinel/discussions) - Ask questions
- 🐛 [GitHub Issues](https://github.com/mystic/sentinel/issues) - Report bugs
- 📧 Email: sentinel@example.com

## Recognition

Contributors are recognized in:
- README.md acknowledgments
- Release notes
- GitHub contributors page

Thank you for making Sentinel better! 🚀
