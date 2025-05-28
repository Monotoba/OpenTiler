# OpenTiler Requirements Guide

## 📦 **Requirements Structure Overview**

OpenTiler uses a modular requirements structure to provide flexibility for different use cases:

### **Core Requirements Files:**

#### **1. `requirements.txt` - Core Dependencies**
**For:** End users who want basic OpenTiler functionality
**Contains:** Minimal dependencies needed to run OpenTiler
```bash
pip install -r requirements.txt
```

**Dependencies:**
- `PySide6>=6.5.0` - GUI framework
- `Pillow>=9.0.0` - Image processing
- `PyMuPDF>=1.23.0` - PDF handling

#### **2. `requirements-optional.txt` - Enhanced Features**
**For:** Users who want all optional features
**Contains:** CAD support, RAW images, automation tools
```bash
pip install -r requirements-optional.txt
```

**Dependencies:**
- `ezdxf>=1.0.0` - CAD file support (DXF)
- `rawpy>=0.18.0` + `numpy>=1.21.0` - RAW image support
- `mss>=9.0.0` + `pywinctl>=0.0.50` - Screen capture and automation

#### **3. `requirements-dev.txt` - Development Environment**
**For:** Developers contributing to OpenTiler
**Contains:** All dependencies plus development tools
```bash
pip install -r requirements-dev.txt
```

**Dependencies:**
- All core and optional requirements
- Testing: `pytest`, `pytest-cov`, `pytest-xvfb`
- Code quality: `black`, `flake8`, `isort`, `mypy`
- Security: `bandit`, `safety`
- Build tools: `pyinstaller`, `setuptools`, `wheel`
- Documentation: `sphinx`, `sphinx-rtd-theme`

#### **4. `requirements-ci.txt` - CI/CD Environment**
**For:** GitHub Actions and continuous integration
**Contains:** Development requirements plus CI-specific tools
```bash
pip install -r requirements-ci.txt
```

**Additional Dependencies:**
- `codecov>=2.1.0` - Coverage reporting
- `pytest-timeout>=2.1.0` - Test timeouts
- `pytest-mock>=3.10.0` - Mocking framework

## 🎯 **Installation Scenarios**

### **Scenario 1: Basic User**
**Goal:** Just want to use OpenTiler for document scaling and tiling
```bash
pip install -r requirements.txt
```
**Result:** ~50MB download, basic functionality

### **Scenario 2: Power User**
**Goal:** Want all features including CAD and RAW image support
```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
```
**Result:** ~200MB download, full functionality

### **Scenario 3: Developer**
**Goal:** Contributing to OpenTiler development
```bash
pip install -r requirements-dev.txt
```
**Result:** ~300MB download, complete development environment

### **Scenario 4: CI/CD**
**Goal:** Automated testing and building
```bash
pip install -r requirements-ci.txt
```
**Result:** Complete testing and build environment

## 🔧 **Setup.py Integration**

The `setup.py` file provides pip-installable extras:

```bash
# Basic installation
pip install opentiler

# With CAD support
pip install opentiler[cad]

# With RAW image support
pip install opentiler[raw]

# With automation support
pip install opentiler[automation]

# With all optional features
pip install opentiler[all]

# Development installation
pip install opentiler[dev]
```

## 📊 **Dependency Breakdown**

### **Core Dependencies (Required)**
| Package | Purpose | Size | License |
|---------|---------|------|---------|
| PySide6 | GUI framework | ~40MB | LGPL |
| Pillow | Image processing | ~3MB | PIL |
| PyMuPDF | PDF handling | ~5MB | AGPL |

### **Optional Dependencies**
| Package | Purpose | Size | License |
|---------|---------|------|---------|
| ezdxf | CAD file support | ~2MB | MIT |
| rawpy | RAW image support | ~50MB | MIT |
| numpy | Numerical computing | ~15MB | BSD |
| mss | Screen capture | ~1MB | MIT |
| pywinctl | Window control | ~1MB | MIT |

### **Development Dependencies**
| Package | Purpose | Size | License |
|---------|---------|------|---------|
| pytest | Testing framework | ~5MB | MIT |
| black | Code formatting | ~2MB | MIT |
| flake8 | Code linting | ~1MB | MIT |
| mypy | Type checking | ~10MB | MIT |
| sphinx | Documentation | ~15MB | BSD |

## 🚀 **Best Practices**

### **For End Users:**
1. **Start with core requirements** - Try basic installation first
2. **Add optional features as needed** - Install extras only if you need them
3. **Use virtual environments** - Keep OpenTiler isolated from system Python

### **For Developers:**
1. **Use requirements-dev.txt** - Get complete development environment
2. **Run tests before committing** - Ensure code quality
3. **Use pre-commit hooks** - Automatic code formatting and linting

### **For CI/CD:**
1. **Use requirements-ci.txt** - Complete testing environment
2. **Cache dependencies** - Speed up CI/CD runs
3. **Test multiple Python versions** - Ensure compatibility

## 🔍 **Troubleshooting**

### **Common Issues:**

**1. Large Download Size**
```bash
# Problem: requirements-dev.txt downloads 300MB+
# Solution: Use core requirements for basic usage
pip install -r requirements.txt
```

**2. Optional Dependencies Failing**
```bash
# Problem: rawpy or ezdxf installation fails
# Solution: Install core requirements only
pip install -r requirements.txt
# Skip optional features that fail
```

**3. Version Conflicts**
```bash
# Problem: Dependency version conflicts
# Solution: Use fresh virtual environment
python -m venv fresh-env
source fresh-env/bin/activate
pip install -r requirements.txt
```

**4. Platform-Specific Issues**
```bash
# Problem: Some packages don't work on your platform
# Solution: Use continue-on-error for optional deps
pip install -r requirements.txt  # Always works
pip install -r requirements-optional.txt || echo "Optional deps skipped"
```

## 📈 **Future Considerations**

### **Planned Additions:**
- **requirements-minimal.txt** - Absolute minimum dependencies
- **requirements-gpu.txt** - GPU acceleration support
- **requirements-cloud.txt** - Cloud deployment dependencies

### **Version Management:**
- All requirements files use minimum version specifiers (`>=`)
- Major version updates tested in CI/CD
- Dependency security scanning with `safety`

**The modular requirements structure ensures OpenTiler works for everyone - from casual users to professional developers!** 🎯
