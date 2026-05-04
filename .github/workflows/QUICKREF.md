# GitHub Workflows Quick Reference

## 🚦 Quality Gates Summary

| Gate | Requirement | Tool | Enforcement |
|------|-------------|------|-------------|
| **Unit Tests** | 100% pass rate | pytest | `pytest -v` |
| **Coverage** | 100% coverage | pytest-cov | `--cov-fail-under=100` |
| **Dependencies** | 0 vulnerabilities | pip-audit | `--strict` |
| **Filesystem** | 0 vulnerabilities | trivy | `--exit-code 1` |

## 🔄 Workflow Triggers

| Workflow | Trigger | When | Purpose |
|----------|---------|------|---------|
| **ci.yml** | push, pull_request | Every commit | Quality gates |
| **testpypi.yml** | workflow_run | After CI passes (main) | Test distribution |
| **pypi.yml** | push (tag) | Version tags `v*.*.*` | Production release |

## 📦 Publishing Commands

### TestPyPI (Automatic)
```bash
# Just push to main - automatic after CI passes
git push origin main
# Wait for CI → TestPyPI auto-publishes
```

### PyPI (Manual Release)
```bash
# 1. Update version in pyproject.toml
version = "1.2.3"

# 2. Commit
git add pyproject.toml
git commit -m "chore: bump version to 1.2.3"
git push

# 3. Create matching tag
git tag v1.2.3
git push origin v1.2.3

# Workflow automatically:
# - Verifies version match
# - Runs quality gates
# - Publishes to PyPI
# - Creates GitHub release
```

## ✅ Pre-Push Checklist

Before pushing to main or creating a release tag:

```bash
# 1. Run tests
pytest --cov=backend --cov-fail-under=100 -v

# 2. Check coverage
coverage report --fail-under=100

# 3. Security audit
pip-audit --strict

# 4. Trivy scan (optional, requires Docker)
trivy fs . --exit-code 1

# 5. Build test (for releases)
python -m build
twine check dist/*
```

## 🔐 Required GitHub Secrets

### For Trusted Publishing (Recommended)
- **No secrets needed!** ✨
- Configure on PyPI/TestPyPI: Account → Publishing → Add Publisher

### Alternative: API Tokens (Legacy)
- `PYPI_API_TOKEN` - PyPI API token
- `TEST_PYPI_API_TOKEN` - TestPyPI API token

### Optional
- `CODECOV_TOKEN` - Codecov integration

## ⚠️ Common Issues

### ❌ Coverage < 100%
```bash
# View coverage report
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html
```

### ❌ Version Mismatch
```bash
# Tag: v1.2.3, pyproject.toml: 1.2.2
# Fix: Update pyproject.toml first!
vim pyproject.toml  # Set version = "1.2.3"
git add pyproject.toml
git commit -m "chore: bump version to 1.2.3"
git tag -d v1.2.3  # Delete old tag
git push origin :refs/tags/v1.2.3
git tag v1.2.3
git push origin v1.2.3
```

### ❌ Vulnerabilities Found
```bash
# Check details
pip-audit --desc
trivy fs . --severity CRITICAL,HIGH

# Fix
pip install --upgrade <vulnerable-package>
```

## 📊 Status Badge Code

```markdown
[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)
[![TestPyPI](https://github.com/USER/REPO/actions/workflows/testpypi.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/testpypi.yml)
[![PyPI](https://github.com/USER/REPO/actions/workflows/pypi.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/pypi.yml)
```

## 🎯 Release Process

1. ✅ All tests pass locally
2. ✅ Coverage at 100%
3. ✅ No security vulnerabilities
4. ✅ Version updated in `pyproject.toml`
5. ✅ Commit and push changes
6. ✅ Create tag: `git tag v<version>`
7. ✅ Push tag: `git push origin v<version>`
8. ✅ Wait for workflow to complete
9. ✅ Verify on PyPI
10. ✅ Update CHANGELOG

## 🔗 Useful Links

- [Full Workflow Documentation](.github/workflows/README.md)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
