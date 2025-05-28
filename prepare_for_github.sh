#!/bin/bash
# OpenTiler GitHub Preparation Script
# Prepares the project for GitHub push with proper Git configuration

echo "🚀 OpenTiler GitHub Preparation Script"
echo "======================================"
echo

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "opentiler" ]; then
    echo "❌ Error: This script must be run from the OpenTiler project root directory"
    echo "   Expected files: main.py, opentiler/ directory"
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

# Check Git status
echo
echo "📊 Current Git status:"
git status --porcelain | head -10
if [ $(git status --porcelain | wc -l) -gt 10 ]; then
    echo "   ... and $(( $(git status --porcelain | wc -l) - 10 )) more files"
fi

# Add all files
echo
echo "📦 Adding all project files to Git..."
git add .

# Show what will be committed
echo
echo "📋 Files to be committed:"
git diff --cached --name-only | head -20
if [ $(git diff --cached --name-only | wc -l) -gt 20 ]; then
    echo "   ... and $(( $(git diff --cached --name-only | wc -l) - 20 )) more files"
fi

# Create initial commit
echo
echo "💾 Creating initial commit..."
git commit -m "Initial release: OpenTiler v1.0.0

🎉 Complete professional document scaling and tiling application

Features:
- Professional PySide6 GUI with comprehensive documentation
- Interactive scaling tool with real-world measurements
- Advanced tiling system with assembly guides
- Extensible plugin architecture with automation support
- Cross-platform support (Windows/macOS/Linux)
- 53 professional screenshots documenting all features
- Complete user and developer manuals
- Multi-platform installers and pip package support

Ready for production use and distribution."

echo "✅ Initial commit created"

# Show commit information
echo
echo "📝 Commit information:"
git log --oneline -1
echo

# Instructions for GitHub
echo "🌐 Next Steps for GitHub:"
echo "========================"
echo
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: OpenTiler"
echo "   - Description: Professional Document Scaling and Tiling Application"
echo "   - Make it public"
echo "   - Don't initialize with README (we already have one)"
echo
echo "2. Add GitHub remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/OpenTiler.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo
echo "3. Verify the upload:"
echo "   - Check that all files are present"
echo "   - Verify README.md displays correctly with images"
echo "   - Test the documentation links"
echo
echo "4. Optional: Create a release:"
echo "   - Go to https://github.com/YOUR_USERNAME/OpenTiler/releases"
echo "   - Click 'Create a new release'"
echo "   - Tag version: v1.0.0"
echo "   - Release title: OpenTiler v1.0.0 - Initial Release"
echo "   - Add release notes from CHANGELOG.md"
echo

# Project statistics
echo "📊 Project Statistics:"
echo "====================="
echo "📁 Total files: $(find . -type f ! -path './venv/*' ! -path './.git/*' | wc -l)"
echo "📄 Python files: $(find . -name '*.py' ! -path './venv/*' | wc -l)"
echo "📸 Screenshots: $(find docs/images -name '*.png' 2>/dev/null | wc -l)"
echo "📚 Documentation files: $(find docs -name '*.md' 2>/dev/null | wc -l)"
echo "🔧 Plugin files: $(find plugins -name '*.py' 2>/dev/null | wc -l)"
echo "🧪 Test files: $(find tests -name '*.py' 2>/dev/null | wc -l)"
echo

# Final verification
echo "✅ OpenTiler is ready for GitHub!"
echo "🎯 Professional-grade application with complete documentation"
echo "🚀 Ready for production use and distribution"
echo
echo "Repository prepared successfully! 🎉"
