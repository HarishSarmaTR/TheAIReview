# FILE: TokenExtraction.py

"""
Author: Vishal Patel (vishal.patel@thomsonreuters.com)

Prerequisite:
pip install selenium webdriver-manager python-dotenv

"""

import getpass
import json
import os
import threading
import time
from typing import Optional
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode
from dotenv import load_dotenv, set_key

# Add user info storage
USER_INFO_FILE = "user_info.json"

class TRAuthenticator:
    def __init__(self, config=None):
        """
        Initialize the TR Authenticator with configuration
        
        Args:
            config (dict, optional): Configuration dictionary. If None, uses default config.
        """
        # Load environment variables from '.env' file 
        load_dotenv('.env')
        
        self.config = config or {
            "client_id": "tgUVZwXAqZWWByus9QSPi1yNyoN2lflI",
            "redirect_uri": "https://dataandanalytics.int.thomsonreuters.com",
            "auth_url": "https://auth.thomsonreuters.com/authorize",
            "token_url": "https://auth.thomsonreuters.com/oauth/token",
            "api_url": "https://aiopenarena.gcs.int.thomsonreuters.com/v1/user",
            "env_file": ".env", 
            "code_verifier": "vFV--SZvnyxmdapz62lNkKz0Nrbtnd_uO0huZe0A60c",
            "code_challenge": "BWtAOz7YKH24sAlLZAAc-xi_UFJm3hiP1stOedx9U00"
        }
    
    def save_tokens_to_env(self, access_token, refresh_token=None, expires_at=None):
        """
        Save tokens to environment file
        
        Args:
            access_token (str): Access token
            refresh_token (str, optional): Refresh token
            expires_at (float, optional): Token expiration timestamp
        """
        env_file = self.config["env_file"]
        
        set_key(env_file, "TR_ACCESS_TOKEN", access_token)
        
        if refresh_token:
            set_key(env_file, "TR_REFRESH_TOKEN", refresh_token)
        
        if expires_at:
            set_key(env_file, "TR_TOKEN_EXPIRES_AT", str(expires_at))
    
    def get_tokens_from_env(self):
        """
        Get tokens from environment variables
        
        Returns:
            dict: Dictionary containing token information
        """
        return {
            "access_token": os.getenv("TR_ACCESS_TOKEN"),
            "refresh_token": os.getenv("TR_REFRESH_TOKEN"),
            "expires_at": float(os.getenv("TR_TOKEN_EXPIRES_AT", "0"))
        }
    
    def get_auth_code(self):
        """
        Get authorization code using Chrome browser automation
        
        Returns:
            str: Authorization code if successful, None otherwise
        """
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            params = {
                "client_id": self.config["client_id"],
                "scope": "openid profile email",
                "redirect_uri": self.config["redirect_uri"],
                "audience": "49d70a58-9509-48a2-ae12-4f6e00ceb270",
                "connection": "sso-auth",
                "response_type": "code",
                "code_challenge": self.config["code_challenge"],
                "code_challenge_method": "S256"
            }
            
            auth_url = f"{self.config['auth_url']}?{urlencode(params)}"
            
            driver.get(auth_url)
            auth_code = None
            last_url = ""
            start_time = time.time()
            stability_count = 0
            stable_url = None
            
            while time.time() - start_time < 300:
                current_url = driver.current_url
                
                if self.config["redirect_uri"] in current_url and "code=" in current_url:
                    if current_url == last_url:
                        stability_count += 1
                        
                        if stability_count >= 3:
                            match = re.search(r'code=([^&]+)', current_url)
                            if match:
                                auth_code = match.group(1)
                                break
                    else:
                        stability_count = 1
                        stable_url = current_url
                
                last_url = current_url
                time.sleep(1)
            
            if not auth_code and stable_url and "code=" in stable_url:
                match = re.search(r'code=([^&]+)', stable_url)
                if match:
                    auth_code = match.group(1)
            
            if auth_code:
                return auth_code
            else:
                url_input = input("Please paste the URL from your browser: ").strip()
                if "code=" in url_input:
                    match = re.search(r'code=([^&]+)', url_input)
                    if match:
                        return match.group(1)
                return None
            
        finally:
            driver.quit()

    def get_tokens(self, auth_code):
        """
        Exchange authorization code for access tokens
        
        Args:
            auth_code (str): Authorization code from OAuth flow
            
        Returns:
            str: Access token if successful, None otherwise
        """
        token_data = {
            "client_id": self.config["client_id"],
            "code_verifier": self.config["code_verifier"],
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.config["redirect_uri"]
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        
        response = requests.post(self.config["token_url"], data=token_data, headers=headers)
        
        if response.status_code == 200:
            token_response = response.json()
            
            expires_at = time.time() + token_response["expires_in"] - 300
            
            self.save_tokens_to_env(
                access_token=token_response["access_token"],
                refresh_token=token_response.get("refresh_token"),
                expires_at=expires_at
            )
                
            return token_response["access_token"]
        else:
            print(f"Token request failed with status {response.status_code}: {response.text}")
            return None

    def refresh_token(self):
        """
        Refresh the access token using refresh token
        
        Returns:
            str: New access token if successful, None otherwise
        """
        try:
            tokens = self.get_tokens_from_env()
            
            refresh_token = tokens.get("refresh_token")
            if not refresh_token:
                print("No refresh token available")
                return None
                
            token_data = {
                "client_id": self.config["client_id"],
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            response = requests.post(self.config["token_url"], data=token_data)
            
            if response.status_code == 200:
                new_tokens = response.json()
                
                expires_at = time.time() + new_tokens["expires_in"] - 300
                
                self.save_tokens_to_env(
                    access_token=new_tokens["access_token"],
                    refresh_token=new_tokens.get("refresh_token", refresh_token),
                    expires_at=expires_at
                )
                    
                return new_tokens["access_token"]
            else:
                print(f"Token refresh failed with status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None

    def get_access_token(self):
        """
        Get a valid access token (from cache, refresh, or new authentication)
        
        Returns:
            str: Valid access token if successful, None otherwise
        """
        try:
            tokens = self.get_tokens_from_env()
            
            # Check if current token is still valid
            if tokens["access_token"] and time.time() < tokens.get("expires_at", 0):
                return tokens["access_token"]
                
            # Try to refresh token
            token = self.refresh_token()
            if token:
                return token
        except Exception as e:
            print(f"Error getting access token from env: {e}")
            
        # Fall back to full authentication
        auth_code = self.get_auth_code()
        if auth_code:
            return self.get_tokens(auth_code)
            
        return None

    def make_api_request(self, token, endpoint=None):
        """
        Make an authenticated API request
        
        Args:
            token (str): Access token
            endpoint (str, optional): API endpoint. If None, uses default user endpoint
            
        Returns:
            dict: API response if successful, None otherwise
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = endpoint or self.config["api_url"]
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API request failed with status {response.status_code}: {response.text}")
            return None

    def authenticate_and_get_token_with_user_info(self):
        """
        Main method to authenticate and get a valid token with user information
        
        Returns:
            tuple: (token, user_info) where user_info contains user details
        """
        token = self.get_access_token()
        user_info = None
        
        if token:
            # Get user information from API
            result = self.make_api_request(token)
            if result:
                user_info = {
                    'first_name': result.get('first_name', ''),
                    'last_name': result.get('last_name', ''),
                    'email': result.get('email', ''),
                    'display_name': f"{result.get('first_name', '')} {result.get('last_name', '')}".strip(),
                    'username': result.get('email', '').split('@')[0] if result.get('email') else '',
                    'extracted_at': time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save user info to file
                save_user_info_to_file(user_info)
                
                print(f"Authenticated as: {user_info['display_name']}")
                return token, user_info
        
        print("Authentication failed")
        return None, None

def save_user_info_to_file(user_info):
    """Save user information to file"""
    try:
        with open(USER_INFO_FILE, 'w') as f:
            json.dump(user_info, f, indent=2)
        print(f"User info saved to {USER_INFO_FILE}")
        return True
    except Exception as e:
        print(f"Error saving user info: {e}")
        return False

def load_user_info_from_file():
    """Load user information from file"""
    try:
        if os.path.exists(USER_INFO_FILE):
            with open(USER_INFO_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading user info: {e}")
        return None

def get_auth_token_with_user_info(url: str) -> tuple:
    """
    Extract authentication token and user information from OpenArena using TR SSO
    
    Args:
        url: The OpenArena URL to authenticate against
        
    Returns:
        tuple: (token, user_info) where user_info is a dict with user details
    """
    try:
        print("🚀 Starting TR SSO authentication...")
        
        # Initialize TR authenticator
        authenticator = TRAuthenticator()
        
        # Get token and user info
        token, user_info = authenticator.authenticate_and_get_token_with_user_info()
        
        if token and user_info:
            print(f"✅ Successfully authenticated as: {user_info['display_name']}")
            print(f"📧 Email: {user_info['email']}")
            return token, user_info
        else:
            print("❌ Authentication failed")
            return None, None
            
    except Exception as e:
        print(f"Error during TR SSO authentication: {e}")
        return None, None

def get_auth_token(url: str) -> Optional[str]:
    """
    Extract authentication token from OpenArena (backward compatibility)
    
    Args:
        url: The OpenArena URL to authenticate against
        
    Returns:
        The authentication token if found, None otherwise
    """
    token, _ = get_auth_token_with_user_info(url)
    return token

def save_token_to_file(token: str) -> bool:
    """
    Save the authentication token to a file in the user's home directory

    Args:
        token: The authentication token to save

    Returns:
        True if successful, False otherwise
    """
    try:
        username = getpass.getuser()
        # Create a settings directory in the user's home directory
        settings_dir = os.path.join(os.path.expanduser("~"), ".apitoken")
        os.makedirs(settings_dir, exist_ok=True)

        token_file = os.path.join(settings_dir, "auth_token.txt")
        with open(token_file, "w") as f:
            f.write(str(token))

        print(f"Token successfully saved to: {token_file}")
        return True
    except Exception as e:
        print(f"Error saving token to file: {str(e)}")
        return False

def load_token_from_file() -> Optional[str]:
    """
    Load the authentication token from the saved file

    Returns:
        The token if found and valid, None otherwise
    """
    try:
        username = getpass.getuser()
        settings_dir = os.path.join(os.path.expanduser("~"), ".apitoken")
        token_file = os.path.join(settings_dir, "auth_token.txt")

        if not os.path.exists(token_file):
            print("No token file found")
            return None

        with open(token_file, "r") as f:
            token = f.read().strip()

        if not token:
            print("Token file is empty")
            return None

        print("Token loaded successfully from file")
        return token
    except Exception as e:
        print(f"Error loading token from file: {str(e)}")
        return None

def main():
    """
    Main function to demonstrate token extraction with user info
    """
    # OpenArena URL
    url = "https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/11d87e9a-6dcd-4926-80ea-e9fdd07f7e9b"

    print("Starting TR SSO authentication process...")

    # Try to extract token and user info
    token, user_info = get_auth_token_with_user_info(url)

    if token:
        print("✅ Token extraction successful!")
        print(f"👤 User: {user_info['display_name']}")
        print(f"📧 Email: {user_info['email']}")

        # Save token to file
        if save_token_to_file(token):
            print("💾 Token saved successfully!")
        else:
            print("❌ Failed to save token to file")
    else:
        print("❌ Failed to extract token")

    # Demonstrate loading token from file
    print("\n🔄 Testing token loading from file...")
    loaded_token = load_token_from_file()
    if loaded_token:
        print("✅ Token loaded successfully from file")
        print(f"📏 Token length: {len(loaded_token)} characters")
    else:
        print("❌ Failed to load token from file")

    # Demonstrate loading user info from file
    print("\n👤 Testing user info loading from file...")
    loaded_user_info = load_user_info_from_file()
    if loaded_user_info:
        print("✅ User info loaded successfully from file")
        print(f"👤 User: {loaded_user_info['display_name']}")
        print(f"📧 Email: {loaded_user_info['email']}")
    else:
        print("❌ Failed to load user info from file")

if __name__ == "__main__":
    main()