#!/usr/bin/env python3
"""
GitHub Token Extraction Module
Checks for existing GitHub Personal Access Tokens and guides token creation if needed
"""

import time
import json
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

GITHUB_TOKEN_FILE = "github_token.json"

class GitHubTokenExtractor:
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def check_existing_tokens(self):
        """
        Check for existing GitHub tokens in common locations
        Returns: token if found, None otherwise
        """
        print("[SEARCH] Checking for existing GitHub tokens...")
        
        # Check multiple possible locations for tokens
        token_sources = [
            # Check our saved token file
            ('Local token file', lambda: self.load_github_token_from_file()),
            # Check git config
            ('Git config', lambda: self.get_token_from_git_config()),
            # Check environment variables
            ('Environment variables', lambda: self.get_token_from_env()),
            # Check Windows Credential Manager (if on Windows)
            ('Windows Credential Manager', lambda: self.get_token_from_credential_manager()),
        ]
        
        for source_name, get_token_func in token_sources:
            try:
                token = get_token_func()
                if token and len(token.strip()) > 10:
                    print(f"[SUCCESS] Found GitHub token in: {source_name}")
                    # Validate the token
                    if self.validate_github_token(token.strip()):
                        print(f"[SUCCESS] Token from {source_name} is valid!")
                        return token.strip()
                    else:
                        print(f"[ERROR] Token from {source_name} is invalid")
            except Exception as e:
                print(f"[WARNING] Error checking {source_name}: {e}")
        
        print("[ERROR] No valid existing GitHub tokens found")
        return None
    
    def get_token_from_git_config(self):
        """Try to get token from git config"""
        try:
            # Check global git config for GitHub token
            result = subprocess.run(['git', 'config', '--global', 'github.token'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def get_token_from_env(self):
        """Check environment variables for GitHub token"""
        env_vars = ['GITHUB_TOKEN', 'GH_TOKEN', 'GITHUB_ACCESS_TOKEN', 'GITHUB_PAT']
        for var in env_vars:
            token = os.environ.get(var)
            if token and len(token.strip()) > 10:
                return token.strip()
        return None
    
    def get_token_from_credential_manager(self):
        """Try to get token from Windows Credential Manager"""
        try:
            if os.name == 'nt':  # Windows only
                # Try to use cmdkey to check for stored GitHub credentials
                result = subprocess.run(['cmdkey', '/list:github.com'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'github.com' in result.stdout:
                    print("📋 Found GitHub credentials in Windows Credential Manager")
                    print("[INFO] You may have existing GitHub credentials stored")
                    return None  # We can't extract the actual token, but we know it exists
        except Exception:
            pass
        return None
    
    def load_github_token_from_file(self):
        """Load GitHub token from our local file"""
        try:
            if os.path.exists(GITHUB_TOKEN_FILE):
                with open(GITHUB_TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                return data.get('token', '')
        except Exception:
            pass
        return None
    
    def setup_driver(self):
        """Setup Chrome driver with necessary options"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 30)
            return True
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Please ensure Chrome and ChromeDriver are installed and accessible.")
            return False
    
    def extract_github_token_interactive(self):
        """
        Guide user through GitHub token creation process
        Returns: GitHub Personal Access Token
        """
        if not self.setup_driver():
            return None
        
        try:
            print("🚀 Starting GitHub token extraction process...")
            print("📋 Please follow the browser instructions to create a GitHub token...")
            
            # Navigate to GitHub token creation page
            token_url = "https://github.com/settings/tokens/new"
            self.driver.get(token_url)
            
            print("[SUCCESS] Browser opened to GitHub token creation page")
            print("\nPLEASE FOLLOW THESE STEPS:")
            print("1. Log in to GitHub if prompted")
            print("2. Fill in the token details:")
            print("   - Note: 'AI Review Tool Token'")
            print("   - Expiration: Set as needed (recommended: 90 days)")
            print("   - Scopes: Select 'repo' (Full control of private repositories)")
            print("3. Click 'Generate token'")
            print("4. COPY the generated token (it will only be shown once)")
            print("5. Come back to this application and enter the token\n")
            
            # Wait for user to complete the process
            input("Press Enter after you have copied your GitHub token...")
            
            # Ask user to input the token
            token = input("\n🔑 Please paste your GitHub Personal Access Token here: ").strip()
            
            if not token:
                print("[ERROR] No token provided")
                return None
            
            # Validate the token
            if self.validate_github_token(token):
                print("[SUCCESS] Token validated successfully!")
                self.save_github_token(token)
                return token
            else:
                print("[ERROR] Token validation failed. Please check the token and try again.")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error during GitHub token extraction: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def validate_github_token(self, token):
        """Validate GitHub token by making a test API call"""
        try:
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"[SUCCESS] Token validated for user: {user_data.get('login', 'Unknown')}")
                return True
            else:
                print(f"[ERROR] Token validation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error validating token: {e}")
            return False
    
    def save_github_token(self, token):
        """Save GitHub token to file"""
        try:
            token_data = {
                'token': token,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'interactive_extraction'
            }
            
            with open(GITHUB_TOKEN_FILE, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print(f"💾 GitHub token saved to {GITHUB_TOKEN_FILE}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error saving GitHub token: {e}")
            return False

def load_github_token_from_file():
    """Load GitHub token from file"""
    try:
        if os.path.exists(GITHUB_TOKEN_FILE):
            with open(GITHUB_TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            return token_data.get('token')
        return None
    except Exception as e:
        print(f"Error loading GitHub token: {e}")
        return None

def get_github_token_smart():
    """
    Smart GitHub token retrieval that checks existing sources first (GUI-friendly)
    Returns: GitHub token if found, None if needs to be created
    """
    extractor = GitHubTokenExtractor()
    
    # First check for existing tokens
    existing_token = extractor.check_existing_tokens()
    if existing_token:
        return existing_token
    
    # If no existing token found, return None (let GUI handle user choice)
    print("\n🔑 No valid GitHub token found in existing sources.")
    return None

def get_github_token_smart_interactive():
    """
    Interactive version for command-line use
    """
    extractor = GitHubTokenExtractor()
    
    # First check for existing tokens
    existing_token = extractor.check_existing_tokens()
    if existing_token:
        return existing_token
    
    # If no existing token found, ask user if they want to create one
    print("\n🔑 No valid GitHub token found in existing sources.")
    print("Would you like to:")
    print("1. Create a new GitHub token automatically (guided)")
    print("2. Enter an existing token manually") 
    print("3. Skip for now")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting automatic token creation...")
        return extractor.extract_github_token_interactive()
    elif choice == "2":
        token = input("\n🔑 Please paste your GitHub Personal Access Token: ").strip()
        if token and extractor.validate_github_token(token):
            extractor.save_github_token(token)
            return token
        else:
            print("[ERROR] Invalid token provided")
            return None
    else:
        print("[SKIP] Skipping GitHub token setup")
        return None

def get_github_token_interactive():
    """Main function to get GitHub token interactively (legacy)"""
    extractor = GitHubTokenExtractor()
    return extractor.extract_github_token_interactive()

def create_github_token_instructions():
    """Return detailed instructions for manual token creation"""
    return """
🔑 GITHUB PERSONAL ACCESS TOKEN CREATION GUIDE

OPTION 1: Automatic Extraction (Recommended)
- Click the 'Get GitHub Token' button in the application
- Follow the browser prompts

OPTION 2: Manual Creation
1. Go to: https://github.com/settings/tokens/new
2. Sign in to your GitHub account
3. Fill in the form:
   - Note: "AI Review Tool Token"
   - Expiration: 90 days (or as needed)
   - Scopes: Check "repo" (Full control of private repositories)
4. Click "Generate token"
5. COPY the token immediately (you won't see it again!)
6. Paste it into the GitHub Token field in this application

[WARNING] IMPORTANT SECURITY NOTES:
- Keep your token secure and never share it
- The token grants access to your repositories
- You can revoke it anytime at: https://github.com/settings/tokens
- This application stores the token locally and encrypted

[REQUIRED] PERMISSIONS:
- repo: Full control of private repositories
  (This allows the tool to read PR content and post review comments)

Need help? Contact your system administrator.
"""

if __name__ == "__main__":
    print("GitHub Token Extractor")
    print("=" * 50)
    token = get_github_token_interactive()
    if token:
        print(f"[SUCCESS] Successfully extracted GitHub token!")
    else:
        print("[ERROR] Failed to extract GitHub token")
