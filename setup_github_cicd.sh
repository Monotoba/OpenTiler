#!/bin/bash
# OpenTiler GitHub CI/CD Setup Script
# Sets up the project with GitHub repository and CI/CD pipeline

echo "🚀 OpenTiler GitHub CI/CD Setup"
echo "==============================="
echo "Repository: https://github.com/Monotoba/OpenTiler"
echo

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "opentiler" ]; then
    echo "❌ Error: This script must be run from the OpenTiler project root directory"
    exit 1
fi

echo "✅ Project directory verified"

# Initialize Git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Configure Git user if not set
if [ -z "$(git config user.name)" ]; then
    echo "👤 Git user not configured. Please enter your details:"
    read -p "Enter your name: " git_name
    read -p "Enter your email: " git_email
    git config user.name "$git_name"
    git config user.email "$git_email"
    echo "✅ Git user configured"
else
    echo "✅ Git user already configured: $(git config user.name) <$(git config user.email)>"
fi

# Set up main branch
echo "🌿 Setting up main branch..."
git branch -M main

# Add GitHub remote
echo "🔗 Adding GitHub remote..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/Monotoba/OpenTiler.git
echo "✅ GitHub remote added"

# Verify CI/CD workflows exist
echo "🔧 Verifying CI/CD workflows..."
if [ -f ".github/workflows/ci.yml" ] && [ -f ".github/workflows/basic-test.yml" ]; then
    echo "✅ CI/CD workflows found:"
    echo "   - .github/workflows/ci.yml (Comprehensive CI/CD)"
    echo "   - .github/workflows/basic-test.yml (Basic testing)"
else
    echo "❌ CI/CD workflows missing!"
    exit 1
fi

# Add all files
echo "📦 Adding all project files..."
git add .

# Show what will be committed
echo
echo "📋 Files to be committed:"
git diff --cached --name-status | head -20
if [ $(git diff --cached --name-status | wc -l) -gt 20 ]; then
    echo "   ... and $(( $(git diff --cached --name-status | wc -l) - 20 )) more files"
fi

# Create initial commit
echo
echo "💾 Creating initial commit..."
git commit -m "Initial release: OpenTiler v1.0.0

🎉 Complete professional document scaling and tiling application

Features:
✅ Professional PySide6 GUI with comprehensive documentation
✅ Interactive scaling tool with real-world measurements
✅ Advanced tiling system with assembly guides
✅ Extensible plugin architecture with automation support
✅ Cross-platform support (Windows/macOS/Linux)
✅ 53 professional screenshots documenting all features
✅ Complete user and developer manuals
✅ Multi-platform installers and pip package support
✅ GitHub Actions CI/CD pipeline

Components:
- Core application with professional UI
- Plugin system with automation capabilities
- Comprehensive test suite
- Multi-platform installers
- Complete documentation with screenshots
- GitHub Actions workflows for CI/CD

Ready for production use and distribution! 🚀"

echo "✅ Initial commit created"

# Push to GitHub
echo
echo "🚀 Pushing to GitHub..."
echo "Repository: https://github.com/Monotoba/OpenTiler"

# Check if we can push
if git push -u origin main; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "❌ Push failed. You may need to authenticate with GitHub."
    echo
    echo "🔐 GitHub Authentication Options:"
    echo "1. Personal Access Token (Recommended):"
    echo "   - Go to https://github.com/settings/tokens"
    echo "   - Generate new token (classic)"
    echo "   - Select 'repo' scope"
    echo "   - Use token as password when prompted"
    echo
    echo "2. SSH Key (Alternative):"
    echo "   - Set up SSH key: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    echo "   - Change remote: git remote set-url origin git@github.com:Monotoba/OpenTiler.git"
    echo
    echo "3. GitHub CLI (Alternative):"
    echo "   - Install: https://cli.github.com/"
    echo "   - Authenticate: gh auth login"
    echo
    echo "After authentication, run: git push -u origin main"
    exit 1
fi

# Verify the push
echo
echo "🔍 Verifying GitHub repository..."
echo "✅ Repository URL: https://github.com/Monotoba/OpenTiler"
echo "✅ CI/CD will start automatically on next push"

# Show CI/CD information
echo
echo "🤖 GitHub Actions CI/CD Information:"
echo "===================================="
echo
echo "📊 Workflows configured:"
echo "1. 📋 Basic Tests (.github/workflows/basic-test.yml)"
echo "   - Runs on: Push to main/develop, Pull Requests"
echo "   - Tests: Python 3.10, 3.11 on Ubuntu & Windows"
echo "   - Checks: Import tests, syntax validation, basic pytest"
echo
echo "2. 🏗️ Comprehensive CI/CD (.github/workflows/ci.yml)"
echo "   - Runs on: Push, PR, Releases"
echo "   - Tests: Python 3.8-3.12 on Ubuntu, Windows, macOS"
echo "   - Quality: flake8, mypy, black, security checks"
echo "   - Build: PyInstaller executables for all platforms"
echo "   - Release: Automatic asset creation and upload"
echo
echo "🎯 CI/CD Features:"
echo "✅ Multi-platform testing (Linux, Windows, macOS)"
echo "✅ Multiple Python versions (3.8-3.12)"
echo "✅ Code quality checks (flake8, black, mypy)"
echo "✅ Security scanning (bandit, safety)"
echo "✅ Test coverage reporting"
echo "✅ Automatic builds with PyInstaller"
echo "✅ Release automation"
echo "✅ Artifact uploads"
echo
echo "📱 Monitoring CI/CD:"
echo "- View workflows: https://github.com/Monotoba/OpenTiler/actions"
echo "- Check status badges in README.md"
echo "- Get email notifications for failures"
echo
echo "🎉 OpenTiler is now live on GitHub with full CI/CD!"
echo "🌍 Ready for community contributions and professional use!"
