# GitHub Workflows Documentation

This document describes the CI/CD pipelines for OmniNode, including quality gates and publishing workflows.

## 🎯 Overview

OmniNode implements a strict quality gate strategy with three GitHub Actions workflows:

1. **CI - Quality Gates** (`ci.yml`) - Runs on every push/PR
2. **Publish to TestPyPI** (`testpypi.yml`) - Runs after CI passes on main branch
3. **Publish to PyPI** (`pypi.yml`) - Runs on version tag with strict validation

## 📊 Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PUSH / PULL REQUEST                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  CI - Quality Gates                          │
├─────────────────────────────────────────────────────────────┤
│ ✓ Unit Tests (100% pass rate required)                      │
│ ✓ Code Coverage (100% required)                             │
│ ✓ pip-audit (Zero vulnerabilities required)                 │
│ ✓ Trivy Scan (Zero vulnerabilities required)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
    [main branch]              [tag: v*.*.*]
         │                           │
         ▼                           ▼
┌────────────────────┐      ┌────────────────────┐
│  TestPyPI Publish  │      │   PyPI Publish     │
│                    │      │                    │
│ • Auto-publish     │      │ • Tag must match   │
│ • Every commit     │      │   version          │
│ • After CI passes  │      │ • Re-runs quality  │
│                    │      │   gates            │
│                    │      │ • Creates release  │
└────────────────────┘      └────────────────────┘
```

## 🔒 Quality Gates

### 1. Unit Tests (100% Pass Rate)

**Requirement:** All unit tests must pass. If any test fails, the workflow fails.

**Enforcement:**
```yaml
pytest -v  # Fails on first test failure
```

**Validation:**
- pytest automatically fails if any test fails
- No partial success allowed

### 2. Code Coverage (100%)

**Requirement:** Complete code coverage of the `backend` package.

**Enforcement:**
```yaml
pytest --cov=backend --cov-fail-under=100
coverage report --fail-under=100
```

**Validation:**
- Double-checked with both pytest-cov and coverage.py
- Fails immediately if coverage < 100%

### 3. pip-audit (Zero Vulnerabilities)

**Requirement:** No known security vulnerabilities in dependencies.

**Enforcement:**
```yaml
pip-audit --strict --desc
```

**Validation:**
- `--strict` flag causes failure on any vulnerability
- Includes detailed descriptions of any issues found

### 4. Trivy Filesystem Scan (Zero Vulnerabilities)

**Requirement:** No security vulnerabilities in the filesystem.

**Enforcement:**
```yaml
trivy fs . --exit-code 1 --severity CRITICAL,HIGH,MEDIUM,LOW
```

**Validation:**
- Scans for vulnerabilities at all severity levels
- Results uploaded to GitHub Security tab (SARIF format)
- Fails on any detected vulnerability

## 🚀 Publishing Workflows

### TestPyPI Publishing

**Trigger:** Automatic after CI passes on `main` branch

**Purpose:** Testing package distribution before production release

**Process:**
1. Wait for CI workflow to complete successfully
2. Verify all quality gates passed
3. Build Python package (wheel + sdist)
4. Validate package with twine
5. Publish to TestPyPI

**Install from TestPyPI:**
```bash
pip install --index-url https://test.pypi.org/simple/ omninode
```

### PyPI Publishing (Production)

**Trigger:** Manual - push a version tag

**Requirements:**
- Tag format: `v*.*.*` (e.g., `v0.1.0`)
- Tag version MUST match `pyproject.toml` version
- All quality gates must pass

**Process:**
1. Extract tag version (e.g., `v1.2.3` → `1.2.3`)
2. Extract pyproject.toml version
3. **Verify versions match** (fail if mismatch)
4. Re-run ALL quality gates:
   - Unit tests (100% pass)
   - Coverage (100%)
   - pip-audit (zero vulnerabilities)
   - Trivy scan (zero vulnerabilities)
5. Build package
6. Publish to PyPI
7. Create GitHub Release with notes
8. Upload distribution artifacts

**Example Release:**
```bash
# Update version in pyproject.toml
vim pyproject.toml  # version = "1.2.3"

# Commit and push
git add pyproject.toml
git commit -m "chore: bump version to 1.2.3"
git push

# Create and push tag
git tag v1.2.3
git push origin v1.2.3

# Workflow automatically:
# - Verifies v1.2.3 matches pyproject.toml
# - Runs quality gates
# - Publishes to PyPI
# - Creates GitHub release
```

## ⚙️ Configuration

### GitHub Secrets

Configure these in GitHub Settings → Secrets and variables → Actions:

#### Required for All Workflows
- None (uses GitHub's trusted publishing)

#### Optional
- `CODECOV_TOKEN` - For uploading coverage reports to Codecov

### Trusted Publishing Setup

Both TestPyPI and PyPI workflows use **Trusted Publishing** (no API tokens needed).

**Setup Instructions:**

1. **TestPyPI** (https://test.pypi.org):
   - Go to Account Settings → Publishing
   - Add a new "pending publisher"
   - Owner: `yourusername`
   - Repository: `omni-node`
   - Workflow name: `testpypi.yml`
   - Environment name: (leave empty)

2. **PyPI** (https://pypi.org):
   - Go to Account Settings → Publishing
   - Add a new "pending publisher"
   - Owner: `yourusername`
   - Repository: `omni-node`
   - Workflow name: `pypi.yml`
   - Environment name: (leave empty)

### Repository Settings

Recommended settings in GitHub:

1. **Branch Protection** (main):
   - Require status checks to pass before merging
   - Required checks:
     - `Unit Tests & Coverage (100% Required)`
     - `Security - pip-audit (Zero Vulnerabilities)`
     - `Security - Trivy Filesystem Scan (Zero Vulnerabilities)`
   - Require branches to be up to date before merging

2. **Actions Permissions**:
   - Allow GitHub Actions to create pull requests: ✓
   - Workflow permissions: Read and write permissions

## 📋 Workflow Status Badges

Add these to your README.md:

```markdown
[![CI - Quality Gates](https://github.com/yourusername/omni-node/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/omni-node/actions/workflows/ci.yml)
[![Publish to TestPyPI](https://github.com/yourusername/omni-node/actions/workflows/testpypi.yml/badge.svg)](https://github.com/yourusername/omni-node/actions/workflows/testpypi.yml)
[![Publish to PyPI](https://github.com/yourusername/omni-node/actions/workflows/pypi.yml/badge.svg)](https://github.com/yourusername/omni-node/actions/workflows/pypi.yml)
[![codecov](https://codecov.io/gh/yourusername/omni-node/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/omni-node)
```

## 🔧 Local Testing

Test quality gates locally before pushing:

```bash
# 1. Unit tests with coverage
pytest --cov=backend --cov-report=term-missing --cov-fail-under=100 -v

# 2. Coverage verification
coverage report --fail-under=100

# 3. Security audit
pip install pip-audit
pip-audit --strict --desc

# 4. Trivy scan (requires Docker)
docker run --rm -v $(pwd):/src aquasec/trivy fs /src --exit-code 1

# 5. Build package
pip install build twine
python -m build
twine check dist/*
```

## 🐛 Troubleshooting

### Quality Gate Failures

#### Unit Tests Failing
```bash
# Run tests locally with verbose output
pytest -vv --tb=short

# Run specific test
pytest tests/test_file.py::test_function -vv
```

#### Coverage Below 100%
```bash
# Generate HTML coverage report
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html in browser

# See missing lines
pytest --cov=backend --cov-report=term-missing
```

#### pip-audit Vulnerabilities
```bash
# See detailed vulnerability report
pip-audit --desc

# Check specific package
pip-audit | grep package-name

# Upgrade vulnerable packages
pip install --upgrade package-name
```

#### Trivy Vulnerabilities
```bash
# Run Trivy locally
trivy fs . --severity CRITICAL,HIGH,MEDIUM,LOW

# Generate detailed report
trivy fs . --format json > trivy-report.json
```

### Version Mismatch Error

```
❌ ERROR: Tag version (1.2.3) does not match pyproject.toml version (1.2.2)
```

**Solution:**
1. Update version in `pyproject.toml`
2. Commit the change
3. Delete and recreate the tag:
   ```bash
   git tag -d v1.2.3
   git push origin :refs/tags/v1.2.3
   git tag v1.2.3
   git push origin v1.2.3
   ```

### TestPyPI Publication Failed

**Common causes:**
- Version already exists on TestPyPI (use `skip-existing: true` - already configured)
- Trusted publishing not configured (see Configuration section)
- Package name conflict

**Check logs:**
- GitHub Actions → TestPyPI workflow → Failed job → Step details

## 📚 Related Documentation

- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions - Publishing Python packages](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python#publishing-to-package-registries)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)

## 🔄 Workflow Updates

To modify workflows:

1. Edit `.github/workflows/*.yml`
2. Test locally if possible
3. Create PR to test in CI environment
4. Merge after verification

**Best Practices:**
- Always test workflow changes in a branch first
- Use `workflow_dispatch` trigger for manual testing
- Review logs carefully after changes
- Keep quality gates strict - don't lower standards

## 📊 Metrics & Monitoring

### Key Metrics
- **Test Pass Rate**: Must be 100%
- **Code Coverage**: Must be 100%
- **Security Vulnerabilities**: Must be 0
- **Build Time**: Target < 10 minutes
- **Publication Success Rate**: Target > 95%

### Monitoring
- GitHub Actions dashboard: Track workflow runs
- Security tab: Review Trivy SARIF reports
- Codecov: Track coverage trends
- PyPI/TestPyPI: Monitor download stats

---

**Last Updated:** May 4, 2026  
**Maintainer:** OmniNode Contributors
