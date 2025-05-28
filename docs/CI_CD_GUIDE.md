# OpenTiler CI/CD Guide

## 🤖 **GitHub Actions CI/CD Overview**

OpenTiler uses **GitHub Actions** for continuous integration and deployment. This is **100% free** for open source projects!

## ✅ **What You Get for Free**

### **GitHub Actions Benefits:**
- ✅ **Unlimited minutes** for public repositories
- ✅ **Multi-platform testing** (Linux, Windows, macOS)
- ✅ **Multiple Python versions** (3.8-3.12)
- ✅ **Automatic testing** on every push/PR
- ✅ **Code quality checks** (linting, formatting)
- ✅ **Security scanning** (vulnerabilities)
- ✅ **Automatic builds** (executables)
- ✅ **Release automation** (asset creation)

## 🔧 **CI/CD Workflows**

### **1. Basic Tests** (`.github/workflows/basic-test.yml`)
**Runs on:** Every push to main/develop, all pull requests

**What it does:**
- Tests Python 3.10 & 3.11 on Ubuntu & Windows
- Verifies all imports work correctly
- Runs basic pytest suite
- Checks code syntax
- Validates code quality with flake8

### **2. Comprehensive CI/CD** (`.github/workflows/ci.yml`)
**Runs on:** Push, pull requests, releases

**What it does:**
- **Testing:** Python 3.8-3.12 on Ubuntu, Windows, macOS
- **Quality:** flake8, black, mypy, bandit security checks
- **Coverage:** Test coverage reporting with Codecov
- **Documentation:** Builds Sphinx docs
- **Building:** Creates PyInstaller executables
- **Releases:** Automatic asset creation and upload

## 📊 **Monitoring Your CI/CD**

### **View Workflow Status:**
1. Go to: https://github.com/Monotoba/OpenTiler/actions
2. See all workflow runs, status, and logs
3. Click on any run to see detailed logs

### **Status Badges:**
The README.md shows real-time status:
- 🟢 Green = All tests passing
- 🔴 Red = Tests failing
- 🟡 Yellow = Tests running

### **Email Notifications:**
GitHub automatically emails you when:
- Tests fail on main branch
- Pull request checks fail
- Workflows complete

## 🚀 **Using CI/CD**

### **Automatic Testing:**
Every time you:
- Push code to GitHub
- Create a pull request
- Merge changes

The CI/CD automatically:
1. Downloads your code
2. Sets up Python environments
3. Installs dependencies
4. Runs all tests
5. Reports results

### **Pull Request Workflow:**
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and commit
3. Push: `git push origin feature/new-feature`
4. Create pull request on GitHub
5. CI/CD runs automatically
6. Merge only if all tests pass ✅

### **Release Workflow:**
1. Create release on GitHub
2. CI/CD automatically builds executables
3. Uploads Windows, macOS, Linux binaries
4. Creates downloadable packages

## 🛠️ **Customizing CI/CD**

### **Adding New Tests:**
Edit `.github/workflows/basic-test.yml`:
```yaml
- name: Run my new test
  run: |
    python -m pytest tests/test_my_feature.py -v
```

### **Adding Dependencies:**
Update the workflow files to install new packages:
```yaml
- name: Install dependencies
  run: |
    pip install my-new-package
```

### **Platform-Specific Tests:**
```yaml
- name: Windows-only test
  if: runner.os == 'Windows'
  run: |
    # Windows-specific commands
```

## 🔍 **Troubleshooting CI/CD**

### **Common Issues:**

**1. Import Errors:**
- Check that all dependencies are in requirements.txt
- Verify package structure is correct

**2. Test Failures:**
- Run tests locally first: `pytest tests/`
- Check test logs in GitHub Actions

**3. Platform Differences:**
- Use `continue-on-error: true` for optional steps
- Add platform-specific conditions

**4. Timeout Issues:**
- Increase timeout: `timeout-minutes: 30`
- Optimize slow tests

### **Debugging Steps:**
1. Check workflow logs in GitHub Actions
2. Run the same commands locally
3. Add debug output: `echo "Debug: $VARIABLE"`
4. Use `continue-on-error: true` to isolate issues

## 📈 **CI/CD Best Practices**

### **For OpenTiler:**
1. **Always test locally** before pushing
2. **Keep tests fast** (< 5 minutes total)
3. **Use caching** for dependencies
4. **Test on multiple platforms** for GUI apps
5. **Monitor CI/CD costs** (though free for OSS)

### **Workflow Tips:**
- Use `continue-on-error: true` for optional checks
- Cache pip dependencies to speed up builds
- Use matrix builds for multiple Python versions
- Add status checks to protect main branch

## 🎯 **Next Steps**

### **Immediate:**
1. Push code to GitHub
2. Watch first CI/CD run
3. Fix any failing tests
4. Add status badges to README

### **Advanced:**
1. Set up Codecov for coverage reports
2. Add security scanning with CodeQL
3. Create deployment workflows
4. Add performance benchmarks

## 📚 **Resources**

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Python CI/CD Guide:** https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python
- **Workflow Syntax:** https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **Marketplace:** https://github.com/marketplace?type=actions

**Your CI/CD is ready to go! 🚀**
