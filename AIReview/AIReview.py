#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Button
import customtkinter # Added customtkinter
import sys
import os
import re
import requests
import webbrowser
from github import Github
import fnmatch
from cryptography.fernet import Fernet
import time
import json
from tkinter import ttk
from PIL import Image, ImageTk  # For handling the background image
import threading
import json
from datetime import datetime, timedelta
import hashlib
import getpass

# Add this import near the top with other imports
try:
    from TokenExtraction import get_auth_token, save_token_to_file, load_token_from_file, get_auth_token_with_user_info, load_user_info_from_file
    HAS_TOKEN_EXTRACTION = True
except ImportError:
    HAS_TOKEN_EXTRACTION = False
    print("TokenExtraction module not found. Manual token entry required.")

def get_authenticated_user_info():
    """Get authenticated user information from SSO and system"""
    user_info = {
        'system_user': getpass.getuser(),  # System username
        'sso_user': None,
        'display_name': None,
        'email': None,
        'first_name': None,
        'last_name': None
    }
    
    try:
        # Try to get SSO user info from TokenExtraction
        if HAS_TOKEN_EXTRACTION:
            sso_info = load_user_info_from_file()
            
            if sso_info:
                user_info['sso_user'] = sso_info.get('username')
                user_info['display_name'] = sso_info.get('display_name')
                user_info['email'] = sso_info.get('email')
                user_info['first_name'] = sso_info.get('first_name')
                user_info['last_name'] = sso_info.get('last_name')
                
                log_activity(f"✅ SSO user info loaded: {user_info['display_name']}")
            else:
                log_activity("ℹ️ No SSO user info found, using system username")
                user_info['display_name'] = user_info['system_user']
        else:
            # Fallback to system username
            user_info['display_name'] = user_info['system_user']
            log_activity(f"ℹ️ Using system username: {user_info['display_name']}")
            
    except Exception as e:
        log_activity(f"⚠️ Could not get SSO user info: {e}")
        user_info['display_name'] = user_info['system_user']
    
    return user_info

def setup_welcome_section():
    """Setup welcome section with user greeting"""
    global welcome_section_frame
    
    # Create welcome section frame
    welcome_section_frame = customtkinter.CTkFrame(left_frame)
    welcome_section_frame.grid(row=0, column=0, padx=2, pady=(10,5), sticky="ew")
    welcome_section_frame.grid_columnconfigure(0, weight=1)  # Welcome message takes most space
    welcome_section_frame.grid_columnconfigure(1, weight=0)  # Dark mode button stays right

    # Welcome message label
    root.welcome_label = customtkinter.CTkLabel(
        welcome_section_frame, 
        text="Welcome! ☺️", 
        font=customtkinter.CTkFont(size=12, weight="bold"),
        text_color="#DC8400"  # Green color for welcome message
    )
    root.welcome_label.grid(row=0, column=0, pady=10, padx=15, sticky="w")
    
    # Create the Dark Mode button in the same frame as welcome message
    global mode_switch
    mode_switch = customtkinter.CTkButton(
        welcome_section_frame, 
        text="Dark Mode" if customtkinter.get_appearance_mode() == "Dark" else "Light Mode",
        command=change_appearance_mode_event,
        width=120,
        height=28
    )
    mode_switch.grid(row=0, column=1, padx=5, sticky="e")  # Place on the right side
    
    # Update welcome message with new user info
    update_welcome_message()

def update_welcome_message():
    """Update the welcome message with authenticated user info"""
    try:
        user_info = get_authenticated_user_info()
        
        # Create a more informative welcome message
        if user_info['first_name']:
            welcome_text = f"Welcome {user_info['first_name']}! 👋"
        elif user_info['display_name']:
            welcome_text = f"Welcome {user_info['display_name']}! 👋"
        else:
            welcome_text = f"Welcome {user_info['system_user']}! 👋"
            
        # Update the welcome label if it exists
        if hasattr(root, 'welcome_label') and root.welcome_label:
            root.welcome_label.configure(text=welcome_text)
            log_activity(f"[UI] Welcome message updated: {welcome_text}")
        
        # Log user session info
        if user_info['email']:
            log_activity(f"📋 User session: {user_info['email']}")
        else:
            log_activity(f"📋 User session: {user_info['system_user']} (system)")
            
        return user_info
        
    except Exception as e:
        log_activity(f"❌ Error updating welcome message: {e}")
        return None

def extract_openarena_token_with_user_info():
    """Extract OpenArena token and user info using TR SSO authentication"""
    url = "https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/11d87e9a-6dcd-4926-80ea-e9fdd07f7e9b"
    
    # Disable button during extraction
    extract_token_button.configure(state="disabled", text="Extracting...")
    root.update_idletasks()
    
    try:
        log_activity("🚀 Starting TR SSO authentication with user info...")
        log_activity("📋 Please complete SSO authentication when browser opens...")
        
        # Run token extraction in a separate thread
        def extraction_thread():
            try:
                # Use the enhanced function that gets both token and user info
                token, user_info = get_auth_token_with_user_info(url)
                
                # Update UI in main thread
                def update_ui():
                    if token:
                        openarena_token_entry.delete(0, tk.END)
                        openarena_token_entry.insert(0, token)
                        log_activity("✅ OpenArena token extracted successfully!")
                        
                        # Update welcome message with new user info
                        update_welcome_message()
                        
                        if user_info:
                            if user_info.get('display_name'):
                                log_activity(f"👤 User authenticated: {user_info['display_name']}")
                            if user_info.get('email'):
                                log_activity(f"📧 Email: {user_info['email']}")
                            if user_info.get('first_name'):
                                log_activity(f"👋 Welcome {user_info['first_name']}!")
                        
                        success_msg = f"Token extracted successfully!"
                        if user_info and user_info.get('display_name'):
                            success_msg += f"\nAuthenticated as: {user_info['display_name']}"
                        if user_info and user_info.get('email'):
                            success_msg += f"\nEmail: {user_info['email']}"
                            
                        messagebox.showinfo("Success", success_msg)
                        
                        # Save token
                        if save_token_to_file(token):
                            log_activity("💾 Token saved to file for future use")
                    else:
                        log_activity("❌ Failed to extract OpenArena token")
                        messagebox.showerror("Error", "Failed to extract token. Please try manual entry.")
                    
                    # Re-enable button
                    extract_token_button.configure(state="normal", text="Get-Token")
                
                root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    log_activity(f"❌ Error during extraction: {e}")
                    messagebox.showerror("Error", f"Extraction failed: {e}")
                    extract_token_button.configure(state="normal", text="Get-Token")
                
                root.after(0, show_error)
        
        # Start extraction in background thread
        thread = threading.Thread(target=extraction_thread, daemon=True)
        thread.start()
        
    except Exception as e:
        log_activity(f"❌ Error starting extraction: {e}")
        messagebox.showerror("Error", f"Failed to start extraction: {e}")
        extract_token_button.configure(state="normal", text="Get-Token")

def setup_enhanced_header():
    """Setup enhanced header with welcome message"""
    

# Enhanced startup sequence
def enhanced_startup_sequence():
    """Enhanced startup sequence with user authentication"""
    try:
        # Migrate token file if needed
        migrate_token_file()
        
        # Load tokens
        load_tokens()
        load_openarena_token_on_startup()
        
        # Setup welcome section
        setup_welcome_section()
        
        # Update welcome message (will load SSO user info if available)
        root.after(1000, update_welcome_message)
        
    except Exception as e:
        print(f"Error during enhanced startup: {e}")
        messagebox.showerror("Startup Error", f"Error during startup: {str(e)}")

def calculate_claude_cost(prompt_tokens, completion_tokens):
    """
    Calculate the cost for Claude 4 Sonnet based on token usage.
    
    Args:
        prompt_tokens: Number of tokens in the prompt/input
        completion_tokens: Number of tokens in the completion/output
    
    Returns:
        Cost in USD
    
    Pricing:
    - Input: $0.003 per 1,000 tokens (up to 200k)
    - Output: $0.015 per 1,000 tokens (up to 64k)
    """
    input_cost = (prompt_tokens / 1000) * 0.003
    output_cost = (completion_tokens / 1000) * 0.015
    return input_cost + output_cost

# Custom modules
try:
    from api_handler import review_code_with_ai
    HAS_API_HANDLER = True
except ImportError:
    HAS_API_HANDLER = False
    print("API handler module not found. Using built-in review function.")

# Global variables to store tokens during the session
github_token = None
openarena_token = None
# Add a global variable for the activity log textbox
activity_log_textbox = None
progress_bar = None
progress_percentage_label = None  # Add progress percentage label
time_taken_label = None
cost_label = None
last_pr_url = None  # Store the last reviewed PR URL for the View PR button
view_pr_button = None
repo_combobox = None  # Combobox for repository selection

# Global variables for AI settings UI elements
temperature_entry = None
top_p_entry = None
max_tokens_entry = None
system_prompt_textbox = None
workflow_entry = None
filter_comments_var = None


TOKEN_FILE = "tokens.txt"

# Define the version as a static date-based version
APP_VERSION = "2.0.6" # Incremented patch version for UI enhancements
                      # Versioning format: Major.Minor.Patch
                      # Major: Significant changes or new features
                      # Minor: Backward-compatible changes or improvements
                      # Patch: Bug fixes or minor changes
                      
# File to store recently used repositories
RECENT_REPOS_FILE = "recent_repos.json"
# Maximum number of repositories to remember
MAX_RECENT_REPOS = 10
                        # Patch: Bug fixes or minor changes


# Add these new constants
GITHUB_DIST_URL = "https://api.github.com/repos/HarishSarmaTR/TheAIReview/contents/dist"
EXE_DOWNLOAD_URL_TEMPLATE = "https://raw.githubusercontent.com/HarishSarmaTR/TheAIReview/main/dist/{filename}"
UPDATE_CHECK_FILE = "last_update_check.json"
UPDATE_NOTIFICATION_FILE = "update_notifications.json"

def open_openarena_link(event):
    """Open the OpenArena link in the default web browser."""
    webbrowser.open("https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/8556ba87-acf8-4049-98a3-fc62a300656c")

def show_info(info_text):
    """Display information about a section."""
    messagebox.showinfo("Information", info_text)

def create_round_info_button(parent, row, column, info_text):
    """Helper function to create a round info button using a Canvas."""
    canvas = tk.Canvas(parent, width=20, height=20, bg="#f0f0f0", highlightthickness=0) # Keep tk.Canvas for now
    canvas.create_oval(2, 2, 18, 18, fill="#0000FF")
    canvas.create_text(10, 10, text="i", fill="white", font=("Helvetica", 8, "bold"))
    canvas.grid(row=row, column=column, padx=5)
    canvas.bind("<Button-1>", lambda e: show_info(info_text))

# Generate or load encryption key
KEY_FILE = "encryption.key"

def generate_key():
    """Generate and save a key for encryption."""
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    """Load the encryption key from the file."""
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

encryption_key = load_key()
cipher = Fernet(encryption_key)

def encrypt_token(token):
    """Encrypt a token."""
    return cipher.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    """Decrypt a token."""
    return cipher.decrypt(encrypted_token.encode()).decode()

def load_tokens():
    """Load GitHub and OpenArena tokens from a file."""
    global github_token, openarena_token
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as file:
                # First try to read as separate lines
                tokens = file.readlines()
                
                # If we don't have enough lines, try reading the whole file and splitting on literal '\n'
                if len(tokens) < 2:
                    file.seek(0)  # Go back to start of file
                    content = file.read()
                    if '\\n' in content:  # Check for literal '\n' characters
                        print("Found literal \\n in token file. Splitting on these.")
                        tokens = content.split('\\n')
                
                if len(tokens) >= 2:
                    try:
                        github_token = decrypt_token(tokens[0].strip())
                        openarena_token = decrypt_token(tokens[1].strip())
                        github_token_entry.insert(0, github_token)
                        openarena_token_entry.insert(0, openarena_token)
                        print("Tokens loaded successfully.")
                    except Exception as e:
                        print(f"Error decrypting tokens: {str(e)}")
                        messagebox.showerror("Token Error", f"Could not decrypt tokens. The token file may be corrupted or was created with a different encryption key.\nError: {str(e)}")
                        # Handle the error by backing up the problematic token file
                        backup_file = f"{TOKEN_FILE}.bak"
                        if os.path.exists(backup_file):
                            os.remove(backup_file)
                        os.rename(TOKEN_FILE, backup_file)
                        print(f"Renamed corrupted token file to {backup_file}")
                else:
                    print("Token file does not contain enough tokens.")
        except Exception as e:
            print(f"Error loading tokens: {str(e)}")
            messagebox.showerror("Token Error", f"Could not load tokens: {str(e)}")

def load_openarena_token_on_startup():
    """Try to load OpenArena token from TokenExtraction module on startup"""
    if HAS_TOKEN_EXTRACTION:
        try:
            saved_token = load_token_from_file()
            if saved_token and not openarena_token_entry.get():
                openarena_token_entry.insert(0, saved_token)
                log_activity("📁 OpenArena token loaded from TokenExtraction file")
        except Exception as e:
            print(f"Could not load OpenArena token from TokenExtraction: {e}")

def save_tokens():
    """Save tokens to a file."""
    global github_token, openarena_token
    github_token = github_token_entry.get()
    openarena_token = openarena_token_entry.get()
    with open(TOKEN_FILE, 'w') as file:
        file.write(f"{encrypt_token(github_token)}\n{encrypt_token(openarena_token)}\n")
    # Use tkinter messagebox as customtkinter doesn't have a direct equivalent integrated here
    messagebox.showinfo("Success", "Tokens saved successfully!")

def clear_tokens():
    """Clear the token entries."""
    github_token_entry.delete(0, tk.END)
    openarena_token_entry.delete(0, tk.END)

def migrate_token_file():
    """Migrate token file from old format to new format if needed."""
    if not os.path.exists(TOKEN_FILE):
        return False
        
    try:
        # Read the file and check if it contains literal \n
        with open(TOKEN_FILE, 'r') as file:
            content = file.read()
            
        if '\\n' in content:
            # This is the old format with literal \n
            print("Migrating token file from old format...")
            tokens = content.split('\\n')
            if len(tokens) >= 2:
                # Write back in new format
                with open(TOKEN_FILE, 'w') as file:
                    file.write(f"{tokens[0]}\n{tokens[1]}\n")
                print("Token file successfully migrated.")
                return True
    except Exception as e:
        print(f"Error migrating token file: {e}")
        
    return False

def load_recent_repos():
    """Load list of recently used repository names."""
    try:
        if os.path.exists(RECENT_REPOS_FILE):
            with open(RECENT_REPOS_FILE, 'r') as file:
                return json.load(file)
        return []
    except Exception as e:
        print(f"Error loading recent repositories: {e}")
        return []
        
def save_recent_repos(repos):
    """Save list of recently used repository names."""
    try:
        # Ensure we don't exceed the max number of repos
        repos = repos[:MAX_RECENT_REPOS]
        
        with open(RECENT_REPOS_FILE, 'w') as file:
            json.dump(repos, file)
    except Exception as e:
        print(f"Error saving recent repositories: {e}")
        
def add_recent_repo(repo_name):
    """Add a repository to the recently used list."""
    if not repo_name or '/' not in repo_name:
        return
        
    repos = load_recent_repos()
    
    # Remove this repo if it already exists (to move it to the top)
    if repo_name in repos:
        repos.remove(repo_name)
        
    # Add the repo to the front of the list
    repos.insert(0, repo_name)
    
    # Save the updated list
    save_recent_repos(repos)
    
    # Update the dropdown if it exists
    if repo_combobox and hasattr(repo_combobox, 'configure'):
        try:
            current_values = repo_combobox['values'] if hasattr(repo_combobox, 'values') else []
            if repo_name not in current_values:
                repo_combobox.configure(values=repos)
        except Exception as e:
            print(f"Error updating repository combobox: {e}")

def run_code_review():
    global github_token, openarena_token, last_pr_url
    github_token = github_token_entry.get()
    openarena_token = openarena_token_entry.get()
    repo_name = repo_name_entry.get()
    pr_number = pr_number_entry.get()
    post_comments = post_comments_var.get()  # Get checkbox state
    
    if not (github_token and openarena_token and repo_name and pr_number):
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return
    
    # Validate OpenArena token format and show specific error if invalid
    if not openarena_token or len(openarena_token.strip()) < 10:
        messagebox.showerror(
            "OpenArena Token Error", 
            "Invalid OpenArena token detected!\n\n"
            "Please ensure you have entered a valid OpenArena API token.\n"
            "The token should be obtained from the OpenArena platform.\n\n"
            "If you don't have a token, please visit the OpenArena platform link above to get one."
        )
        return
    
    # Test OpenArena token by making a simple API call
    try:
        test_headers = {
            'Authorization': f'Bearer {openarena_token}',
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'AICodeReviewTool',
            'Connection': 'keep-alive'  
        }
        test_payload = {
            "query": "test",
            "workflow_id": "7c41c3ab-c214-4394-ba38-9da289975d85",
            "is_persistence_allowed": False,
            "modelparams": {
                "anthropic_direct.claude-v4-sonnet": {
                    "temperature": "0.7",
                    "max_tokens": "10"
                }
            }
        }
        
        log_activity("Validating OpenArena token...")
        test_response = requests.post(
            "https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference",
            headers=test_headers, 
            json=test_payload, 
            timeout=10
        )
        
        if test_response.status_code == 401:
            messagebox.showerror(
                "OpenArena Token Authentication Failed", 
                "The OpenArena token you provided is invalid or expired.\n\n"
                "Please check your token and try again.\n"
                "You can get a valid token from the OpenArena platform."
            )
            return
        elif test_response.status_code >= 400:
            log_activity(f"[INFO] OpenArena API test returned status {test_response.status_code}, but proceeding with review...")
        else:
            log_activity("[SUCCESS] OpenArena token validation successful")
            
    except Exception as e:
        log_activity(f"[WARNING] Could not validate OpenArena token (network issue?): {e}")
        # Don't stop the process for network issues, just warn
        messagebox.showwarning(
            "Token Validation Warning", 
            "Could not validate OpenArena token due to network issues.\n\n"
            "Proceeding with code review. If the token is invalid, the review will fail."
        )
        
    log_activity(f"Post comments to PR: {'Yes' if post_comments else 'No - comments will be shown only in log'}")
    
    # Log current AI settings
    if 'temperature_entry' in globals() and temperature_entry:
        temp = temperature_entry.get() or "0.7"
        top_p = top_p_entry.get() or "1.0"
        max_tok = max_tokens_entry.get() or "16384"
        workflow = workflow_entry.get() or "default"
        filtering = ai_settings.get("filter_comments", True)
        log_activity(f"[CONFIG] AI Settings: Temp={temp}, Top-P={top_p}, Max-Tokens={max_tok}, Filtering={'On' if filtering else 'Off'}")
    
    # Update status via activity log and status label
    log_activity("Starting code review...")
    status_message.set("Running code review...")
    if progress_bar:
        progress_bar.set(0)
        if progress_percentage_label:
            progress_percentage_label.configure(text="🚀 Initializing...")
    if time_taken_label:
        time_taken_label.configure(text="-")
    if cost_label:
        cost_label.configure(text="-")
    if view_pr_button:
        view_pr_button.configure(state="disabled")
    if view_report_button:
        view_report_button.configure(state="disabled")
    root.update_idletasks()
    start_time = time.time()
    result = main(repo_name, pr_number, post_comments)
    
    # Unpack the results with proper handling for older versions
    if len(result) >= 6:
        total_files, reviewed_files_count, all_posted_comments_count, pr_url, total_cost, total_tokens = result
    else:
        total_files, reviewed_files_count, all_posted_comments_count, pr_url = result[:4]
        total_cost = 0.0
        total_tokens = 0
        
    end_time = time.time()
    duration = end_time - start_time
    
    if time_taken_label:
        # Format time as mm:ss min for clarity
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        time_taken_label.configure(text=f"{minutes:02d}:{seconds:02d} min")
    if cost_label:
        if total_cost > 0:
            cost_label.configure(text=f"Est. Cost: ${total_cost:.4f} ({total_tokens} tokens)")
        else:
            # Even if API reports 0 cost, provide an estimate based on response length
            if all_posted_comments_count > 0:
                # Rough estimate: $0.01 per comment as a minimum
                min_cost = all_posted_comments_count * 0.01
                cost_label.configure(text=f"Min. Est. Cost: ${min_cost:.4f}")
            else:
                cost_label.configure(text=f"Est. Cost: ${total_cost:.4f}")
    review_button.configure(state="normal")
    
    if reviewed_files_count > 0:
        log_activity(f"Code review completed. Reviewed {reviewed_files_count}/{total_files} files. Posted {all_posted_comments_count} comments.")
        status_message.set("Completed ✅")
        messagebox.showinfo("Success", f"Code review completed successfully! Reviewed {reviewed_files_count}/{total_files} files.")
        last_pr_url = pr_url
        
        # Save the repository to the recently used list
        add_recent_repo(repo_name)
        if view_pr_button:
            view_pr_button.configure(state="normal")
    elif total_files == 0:
        log_activity("No files found in the PR to review.")
        status_message.set("No files to review")
        messagebox.showinfo("Info", "No files found in the PR to review.")
        last_pr_url = None
        if view_pr_button:
            view_pr_button.configure(state="disabled")
    else:
        log_activity("Code review finished. No comments were posted or an error occurred.")
        status_message.set("Finished (No comments/Error)")
        messagebox.showwarning("Warning", "Code review finished, but no comments were posted or an error occurred during the process.")
        last_pr_url = pr_url
        if view_pr_button:
            view_pr_button.configure(state="normal" if pr_url else "disabled")


# Function to log messages to the activity log and print to console
def log_activity(message):
    # Properly format message for printing (replace literal \n with newlines)
    formatted_message = message.replace('\\n', '\n')
    print(formatted_message) # Keep console logging with proper newlines
    
    if activity_log_textbox:
        # Add timestamp with date to the message for GUI display
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamped_message = f"[{timestamp}] {message}"
        # For the GUI, we add a proper newline character
        activity_log_textbox.insert(tk.END, timestamped_message + "\n")
        activity_log_textbox.see(tk.END) # Scroll to the end
    root.update_idletasks()


# Extract exact modified lines from the patch
def get_modified_lines_from_patch(patch_text):
    """
    Parse a git diff patch to extract added and removed lines.
    For new files (starting with @@ -0,0), all lines are considered as added.
    For modified files, both added and removed lines are tracked.
    
    Returns a dictionary where:
    - Keys > 0 are added/modified lines (line number in new file)
    - Keys < 0 are removed lines (-line number in old file)
    - Values are the content of those lines
    """
    modified_lines = {}
    current_new_line = None
    is_new_file = False
    
    if not patch_text: # Added safety check
        return modified_lines

    # Handle newline escapes in patch text
    cleaned_patch = patch_text.replace('\\n', '\n')
    
    # Check if this is a new file
    if "@@ -0,0 " in cleaned_patch:
        is_new_file = True
        
    for line in cleaned_patch.split('\n'):
        # Match the hunk header to get line numbers
        hunk_match = re.match(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
        if hunk_match:
            old_line = int(hunk_match.group(1))
            current_new_line = int(hunk_match.group(2))
            # Detect if this is a new file based on hunk header
            if old_line == 0:
                is_new_file = True
            continue

        if current_new_line is None:
            continue

        # For new files, all lines with '+' are considered as added
        if is_new_file and line.startswith('+') and not line.startswith('+++'):
            modified_lines[current_new_line] = line[1:].strip()
            current_new_line += 1
        # For existing files, process added/modified and removed lines
        elif not is_new_file:
            if line.startswith('+') and not line.startswith('+++'):
                # Added/modified line
                modified_lines[current_new_line] = line[1:].strip()
                current_new_line += 1
            elif line.startswith('-') and not line.startswith('---'):
                # Removed line (use negative line number to differentiate)
                modified_lines[-current_new_line] = line[1:].strip()
            # Context lines just increment the line counter
            elif not line.startswith(('---', '+++', 'diff', 'index', '@@')):
                if line.strip() != "":
                    current_new_line += 1
            
    return modified_lines

# Send modified lines to AI for review
def filter_review_comments(comments, filename):
    """
    Filter review comments based on specified rules.
    
    Rules:
    1. Skip comments about CCMMDDYY date format (8-digit dates)
    2. Skip comments about date arithmetic or Base_Date calculations
    3. Skip comments about date constants and thresholds
    """
    if not comments:
        return comments
    
    filtered_comments = []
    
    # Keywords that indicate date-related comments to filter out
    date_keywords = [
        'date format', 'date calculation', 'ccmmddyy', 'yyyymmdd', 
        'base_date', 'base date', 'date arithmetic', '20123100',
        'invalid date', 'malformed date', 'date value', 'date functions',
        'gadateannual', 'gadateext', 'dateext', 'datethresholds',
        'iga::thresholds', 'extension due date', 'year-end calculations'
    ]
    
    for comment in comments:
        comment_lower = comment.lower()
        
        # Check if this comment is about dates (which we want to filter out)
        is_date_comment = any(keyword in comment_lower for keyword in date_keywords)
        
        # Also check for 8-digit number patterns that might be dates
        import re
        has_8_digit_pattern = bool(re.search(r'\b\d{8}\b', comment))
        
        if is_date_comment or has_8_digit_pattern:
            log_activity(f"[FILTER] Filtered out date-related comment: {comment[:100]}...")
            continue
            
        filtered_comments.append(comment)
    
    return filtered_comments

# Enhancement logic is now directly included in the AI query
# No separate function needed for enhancing review comments

def review_code(diff, openarena_token):
    """Send code to AI for review through the OpenArena API"""
    try:
        # Try importing the external modules first
        try:
            # Try importing the api_handler module
            from api_handler import review_code_with_ai
            log_activity("Using api_handler for code review")
            return review_code_with_ai(diff, openarena_token, log_activity)
        except ImportError:
            # If api_handler fails, try simple_reviewer
            try:
                from simple_reviewer import simple_review_code
                log_activity("Using simple_reviewer for code review")
                return simple_review_code(diff, openarena_token, log_activity)
            except ImportError:
                # If both imports fail, use the basic implementation
                log_activity("[WARNING] External reviewers not available. Using basic review function.")
                pass
                
        # Basic fallback implementation
        import requests
        import time
        
        # Basic API request with Claude 4 Sonnet parameters
        headers = {
            'Authorization': f'Bearer {openarena_token}',
            'Content-Type': 'application/json'
        }        # Full payload with detailed prompt        
        
        # Get AI settings from global configuration
        try:
            # Use global AI settings with validation
            workflow_id = ai_settings.get("workflow_id", "7c41c3ab-c214-4394-ba38-9da289975d85")
            
            # Validate and get temperature
            temp_str = ai_settings.get("temperature", "0.7")
            try:
                temp_float = float(temp_str)
                if 0.0 <= temp_float <= 2.0:
                    temperature = temp_str
                else:
                    log_activity(f"[ERROR] Invalid temperature {temp_str}, using default 0.7")
                    temperature = "0.7"
            except ValueError:
                log_activity(f"[ERROR] Invalid temperature format {temp_str}, using default 0.7")
                temperature = "0.7"
            
            # Validate and get top_p
            top_p_str = ai_settings.get("top_p", "1.0")
            try:
                top_p_float = float(top_p_str)
                if 0.0 <= top_p_float <= 1.0:
                    top_p = top_p_str
                else:
                    log_activity(f"[ERROR] Invalid top_p {top_p_str}, using default 1.0")
                    top_p = "1.0"
            except ValueError:
                log_activity(f"[ERROR] Invalid top_p format {top_p_str}, using default 1.0")
                top_p = "1.0"
            
            # Validate and get max_tokens
            max_tokens_str = ai_settings.get("max_tokens", "16384")
            try:
                max_tokens_int = int(max_tokens_str)
                if 1 <= max_tokens_int <= 200000:
                    max_tokens = max_tokens_str
                else:
                    log_activity(f"[ERROR] Invalid max_tokens {max_tokens_str}, using default 16384")
                    max_tokens = "16384"
            except ValueError:
                log_activity(f"[ERROR] Invalid max_tokens format {max_tokens_str}, using default 16384")
                max_tokens = "16384"
            
            # Get system prompt from global settings
            system_prompt = ai_settings.get("system_prompt", default_system_prompt)
            if not system_prompt.strip():  # If empty, use default
                system_prompt = default_system_prompt
            
            # Log the configuration being used
            log_activity(f"[CONFIG] Using AI configuration: Workflow={workflow_id[:12]}..., Temp={temperature}, TopP={top_p}, MaxTokens={max_tokens}")
            
        except Exception as e:
            log_activity(f"[ERROR] Error getting AI settings, using defaults: {e}")
            workflow_id = "7c41c3ab-c214-4394-ba38-9da289975d85"
            temperature = "0.7"
            top_p = "1.0"
            max_tokens = "16384"
            system_prompt = default_system_prompt
        
        payload = {
            "query": f"Review the following code changes and provide feedback only for actual issues:\n{diff}",
            "workflow_id": workflow_id,
            "is_persistence_allowed": False,
            "modelparams": {
                "anthropic_direct.claude-v4-sonnet": {
                    "temperature": temperature,
                    "top_p": top_p, 
                    "max_tokens": max_tokens,
                    "system_prompt": system_prompt
                }
            }
        }
        
        # Log payload preview for transparency (excluding the full system prompt to keep log clean)
        log_activity(f"[API] API Payload: Workflow={workflow_id}, Temp={temperature}, TopP={top_p}, MaxTokens={max_tokens}")
        log_activity(f"[API] System Prompt: {system_prompt[:100]}..." if len(system_prompt) > 100 else f"[API] System Prompt: {system_prompt}")
        
        # Add retry logic for API timeouts
        max_retries = 2
        retry_count = 0
        retry_delay = 5  # seconds
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    log_activity(f"Retry attempt {retry_count}/{max_retries} for OpenArena API call...")
                    
                # Make the API request
                log_activity("Sending request to OpenArena API (Claude 4 Sonnet)...")
                response = requests.post(
                    "https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference",
                    headers=headers, 
                    json=payload, 
                    timeout=60
                )
                
                log_activity(f"OpenArena API Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    ai_response = response.json()
                      # Try to get the answer from multiple possible model names
                    model_answer = ai_response.get('result', {}).get('answer', {})
                    feedback = (
                        model_answer.get('anthropic_direct.claude-v4-sonnet', '') or
                        model_answer.get('openai_gpt-4o', '') or
                        model_answer.get('vertexai_gemini-2.5-pro', '') or
                        model_answer.get('vertexai_palm-2', '')
                    )
                    
                    if not feedback:
                        log_activity("[WARNING] Received empty feedback despite 200 status")
                        if retry_count < max_retries:
                            retry_count += 1
                            time.sleep(retry_delay)
                            continue
                        else:
                            log_activity("[WARNING] Empty response received after all retries.")
                            return "Line 1: No specific issues detected in the code changes.", 0.0, 0
                    
                    log_activity("[SUCCESS] AI Code Review Feedback received.")
                      # Extract cost information from the response
                    cost_info = ai_response.get('result', {}).get('cost', {})
                    token_usage = cost_info.get('token_usage', {})
                    prompt_tokens = token_usage.get('prompt_tokens', 0)
                    completion_tokens = token_usage.get('completion_tokens', 0)
                    total_tokens = token_usage.get('total_tokens', 0)
                    
                    # Calculate cost using our pricing function for Claude 4 Sonnet
                    if prompt_tokens == 0 and completion_tokens == 0 and total_tokens > 0:
                        # If we only have total tokens but not the split, estimate prompt/completion ratio
                        # Assuming typical ratio of 70% prompt, 30% completion
                        prompt_tokens = int(total_tokens * 0.7)
                        completion_tokens = total_tokens - prompt_tokens
                    
                    cost_usd = calculate_claude_cost(prompt_tokens, completion_tokens)
                    
                    log_activity(f"[TOKENS] Token usage: {total_tokens} tokens (Prompt: {prompt_tokens}, Completion: {completion_tokens})")
                    log_activity(f"[COST] Est. cost: ${cost_usd:.5f} (Input: ${(prompt_tokens/1000)*0.003:.5f}, Output: ${(completion_tokens/1000)*0.015:.5f})")
                    return feedback, cost_usd, total_tokens
                
                elif response.status_code in [504, 408, 502, 503]:  # Timeout and server errors
                    if retry_count < max_retries:
                        log_activity(f"[ERROR] OpenArena API timeout/error: {response.status_code}, {response.text}")
                        log_activity(f"Waiting {retry_delay} seconds before retry...")
                        retry_count += 1
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        log_activity(f"[ERROR] Maximum retries reached. Could not get response from OpenArena API.")
                        return f"API Error ({response.status_code}): Could not process review after {max_retries} retries.", 0.0, 0
                        
                else:
                    log_activity(f"[ERROR] OpenArena API Error: {response.status_code}, {response.text}")
                    return f"API Error ({response.status_code}): Could not process review.", 0.0, 0
                    
            except Exception as e:
                if retry_count < max_retries:
                    log_activity(f"[RETRY] API call failed with error: {e}. Retrying in {retry_delay} seconds...")
                    retry_count += 1
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    log_activity(f"[ERROR] Failed to review code after {max_retries} retries: {e}")
                    return f"Error: {str(e)}", 0.0, 0
        
        return "Error: Failed to get a response from the API after multiple attempts", 0.0, 0
    
    except Exception as e:
        log_activity(f"[ERROR] Unexpected error in review_code function: {str(e)}")
        return f"Error: {str(e)}", 0.0, 0
    
    return ""  # Fallback return if all retries fail

# Add this function to categorize comments by severity
def determine_severity(comment_content):
    """Determine severity level based on comment content"""
    content_lower = comment_content.lower()
    
    # Critical issues - severe confirmed security or stability issues
    if any(word in content_lower for word in [
        'critical security vulnerability', 'remote code execution', 'sql injection',
        'authenticated bypass', 'privilege escalation', 'data breach',
        'confirmed memory leak', 'proven buffer overflow', 'guaranteed crash'
    ]):
        return "🔴 Critical"
    
    # High priority issues
    elif any(word in content_lower for word in [
        'logic error', 'incorrect', 'bug', 'failure', 'exception', 'error',
        'undefined behavior', 'infinite loop', 'resource leak', 'null pointer dereference',
        'segmentation fault', 'deadlock', 'race condition', 'buffer overflow',
        'memory leak', 'potential security', 'potential vulnerability'
    ]):
        return "🟠 High"
    
    # Medium priority issues
    elif any(word in content_lower for word in [
        'performance', 'inefficient', 'optimization', 'deprecated',
        'maintainability', 'readability', 'complexity', 'potential issue',
        'potential runtime issue', 'potential bug', 'edge case', 'possible error'
    ]):
        return "🟡 Medium"
    
    # Low priority issues
    elif any(word in content_lower for word in [
        'style', 'convention', 'formatting', 'naming', 'comment',
        'documentation', 'suggestion', 'consider'
    ]):
        return "🟢 Low"
    
    # Default to medium if can't categorize
    return "🟡 Medium"

# Post comments on GitHub PR
def post_comments_on_pr(pr, comments, filename, modified_lines):
    """
    Post comments on a GitHub PR with improved line detection and comment parsing.
    This function parses AI-generated comments and posts them to the appropriate lines in the PR.
    All comments are clearly marked as AI-generated.
    """
    added_comments = set()
    commits = list(pr.get_commits())
    latest_commit = commits[-1]

    # Process comments - split long multi-line comments into individual line comments
    parsed_comments = []
    
    # Join all comments into a single string for processing
    all_comments_text = "\n".join([c.strip() for c in comments if c.strip()])
    
    # Enhanced regex pattern to better capture individual line comments
    line_pattern = re.compile(r'Line\s+(\d+)\s*:\s*(.*?)(?=\n\s*Line\s+\d+\s*:|$)', re.DOTALL)
    matches = line_pattern.findall(all_comments_text)
    
    log_activity(f"Found {len(matches)} parsed comments using primary pattern")
    
    for line_num, content in matches:
        try:
            line_number = int(line_num)
            # Determine severity level
            severity = determine_severity(content)
            
            # Enhanced AI comment format with severity
            ai_comment = f"🤖 **AI Code Review** • {severity}\n\nLine {line_num}: {content.strip()}"
            parsed_comments.append((line_number, ai_comment))
        except ValueError:
            log_activity(f"[ERROR] Invalid line number format: {line_num}")
            continue
    
    # If no matches were found, try alternative parsing approaches
    if not parsed_comments and all_comments_text:
        log_activity("[WARNING] Could not parse individual line comments. Trying alternative parsing...")
        
        # Try splitting by double newlines which often separate comments
        comment_blocks = re.split(r'\n\s*\n', all_comments_text)
        for block in comment_blocks:
            if not block.strip():
                continue
                
            # Look for line number pattern at the start of each block
            line_match = re.match(r'Line\s+(\d+)\s*:\s*(.*)', block, re.DOTALL)
            if line_match:
                try:
                    line_number = int(line_match.group(1))
                    # Add simple AI identifier to the comment
                    ai_comment = f"🤖 **AI Code Review**\n\n{block.strip()}"
                    parsed_comments.append((line_number, ai_comment))
                except ValueError:
                    continue
    
        log_activity(f"Found {len(parsed_comments)} parsed comments using alternative pattern")
        
        # If still no parsed comments, try processing each original comment individually
        if not parsed_comments:
            log_activity("[WARNING] Still no structured comments. Checking each line individually...")
            for line_content in comments:
                line_content = line_content.strip()
                if not line_content:
                    continue
                    
                # Try to extract line number from beginning of the comment
                matches = re.findall(r'^Line\s+(\d+):', line_content)
                if matches:
                    try:
                        line_number = int(matches[0])
                        # Add simple AI identifier to the comment
                        ai_comment = f"🤖 **AI Code Review**\n\n{line_content}"
                        parsed_comments.append((line_number, ai_comment))
                    except ValueError:
                        continue
    
    log_activity(f"[COMMENT] Starting comment posting for {len(parsed_comments)} AI-identified comments")
    log_activity(f"[COMMENT] Modified lines detected: {len(modified_lines)} total")
    
    # Debug: Show what lines are available
    positive_lines = [l for l in modified_lines.keys() if l > 0]
    negative_lines = [l for l in modified_lines.keys() if l < 0]
    log_activity(f"[COMMENT] Available modified lines: {sorted(positive_lines)}")
    
    # Sort comments by line number for more organized posting
    parsed_comments.sort(key=lambda x: x[0])
    
    # Post each comment to GitHub (always on RIGHT side)
    for line_position, line_content in parsed_comments:
        log_activity(f"[COMMENT] Processing AI comment for line {line_position}...")
        
        # Check if this is a modified line in the PR
        line_exists = line_position in modified_lines
        original_line = line_position
        
        # If not found, try to find the nearest modified line
        if not line_exists:
            # Get all positive line numbers (added/modified lines)
            positive_lines = [l for l in modified_lines.keys() if l > 0]
            if positive_lines:
                # Find the closest modified line
                closest_lines = sorted(positive_lines, key=lambda l: abs(l - line_position))
                if closest_lines:
                    closest_line = closest_lines[0]
                    # Use the closest line if within a reasonable distance
                    if abs(closest_line - line_position) <= 10:
                        log_activity(f"[COMMENT] Adjusting AI comment from line {line_position} to closest modified line {closest_line}")
                        line_position = closest_line
                        line_exists = True
                    else:
                        # If too far, still try to use the closest line but expand range
                        line_position = closest_line
                        line_exists = True
                        log_activity(f"[COMMENT] Line {original_line} distant from modifications, using closest line {closest_line} anyway")
            else:
                # No positive lines available, this shouldn't happen but handle it
                log_activity(f"[COMMENT] No positive lines available for AI comment placement")

        # If we still can't find a line, try to use any available modified line
        if not line_exists:
            available_lines = [l for l in modified_lines.keys() if l > 0]
            if available_lines:
                line_position = available_lines[0]  # Use first available line
                line_exists = True
                log_activity(f"[COMMENT] Using first available modified line {line_position} as fallback for AI comment on line {original_line}")

        # Skip if we can't find a suitable line to attach the comment to
        if not line_exists:
            log_activity(f"[COMMENT] Skipping AI comment for invalid line {original_line} in {filename}. No modified lines available.")
            continue

        # Skip duplicate comments
        if line_content in added_comments:
            log_activity(f"[COMMENT] Skipping duplicate AI comment at line {line_position}")
            continue

        try:
            log_activity(f"[COMMENT] Posting AI comment to RIGHT side of diff at line {line_position}")
            log_activity(f"[COMMENT] Target file: {filename}, Line: {line_position}, Side: RIGHT")
            
            comment_result = pr.create_review_comment(
                body=line_content,
                commit=latest_commit,
                path=filename,
                line=line_position,
                side="RIGHT"
            )
            
            # Verify the comment was posted correctly
            if hasattr(comment_result, 'side'):
                actual_side = getattr(comment_result, 'side', 'unknown')
                log_activity(f"[SUCCESS] AI comment posted! Confirmed side: {actual_side}")
            else:
                log_activity(f"[SUCCESS] AI comment posted successfully (side verification unavailable)")
            
            added_comments.add(line_content)
            log_activity(f"[SUCCESS] AI comment posted successfully")
            
        except Exception as e:
            error_msg = str(e).lower()
            log_activity(f"[ERROR] Error posting AI comment on PR #{pr.number}, file {filename}, line {line_position}: {e}")
            
            # If the error is about line position, try alternative approaches
            if "line" in error_msg or "position" in error_msg or "diff" in error_msg:
                try:
                    # Try posting to the first available modified line
                    if modified_lines:
                        available_lines = [l for l in modified_lines.keys() if l > 0]
                        if available_lines:
                            fallback_line = min(available_lines)  # Use the first modified line
                            log_activity(f"[FALLBACK] Retrying AI comment on first available line {fallback_line} (RIGHT side)")
                            
                            # Add additional context for fallback comments
                            fallback_content = f"🤖 **AI Code Review** (originally for line {line_position})\n\n{line_content}"
                            
                            fallback_result = pr.create_review_comment(
                                body=fallback_content,
                                commit=latest_commit,
                                path=filename,
                                line=fallback_line,
                                side="RIGHT"
                            )
                            
                            added_comments.add(line_content)
                            log_activity(f"[SUCCESS] Posted AI comment to fallback line {fallback_line} on RIGHT side")
                        else:
                            log_activity(f"[FALLBACK] No available lines found for AI comment posting")
                            
                except Exception as fallback_error:
                    log_activity(f"[FALLBACK] Fallback AI comment posting also failed: {fallback_error}")
                    
                    # Last resort: try posting as a general PR comment (not line-specific)
                    try:
                        log_activity(f"[FALLBACK] Attempting to post AI comment as general PR comment")
                        general_comment = f"🤖 **AI Code Review for {filename} (line {line_position}):**\n\n{line_content}"
                        pr.create_issue_comment(body=general_comment)
                        log_activity(f"[SUCCESS] Posted AI comment as general PR comment")
                    except Exception as general_error:
                        log_activity(f"[ERROR] General AI comment posting also failed: {general_error}")
            else:
                log_activity(f"[ERROR] Non-positioning error for AI comment, skipping fallback attempts")

    return added_comments

# Function to create HTML report of comments for browser viewing
# Update the create_comments_html_report function
def create_comments_html_report(comments, pr_url, repo_name, pr_number):
    """Create an HTML file with all review comments for viewing in a browser"""
    # Group comments by file
    comments_by_file = {}
    for comment in comments:
        filename = comment["file"]
        if filename not in comments_by_file:
            comments_by_file[filename] = []
        # Add severity level to each comment
        severity = determine_severity(comment["content"])
        comments_by_file[filename].append({
            "line_number": comment["line_number"],
            "content": comment["content"],
            "severity": severity
        })
    
    # Create timestamps for filename and display
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    review_datetime = time.strftime("%B %d, %Y at %I:%M:%S %p")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Code Review - {repo_name} PR #{pr_number}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
            h1 {{ color: #0078D7; }}
            h2 {{ color: #0078D7; margin-top: 30px; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
            .file-section {{ margin-bottom: 30px; background: #f9f9f9; padding: 15px; border-radius: 5px; }}
            .comment {{ margin-bottom: 15px; padding: 10px; background: #fff; border-left: 4px solid #0078D7; }}
            .line-number {{ font-weight: bold; color: #0078D7; }}
            .severity {{ font-weight: bold; color: #FF0000; }}
            .content {{ margin-top: 5px; white-space: pre-wrap; }}
            .pr-link {{ margin-bottom: 20px; }}
            .pr-link a {{ color: #0078D7; text-decoration: none; }}
            .pr-link a:hover {{ text-decoration: underline; }}
            .summary {{ margin-top: 20px; padding: 15px; background: #e6f3ff; border-radius: 5px; }}
            .review-info {{ margin-bottom: 25px; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #28a745; }}
            .timestamp {{ color: #666; font-size: 14px; font-style: italic; }}
        </style>
    </head>
    <body>
        <h1>AI Code Review Report</h1>
        
        <div class="review-info">
            <div class="timestamp">Review completed on {review_datetime}</div>
        </div>
        
        <div class="pr-link">
            <strong>Repository:</strong> {repo_name} | <strong>PR #:</strong> {pr_number}
            <br>
            <a href="{pr_url}" target="_blank">View PR on GitHub</a>
        </div>
        
        <div class="summary">
            <strong>Total files with comments:</strong> {len(comments_by_file)}
            <br>
            <strong>Total comments:</strong> {len(comments)}
        </div>
    """
    
    # Add each file section with its comments
    for filename, file_comments in comments_by_file.items():
        html_content += f"""
        <h2>{filename}</h2>
        <div class="file-section">
        """
        
        for comment in file_comments:
            html_content += f"""
            <div class="comment">
                <div class="line-number">Line {comment["line_number"]}</div>
                <div class="severity">Severity: {comment["severity"]}</div>
                <div class="content">{comment["content"]}</div>
            </div>
            """
        
        html_content += "</div>"
    
    html_content += """
    </body>
    </html>
    """
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "reports")
    if not os.path.exists(reports_dir):
        os.mkdir(reports_dir)
    # Save the HTML file
    report_file = os.path.join(reports_dir, f"review_report_{repo_name.replace('/', '_')}_PR{pr_number}_{timestamp}.html")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log_activity(f"[REPORT] HTML report saved to: {report_file}")
    
    # Store the latest report path globally
    global latest_report_path
    latest_report_path = report_file
    
    # Enable the view report button
    if view_report_button:
        view_report_button.configure(state="normal")
    
    # Open the report in the browser (use threading to avoid GIL issues)
    def open_report_safely():
        try:
            if os.name == 'nt':  # Windows
                log_activity(f"[REPORT] Opening review report using os.startfile: {report_file}")
                os.startfile(report_file)
            else:  # Unix/Linux/Mac
                # For non-Windows systems, use webbrowser with proper file URL
                file_url = f"file://{os.path.abspath(report_file)}"
                log_activity(f"[REPORT] Opening review report URL: {file_url}")
                webbrowser.open(file_url)
            log_activity(f"[SUCCESS] Review report opened in browser")
        except Exception as open_error:
            log_activity(f"? Failed to open report with primary method: {open_error}")
            # Fallback: try using webbrowser with different URL formats
            try:
                # Convert backslashes to forward slashes for URL
                abs_path = os.path.abspath(report_file)
                url_path = abs_path.replace('\\', '/')
                if not url_path.startswith('/'):
                    url_path = '/' + url_path
                file_url = f"file://{url_path}"
                log_activity(f"[FALLBACK] Fallback: Opening report URL: {file_url}")
                webbrowser.open(file_url)
                log_activity(f"[SUCCESS] Review report opened in browser (fallback method)")
            except Exception as fallback_error:
                log_activity(f"? Report opening fallback also failed: {fallback_error}")
                # Don't raise exception here as this is not critical to the main functionality
    
    # Use threading to avoid GIL issues when opening files from GUI context
    import threading
    thread = threading.Thread(target=open_report_safely, daemon=True)
    thread.start()
    
def main(repo_name, pr_number, post_comments=True):
    total_files_in_pr = 0
    reviewed_files_count = 0
    all_posted_comments_total_count = 0
    all_comments = []  # Store all comments for potential viewing
    total_cost = 0.0
    total_tokens = 0
    pr_url = None
    summary_message = ""  # Initialize summary_message at the beginning
    
    try:
        global github_token, openarena_token
        if not github_token or not openarena_token:
            log_activity("Tokens must be provided.")
            raise ValueError("Tokens must be provided.")

        log_activity(f"Initializing GitHub client for repo: {repo_name}, PR: {pr_number}")
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))
        pr_url = pr.html_url
        log_activity(f"Successfully connected to PR #{pr.number}.")

        # Define patterns to ignore
        ignore_patterns = ["*.vcxproj", "*.vcxproj.filters"]

        files_to_review = list(pr.get_files())
        total_files_in_pr = len(files_to_review)
        log_activity(f"Found {total_files_in_pr} files in PR #{pr.number}.")
        
        if progress_bar:
            progress_bar.set(0) # Initialize progress bar
            if progress_percentage_label:
                progress_percentage_label.configure(text="0%")

        current_file_num = 0
        for file in files_to_review:
            current_file_num += 1
            log_activity(f"Processing file {current_file_num}/{total_files_in_pr}: {file.filename}")
            
            if progress_bar:
                progress_value = float(current_file_num) / total_files_in_pr
                progress_bar.set(progress_value)
                if progress_percentage_label:
                    percentage = int(progress_value * 100)
                    progress_percentage_label.configure(text=f"{percentage}%")
                root.update_idletasks()

            # Check if the file matches any of the ignore patterns
            if any(fnmatch.fnmatch(file.filename, pattern) for pattern in ignore_patterns):
                log_activity(f"[SKIP] Skipping file: {file.filename} (matches ignore patterns)")
                continue
            
            reviewed_files_count += 1 # Count as reviewed even if no comments are made, but processing attempted

            diff = file.patch
            # Extract exact modified lines
            modified_lines = get_modified_lines_from_patch(diff)
            
            # Log raw diff for debugging if needed
            if not modified_lines:
                log_activity(f"Raw patch for debugging:\n{diff[:500]}{'...' if len(diff) > 500 else ''}")
                
            # Convert extracted lines into a formatted string for AI review
            diff_text = "\\n".join([f"{line_num}: {content}" for line_num, content in modified_lines.items()])
            
            # Debug: Show what line numbers are being sent to AI
            if modified_lines:
                line_numbers_sent = [line for line in modified_lines.keys() if line > 0]
                log_activity(f"[DEBUG] Sending line numbers to AI: {sorted(line_numbers_sent)}")
            
            # Debug output to see what changes were detected
            if modified_lines:
                added_count = sum(1 for k in modified_lines.keys() if k > 0)
                removed_count = sum(1 for k in modified_lines.keys() if k < 0)
                log_activity(f"Found {len(modified_lines)} modified lines in {file.filename} ({added_count} added/modified, {removed_count} removed)")
            else:
                log_activity(f"[DEBUG] No modified lines detected in {file.filename} patch")
            
            if not diff_text.strip():
                log_activity(f"No reviewable changes found in {file.filename} after parsing patch.")
                continue
                
            # Send modified lines to AI
            review_result = review_code(diff_text, openarena_token)
            
            if isinstance(review_result, tuple) and len(review_result) >= 3:
                comments_text, file_cost, file_tokens = review_result
            else:
                comments_text = review_result
                file_cost = 0.0
                file_tokens = 0
                
            if not comments_text:
                log_activity(f"No AI feedback for {file.filename}")
                continue
                
            # If we received valid feedback but no token count (API limitation),
            # estimate tokens based on the text length (1 token ~= 4 chars for English text)
            if file_tokens == 0 and comments_text:
                # Estimate input tokens from diff size (roughly)
                estimated_input_tokens = len(diff_text) // 4
                # Estimate output tokens from comments size
                estimated_output_tokens = len(comments_text) // 4
                # Calculate estimated cost
                estimated_cost = calculate_claude_cost(estimated_input_tokens, estimated_output_tokens)
                log_activity(f"[ESTIMATION] No token data from API. Estimating based on text length.")
                log_activity(f"[ESTIMATION] Estimated tokens - Input: {estimated_input_tokens}, Output: {estimated_output_tokens}")
                log_activity(f"[ESTIMATION] Estimated cost: ${estimated_cost:.5f}")
                file_cost = estimated_cost
                file_tokens = estimated_input_tokens + estimated_output_tokens
                
            # Track accumulated costs
            total_cost += file_cost
            total_tokens += file_tokens

            # Process AI feedback comments
            comment_lines = comments_text.split('\\n')
            
            # Apply additional filtering to catch any date-related comments that slipped through (if enabled)
            if ai_settings.get("filter_comments", True):
                comment_lines = filter_review_comments(comment_lines, file.filename)
            
            # Store the comments for this file (for potential browser viewing)
            if comment_lines:
                all_comments.extend([{
                    "file": file.filename, 
                    "line_number": re.findall(r'\d+', line)[0] if re.findall(r'\d+', line) else "N/A",
                    "content": line
                } for line in comment_lines if line.strip()])
            
            # Post comments if enabled
            if post_comments:
                posted_comments_for_file = post_comments_on_pr(pr, comment_lines, file.filename, modified_lines)
                all_posted_comments_total_count += len(posted_comments_for_file)
            else:
                # Count the comments without posting but don't log content to keep activity log clean
                log_activity(f"[SUMMARY] Found {len([line for line in comment_lines if line.strip()])} comments for {file.filename} (not posted to GitHub)")
                # Count the comments even though they're not posted
                all_posted_comments_total_count += len([line for line in comment_lines if line.strip()])
        
        # Generate summary message based on results
        if all_posted_comments_total_count > 0:
                summary_message = f"✅ AI code review complete. Reviewed {reviewed_files_count}/{total_files_in_pr} files. A total of {all_posted_comments_total_count} comments were generated."
                pr.create_issue_comment(summary_message)
                log_activity(f"\\n[SUMMARY] Posted AI summary issue comment on PR #{pr.number}: {summary_message}")
        else:
                log_activity(f"\\n[SUMMARY] {summary_message} (Comments were not posted to GitHub - see HTML report for details)")
                
            # Create an HTML report for viewing in browser if not posting to GitHub
        if not post_comments and all_comments:
                create_comments_html_report(all_comments, pr_url, repo_name, pr_number)
                
        elif reviewed_files_count > 0:
            summary_message = f"✅ AI code review complete. Reviewed {reviewed_files_count}/{total_files_in_pr} files. No specific issues found by AI requiring comments."
            log_activity(f"\\n{summary_message}")
        else:
            summary_message = f"[INFO] No files were reviewed in PR #{pr.number}."
            log_activity(f"\\n{summary_message}")
            
        # Log cost summary
        log_activity(f"[COST] COST SUMMARY")
        log_activity(f"[COST] Total estimated cost: ${total_cost:.5f} for {total_tokens} tokens")
        
        # Calculate the input/output cost breakdown (assuming 70/30 split if not detailed)
        input_tokens = int(total_tokens * 0.7)
        output_tokens = total_tokens - input_tokens
        input_cost = (input_tokens / 1000) * 0.003
        output_cost = (output_tokens / 1000) * 0.015
        log_activity(f"[COST] Breakdown: Input ${input_cost:.5f} + Output ${output_cost:.5f}")
        log_activity(f"[COST] Claude 4 Sonnet pricing: $0.003/1K input tokens, $0.015/1K output tokens")
        
    except Exception as e:
        log_activity(f"[ERROR] Error in main function: {e}")
        summary_message = f"[ERROR] Code review failed: {str(e)}"
        
    return total_files_in_pr, reviewed_files_count, all_posted_comments_total_count, pr_url, total_cost, total_tokens

# Create the main Tkinter window
# root = tk.Tk() # Old Tkinter root

# Theme change callback
def change_appearance_mode_event(new_mode=None):
    # Toggle between light and dark mode if no mode is specified
    if new_mode is None or new_mode not in ["Light", "Dark"]:
        current_mode = customtkinter.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
    
    # Set the new appearance mode
    customtkinter.set_appearance_mode(new_mode)
    
    # Update the switch text if it exists
    if 'mode_switch' in globals() and mode_switch is not None:
        try:
            mode_switch.configure(text=f"{new_mode} Mode")
        except Exception as e:
            print(f"Error updating mode switch: {e}")

customtkinter.set_appearance_mode("Dark")  # Default to Dark mode

# Try to load the custom theme file, fall back to built-in theme if not found
try:
    # Check multiple possible theme file locations (for development and PyInstaller)
    theme_locations = [
        os.path.join(os.path.dirname(__file__), "blue.json"),  # Development environment
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "AIReview", "blue.json"),  # Relative to root
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "blue.json"),  # Root directory
    ]
    
    # If running from PyInstaller bundle, add those paths too
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
        theme_locations.extend([
            os.path.join(bundle_dir, "AIReview", "blue.json"),  # PyInstaller bundle AIReview folder
            os.path.join(bundle_dir, "blue.json"),  # PyInstaller bundle root
        ])
    
    # Try each location until we find a valid theme file
    theme_found = False
    for theme_path in theme_locations:
        if os.path.exists(theme_path):
            print(f"Found theme file at: {theme_path}")
            customtkinter.set_default_color_theme(theme_path)
            theme_found = True
            break
    
    if not theme_found:
        print(f"Theme file not found in any expected locations, using default theme.")
        customtkinter.set_default_color_theme("blue")  # Fall back to built-in blue theme
except Exception as e:
    print(f"Error loading theme: {e}, falling back to default theme")
    customtkinter.set_default_color_theme("blue")  # Fall back to built-in blue theme

root = customtkinter.CTk() # New CustomTkinter root
root.title("AI Code Review Tool")
root.geometry("1000x700") # Adjusted initial geometry, will be resizable

# Set application icon - search for it in various possible locations
def find_resource_path(resource_name):
    """Find a resource file in various possible locations including PyInstaller bundles"""
    # Define potential locations to check
    locations = []
    
    # Development environment locations
    app_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    locations.extend([
        os.path.join(app_dir, "images", resource_name),  # AIReview/images/
        os.path.join(root_dir, "images", resource_name),  # /images/
    ])
    
    # If running from PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
        locations.extend([
            os.path.join(bundle_dir, "images", resource_name),  # /images/ in bundle
            os.path.join(bundle_dir, resource_name),  # / in bundle
        ])
    
    # Check each location
    for location in locations:
        if os.path.exists(location):
            print(f"Found resource '{resource_name}' at: {location}")
            return location
            
    print(f"Warning: Resource '{resource_name}' not found in any expected location")
    return None

# Find the icon file
icon_path = find_resource_path("ai.ico")

if icon_path:
    try:
        root.iconbitmap(icon_path)
        print(f"Icon set with iconbitmap from {icon_path}")
        
        # Additional Windows-specific code to ensure taskbar icon is properly set
        try:
            # For Windows OS - explicitly set the taskbar icon
            import ctypes
            app_id = f"TR.AIReviewTool.{APP_VERSION}"  # Unique application ID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            print(f"Successfully set taskbar icon with app ID: {app_id}")
        except Exception as e:
            print(f"Warning: Could not set taskbar icon with Windows API: {e}")
            
            # Try PIL approach as backup
            try:
                # Alternative approach using PIL for cross-platform compatibility
                from PIL import Image, ImageTk
                icon_img = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_img)
                root.iconphoto(True, icon_photo)  # This sets both window and taskbar icon
                print("? Taskbar icon set successfully using PIL")
            except Exception as pil_error:
                print(f"Note: Could not set taskbar icon with PIL: {pil_error}")
    except Exception as icon_error:
        print(f"Error setting icon with iconbitmap: {icon_error}")
        
        # Try PIL approach as fallback
        try:
            from PIL import Image, ImageTk
            icon_img = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_img)
            root.iconphoto(True, icon_photo)
            print("? Icon set with PIL as fallback")
        except Exception as fallback_error:
            print(f"Failed to set icon with fallback method: {fallback_error}")
else:
    print("No suitable icon file found in any location")

# Make window resizable
root.resizable(True, True)
# Configure root grid for expansion
root.grid_columnconfigure(0, weight=2)  # Left side takes 2/3
root.grid_columnconfigure(1, weight=1)  # Activity log takes 1/3
root.grid_rowconfigure(0, weight=1)

# Create the main content frame
content_frame = customtkinter.CTkFrame(root)
content_frame.grid(row=0, column=0, sticky="nsew")
content_frame.grid_columnconfigure(0, weight=1)
content_frame.grid_rowconfigure(0, weight=1)

# We'll define the mode_switch variable later in the UI setup section

# --- MENU BAR (Menu + Help) with CustomTkinter ---
def show_release_notes():
    notes = (
        "🚀 Release Notes (v2.0.7) 🚀\n\n"
        "🔑 NEW: Automated Token Extraction\n"
        "   • One-click OpenArena token extraction with 'Get-Token' button\n"
        "   • Automated Chrome browser integration for seamless authentication\n"
        "   • Persistent token storage with automatic loading on startup\n"
        "   • Eliminates manual copy-paste errors and saves time\n\n"
        "🎯 Smart Update Management\n"
        "   • Daily automatic update checks (configurable)\n"
        "   • Version comparison with proper semantic versioning\n"
        "   • Notification history to prevent duplicate alerts\n"
        "   • Manual 'Check for Updates' option in menu\n"
        "   • Update status tracking and logging\n\n"
        "🎨 Modern UI Enhancements\n"
        "   • Sleek customtkinter interface with professional blue theme\n"
        "   • Enhanced layout with improved visual elements\n"
        "   • Added Dark/Light mode button with instant switching\n\n"
        "📊 Advanced Activity Tracking\n"
        "   • Real-time activity log with timestamps for every action\n"
        "   • Progress bar with percentage display for better feedback\n"
        "   • Clear button that resets both log and review metrics\n"
        "   • Detailed performance metrics and cost estimation\n\n"
        "⚡ Enhanced Usability Features\n"
        "   • Recent repositories dropdown for quick access\n"
        "   • Comprehensive HTML user guide with screenshots\n"
        "   • One-click PR viewing on GitHub\n"
        "   • Improved token management with secure encryption\n"
        "   • Streamlined menu organization with user guide documentation\n\n"
        "🤖 AI Review Improvements\n"
        "   • Enhanced Open Arena AI chain with Claude 4 Sonnet integration\n"
        "   • Accurate token tracking and cost calculation\n"
        "   • Smarter review prompts for more relevant feedback\n"
        "   • Better error handling and retry mechanisms\n\n"
        "✨ Ready to transform your code review process with automated token extraction!"
    )
    dialog = customtkinter.CTkToplevel(root)
    dialog.title("Release Notes")
    dialog.geometry("500x500")  # Increased size to fit enhanced content
    dialog.resizable(False, False)
    dialog.grab_set()
    
    # Make dialog modal
    dialog.transient(root)
    dialog.focus_set()
    
    # Content frame
    content_frame = customtkinter.CTkFrame(dialog)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Notes text - using a text widget instead of label for better text handling
    notes_text = customtkinter.CTkTextbox(content_frame, height=400, width=450)
    notes_text.pack(pady=10, padx=10, fill="both", expand=True)
    notes_text.insert("1.0", notes)
    notes_text.configure(state="disabled")  # Make it read-only
    
    # Close button
    close_button = customtkinter.CTkButton(
        content_frame, 
        text="Close", 
        command=dialog.destroy
    )
    close_button.pack(pady=10)

def show_about():
    about = (
        "🤖 AI Code Review Tool 🤖\n\n"
        "💡 What it does:\n"
        "This intelligent application leverages advanced AI to automatically review "
        "code changes in GitHub pull requests. It analyzes modifications, posts helpful "
        "comments, and generates comprehensive review metrics to improve code quality.\n\n"
        "🔑 NEW in v2.0.3:\n"
        "• Automated OpenArena token extraction with one-click authentication\n"
        "• Seamless Chrome browser integration for token capture\n"
        "• Persistent token storage with automatic loading\n\n"
        "✅ Benefits:\n"
        "• Faster code reviews with consistent quality\n"
        "• Early detection of potential issues\n"
        "• Improved code standards across your team\n"
        "• Time savings for developers and reviewers\n"
        "• Eliminates manual token management hassles\n\n"
        "🏆 Built with pride by the Ultratax Team, 2025"
    )
    dialog = customtkinter.CTkToplevel(root)
    dialog.title("About")
    dialog.geometry("500x450")  # Increased size for enhanced content
    dialog.resizable(False, False)
    dialog.grab_set()
    
    # Make dialog modal
    dialog.transient(root)
    dialog.focus_set()
    
    # Content frame
    content_frame = customtkinter.CTkFrame(dialog)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # About text - using a text widget instead of label for better text handling
    about_text = customtkinter.CTkTextbox(content_frame, height=350, width=450)
    about_text.pack(pady=10, padx=10, fill="both", expand=True)
    about_text.insert("1.0", about)
    about_text.configure(state="disabled")  # Make it read-only
    
    # Close button
    close_button = customtkinter.CTkButton(
        content_frame, 
        text="Close", 
        command=dialog.destroy
    )
    close_button.pack(pady=10)

def show_contact():
    import webbrowser
    import urllib.parse
    
    # Define email addresses
    to_addresses = [
        "Velavalapalli.HarishSarma@thomsonreuters.com",
        "KALYANI.KANDUNURI@thomsonreuters.com", 
        "Ravi.Bitra@thomsonreuters.com"
    ]
    cc_addresses = [
        "Radhika.Ramagiri@thomsonreuters.com"
    ]
    
    # Create mailto URL with multiple recipients and CC
    to_list = ";".join(to_addresses)
    cc_list = ";".join(cc_addresses)
    subject = "AI Code Review Tool - Feedback"
    
    # URL encode the parameters
    mailto_url = f"mailto:{to_list}?cc={cc_list}&subject={urllib.parse.quote(subject)}"
    
    webbrowser.open(mailto_url)

def open_user_guide():
    """Open the user guide HTML file in the default browser"""
    import webbrowser
    import os
    import sys
    import tempfile
    import shutil
    import re
    
    # Handle both development environment and PyInstaller frozen environment
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (compiled with PyInstaller)
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
        log_activity(f"[DEBUG] Base path: {base_path}")
        
        # List files in the base path to debug
        try:
            log_activity("[DEBUG] Available files in base directory:")
            for item in os.listdir(base_path):
                log_activity(f" - {item}")
                
            # Check if docs directory exists
            docs_path = os.path.join(base_path, "docs")
            if os.path.exists(docs_path) and os.path.isdir(docs_path):
                log_activity("[DEBUG] Docs directory found, listing contents:")
                for item in os.listdir(docs_path):
                    log_activity(f" - {item}")
            else:
                log_activity("? Docs directory not found")
        except Exception as e:
            log_activity(f"? Error listing files: {str(e)}")
            
        original_guide_path = os.path.join(base_path, "docs", "user_guide.html")
        
        # Check if the user guide file exists
        if not os.path.exists(original_guide_path):
            log_activity(f"? User guide not found at {original_guide_path}")
            messagebox.showerror("Error", 
                            "User guide file not found. Please ensure the documentation is properly installed.")
            return
            
        log_activity(f"? Found user guide at {original_guide_path}")
        
        # Create a temp directory to hold a modified copy of the guide with correct image paths
        # Use a unique name to avoid conflicts with other instances
        temp_dir = os.path.join(tempfile.gettempdir(), f"AIReviewTool_docs_{os.getpid()}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create images directory structure in the temp folder
        temp_images = os.path.join(temp_dir, "images")
        temp_images_docs = os.path.join(temp_dir, "images", "docs")
        os.makedirs(temp_images, exist_ok=True)
        os.makedirs(temp_images_docs, exist_ok=True)
        
        log_activity(f"[DEBUG] Preparing user guide with images in temp directory: {temp_dir}")
        
        # Copy images to the temp location and track which ones we actually found
        found_images = []
        for img_file in ["TR.png", "logo.png", "bot.JPG"]:
            src = os.path.join(base_path, "images", img_file)
            dest = os.path.join(temp_images, img_file)
            if os.path.exists(src):
                shutil.copy(src, dest)
                found_images.append(("../images/" + img_file, "images/" + img_file))
                log_activity(f"[DEBUG] Copied image: {img_file} to temp directory")
            else:
                log_activity(f"[WARNING] Image file not found: {src}")
        
        found_doc_images = []
        for img_file in ["AIR.png", "AIR_2.png", "Gt_1.png", "Gt_2.png", "Gt_3.png"]:
            src = os.path.join(base_path, "images", "docs", img_file)
            dest = os.path.join(temp_images_docs, img_file)
            if os.path.exists(src):
                shutil.copy(src, dest)
                found_doc_images.append(("../images/docs/" + img_file, "images/docs/" + img_file))
                log_activity(f"[DEBUG] Copied doc image: {img_file} to temp directory")
            else:
                log_activity(f"[WARNING] Doc image file not found: {src}")
        
        # Read the original HTML content
        with open(original_guide_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace the image paths in the HTML content
        for old_path, new_path in found_images + found_doc_images:
            html_content = html_content.replace(old_path, new_path)
        
        # Also replace any url('../images/... references in CSS
        html_content = re.sub(r"url\(['\"]?\.\.\/images\/", r"url('images/", html_content)
        log_activity("[DEBUG] Updated image paths in HTML content")
        
        # Write the modified HTML to the temp directory
        temp_guide_path = os.path.join(temp_dir, "user_guide.html")
        with open(temp_guide_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        guide_path = temp_guide_path
        log_activity(f"[DEBUG] Created modified user guide at: {temp_guide_path}")
    else:
        # Standard development environment - no path modification needed
        guide_path = os.path.join(os.path.dirname(__file__), "..", "docs", "user_guide.html")
        log_activity("[DEBUG] Using standard development path for user guide")
        
        # Check if the user guide file exists in development mode
        if not os.path.exists(guide_path):
            log_activity(f"? User guide not found at {guide_path}")
            messagebox.showerror("Error", 
                            "User guide file not found. Please ensure the documentation is properly installed.")
            return
    
    guide_path = os.path.abspath(guide_path)
    
    # At this point we've already verified the guide exists, so just open it
    # Use threading to avoid GIL issues when opening files from GUI context
    def open_guide_safely():
        try:
            if os.name == 'nt':  # Windows
                log_activity(f"[DEBUG] Opening user guide using os.startfile: {guide_path}")
                os.startfile(guide_path)
            else:  # Unix/Linux/Mac
                # For non-Windows systems, use webbrowser with proper file URL
                file_url = f"file://{guide_path}"
                log_activity(f"[DEBUG] Opening user guide URL: {file_url}")

                webbrowser.open(file_url)
            log_activity("[SUCCESS] User guide opened in browser")
        except Exception as open_error:
            log_activity(f"? Failed to open with primary method: {open_error}")
            # Fallback: try using webbrowser with different URL formats
            try:
                # Convert backslashes to forward slashes for URL
                url_path = guide_path.replace('\\', '/')
                if not url_path.startswith('/'):
                    url_path = '/' + url_path
                file_url = f"file://{url_path}"
                webbrowser.open(file_url)
                log_activity("[SUCCESS] User guide opened in browser (fallback method)")
            except Exception as fallback_error:
                log_activity(f"? Fallback also failed: {fallback_error}")
                # Don't raise exception here as this is not critical to the main functionality

    # Use threading to avoid GIL issues when opening files from GUI context
    import threading
    thread = threading.Thread(target=open_guide_safely, daemon=True)
    thread.start()

# Create standard menu bar (like in the second image)
menu_bar = tk.Menu(root, font=("Arial", 9, "bold"))
root.configure(menu=menu_bar)

class UpdateChecker:
    def __init__(self, current_version, parent_window):
        self.current_version = current_version
        self.parent_window = parent_window
        self.check_interval_days = 1  # Check daily
        
    def get_latest_exe_info(self):
        try:
            response = requests.get(GITHUB_DIST_URL, timeout=10)
            if response.status_code == 200:
                files = response.json()
                
                # Find EXE files and extract version info
                exe_files_with_versions = []
                for f in files:
                    if f['name'].endswith('.exe'):
                        version_match = re.search(r'[Vv]?(\d+\.\d+\.\d+)', f['name'])
                        if version_match:
                            version_str = version_match.group(1)
                            # Convert version to tuple for proper sorting (2.0.10 > 2.0.9)
                            version_tuple = tuple(map(int, version_str.split('.')))
                            exe_files_with_versions.append((f, version_str, version_tuple))
                
                if exe_files_with_versions:
                    # Sort by version tuple to get the truly latest version
                    latest_file, latest_version, _ = max(exe_files_with_versions, key=lambda x: x[2])
                    
                    return {
                        'version': latest_version,
                        'filename': latest_file['name'],
                        'download_url': latest_file['download_url'],
                        'size': latest_file['size']
                    }
            return None
        except Exception as e:
            log_activity(f"[UPDATE] Error getting EXE info: {e}")
            return None
    
    def download_update(self, exe_info, progress_callback=None):
        """Download the update EXE file"""
        try:
            import tempfile
            import shutil
            
            # Create temp directory for download
            temp_dir = tempfile.mkdtemp()
            temp_exe_path = os.path.join(temp_dir, exe_info['filename'])
            
            log_activity(f"[UPDATE] Downloading {exe_info['filename']}...")
            
            # Download the file
            response = requests.get(exe_info['download_url'], stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            log_activity(f"[UPDATE] Download completed: {temp_exe_path}")
            return temp_exe_path
            
        except Exception as e:
            log_activity(f"[UPDATE] Download failed: {e}")
            return None
    
    def install_update(self, downloaded_exe_path):
        """Install the downloaded update"""
        try:
            import subprocess
            import sys
            
            current_exe = sys.executable if getattr(sys, 'frozen', False) else __file__
            current_dir = os.path.dirname(current_exe)
            
            # Create backup of current version
            backup_path = os.path.join(current_dir, f"AIReviewTool_backup_{self.current_version}.exe")
            if os.path.exists(current_exe) and current_exe.endswith('.exe'):
                shutil.copy2(current_exe, backup_path)
                log_activity(f"[UPDATE] Backup created: {backup_path}")
            
            # Create update script
            update_script = os.path.join(current_dir, "update_script.bat")
            script_content = f'''@echo off
echo Updating AI Review Tool...
timeout /t 3 /nobreak >nul
copy "{downloaded_exe_path}" "{current_exe}"
if errorlevel 1 (
    echo Update failed!
    pause
    exit /b 1
)
echo Update completed successfully!
start "" "{current_exe}"
del "%~f0"
'''
            
            with open(update_script, 'w') as f:
                f.write(script_content)
            
            log_activity("[UPDATE] Starting update process...")
            
            # Show update dialog
            messagebox.showinfo("Update", 
                              "The application will now close to complete the update.\n"
                              "The updated version will start automatically.")
            
            # Start update script and exit
            subprocess.Popen([update_script], shell=True)
            self.parent_window.quit()
            
        except Exception as e:
            log_activity(f"[UPDATE] Installation failed: {e}")
            messagebox.showerror("Update Error", f"Failed to install update: {e}")
    
    def check_for_updates_async(self):
        """Check for updates in a background thread"""
        def check_updates():
            try:
                if not self.should_check_for_updates():
                    return
                
                log_activity("[UPDATE] Checking for application updates...")
                
                # Get latest EXE info from dist folder
                exe_info = self.get_latest_exe_info()
                
                if exe_info and self.compare_versions(self.current_version, exe_info['version']) < 0:
                    # New version available
                    if not self.has_been_notified(exe_info['version']):
                        self.show_update_notification_with_download(exe_info)
                        self.record_notification(exe_info['version'])
                        log_activity(f"[UPDATE] New version available: {exe_info['version']}")
                    else:
                        log_activity(f"[UPDATE] New version {exe_info['version']} available (already notified)")
                else:
                    log_activity("[UPDATE] Application is up to date")
                
                self.record_update_check()
                
            except Exception as e:
                log_activity(f"[UPDATE] Error checking for updates: {e}")
        
        # Run in background thread
        thread = threading.Thread(target=check_updates, daemon=True)
        thread.start()
    
    def show_update_notification_with_download(self, exe_info):
        """Show update notification dialog with download functionality"""
        def show_dialog():
            try:
                dialog = customtkinter.CTkToplevel(self.parent_window)
                dialog.title("Update Available")
                dialog.geometry("500x400")
                dialog.resizable(False, False)
                dialog.grab_set()
                dialog.transient(self.parent_window)
                
                # Center the dialog
                dialog.update_idletasks()
                x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
                y = (dialog.winfo_screenheight() // 2) - (400 // 2)
                dialog.geometry(f"500x400+{x}+{y}")
                
                # Content frame
                content_frame = customtkinter.CTkFrame(dialog)
                content_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Title
                title_label = customtkinter.CTkLabel(
                    content_frame, 
                    text="🚀 Update Available!",
                    font=customtkinter.CTkFont(size=18, weight="bold")
                )
                title_label.pack(pady=(0, 10))
                
                # Version info
                file_size_mb = exe_info['size'] / (1024 * 1024)
                version_text = f"Current Version: {self.current_version}\nLatest Version: {exe_info['version']}\nFile: {exe_info['filename']}\nSize: {file_size_mb:.1f} MB"
                version_label = customtkinter.CTkLabel(content_frame, text=version_text)
                version_label.pack(pady=(0, 10))
                
                # Progress bar (initially hidden)
                progress_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
                progress_frame.pack(fill="x", pady=10)
                progress_frame.pack_forget()  # Hide initially
                
                progress_bar = customtkinter.CTkProgressBar(progress_frame)
                progress_bar.pack(fill="x", pady=5)
                progress_bar.set(0)
                
                progress_label = customtkinter.CTkLabel(progress_frame, text="Downloading...")
                progress_label.pack()
                
                # Status label
                status_label = customtkinter.CTkLabel(content_frame, text="")
                status_label.pack(pady=5)
                
                # Buttons
                button_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
                button_frame.pack(fill="x", pady=(10, 0))
                
                def download_and_install():
                    # Show progress
                    progress_frame.pack(fill="x", pady=10)
                    download_button.configure(state="disabled", text="Downloading...")
                    later_button.configure(state="disabled")
                    skip_button.configure(state="disabled")
                    
                    def progress_callback(progress):
                        def update_progress():
                            progress_bar.set(progress / 100)
                            progress_label.configure(text=f"Downloading... {progress:.1f}%")
                        dialog.after(0, update_progress)
                    
                    def download_thread():
                        try:
                            # Download the update
                            downloaded_path = self.download_update(exe_info, progress_callback)
                            
                            if downloaded_path:
                                def install_update():
                                    status_label.configure(text="Installing update...")
                                    dialog.after(1000, lambda: self.install_update(downloaded_path))
                                
                                dialog.after(0, install_update)
                            else:
                                def show_error():
                                    status_label.configure(text="Download failed!")
                                    download_button.configure(state="normal", text="Retry Download")
                                    later_button.configure(state="normal")
                                    skip_button.configure(state="normal")
                                
                                dialog.after(0, show_error)
                                
                        except Exception as e:
                            def show_error():
                                status_label.configure(text=f"Error: {e}")
                                download_button.configure(state="normal", text="Retry Download")
                                later_button.configure(state="normal")
                                skip_button.configure(state="normal")
                            
                            dialog.after(0, show_error)
                    
                    # Start download in background
                    thread = threading.Thread(target=download_thread, daemon=True)
                    thread.start()
                
                def remind_later():
                    dialog.destroy()
                
                def skip_version():
                    self.record_notification(exe_info['version'])
                    dialog.destroy()
                
                download_button = customtkinter.CTkButton(
                    button_frame, 
                    text="Download & Install Update",
                    command=download_and_install,
                    fg_color="#2E8B57",
                    hover_color="#3CB371"
                )
                download_button.pack(side="left", padx=5)
                
                later_button = customtkinter.CTkButton(
                    button_frame,
                    text="Remind Later",
                    command=remind_later,
                    fg_color="#4169E1",
                    hover_color="#6495ED"
                )
                later_button.pack(side="left", padx=5)
                
                skip_button = customtkinter.CTkButton(
                    button_frame,
                    text="Skip This Version",
                    command=skip_version,
                    fg_color="#8B4513",
                    hover_color="#A0522D"
                )
                skip_button.pack(side="right", padx=5)
                
                log_activity(f"[UPDATE] User notified about version {exe_info['version']}")
                
            except Exception as e:
                log_activity(f"[UPDATE] Error showing update dialog: {e}")
        
        # Schedule dialog to show in main thread
        self.parent_window.after(100, show_dialog)

# Add this function to check for updates on startup
def check_for_updates_on_startup():
    """Check for updates when the application starts"""
    try:
        update_checker = UpdateChecker(APP_VERSION, root)
        # Delay the check by 2 seconds to let the UI fully load
        root.after(2000, update_checker.check_for_updates_async)
    except Exception as e:
        print(f"Error initializing update checker: {e}")

# Add manual update check function for menu
def manual_update_check():
    """Manually check for updates (called from menu)"""
    try:
        update_checker = UpdateChecker(APP_VERSION, root)
        
        def check_and_notify():
            try:
                log_activity("[UPDATE] Manually checking for updates...")
                
                # Get latest EXE info from dist folder
                exe_info = update_checker.get_latest_exe_info()
                
                if exe_info and update_checker.compare_versions(APP_VERSION, exe_info['version']) < 0:
                    update_checker.show_update_notification_with_download(exe_info)
                    log_activity(f"[UPDATE] Manual check found new version: {exe_info['version']}")
                else:
                    current_version = exe_info['version'] if exe_info else "Unknown"
                    messagebox.showinfo("Update Check", f"You are using the latest version!\n\nCurrent: v{APP_VERSION}\nLatest: v{current_version}")
                    log_activity(f"[UPDATE] Manual check: up to date (Current: {APP_VERSION}, Latest: {current_version})")
                
                update_checker.record_update_check()
                
            except Exception as e:
                messagebox.showerror("Update Check", f"Error checking for updates: {e}")
                log_activity(f"[UPDATE] Manual check error: {e}")
        
        # Run in background thread
        thread = threading.Thread(target=check_and_notify, daemon=True)
        thread.start()
        
    except Exception as e:
        messagebox.showerror("Update Check", f"Error initializing update check: {e}")

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0, font=("Arial", 9, "normal"))
menu_bar.add_cascade(label="Menu", menu=file_menu)
file_menu.add_command(label="New Review", command=lambda: file_menu_callback("New Review"))
file_menu.add_command(label="Check for Updates", command=manual_update_check)  # Add this line
file_menu.add_command(label="View Latest Report", command=lambda: open_latest_report())
file_menu.add_separator()
file_menu.add_command(label="Release Notes", command=show_release_notes)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

def reset_ai_settings_to_defaults():
    """Reset AI settings to defaults and save to file"""
    global ai_settings
    
    result = messagebox.askyesno("Reset Settings", 
                               "Are you sure you want to reset all AI settings to defaults?\n\n"
                               "This will:\n"
                               "? Reset Temperature to 0.7\n"
                               "? Reset Top P to 1.0\n"
                               "? Reset Max Tokens to 16384\n"
                               "? Reset System Prompt to default\n"
                               "? Reset Workflow ID to default\n"
                               "? Reset filtering to enabled\n\n"
                               "Your current settings will be lost.")
    
    if result:
        ai_settings = {
            "temperature": "0.7",
            "top_p": "1.0", 
            "max_tokens": "16384",
            "system_prompt": default_system_prompt,
            "workflow_id": "7c41c3ab-c214-4394-ba38-9da289975d85",
            "filter_comments": True
        }
        save_ai_settings_to_file()
        messagebox.showinfo("Success", "All AI settings have been reset to defaults!")
        
        if 'log_activity' in globals():
            log_activity("[SETTINGS] AI Settings reset to defaults from Settings menu")

# Settings menu
settings_menu = tk.Menu(menu_bar, tearoff=0, font=("Arial", 9, "normal"))
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="AI Payload Configuration", command=lambda: open_ai_settings_dialog())
settings_menu.add_separator()
settings_menu.add_command(label="Save Current Settings", command=lambda: save_ai_settings_to_file())
settings_menu.add_command(label="Load Saved Settings", command=lambda: load_ai_settings_from_file() and messagebox.showinfo("Success", "AI settings loaded!"))
settings_menu.add_separator()
settings_menu.add_command(label="Reset to Defaults", command=lambda: reset_ai_settings_to_defaults())

# Help menu
help_menu = tk.Menu(menu_bar, tearoff=0, font=("Arial", 9, "normal"))
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="User Guide", command=lambda: open_user_guide())
help_menu.add_separator()
help_menu.add_command(label="About", command=show_about)
help_menu.add_command(label="Feedback", command=show_contact)

# File Menu callback function (used in lambda above)
def clear_activity_log():
    """Clear the content of the activity log textbox and reset review metrics"""
    if activity_log_textbox:
        activity_log_textbox.delete("1.0", tk.END)
        log_activity("Activity log cleared")
    
    # Reset review metrics
    if time_taken_label:
        time_taken_label.configure(text="-")
    if cost_label:
        cost_label.configure(text="-")
    
    # Reset progress bar
    if progress_bar:
        progress_bar.set(0)
        # Clear progress percentage if it exists
        if progress_percentage_label:
            progress_percentage_label.configure(text="Ready to start")

def file_menu_callback(choice):
    if choice == "New Review":
        # Reset the form
        clear_tokens()
        repo_name_entry.delete(0, tk.END)
        pr_number_entry.delete(0, tk.END)
        if activity_log_textbox:
            activity_log_textbox.delete("1.0", tk.END)
        if progress_bar:
            progress_bar.set(0)
            if progress_percentage_label:
                progress_percentage_label.configure(text="Ready to start")
        status_message.set("")
        if time_taken_label:
            time_taken_label.configure(text="-")
        if cost_label:
            cost_label.configure(text="-")
        if view_pr_button:
            view_pr_button.configure(state="disabled")

# --- MAIN UI LAYOUT ---
# Controls (left)
left_frame = customtkinter.CTkFrame(content_frame)
left_frame.grid(row=0, column=0, padx=(10,5), pady=(5,10), sticky="nsew")
left_frame.grid_columnconfigure(0, weight=1)

# --- Settings Frame ---
settings_frame = customtkinter.CTkFrame(left_frame)
settings_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")  # Changed from row=0 to row=1
settings_frame.grid_columnconfigure(0, weight=1)
settings_frame.grid_columnconfigure(1, weight=0)

# Add header label to settings frame
header_label = customtkinter.CTkLabel(settings_frame, text="🤖 AI Code Review Tool", font=customtkinter.CTkFont(size=20, weight="bold"))
header_label.grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

# --- Input Fields Frame ---
input_frame = customtkinter.CTkFrame(left_frame)
input_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")  # Changed from row=1 to row=2
input_frame.grid_columnconfigure(1, weight=1)

# --- Updated Info Button ---
def create_ctk_info_button(parent, row, column, info_text):
    def show_tooltip():
        top = Toplevel(root)
        top.title("Info")
        Label(top, text=info_text, padx=20, pady=20, font=("Arial", 10)).pack()
        Button(top, text="Close", command=top.destroy).pack(pady=5)
        top.grab_set()
    btn = customtkinter.CTkButton(parent, text="i", width=24, height=24, fg_color="#0078D7", text_color="white", font=customtkinter.CTkFont(size=14, weight="bold"), command=show_tooltip)
    btn.grid(row=row, column=column, padx=5)

# GitHub Token
gh_token_label = customtkinter.CTkLabel(input_frame, text="GitHub Token:", font=customtkinter.CTkFont(weight="bold"))
gh_token_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
github_token_entry = customtkinter.CTkEntry(input_frame, show="*", placeholder_text="Enter GitHub PAT")
github_token_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
create_ctk_info_button(input_frame, 0, 2, "Enter your GitHub personal access token. Required for GitHub API access.")

# OpenArena Token
# OpenArena Token with extraction button
oa_token_label = customtkinter.CTkLabel(input_frame, text="OpenArena Token:", font=customtkinter.CTkFont(weight="bold"))
oa_token_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)

# Create frame for token entry and extraction button
oa_token_frame = customtkinter.CTkFrame(input_frame, fg_color="transparent")
oa_token_frame.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
oa_token_frame.grid_columnconfigure(0, weight=1)

openarena_token_entry = customtkinter.CTkEntry(oa_token_frame, show="*", placeholder_text="Enter OpenArena API Token")
openarena_token_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

# Add token extraction button
if HAS_TOKEN_EXTRACTION:
    def extract_openarena_token():
        """Extract OpenArena token using automated browser method"""
        url = "https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/11d87e9a-6dcd-4926-80ea-e9fdd07f7e9b"
        
        # Disable button during extraction
        extract_token_button.configure(state="disabled", text="Extracting...")
        root.update_idletasks()
        
        try:
            log_activity("🚀 Starting automated token extraction...")
            log_activity("📋 Please log in to OpenArena when the browser opens...")
            
            # Run token extraction in a separate thread to avoid blocking UI
            def extraction_thread():
                try:
                    token = get_auth_token(url)
                    
                    # Update UI in main thread
                    def update_ui():
                        if token:
                            openarena_token_entry.delete(0, tk.END)
                            openarena_token_entry.insert(0, token)
                            log_activity("✅ OpenArena token extracted successfully!")
                            messagebox.showinfo("Success", "OpenArena token extracted and populated successfully!")
                            
                            # Optionally save the token
                            if save_token_to_file(token):
                                log_activity("💾 Token saved to file for future use")
                        else:
                            log_activity("❌ Failed to extract OpenArena token")
                            messagebox.showerror("Error", "Failed to extract OpenArena token. Please try manual entry.")
                        
                        # Re-enable button
                        extract_token_button.configure(state="normal", text="Get-Token")
                    
                    root.after(0, update_ui)
                    
                except Exception as e:
                    def show_error():
                        log_activity(f"❌ Error during token extraction: {e}")
                        messagebox.showerror("Error", f"Token extraction failed: {e}")
                        extract_token_button.configure(state="normal", text="Get-Token")
                    
                    root.after(0, show_error)
            
            # Start extraction in background thread
            thread = threading.Thread(target=extraction_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            log_activity(f"❌ Error starting token extraction: {e}")
            messagebox.showerror("Error", f"Failed to start token extraction: {e}")
            extract_token_button.configure(state="normal", text="Get-Token")
    
    extract_token_button = customtkinter.CTkButton(
        oa_token_frame, 
        text="Get-Token", 
        command=extract_openarena_token_with_user_info,
        width=100,
        fg_color="#2E8B57",
        hover_color="#3CB371"
    )
    extract_token_button.grid(row=0, column=1, padx=(5, 0))

create_ctk_info_button(input_frame, 1, 2, "Enter your OpenArena token for AI API authentication. Use Get-Token to get token automatically.")

# Repository Name
repo_label = customtkinter.CTkLabel(input_frame, text="Repository Name:", font=customtkinter.CTkFont(weight="bold"))
repo_label.grid(row=3, column=0, sticky='w', padx=10, pady=5)

# Create a frame to hold the combobox and integrate it with customtkinter
repo_frame = customtkinter.CTkFrame(input_frame, fg_color="transparent")
repo_frame.grid(row=3, column=1, pady=5, padx=10, sticky="ew")
repo_frame.grid_columnconfigure(0, weight=1)  # Make the combobox expand

# Load recent repositories
recent_repos = load_recent_repos()

# Create a standard ttk Combobox for repository selection with improved sizing
repo_combobox = ttk.Combobox(repo_frame, values=recent_repos, height=10)  # Increased dropdown height for better visibility
repo_combobox.pack(fill='x', expand=True, pady=4)  # Increased vertical padding to match PR entry box

# Set placeholder text if no repos exist
if recent_repos:
    repo_combobox.set("")  # Empty by default, user needs to select
else:
    repo_combobox.set("owner/repo-name")  # Placeholder text

# For compatibility with existing code
repo_name_entry = repo_combobox

create_ctk_info_button(input_frame, 3, 2, "Select or enter repository name (e.g., 'owner/repo').")

# Pull Request Number
pr_label = customtkinter.CTkLabel(input_frame, text="Pull Request No.:", font=customtkinter.CTkFont(weight="bold"))
pr_label.grid(row=4, column=0, sticky='w', padx=10, pady=5)
pr_number_entry = customtkinter.CTkEntry(input_frame, placeholder_text="Enter PR number")
pr_number_entry.grid(row=4, column=1, pady=5, padx=10, sticky="ew")
create_ctk_info_button(input_frame, 4, 2, "Enter the pull request number.")

# Add a checkbox for posting comments option
post_comments_var = tk.BooleanVar(value=True)
post_comments_checkbox = customtkinter.CTkCheckBox(
    input_frame, 
    text="Post comments to PR", 
    variable=post_comments_var, 
    onvalue=True, 
    offvalue=False
)
post_comments_checkbox.grid(row=5, column=0, columnspan=2, sticky='w', padx=10, pady=5)
create_ctk_info_button(input_frame, 5, 2, "When unchecked, comments will be shown in the log but not posted to GitHub PR.")


# --- Control Buttons Frame ---
controls_frame = customtkinter.CTkFrame(left_frame)
controls_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
controls_frame.grid_columnconfigure(0, weight=1) # Center the review button
controls_frame.grid_columnconfigure(1, weight=0) # Token buttons
controls_frame.grid_columnconfigure(2, weight=1) # Center the review button


token_button_frame = customtkinter.CTkFrame(controls_frame) # Frame for save/clear
token_button_frame.grid(row=0, column=1, pady=5, padx=5) # Place in middle column

save_button = customtkinter.CTkButton(token_button_frame, text="Save Tokens", command=save_tokens)
save_button.pack(side="left", padx=5)

clear_button = customtkinter.CTkButton(token_button_frame, text="Clear Tokens", command=clear_tokens, fg_color="red", hover_color="#C4302B")
clear_button.pack(side="left", padx=5)

review_button = customtkinter.CTkButton(controls_frame, text="Run Code Review", command=run_code_review, font=customtkinter.CTkFont(size=14, weight="bold"))
review_button.grid(row=1, column=0, columnspan=3, pady=(10,5)) # Spans all columns to center


# --- Progress Frame ---
progress_frame = customtkinter.CTkFrame(left_frame)
progress_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
progress_frame.grid_columnconfigure(0, weight=1)

# Progress bar with percentage display
progress_container = customtkinter.CTkFrame(progress_frame, fg_color="transparent")
progress_container.grid(row=0, column=0, pady=(0,10), padx=10, sticky="ew")
progress_container.grid_columnconfigure(0, weight=1)

progress_bar = customtkinter.CTkProgressBar(progress_container)
progress_bar.grid(row=0, column=0, sticky="ew", pady=(0,5))
progress_bar.set(0)

# Progress percentage label
progress_percentage_label = customtkinter.CTkLabel(
    progress_container, 
    text="Ready to start", 
    font=customtkinter.CTkFont(size=11, weight="bold"),
    text_color="#FF6F00"
)
progress_percentage_label.grid(row=1, column=0, sticky="ew")


# View buttons frame
view_buttons_frame = customtkinter.CTkFrame(left_frame)
view_buttons_frame.grid(row=5, column=0, padx=10, pady=(0,10), sticky="ew")
view_buttons_frame.grid_columnconfigure(0, weight=1)
view_buttons_frame.grid_columnconfigure(1, weight=1)

# View PR on GitHub button
def open_pr_in_browser():
    global last_pr_url
    if last_pr_url:
        webbrowser.open(last_pr_url)

view_pr_button = customtkinter.CTkButton(view_buttons_frame, text="View PR on GitHub", command=open_pr_in_browser, state="disabled")
view_pr_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

# View latest report button
latest_report_path = None

def open_latest_report():
    global latest_report_path
    
    def open_report_safely(report_path):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(report_path)
            else:  # Unix/Linux/Mac
                file_url = f"file://{os.path.abspath(report_path)}"
                webbrowser.open(file_url)
        except Exception as e:
            # Fallback method
            try:
                abs_path = os.path.abspath(report_path)
                url_path = abs_path.replace('\\', '/')
                if not url_path.startswith('/'):
                    url_path = '/' + url_path
                file_url = f"file://{url_path}"
                webbrowser.open(file_url)
            except Exception as fallback_error:
                messagebox.showerror("Error", f"Failed to open report: {e}")
    
    if latest_report_path and os.path.exists(latest_report_path):
        # Use threading to avoid GIL issues when opening files from GUI context
        import threading
        thread = threading.Thread(target=lambda: open_report_safely(latest_report_path), daemon=True)
        thread.start()
    else:
        # Look for most recent report in the reports directory
        reports_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "reports")
        if os.path.exists(reports_dir):
            reports = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir) if f.startswith("review_report_") and f.endswith(".html")]
            if reports:
                latest_report = max(reports, key=os.path.getmtime)
                # Use threading to avoid GIL issues when opening files from GUI context
                import threading
                thread = threading.Thread(target=lambda: open_report_safely(latest_report), daemon=True)
                thread.start()
            else:
                messagebox.showinfo("No Reports", "No reports found. Please run a review first.")
        else:
            messagebox.showinfo("No Reports", "Reports directory not found. Please run a review first.")

view_report_button = customtkinter.CTkButton(
    view_buttons_frame, 
    text="View Report in Browser", 
    command=open_latest_report, 
    state="disabled"
)
view_report_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


# --- Status and Footer Frame ---
status_footer_frame = customtkinter.CTkFrame(left_frame)
status_footer_frame.grid(row=6, column=0, padx=10, pady=(10,0), sticky="ew")
status_footer_frame.grid_columnconfigure(0, weight=1) # For centering status message

status_message = tk.StringVar()
status_label = customtkinter.CTkLabel(status_footer_frame, textvariable=status_message, font=customtkinter.CTkFont(size=12))
status_label.grid(row=0, column=0, columnspan=2, pady=(0,5))

version_label_bottom = customtkinter.CTkLabel(status_footer_frame, text=f"AI Code Review Tool v{APP_VERSION}", font=customtkinter.CTkFont(size=10, weight="bold"))
version_label_bottom.grid(row=1, column=0, sticky="w", padx=5)

footer_label = customtkinter.CTkLabel(status_footer_frame, text="Built by Ultratax Team, 2025", font=customtkinter.CTkFont(size=10))
footer_label.grid(row=1, column=1, sticky="e", padx=5)


# Activity Log (right) with Review Metrics below
activity_log_frame = customtkinter.CTkFrame(root)
activity_log_frame.grid(row=0, column=1, rowspan=1, padx=(5,10), pady=(5,10), sticky="nsew")
activity_log_frame.grid_rowconfigure(1, weight=3) # 3/4 height for log
activity_log_frame.grid_rowconfigure(3, weight=1) # 1/4 height for metrics
activity_log_frame.grid_columnconfigure(0, weight=1)

# Activity Log Title with Clear Button
activity_log_title_frame = customtkinter.CTkFrame(activity_log_frame, fg_color="transparent")
activity_log_title_frame.grid(row=0, column=0, pady=(0,5), padx=10, sticky="ew")
activity_log_title_frame.grid_columnconfigure(0, weight=1)
activity_log_title_frame.grid_columnconfigure(1, weight=0)

activity_log_title_label = customtkinter.CTkLabel(
    activity_log_title_frame, 
    text="Activity Logs:", 
    font=customtkinter.CTkFont(size=12, weight="bold")
)
activity_log_title_label.grid(row=0, column=0, sticky="w")

# Clear button for activity log
clear_log_button = customtkinter.CTkButton(
    activity_log_title_frame, 
    text="Clear", 
    command=clear_activity_log, 
    width=80,  # Increased from 60
    height=28,  # Increased from 24
    font=customtkinter.CTkFont(size=12)  # Increased from 10
)
clear_log_button.grid(row=0, column=1, sticky="e", padx=5)

# Activity Log Textbox (3/4 height)
activity_log_textbox = customtkinter.CTkTextbox(
    activity_log_frame, 
    height=150
)
activity_log_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
activity_log_textbox.configure(state="normal")

# Review Metrics Section Title
metrics_title_label = customtkinter.CTkLabel(
    activity_log_frame, 
    text="Review Metrics:", 
    font=customtkinter.CTkFont(size=12, weight="bold")
)
metrics_title_label.grid(row=2, column=0, pady=(10,5), padx=10, sticky="w")

# Review Metrics Frame
metrics_frame = customtkinter.CTkFrame(activity_log_frame)
metrics_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,10))
metrics_frame.grid_columnconfigure((0,1), weight=1)
metrics_frame.grid_rowconfigure(0, weight=1)

# Time Taken
time_label = customtkinter.CTkLabel(
    metrics_frame, 
    text="Time Taken:", 
    font=customtkinter.CTkFont(size=12)
)
time_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

time_taken_label = customtkinter.CTkLabel(
    metrics_frame, 
    text="-", 
    font=customtkinter.CTkFont(size=12, weight="bold"),
    text_color="#FF6F00"
)
time_taken_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Estimated Cost
cost_label = customtkinter.CTkLabel(
    metrics_frame, 
    text="Est. Cost:", 
    font=customtkinter.CTkFont(size=12)
)
cost_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

cost_label = customtkinter.CTkLabel(
    metrics_frame, 
    text="-", 
    font=customtkinter.CTkFont(size=12, weight="bold"),
    text_color="#FF6F00"
)
cost_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Try to migrate the token file from old format if needed
migrate_token_file()

# Load tokens on startup
try:
    load_tokens()
    # Add this line:
    load_openarena_token_on_startup()
except Exception as e:
    print(f"Error during token loading on startup: {e}")
    messagebox.showerror("Token Loading Error", 
                       "There was an error loading saved tokens. You may need to re-enter them.\n\n"
                       f"Error details: {str(e)}")

# Theme is now set via customtkinter.set_appearance_mode("Dark") at initialization

# --- AI SETTINGS (Global Variables for Modal Dialog) ---
# Default system prompt
# Update the system prompt to include severity levels
default_system_prompt = """You are a senior Software Developer with 20+ years of experience reviewing code changes for a team of skilled professionals. You understand that over-commenting on trivial matters is counter-productive. Focus ONLY on significant issues in the code that could cause actual bugs, serious performance problems, or major maintainability challenges.

*** CRITICAL DATE FORMAT RULE ***
This codebase uses CCMMDDYY date format (Century, Month, Day, Year) for 8-digit date literals.
Examples: 20010123 = January 23, 2001 | 20123100 = December 31, 2012
NEVER flag 8-digit date literals or date arithmetic as issues - they are CORRECT.
Variables like Base_Date, _GADateExtSnl_, GADateAnnual are CORRECT date constants.
*** END DATE FORMAT RULE ***

FOCUS ONLY ON:
1. ACTUAL Logic Errors that could cause bugs
2. Syntax Errors causing compilation failures  
3. Potential Runtime Errors (crashes, memory leaks)
4. Security Vulnerabilities
5. SIGNIFICANT Performance Issues only
6. MAJOR Maintainability Issues only

DO NOT COMMENT ON:
- Code following best practices
- Trivial stylistic issues
- Test code patterns (EXPECT_EQ, try-catch in tests, etc.)
- Date formats or date arithmetic
- Well-established macros or utility functions

FORMAT: Start each comment with 'Line X: [SEVERITY]:' where SEVERITY is one of:
- CRITICAL: Security vulnerabilities, crashes, memory leaks
- HIGH: Logic errors, bugs, runtime failures
- MEDIUM: Performance issues, maintainability problems
- LOW: Minor suggestions, style improvements

Example: Line 45: [HIGH]: Logic error that could cause null pointer exception...

If no substantial issues found, provide NO comments."""

# Global AI settings variables (to store current values)
ai_settings = {
    "temperature": "0.7",
    "top_p": "1.0", 
    "max_tokens": "16384",
    "system_prompt": default_system_prompt,
    "workflow_id": "7c41c3ab-c214-4394-ba38-9da289975d85",
    "filter_comments": True
}

class AISettingsDialog:
    """Modal dialog for AI settings configuration"""
    
    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings.copy()  # Work with a copy
        self.result = None
        
        try:
            print("Creating AI Settings dialog...")
            # Create modal dialog
            self.dialog = customtkinter.CTkToplevel(parent)
            self.dialog.title("AI Settings Configuration")
            
            # Set proper size and make it resizable  
            dialog_width = 900
            dialog_height = 700
            self.dialog.geometry(f"{dialog_width}x{dialog_height}")
            self.dialog.minsize(800, 600)
            self.dialog.resizable(True, True)
            
            # Center the dialog on screen
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (dialog_width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (dialog_height // 2)
            self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
            self.dialog.transient(parent)
            self.dialog.grab_set()  # Make it modal
            self.dialog.lift()  # Bring to front
            self.dialog.focus_force()  # Force focus
            
            print("Setting up dialog UI...")
            self.setup_ui()
            print("Loading current settings...")
            self.load_current_settings()
            print("Dialog initialization complete!")
            
            # Wait for dialog to close
            self.dialog.wait_window()
            
        except Exception as e:
            print(f"Error in AISettingsDialog.__init__: {e}")
            raise
    
    def setup_ui(self):
        """Setup the UI for the AI settings dialog"""
        
        try:
            print("Creating scrollable main frame...")
            print("Creating main frame with scrollbar...")
            # Create a main container frame
            container = customtkinter.CTkFrame(self.dialog)
            container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Create canvas and scrollbar for scrolling
            canvas = tk.Canvas(container, bg='#212121', highlightthickness=0)
            scrollbar = customtkinter.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
            
            # Create the main frame that will contain all content
            self.main_frame = customtkinter.CTkFrame(canvas)
            
            # Configure scrolling
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack the scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Create window in canvas for the main frame
            canvas_frame = canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
            
            # Bind canvas resize to update frame width and scroll region
            def configure_canvas(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.itemconfig(canvas_frame, width=event.width-20)  # Account for scrollbar
            
            canvas.bind('<Configure>', configure_canvas)
            
            # Update scroll region when main frame changes
            def update_scroll_region():
                self.main_frame.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            self.main_frame.bind('<Configure>', lambda e: update_scroll_region())
            
            # Add mouse wheel scrolling
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind("<MouseWheel>", on_mousewheel)
            
            # Configure main frame
            self.main_frame.grid_columnconfigure(1, weight=1)
            
            print("Adding title...")
            # Title
            title_label = customtkinter.CTkLabel(self.main_frame, text="AI Configuration Settings", 
                                               font=customtkinter.CTkFont(size=20, weight="bold"))
            title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
            
            print("Adding model parameters section...")
            # Model Parameters Section
            model_section_label = customtkinter.CTkLabel(self.main_frame, text="Model Parameters", 
                                                        font=customtkinter.CTkFont(size=16, weight="bold"))
            model_section_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 5))
            
            print("Adding temperature field...")
            # Temperature
            temp_label = customtkinter.CTkLabel(self.main_frame, text="Temperature:", font=customtkinter.CTkFont(weight="bold"))
            temp_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
            self.temperature_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="0.7")
            self.temperature_entry.grid(row=2, column=1, pady=5, padx=10, sticky="ew")
            self.create_info_button(self.main_frame, 2, 2, "Controls AI creativity/randomness (0.0-2.0). Lower values (0.1-0.3) = more focused/deterministic responses. Higher values (0.7-1.0) = more creative/varied responses.")
            
            print("Adding top_p field...")
            # Top P
            top_p_label = customtkinter.CTkLabel(self.main_frame, text="Top P:", font=customtkinter.CTkFont(weight="bold"))
            top_p_label.grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
            self.top_p_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="1.0")
            self.top_p_entry.grid(row=3, column=1, pady=5, padx=10, sticky="ew")
            self.create_info_button(self.main_frame, 3, 2, "Nucleus sampling parameter (0.0-1.0). Controls the cumulative probability cutoff for token selection. 1.0 = consider all tokens, 0.9 = only top 90% probable tokens.")
            
            print("Adding max tokens field...")
            # Max Tokens
            max_tokens_label = customtkinter.CTkLabel(self.main_frame, text="Max Tokens:", font=customtkinter.CTkFont(weight="bold"))
            max_tokens_label.grid(row=4, column=0, sticky="w", padx=(0, 10), pady=5)
            self.max_tokens_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="16384")
            self.max_tokens_entry.grid(row=4, column=1, pady=5, padx=10, sticky="ew")
            self.create_info_button(self.main_frame, 4, 2, "Maximum number of tokens the AI can generate in response (1-200000). Claude 4 Sonnet supports up to 64K output tokens.")
            
            print("Adding system prompt section...")
            # System Prompt Section
            prompt_section_label = customtkinter.CTkLabel(self.main_frame, text="System Prompt", 
                                                         font=customtkinter.CTkFont(size=16, weight="bold"))
            prompt_section_label.grid(row=5, column=0, columnspan=3, sticky="w", pady=(20, 5))
            
            # System Prompt Text Box
            self.system_prompt_textbox = customtkinter.CTkTextbox(self.main_frame, height=150, width=600)
            self.system_prompt_textbox.grid(row=6, column=0, columnspan=3, pady=5, sticky="ew")
            
            print("Adding prompt buttons...")
            # Prompt buttons
            prompt_buttons_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
            prompt_buttons_frame.grid(row=7, column=0, columnspan=3, pady=5, sticky="ew")
            
            reset_prompt_button = customtkinter.CTkButton(prompt_buttons_frame, text="Reset to Default", 
                                                         command=self.reset_prompt, fg_color="#8B4513", hover_color="#A0522D")
            reset_prompt_button.pack(side="left", padx=5)
            
            print("Adding OpenArena section...")
            # OpenArena Section
            openarena_section_label = customtkinter.CTkLabel(self.main_frame, text="OpenArena Configuration", 
                                                            font=customtkinter.CTkFont(size=16, weight="bold"))
            openarena_section_label.grid(row=8, column=0, columnspan=3, sticky="w", pady=(20, 5))
            
            # Workflow ID
            workflow_label = customtkinter.CTkLabel(self.main_frame, text="Workflow ID:", font=customtkinter.CTkFont(weight="bold"))
            workflow_label.grid(row=9, column=0, sticky="w", padx=(0, 10), pady=5)
            self.workflow_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="Enter OpenArena Workflow ID")
            self.workflow_entry.grid(row=9, column=1, pady=5, padx=10, sticky="ew")
            self.create_info_button(self.main_frame, 9, 2, "OpenArena workflow/chain ID for AI processing. This determines which AI model and configuration chain is used for code review.")
            
            print("Adding comment filtering...")
            # Comment filtering
            self.filter_comments_var = tk.BooleanVar(value=True)
            filter_comments_checkbox = customtkinter.CTkCheckBox(self.main_frame, text="Enable post-processing comment filtering", 
                                                                variable=self.filter_comments_var)
            filter_comments_checkbox.grid(row=10, column=0, columnspan=2, sticky="w", pady=5)
            self.create_info_button(self.main_frame, 10, 2, "Apply additional filtering to remove date-related and noise comments")
            
            print("Adding bottom buttons...")
            # Buttons
            button_frame = customtkinter.CTkFrame(self.dialog, fg_color="transparent")
            button_frame.pack(side="bottom", fill="x", padx=20, pady=10)
            
            save_button = customtkinter.CTkButton(button_frame, text="Save & Apply", command=self.save_settings,
                                                fg_color="#2E8B57", hover_color="#3CB371")
            save_button.pack(side="right", padx=5)
            
            cancel_button = customtkinter.CTkButton(button_frame, text="Cancel", command=self.cancel,
                                                   fg_color="#8B4513", hover_color="#A0522D")
            cancel_button.pack(side="right", padx=5)
            
            test_button = customtkinter.CTkButton(button_frame, text="Test Configuration", command=self.test_configuration,
                                                fg_color="#4169E1", hover_color="#6495ED")
            test_button.pack(side="left", padx=5)
            
            reset_button = customtkinter.CTkButton(button_frame, text="Reset to Defaults", command=self.reset_all,
                                                 fg_color="#DC143C", hover_color="#B22222")
            reset_button.pack(side="left", padx=5)
            
            print("UI setup complete!")
            
        except Exception as e:
            print(f"Error in setup_ui: {e}")
            raise
    
    def create_info_button(self, parent, row, column, info_text):
        """Create info button for tooltips"""
        info_button = customtkinter.CTkButton(parent, text="?", width=25, height=25,
                                             command=lambda: messagebox.showinfo("Information", info_text))
        info_button.grid(row=row, column=column, padx=5)
    
    def load_current_settings(self):
        """Load current settings into the dialog"""
        self.temperature_entry.insert(0, self.settings["temperature"])
        self.top_p_entry.insert(0, self.settings["top_p"])
        self.max_tokens_entry.insert(0, self.settings["max_tokens"])
        self.system_prompt_textbox.insert("1.0", self.settings["system_prompt"])
        self.workflow_entry.insert(0, self.settings["workflow_id"])
        self.filter_comments_var.set(self.settings["filter_comments"])
    
    def reset_prompt(self):
        """Reset system prompt to default"""
        self.system_prompt_textbox.delete("1.0", tk.END)
        self.system_prompt_textbox.insert("1.0", default_system_prompt)
    
    def reset_all(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Reset all AI settings to defaults?"):
            self.temperature_entry.delete(0, tk.END)
            self.temperature_entry.insert(0, "0.7")
            self.top_p_entry.delete(0, tk.END)
            self.top_p_entry.insert(0, "1.0")
            self.max_tokens_entry.delete(0, tk.END)
            self.max_tokens_entry.insert(0, "16384")
            self.workflow_entry.delete(0, tk.END)
            self.workflow_entry.insert(0, "7c41c3ab-c214-4394-ba38-9da289975d85")
            self.filter_comments_var.set(True)
            self.reset_prompt()
            self.filter_comments_var.set(True)
            self.reset_prompt()
    
    def test_configuration(self):
        """Test current configuration"""
        config_text = f"""Current API Configuration:

Workflow ID: {self.workflow_entry.get()}
Temperature: {self.temperature_entry.get()}
Top P: {self.top_p_entry.get()}
Max Tokens: {self.max_tokens_entry.get()}
Comment Filtering: {'Enabled' if self.filter_comments_var.get() else 'Disabled'}
System Prompt: {self.system_prompt_textbox.get("1.0", tk.END).strip()[:200]}{'...' if len(self.system_prompt_textbox.get("1.0", tk.END).strip()) > 200 else ''}

This configuration will be used for AI code reviews."""
        
        messagebox.showinfo("Configuration Test", config_text)
    
    def save_settings(self):
        """Save settings and close dialog"""
        self.settings["temperature"] = self.temperature_entry.get()
        self.settings["top_p"] = self.top_p_entry.get()
        self.settings["max_tokens"] = self.max_tokens_entry.get()
        self.settings["system_prompt"] = self.system_prompt_textbox.get("1.0", tk.END).strip()
        self.settings["workflow_id"] = self.workflow_entry.get()
        self.settings["filter_comments"] = self.filter_comments_var.get()
        
        self.result = "save"
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = "cancel"
        self.dialog.destroy()

def open_ai_settings_dialog():
    """Open the AI settings modal dialog"""
    global ai_settings
    
    try:
        print("Opening AI Settings dialog...")
        dialog = AISettingsDialog(root, ai_settings)
        print(f"Dialog closed with result: {dialog.result}")
        
        if dialog.result == "save":
            # Update global settings
            ai_settings.update(dialog.settings)
            save_ai_settings_to_file()
            messagebox.showinfo("Success", "AI settings saved successfully!")
            if 'log_activity' in globals():
                log_activity("? AI Settings updated via Settings dialog")
    except Exception as e:
        print(f"Error opening AI settings dialog: {e}")
        messagebox.showerror("Error", f"Failed to open AI settings dialog: {e}")

def save_ai_settings_to_file():
    """Save AI settings to file"""
    try:
        with open("ai_settings.json", "w", encoding="utf-8") as f:
            json.dump(ai_settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save AI settings: {e}")

def load_ai_settings_from_file():
    """Load AI settings from file"""
    global ai_settings
    try:
        with open("ai_settings.json", "r", encoding="utf-8") as f:
            loaded_settings = json.load(f)
            ai_settings.update(loaded_settings)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load AI settings: {e}")
        return False

# Load settings on startup
load_ai_settings_from_file()

# --- OLD AI SETTINGS (TO BE REMOVED) ---
# --- OLD AI SETTINGS SECTION REMOVED ---
# The AI settings have been moved to a modal dialog accessible from the Settings menu.
# This keeps the main workflow screen clean and uncluttered.

# --- FINAL INITIALIZATION ---
# Try to load the custom theme file, fall back to built-in theme if not found
try:
    # Check multiple possible theme file locations (for development and PyInstaller)
    theme_locations = [
        os.path.join(os.path.dirname(__file__), "blue.json"),  # Development environment
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "AIReview", "blue.json"),  # Relative to root
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "blue.json"),  # Root directory
    ]
    
    # If running from PyInstaller bundle, add those paths too
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
        theme_locations.extend([
            os.path.join(bundle_dir, "AIReview", "blue.json"),  # PyInstaller bundle AIReview folder
            os.path.join(bundle_dir, "blue.json"),  # PyInstaller bundle root
        ])
    
    # Try each location until we find a valid theme file
    theme_found = False
    for theme_path in theme_locations:
        if os.path.exists(theme_path):
            print(f"Found theme file at: {theme_path}")
            customtkinter.set_default_color_theme(theme_path)
            theme_found = True
            break
    
    if not theme_found:
        print(f"Theme file not found in any expected locations, using default theme.")
        customtkinter.set_default_color_theme("blue")  # Fall back to built-in blue theme
except Exception as e:
    print(f"Error loading theme: {e}, falling back to default theme")
    customtkinter.set_default_color_theme("blue")  # Fall back to built-in blue theme


check_for_updates_on_startup()

# Add this line before root.mainloop()
enhanced_startup_sequence()

# Run the Tkinter event loop (now CustomTkinter)
root.mainloop()