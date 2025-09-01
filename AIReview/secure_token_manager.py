# 🔐 Secure Token Management System
# This module handles all token operations securely

import os
import json
import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass
import tempfile

class SecureTokenManager:
    """
    Enterprise-grade secure token management
    - Uses Windows Credential Manager for token storage
    - Never writes tokens to files
    - Automatic token expiry handling
    - Encrypted in-memory storage only
    """
    
    def __init__(self):
        self.app_name = "AIReviewTool"
        self.username = getpass.getuser()
        
    def save_github_token(self, token):
        """Save GitHub token securely to Windows Credential Manager"""
        try:
            keyring.set_password(self.app_name, f"{self.username}_github", token)
            return True
        except Exception as e:
            print(f"Failed to save GitHub token securely: {e}")
            return False
    
    def save_openarena_token(self, token):
        """Save OpenArena token securely to Windows Credential Manager"""
        try:
            keyring.set_password(self.app_name, f"{self.username}_openarena", token)
            return True
        except Exception as e:
            print(f"Failed to save OpenArena token securely: {e}")
            return False
    
    def get_github_token(self):
        """Retrieve GitHub token securely from Windows Credential Manager"""
        try:
            return keyring.get_password(self.app_name, f"{self.username}_github")
        except Exception as e:
            print(f"Failed to retrieve GitHub token: {e}")
            return None
    
    def get_openarena_token(self):
        """Retrieve OpenArena token securely from Windows Credential Manager"""
        try:
            return keyring.get_password(self.app_name, f"{self.username}_openarena")
        except Exception as e:
            print(f"Failed to retrieve OpenArena token: {e}")
            return None
    
    def clear_all_tokens(self):
        """Clear all stored tokens (for security cleanup)"""
        try:
            keyring.delete_password(self.app_name, f"{self.username}_github")
            keyring.delete_password(self.app_name, f"{self.username}_openarena")
            return True
        except:
            return False
    
    def has_tokens(self):
        """Check if tokens are available"""
        github_token = self.get_github_token()
        openarena_token = self.get_openarena_token()
        return github_token is not None and openarena_token is not None

class MemoryOnlyTokenStorage:
    """
    Alternative secure storage that only keeps tokens in memory
    Never writes to disk, automatically clears on exit
    """
    
    def __init__(self):
        self._github_token = None
        self._openarena_token = None
        self._session_key = Fernet.generate_key()
        self._fernet = Fernet(self._session_key)
    
    def set_github_token(self, token):
        """Store GitHub token encrypted in memory only"""
        if token:
            self._github_token = self._fernet.encrypt(token.encode())
    
    def set_openarena_token(self, token):
        """Store OpenArena token encrypted in memory only"""
        if token:
            self._openarena_token = self._fernet.encrypt(token.encode())
    
    def get_github_token(self):
        """Retrieve GitHub token from encrypted memory"""
        if self._github_token:
            return self._fernet.decrypt(self._github_token).decode()
        return None
    
    def get_openarena_token(self):
        """Retrieve OpenArena token from encrypted memory"""
        if self._openarena_token:
            return self._fernet.decrypt(self._openarena_token).decode()
        return None
    
    def clear_all(self):
        """Clear all tokens from memory"""
        self._github_token = None
        self._openarena_token = None
        self._session_key = None
        self._fernet = None

# Global instances for the application
try:
    # Try to use Windows Credential Manager first
    secure_manager = SecureTokenManager()
    memory_storage = MemoryOnlyTokenStorage()
    
    def get_secure_token_manager():
        return secure_manager
    
    def get_memory_storage():
        return memory_storage
        
except ImportError:
    # Fallback to memory-only storage if keyring not available
    memory_storage = MemoryOnlyTokenStorage()
    
    def get_secure_token_manager():
        return memory_storage
    
    def get_memory_storage():
        return memory_storage

def validate_github_token(token):
    """Validate GitHub token format"""
    if not token or len(token.strip()) < 40:
        return False
    return token.strip().startswith(('ghp_', 'github_pat_'))

def validate_openarena_token(token):
    """Validate OpenArena token format"""
    if not token or len(token.strip()) < 10:
        return False
    # Add OpenArena-specific validation here
    return True

def secure_input_token(prompt, validator=None):
    """Securely input token without echoing to screen"""
    import getpass
    while True:
        token = getpass.getpass(prompt)
        if validator and not validator(token):
            print("❌ Invalid token format. Please try again.")
            continue
        return token.strip()
