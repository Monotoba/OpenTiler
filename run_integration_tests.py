#!/usr/bin/env python3
"""
OpenTiler Plugin System Integration Test Runner

This script runs comprehensive integration tests between the plugin system
and real OpenTiler components, demonstrating full system integration.

Usage:
    python run_integration_tests.py                    # Run all integration tests
    python run_integration_tests.py --verbose          # Verbose output
    python run_integration_tests.py --coverage         # Run with coverage
    python run_integration_tests.py --specific doc     # Run specific integration
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_integration_tests(args):
    """Run plugin system integration tests with specified options."""
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Test directory
    test_dir = Path(__file__).parent / "tests" / "integration"
    
    # Determine which tests to run
    if args.specific:
        if args.specific == "doc":
            cmd.append(str(test_dir / "test_opentiler_integration.py::TestOpenTilerDocumentIntegration"))
        elif args.specific == "render":
            cmd.append(str(test_dir / "test_opentiler_integration.py::TestOpenTilerRenderingIntegration"))
        elif args.specific == "measurement":
            cmd.append(str(test_dir / "test_opentiler_integration.py::TestOpenTilerMeasurementIntegration"))
        elif args.specific == "tile":
            cmd.append(str(test_dir / "test_opentiler_integration.py::TestOpenTilerTileIntegration"))
        elif args.specific == "export":
            cmd.append(str(test_dir / "test_opentiler_integration.py::TestOpenTilerExportIntegration"))
        elif args.specific == "workflow":
            cmd.append(str(test_dir / "test_opentiler_integration.py::TestOpenTilerFullWorkflowIntegration"))
        else:
            print(f"Unknown integration test: {args.specific}")
            print("Available integrations: doc, render, measurement, tile, export, workflow")
            return 1
    else:
        # Run all integration tests
        cmd.append(str(test_dir))
    
    # Add verbose output
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        cmd.extend([
            "--cov=plugins",
            "--cov-report=html:htmlcov_integration",
            "--cov-report=term-missing"
        ])
    
    # Add integration test markers
    cmd.extend([
        "-m", "not slow",  # Skip slow tests unless specifically requested
        "--tb=short",      # Shorter traceback format
        "--strict-markers" # Strict marker checking
    ])
    
    print("🔗 Running OpenTiler Plugin System Integration Tests")
    print("=" * 55)
    print(f"Command: {' '.join(cmd)}")
    print()
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Integration tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return 1


def check_integration_dependencies():
    """Check if required dependencies for integration tests are available."""
    required_packages = [
        "pytest",
        "PySide6"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages for integration tests:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def run_simple_integration_demo():
    """Run a simple integration demonstration."""
    print("🔗 Simple Integration Test Demonstration")
    print("=" * 45)
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Test 1: Plugin Manager with Mock OpenTiler
        print("\n🧪 Test 1: Plugin Manager Integration")
        from unittest.mock import Mock
        from plugins.plugin_manager import PluginManager
        
        mock_window = Mock()
        plugin_manager = PluginManager(mock_window)
        print("   ✅ Plugin manager created with mock OpenTiler window")
        
        discovered = plugin_manager.discover_plugins()
        print(f"   ✅ Plugin discovery found: {discovered}")
        
        # Test 2: Content Access Integration
        print("\n🔐 Test 2: Content Access Integration")
        from plugins.content_access import ContentAccessManager, AccessLevel
        
        access_manager = ContentAccessManager(mock_window)
        requirements = {
            'plan_view': True,
            'tile_preview': True,
            'measurements': True
        }
        
        access_objects = access_manager.grant_access(
            "test_plugin", requirements, AccessLevel.READ_WRITE
        )
        print(f"   ✅ Content access granted for {len(access_objects)} components")
        
        # Test 3: Hook System Integration
        print("\n🔗 Test 3: Hook System Integration")
        from plugins.hook_system import get_hook_manager, HookType
        
        hook_manager = get_hook_manager()
        context = hook_manager.execute_hook(
            HookType.DOCUMENT_AFTER_LOAD,
            {'document_path': 'test.pdf', 'page_count': 3}
        )
        print("   ✅ Hook execution successful")
        print(f"   ✅ Context data: {context.data}")
        
        # Test 4: Plugin Lifecycle Integration
        print("\n🔄 Test 4: Plugin Lifecycle Integration")
        from plugins.builtin.automation_plugin import AutomationPlugin
        
        automation_plugin = AutomationPlugin(mock_window)
        plugin_manager.plugins["automation"] = automation_plugin
        
        # Initialize plugin
        init_result = plugin_manager.initialize_plugin("automation")
        print(f"   ✅ Plugin initialization: {init_result}")
        
        # Get plugin info
        info = plugin_manager.get_plugin_info("automation")
        print(f"   ✅ Plugin info: {info.name} v{info.version}")
        
        # Test hook handlers
        handlers = automation_plugin.get_hook_handlers()
        print(f"   ✅ Plugin provides {len(handlers)} hook handlers")
        
        print("\n🎉 Integration demonstration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run OpenTiler Plugin System Integration Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Run all integration tests
  %(prog)s --verbose           # Verbose output
  %(prog)s --coverage          # Run with coverage report
  %(prog)s --specific doc      # Run only document integration tests
  %(prog)s --specific workflow # Run only workflow integration tests
  %(prog)s --demo              # Run simple integration demonstration
        """
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose test output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    
    parser.add_argument(
        "--specific", "-s",
        choices=["doc", "render", "measurement", "tile", "export", "workflow"],
        help="Run specific integration test only"
    )
    
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="Run simple integration demonstration"
    )
    
    args = parser.parse_args()
    
    # Run simple demo if requested
    if args.demo:
        return 0 if run_simple_integration_demo() else 1
    
    # Check dependencies
    if not check_integration_dependencies():
        return 1
    
    # Run integration tests
    return run_integration_tests(args)


if __name__ == "__main__":
    sys.exit(main())
