#!/usr/bin/env python3
"""
Plugin Registry for OpenTiler Plugin System

This module maintains a registry of available and loaded plugins.
"""

from typing import Dict, List, Optional, Set
from dataclasses import asdict
import json
from pathlib import Path

from .base_plugin import PluginInfo


class PluginRegistry:
    """
    Registry for tracking plugin information and dependencies.
    """
    
    def __init__(self):
        """Initialize the plugin registry."""
        self.plugins: Dict[str, PluginInfo] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.dependents: Dict[str, Set[str]] = {}
    
    def register_plugin(self, plugin_info: PluginInfo) -> bool:
        """
        Register a plugin in the registry.
        
        Args:
            plugin_info: Plugin information to register
            
        Returns:
            True if registered successfully
        """
        try:
            self.plugins[plugin_info.name] = plugin_info
            
            # Track dependencies
            if plugin_info.dependencies:
                self.dependencies[plugin_info.name] = set(plugin_info.dependencies)
                
                # Update dependents
                for dep in plugin_info.dependencies:
                    if dep not in self.dependents:
                        self.dependents[dep] = set()
                    self.dependents[dep].add(plugin_info.name)
            
            return True
            
        except Exception:
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin from the registry.
        
        Args:
            plugin_name: Name of plugin to unregister
            
        Returns:
            True if unregistered successfully
        """
        try:
            if plugin_name in self.plugins:
                del self.plugins[plugin_name]
            
            # Clean up dependencies
            if plugin_name in self.dependencies:
                deps = self.dependencies[plugin_name]
                for dep in deps:
                    if dep in self.dependents:
                        self.dependents[dep].discard(plugin_name)
                del self.dependencies[plugin_name]
            
            # Clean up dependents
            if plugin_name in self.dependents:
                del self.dependents[plugin_name]
            
            return True
            
        except Exception:
            return False
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        Get plugin information.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            PluginInfo object or None if not found
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names.
        
        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())
    
    def get_dependencies(self, plugin_name: str) -> Set[str]:
        """
        Get dependencies for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Set of dependency names
        """
        return self.dependencies.get(plugin_name, set())
    
    def get_dependents(self, plugin_name: str) -> Set[str]:
        """
        Get plugins that depend on this plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Set of dependent plugin names
        """
        return self.dependents.get(plugin_name, set())
    
    def check_dependencies(self, plugin_name: str, available_plugins: Set[str]) -> List[str]:
        """
        Check if plugin dependencies are satisfied.
        
        Args:
            plugin_name: Name of the plugin to check
            available_plugins: Set of available plugin names
            
        Returns:
            List of missing dependencies
        """
        dependencies = self.get_dependencies(plugin_name)
        missing = []
        
        for dep in dependencies:
            if dep not in available_plugins:
                missing.append(dep)
        
        return missing
    
    def get_load_order(self, plugin_names: List[str]) -> List[str]:
        """
        Calculate load order based on dependencies.
        
        Args:
            plugin_names: List of plugin names to order
            
        Returns:
            List of plugin names in load order
        """
        # Topological sort based on dependencies
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(plugin_name: str):
            if plugin_name in temp_visited:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected involving {plugin_name}")
            
            if plugin_name not in visited:
                temp_visited.add(plugin_name)
                
                # Visit dependencies first
                deps = self.get_dependencies(plugin_name)
                for dep in deps:
                    if dep in plugin_names:  # Only consider plugins we're loading
                        visit(dep)
                
                temp_visited.remove(plugin_name)
                visited.add(plugin_name)
                result.append(plugin_name)
        
        try:
            for plugin_name in plugin_names:
                if plugin_name not in visited:
                    visit(plugin_name)
            
            return result
            
        except ValueError:
            # If circular dependency, return original order
            return plugin_names
    
    def find_plugins_by_category(self, category: str) -> List[str]:
        """
        Find plugins by category (based on description or name).
        
        Args:
            category: Category to search for
            
        Returns:
            List of matching plugin names
        """
        matches = []
        category_lower = category.lower()
        
        for name, info in self.plugins.items():
            if (category_lower in info.description.lower() or
                category_lower in name.lower()):
                matches.append(name)
        
        return matches
    
    def export_registry(self, file_path: Path) -> bool:
        """
        Export registry to JSON file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if exported successfully
        """
        try:
            registry_data = {
                'plugins': {name: asdict(info) for name, info in self.plugins.items()},
                'dependencies': {name: list(deps) for name, deps in self.dependencies.items()},
                'dependents': {name: list(deps) for name, deps in self.dependents.items()}
            }
            
            with open(file_path, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def import_registry(self, file_path: Path) -> bool:
        """
        Import registry from JSON file.
        
        Args:
            file_path: Path to import file
            
        Returns:
            True if imported successfully
        """
        try:
            with open(file_path, 'r') as f:
                registry_data = json.load(f)
            
            # Import plugins
            for name, info_dict in registry_data.get('plugins', {}).items():
                plugin_info = PluginInfo(**info_dict)
                self.plugins[name] = plugin_info
            
            # Import dependencies
            for name, deps_list in registry_data.get('dependencies', {}).items():
                self.dependencies[name] = set(deps_list)
            
            # Import dependents
            for name, deps_list in registry_data.get('dependents', {}).items():
                self.dependents[name] = set(deps_list)
            
            return True
            
        except Exception:
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_plugins': len(self.plugins),
            'plugins_with_dependencies': len(self.dependencies),
            'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
            'plugins_with_dependents': len(self.dependents),
            'total_dependents': sum(len(deps) for deps in self.dependents.values())
        }
