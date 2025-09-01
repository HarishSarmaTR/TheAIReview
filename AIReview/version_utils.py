"""
Version Configuration Utility
Centralized version management for AI Review Tool
"""
import json
import os

def get_version_config():
    """Load version configuration from JSON file"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'version_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # Fallback to hardcoded values if config file is missing
        return {
            "app_version": "2.1.8",
            "app_name": "AI Code Review Tool",
            "release_date": "2025-09-01"
        }

def get_app_version():
    """Get the current application version"""
    config = get_version_config()
    return config.get("app_version", "2.1.8")

def get_app_name():
    """Get the application name"""
    config = get_version_config()
    return config.get("app_name", "AI Code Review Tool")

def get_release_date():
    """Get the release date"""
    config = get_version_config()
    return config.get("release_date", "2025-08-28")

def get_version_info():
    """Get complete version information"""
    config = get_version_config()
    return {
        'version': config.get("app_version", "2.1.8"),
        'name': config.get("app_name", "AI Code Review Tool"),
        'release_date': config.get("release_date", "2025-08-28"),
        'features': config.get("major_features", [])
    }

# Global variables for easy access
APP_VERSION = get_app_version()
APP_NAME = get_app_name()
RELEASE_DATE = get_release_date()

if __name__ == "__main__":
    print(f"{APP_NAME} v{APP_VERSION}")
    print(f"Released: {RELEASE_DATE}")
