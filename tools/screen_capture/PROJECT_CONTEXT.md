# Screen Capture Tool - Project Context

## 🎯 Project Overview

The **Cross-Platform Screen Capture Tool** is a professional utility designed for automated screenshot generation across Windows, macOS, and Linux platforms. Originally developed as a sub-project within the OpenTiler ecosystem, it's designed to be extracted as a standalone project.

## 🏗️ Architecture & Design

### Core Components

#### **screen_capture.py** - Main Module
- **ScreenCapture Class**: Primary interface for all capture operations
- **Cross-Platform Support**: Uses pywinctl + mss for universal compatibility
- **Multiple Capture Modes**: Active window, window by title, fullscreen
- **Format Support**: PNG, JPEG, WebP, BMP, TIFF with quality control
- **Error Handling**: Robust error handling with detailed logging

#### **Command Line Interface**
- **Argument Parsing**: Comprehensive CLI with argparse
- **Flexible Options**: Window/fullscreen modes, output control, format selection
- **User-Friendly**: Intuitive flags and helpful error messages

### Dependencies

#### **Core Dependencies**
- **pywinctl**: Cross-platform window management and detection
- **mss**: Fast, cross-platform screen capture library
- **Pillow**: Image processing, format conversion, and optimization

#### **Development Dependencies**
- **pytest**: Unit testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking

## 🎨 Key Features

### **Cross-Platform Compatibility**
- **Windows**: Full native support with no additional requirements
- **macOS**: Native support with Screen Recording permission handling
- **Linux**: X11 and Wayland support with automatic detection

### **Flexible Capture Options**
- **Active Window**: Capture currently focused window
- **Window by Title**: Find and capture specific applications
- **Full Screen**: Capture entire desktop or specific monitors
- **Batch Operations**: Multiple captures with consistent settings

### **Professional Output**
- **Multiple Formats**: PNG, JPEG, WebP, BMP, TIFF support
- **Quality Control**: Configurable compression and optimization
- **Size Control**: Target resolution with aspect ratio preservation
- **Directory Management**: Automatic output directory creation

### **Developer-Friendly**
- **Python API**: Clean, object-oriented interface
- **Error Handling**: Comprehensive exception handling
- **Logging**: Detailed logging with configurable levels
- **Documentation**: Complete API documentation and examples

## 🚀 Use Cases

### **Primary Use Case: OpenTiler Documentation**
- **Automated Screenshots**: Generate documentation images for OpenTiler
- **Consistent Quality**: Standardized screenshot format and quality
- **CI/CD Integration**: Automated documentation updates
- **Multi-Platform**: Screenshots from all supported platforms

### **General Use Cases**
- **Application Testing**: Automated UI testing and verification
- **Documentation**: Software documentation and tutorials
- **Monitoring**: System monitoring and reporting
- **Automation**: Workflow automation and scripting

## 📁 Project Structure

```
tools/screen_capture/
├── screen_capture.py           # Main module
├── setup.py                    # Package configuration
├── requirements.txt            # Dependencies
├── README.md                   # Project overview
├── PROJECT_CONTEXT.md          # This file
├── docs/                       # Comprehensive documentation
│   ├── api.md                  # API reference
│   ├── platforms.md            # Platform-specific notes
│   ├── integration.md          # Integration guide
│   └── troubleshooting.md      # Troubleshooting guide
├── tests/                      # Test suite
│   └── test_screen_capture.py  # Unit and integration tests
└── examples/                   # Usage examples
    ├── basic_usage.py          # Basic usage patterns
    └── opentiler_documentation.py # OpenTiler integration
```

## 🔧 Technical Implementation

### **Window Management**
- **pywinctl Integration**: Cross-platform window detection and control
- **Window Activation**: Automatic window focusing and restoration
- **Title Matching**: Flexible partial and exact title matching
- **State Management**: Handle minimized, hidden, and background windows

### **Screen Capture**
- **mss Integration**: Fast, efficient screen capture
- **Multi-Monitor**: Support for multiple displays
- **Coordinate Handling**: Accurate window positioning and sizing
- **Format Optimization**: Efficient image processing and compression

### **Error Handling**
- **Permission Management**: Handle platform-specific permissions
- **Graceful Degradation**: Continue operation when possible
- **Detailed Logging**: Comprehensive error reporting
- **User Feedback**: Clear error messages and solutions

## 🎯 Design Principles

### **Cross-Platform First**
- **Universal API**: Consistent interface across all platforms
- **Platform Abstraction**: Hide platform-specific complexities
- **Graceful Handling**: Adapt to platform limitations

### **Developer Experience**
- **Simple API**: Easy to use for basic cases
- **Powerful Options**: Advanced features for complex needs
- **Clear Documentation**: Comprehensive guides and examples
- **Reliable Operation**: Robust error handling and recovery

### **Performance**
- **Efficient Capture**: Fast screenshot generation
- **Memory Management**: Minimal memory footprint
- **Batch Optimization**: Efficient multi-capture operations
- **Resource Cleanup**: Proper resource management

## 🔄 Integration Patterns

### **Python Integration**
```python
from screen_capture import ScreenCapture

capture = ScreenCapture()
success = capture.capture_active_window("screenshot.png")
```

### **Command Line Usage**
```bash
python screen_capture.py --window --output-file screenshot.png
python screen_capture.py --window-title "MyApp" --output-file app.png
```

### **CI/CD Integration**
```yaml
- name: Generate Screenshots
  run: python screen_capture.py --fullscreen --output-file desktop.png
```

## 🚀 Future Roadmap

### **Immediate Goals (v1.0)**
- **Stable API**: Finalize core API design
- **Complete Testing**: Comprehensive test coverage
- **Documentation**: Complete user and developer guides
- **Package Release**: PyPI package publication

### **Enhanced Features (v1.1+)**
- **Annotation Support**: Add arrows, highlights, text overlays
- **Video Capture**: Screen recording capabilities
- **Advanced Automation**: GUI automation integration
- **Performance Optimization**: Further speed improvements

### **Advanced Features (v2.0+)**
- **Cloud Integration**: Direct upload to cloud services
- **AI Integration**: Automatic content detection and cropping
- **Plugin System**: Extensible architecture
- **Web Interface**: Browser-based control panel

## 🎨 OpenTiler Integration

### **Current Integration**
- **Documentation Generation**: Automated OpenTiler screenshot creation
- **Development Workflow**: Integrated into OpenTiler development process
- **Testing Support**: UI testing and verification

### **Planned Integration**
- **Built-in Screenshots**: Direct integration into OpenTiler for user guides
- **Export Preview**: Screenshot generation during export process
- **Help System**: Contextual help with screenshots

## 📊 Success Metrics

### **Technical Metrics**
- **Cross-Platform Compatibility**: 100% feature parity across platforms
- **Performance**: <1 second capture time for typical windows
- **Reliability**: >99% success rate for valid operations
- **Memory Efficiency**: <50MB memory usage during operation

### **User Experience Metrics**
- **API Simplicity**: Single-line capture for basic use cases
- **Documentation Quality**: Complete examples for all features
- **Error Clarity**: Clear error messages with actionable solutions
- **Integration Ease**: <5 minutes to integrate into existing projects

## 🔗 Related Projects

### **OpenTiler Ecosystem**
- **OpenTiler**: Main application using this tool for documentation
- **Build Tools**: Integration with OpenTiler build and release process
- **Documentation System**: Part of OpenTiler's documentation pipeline

### **External Dependencies**
- **pywinctl**: Window management library
- **mss**: Screen capture library  
- **Pillow**: Image processing library

## 📝 Development Notes

### **Code Style**
- **PEP 8 Compliance**: Standard Python code formatting
- **Type Hints**: Full type annotation for better IDE support
- **Docstrings**: Comprehensive documentation for all public APIs
- **Error Messages**: User-friendly error descriptions

### **Testing Strategy**
- **Unit Tests**: Core functionality testing
- **Integration Tests**: Cross-platform compatibility testing
- **Mock Testing**: Isolated component testing
- **CI Testing**: Automated testing across platforms

### **Documentation Strategy**
- **API Documentation**: Complete reference for all methods
- **Usage Examples**: Practical examples for common use cases
- **Platform Guides**: Platform-specific setup and troubleshooting
- **Integration Guides**: How to integrate into various workflows

This project represents a professional, production-ready screen capture solution designed for both standalone use and integration into larger applications like OpenTiler.
