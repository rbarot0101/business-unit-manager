# Contributing to Business Unit Manager

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `.streamlit/secrets.toml` with your Snowflake credentials

## Development Workflow

### 1. Always Use Backup Tables

- Development MUST use backup tables (ZZZ_*_20260417)
- Never test on production tables
- Verify `config/table_config.py` has `USE_BACKUP_TABLES = True`

### 2. Code Standards

**Python Style**
- Follow PEP 8 guidelines
- Use type hints where applicable
- Maximum line length: 100 characters
- Use meaningful variable names

**Security**
- Always use parameterized queries
- Never concatenate user input into SQL
- Validate all user inputs before processing
- Never commit secrets or credentials

**Error Handling**
- Catch specific exceptions, not bare `except:`
- Provide user-friendly error messages
- Log errors with context for debugging

### 3. Testing Requirements

Before submitting changes:
- [ ] Test locally with `streamlit run app.py`
- [ ] Verify all features work in backup mode
- [ ] Test search functionality
- [ ] Test edit and update operations
- [ ] Verify validation catches invalid inputs
- [ ] Check error messages are clear
- [ ] Review changes don't affect production tables

### 4. Documentation

Update documentation when:
- Adding new features
- Changing configuration options
- Modifying database schema
- Adding new dependencies

Files to update:
- `README.md` - User-facing features
- `CLAUDE.md` - Development guidelines
- `docs/specs/spec.md` - Feature specifications
- Inline code comments for complex logic

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-export-functionality`
- `bugfix/fix-search-filter`
- `docs/update-deployment-guide`

### Commit Messages

Follow conventional commits:
```
type(scope): brief description

Longer description if needed

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat(search): add advanced filter options
fix(validation): correct latitude range check
docs(readme): update deployment instructions
```

### Pull Request Process

1. Update documentation
2. Add tests if applicable
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR with clear description
6. Address review feedback

## Code Review Guidelines

Reviewers check for:
- Security vulnerabilities
- SQL injection risks
- Input validation
- Error handling
- Code clarity
- Documentation updates
- CLAUDE.md adherence

## Project Architecture

### Key Principles

1. **Separation of Concerns**
   - Database operations in `src/database/`
   - Validation in `src/utils/`
   - UI in `app.py` / `streamlit_app.py`
   - Configuration in `config/`

2. **Security First**
   - Parameterized queries only
   - Input validation before database calls
   - Secrets never in code

3. **Backup-First Development**
   - Test on backup tables
   - Production toggle in one place
   - Clear mode indicators

### File Organization

```
config/          - Configuration and settings
src/database/    - Database operations
src/utils/       - Validation and helpers
scripts/         - Deployment and maintenance
docs/            - Documentation
deployment/      - Deployment guides
tests/           - Test suite (future)
```

## Testing Checklist

Complete before submitting:

**Functional Testing**
- [ ] App starts without errors
- [ ] Both tables load data
- [ ] Search filters correctly
- [ ] Selection works via dropdown
- [ ] Edit form displays with correct data
- [ ] Updates save successfully
- [ ] Validation catches invalid input
- [ ] Clear button resets state

**Security Testing**
- [ ] No SQL injection vulnerabilities
- [ ] Input validation on all fields
- [ ] Parameterized queries used
- [ ] No secrets in code

**Documentation**
- [ ] README updated if needed
- [ ] Comments added for complex logic
- [ ] CLAUDE.md updated if architecture changed

## Questions?

- Check [CLAUDE.md](CLAUDE.md) for development guidelines
- Review [docs/specs/spec.md](docs/specs/spec.md) for feature details
- See existing code for examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
