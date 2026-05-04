# GitHub Workflows Documentation

## Overview

OmniNode uses a modular workflow architecture with four separate workflows, each focused on a specific responsibility:

1. **Unit Tests** - Test execution and coverage validation
2. **Security Scanning** - Dependency and filesystem vulnerability scanning
3. **TestPyPI Publish** - Automatic publishing to TestPyPI
4. **PyPI Publish** - Production release to PyPI

---

## 1. Unit Tests (`unit-tests.yml`)

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to these branches
- Manual dispatch

**Purpose:**
Ensures code quality through comprehensive testing and coverage requirements.

**Quality Gates:**
- ✅ 100% unit test pass rate (all tests must pass)
- ✅ 100% code coverage requirement
- 📊 Coverage reports uploaded to Codecov

**Artifacts:**
- `coverage-report` - Coverage XML file for analysis

---

## 2. Security Scanning (`security.yml`)

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to these branches
- Manual dispatch
- Daily scheduled scan at 2 AM UTC

**Purpose:**
Identifies security vulnerabilities in dependencies and codebase.

**Security Checks:**

### pip-audit
- Scans Python dependencies for known vulnerabilities
- Uses `--strict` mode (fails on any vulnerability)
- Skips editable packages with `--skip-editable`

### Trivy Scan
- Filesystem vulnerability scanner
- Checks for CRITICAL, HIGH, MEDIUM, and LOW severity issues
- Results uploaded to GitHub Security tab
- Zero vulnerabilities required

**Exit Criteria:**
Both pip-audit and Trivy must pass with zero vulnerabilities.

---

## 3. TestPyPI Publish (`testpypi.yml`)

**Triggers:**
- Automatically after successful completion of Unit Tests AND Security Scanning workflows
- Runs on `main`, `master`, `develop` branches

**Purpose:**
Automatically publishes package to TestPyPI for pre-release testing.

**Prerequisites:**
- ✅ Unit Tests workflow completed successfully
- ✅ Security Scanning workflow completed successfully

**Publishing:**
- Uses PyPA trusted publishing (no API tokens required)
- Builds source distribution and wheel
- Publishes to https://test.pypi.org/project/omni-node/

**Package Installation from TestPyPI:**
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple omni-node
```

---

## 4. PyPI Publish (`pypi.yml`)

**Triggers:**
- Version tags matching pattern `v*.*.*` (e.g., `v0.3.0`, `v1.0.0`)
- Manual dispatch

**Purpose:**
Production release to PyPI with comprehensive quality validation.

**Workflow Steps:**

### 1. Version Verification
- Extracts version from tag (e.g., `v0.3.0` → `0.3.0`)
- Reads version from `pyproject.toml`
- **Fails if versions don't match exactly**

### 2. Quality Gate Validation
- Triggers Unit Tests workflow
- Triggers Security Scanning workflow
- Waits for both to complete successfully
- **Fails if either workflow fails**

### 3. PyPI Publication
- Builds source distribution and wheel
- Validates package with `twine check`
- Publishes to https://pypi.org/project/omni-node/ using trusted publishing
- Creates GitHub Release with built artifacts

**Release Creation:**
```bash
# Example release process
git tag v0.3.0
git push origin v0.3.0
# Workflow automatically handles the rest
```

---

## Workflow Dependencies

```
┌─────────────────┐    ┌──────────────────┐
│  Unit Tests     │    │ Security Scanning│
│  (unit-tests)   │    │   (security)     │
└────────┬────────┘    └────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────▼──────────┐
         │  TestPyPI Publish   │
         │   (testpypi)        │
         └─────────────────────┘

                  OR

    ┌─────────────────────┐
    │   Version Tag       │
    │   (v*.*.*)         │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │ Verify Tag Version  │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │ Trigger Quality     │
    │ Gates (both above)  │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   PyPI Publish      │
    │    (pypi)          │
    └─────────────────────┘
```

---

## Quality Gate Summary

All workflows enforce strict quality requirements:

| Requirement | Standard | Workflow |
|------------|----------|----------|
| Unit Test Pass Rate | 100% | unit-tests.yml |
| Code Coverage | 100% | unit-tests.yml |
| Dependency Vulnerabilities | 0 | security.yml |
| Filesystem Vulnerabilities | 0 | security.yml |
| Version Tag Match | Exact | pypi.yml |

---

## Configuration Requirements

### GitHub Secrets
No API tokens required! All publishing uses trusted publishing.

### PyPI Trusted Publishing Setup

**TestPyPI:**
1. Go to https://test.pypi.org/manage/account/publishing/
2. Add publisher:
   - PyPI Project Name: `omni-node`
   - Owner: `ShanKonduru`
   - Repository: `omni-node`
   - Workflow: `testpypi.yml`
   - Environment: (leave blank)

**PyPI:**
1. Go to https://pypi.org/manage/account/publishing/
2. Add publisher:
   - PyPI Project Name: `omni-node`
   - Owner: `ShanKonduru`
   - Repository: `omni-node`
   - Workflow: `pypi.yml`
   - Environment: (leave blank)

### Optional: Codecov Token
Set `CODECOV_TOKEN` secret for coverage report uploads (optional, workflow continues if missing).

---

## Troubleshooting

### TestPyPI Publish Not Triggering
- Ensure both Unit Tests and Security Scanning workflows completed successfully
- Check workflow_run trigger is enabled on target branches
- Verify workflows are on the same branch

### PyPI Publish Failing
- Check tag format matches `v*.*.*` pattern
- Verify tag version matches `pyproject.toml` version exactly
- Ensure all quality gates pass
- Confirm trusted publishing is configured on PyPI

### Security Scan Failures
- Run `pip-audit --skip-editable` locally to identify vulnerable dependencies
- Run `trivy fs .` locally to identify filesystem vulnerabilities
- Update dependencies to patched versions
- Add exclusions only if absolutely necessary (not recommended)

### Coverage Below 100%
- Check which files are missing coverage with `pytest --cov=backend --cov-report=term-missing`
- Add tests for uncovered code paths
- Update coverage exclusions in `pyproject.toml` [tool.coverage.run] if needed
- Excluded: `backend/api/*`, `backend/services/*`, `backend/main.py`, `backend/core/database.py`

---

## Manual Workflow Dispatch

All workflows support manual triggering:

```bash
# Via GitHub CLI
gh workflow run unit-tests.yml
gh workflow run security.yml
gh workflow run testpypi.yml
gh workflow run pypi.yml
```

Or use the GitHub Actions UI: Actions → Select Workflow → Run workflow

---

## Best Practices

1. **Never skip quality gates** - They exist for a reason
2. **Test locally first** - Run pytest and security scans before pushing
3. **Version tags are immutable** - Delete and recreate if needed
4. **Monitor security scans** - Daily scans help catch new vulnerabilities
5. **Review coverage reports** - 100% coverage ensures comprehensive testing
6. **Use TestPyPI** - Always test on TestPyPI before production release

---

## Quick Reference

| Task | Command |
|------|---------|
| Run tests locally | `pytest --cov=backend --cov=src --cov-fail-under=100` |
| Check security | `pip-audit --skip-editable && trivy fs .` |
| Publish to TestPyPI | Push to main/master/develop (automatic) |
| Publish to PyPI | `git tag v0.3.0 && git push origin v0.3.0` |
| Delete bad tag | `git tag -d v0.3.0 && git push origin :refs/tags/v0.3.0` |
