#!/usr/bin/env python3
"""
Simple Plugin System Test

Tests core plugin system functionality without complex dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_imports():
    """Test that all plugin system modules can be imported."""
    print("📦 Testing Basic Imports...")
    
    try:
        # Test hook system
        from plugins.hook_system import HookType, HookManager
        print("   ✅ Hook system imported")
        
        # Test plugin manager  
        from plugins.plugin_manager import PluginManager
        print("   ✅ Plugin manager imported")
        
        # Test content access
        from plugins.content_access import ContentAccessManager, AccessLevel
        print("   ✅ Content access imported")
        
        # Test base plugin
        from plugins.base_plugin import BasePlugin, PluginInfo
        print("   ✅ Base plugin imported")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_hook_types():
    """Test hook type definitions."""
    print("🔗 Testing Hook Types...")
    
    try:
        from plugins.hook_system import HookType
        
        # Check key hook types exist
        required_hooks = [
            'DOCUMENT_BEFORE_LOAD',
            'DOCUMENT_AFTER_LOAD', 
            'RENDER_BEFORE_DRAW',
            'RENDER_AFTER_DRAW',
            'MEASUREMENT_BEFORE_START',
            'MEASUREMENT_AFTER_FINISH'
        ]
        
        for hook_name in required_hooks:
            assert hasattr(HookType, hook_name), f"Missing hook: {hook_name}"
        
        print(f"   ✅ All {len(required_hooks)} required hook types found")
        print(f"   ✅ Total hook types: {len(list(HookType))}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Hook types test failed: {e}")
        return False


def test_access_levels():
    """Test access level definitions."""
    print("🔐 Testing Access Levels...")
    
    try:
        from plugins.content_access import AccessLevel
        
        # Check access levels
        levels = [level.value for level in AccessLevel]
        expected_levels = ['read_only', 'read_write', 'full_control']
        
        for level in expected_levels:
            assert level in levels, f"Missing access level: {level}"
        
        print(f"   ✅ All access levels found: {levels}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Access levels test failed: {e}")
        return False


def test_plugin_info():
    """Test plugin info structure."""
    print("📋 Testing Plugin Info...")
    
    try:
        from plugins.base_plugin import PluginInfo
        
        # Create test plugin info
        info = PluginInfo(
            name="Test Plugin",
            version="1.0.0",
            description="Test plugin for validation",
            author="Test Author"
        )
        
        assert info.name == "Test Plugin"
        assert info.version == "1.0.0"
        assert info.description == "Test plugin for validation"
        assert info.author == "Test Author"
        
        print("   ✅ Plugin info structure working correctly")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Plugin info test failed: {e}")
        return False


def main():
    """Run simple plugin system tests."""
    print("🧪 Simple Plugin System Test")
    print("=" * 30)
    
    tests = [
        test_basic_imports,
        test_hook_types,
        test_access_levels,
        test_plugin_info
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("📊 Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 Plugin system basic functionality verified!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
