#!/usr/bin/env python3
"""
OpenTiler Plugin System Test Runner

This script runs comprehensive tests for the OpenTiler plugin system,
including hook system, plugin manager, content access, and automation plugin tests.

Usage:
    python run_plugin_tests.py                    # Run all plugin tests
    python run_plugin_tests.py --verbose          # Verbose output
    python run_plugin_tests.py --coverage         # Run with coverage
    python run_plugin_tests.py --integration      # Include integration tests
    python run_plugin_tests.py --specific hook    # Run specific test module
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(args):
    """Run plugin system tests with specified options."""
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Test directory
    test_dir = Path(__file__).parent / "tests" / "plugins"
    
    # Determine which tests to run
    if args.specific:
        if args.specific == "hook":
            cmd.append(str(test_dir / "test_hook_system.py"))
        elif args.specific == "manager":
            cmd.append(str(test_dir / "test_plugin_manager.py"))
        elif args.specific == "content":
            cmd.append(str(test_dir / "test_content_access.py"))
        elif args.specific == "automation":
            cmd.append(str(test_dir / "test_automation_plugin.py"))
        else:
            print(f"Unknown test module: {args.specific}")
            print("Available modules: hook, manager, content, automation")
            return 1
    else:
        # Run all plugin tests
        cmd.append(str(test_dir))
    
    # Add verbose output
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        cmd.extend([
            "--cov=plugins",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    # Include integration tests
    if args.integration:
        cmd.append("-m")
        cmd.append("not slow")
    else:
        # Skip integration and slow tests by default
        cmd.append("-m")
        cmd.append("not integration and not slow")
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "--disable-warnings"  # Disable warnings for cleaner output
    ])
    
    print("🧪 Running OpenTiler Plugin System Tests")
    print("=" * 50)
    print(f"Command: {' '.join(cmd)}")
    print()
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def check_dependencies():
    """Check if required test dependencies are available."""
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
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run OpenTiler Plugin System Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Run all plugin tests
  %(prog)s --verbose           # Verbose output
  %(prog)s --coverage          # Run with coverage report
  %(prog)s --integration       # Include integration tests
  %(prog)s --specific hook     # Run only hook system tests
  %(prog)s --specific manager  # Run only plugin manager tests
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
        "--integration", "-i",
        action="store_true",
        help="Include integration tests (slower)"
    )
    
    parser.add_argument(
        "--specific", "-s",
        choices=["hook", "manager", "content", "automation"],
        help="Run specific test module only"
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Run tests
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
