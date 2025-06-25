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
time_taken_label = None
cost_label = None
last_pr_url = None  # Store the last reviewed PR URL for the View PR button
view_pr_button = None
repo_combobox = None  # Combobox for repository selection


TOKEN_FILE = "tokens.txt"

# Define the version as a static date-based version
APP_VERSION = "2.0.0" # Incremented patch version for UI enhancements
                      # Versioning format: Major.Minor.Patch
                      # Major: Significant changes or new features
                      # Minor: Backward-compatible changes or improvements
                      
# File to store recently used repositories
RECENT_REPOS_FILE = "recent_repos.json"
# Maximum number of repositories to remember
MAX_RECENT_REPOS = 10
                        # Patch: Bug fixes or minor changes

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
        
    log_activity(f"Post comments to PR: {'Yes' if post_comments else 'No - comments will be shown only in log'}")
    # Update status via activity log and status label
    log_activity("Starting code review...🔍")
    status_message.set("Running code review...🔍")
    if progress_bar:
        progress_bar.set(0)
    if time_taken_label:
        time_taken_label.configure(text="Time Taken: -")
    if cost_label:
        cost_label.configure(text="Est. Cost: -")
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
        time_taken_label.configure(text=f"Time Taken: {duration:.2f}s")
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
        # For the GUI, we add a proper newline character
        activity_log_textbox.insert(tk.END, message + "\n")
        activity_log_textbox.see(tk.END) # Scroll to the end
    root.update_idletasks()


# 🎯 Extract exact modified lines from the patch
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

# 🚀 Send modified lines to AI for review
def filter_review_comments(comments, filename):
    """
    Filter review comments based on specified rules.
    
    Rules:
    1. Skip stdafx.h inclusion comments
    2. Skip macro definition comments in certain contexts
    3. Skip carry value comments
    4. Add recommendations for non-const variables that could be const
    5. Add recommendations against char* usage in favor of std::string/CString
    """
    if not comments:
        return comments
        
    # Simplified: No more filtering here since it's now part of the AI query
    return comments

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
                log_activity("⚠️ External reviewers not available. Using basic review function.")
                pass
                
        # Basic fallback implementation
        import requests
        import time
        
        # Basic API request with Claude v4 parameters
        headers = {
            'Authorization': f'Bearer {openarena_token}',
            'Content-Type': 'application/json'
        }        # Full payload with detailed prompt        
        payload = {
            "query": (
                "Review the following code from:" + diff + ", and provide SEPARATE COMMENTS FOR EACH MODIFIED LINE or logical block from the pull request ONLY where there are actual issues or improvements needed. DO NOT combine all comments into a single block.\n"
                "Focus ONLY on the following aspects that require attention and don't comment on code that already follows best practices:\n"
                "1. ACTUAL Logic Errors: Identify faulty logic that could lead to incorrect behavior or bugs\n"
                "2. Syntax Errors: Point out syntax issues that would cause compilation failures\n"
                "3. Potential Runtime Errors: Flag operations that could lead to crashes, memory leaks, or unexpected behavior\n"
                "4. Security Vulnerabilities: Highlight code that could introduce security risks\n"
                "5. Performance Issues: Identify ONLY SIGNIFICANT performance issues that would impact execution speed\n"
                "6. Serious Maintainability Issues: Comment ONLY on MAJOR readability or maintainability concerns\n"
                  "DO NOT COMMENT ON:\n"
                "1. Code that already follows best practices (like already using const)\n"
                "2. Trivial stylistic issues\n"
                "3. Include statements or namespaces unless they cause actual issues\n"
                "4. Variable names unless they are misleading or confusing\n"
                "5. Test fixtures or macro definitions in test files unless they're broken\n"
                "6. Issues already addressed in other parts of the code\n"
                "7. Things that are just working as expected and don't need improvement\n"
                "8. Common test patterns like try-catch blocks in test code\n"
                "9. Performance micro-optimizations that would be premature optimization\n"
                "10. Assume macros like NLTZ, WD, LO, _IDExtsnRulePct_ are well-tested utility functions or threshold variables\n"
                "11. Do not comment on code in test files unless there's a critical issue\n"
                "12. Functions like AssignCharToInSh or AssignLongToInSh that are for test data setup\n"
                "13. Standard test expectations and assertions like EXPECT_EQ statements in tests\n"
                "14. Try-catch blocks that wrap test function calls, especially in Google Test framework\n"
                "15. Functions that begin with 'test' as they are test functions\n"
                "16. Form reference checks using R() function with EXPECT_EQ statements\n"
                "17. Any EXPECT_EQ assertions comparing calculated values with form references like R(311), R(313), etc.\n"                "IMPORTANT CONTEXT:\n"
                "1. The code is written by experienced developers - only point out non-trivial issues\n"
                "2. For test files (containing 'test' in the name), assume test methodologies are intentional\n"
                "3. Honor defined patterns and conventions already established in the code\n"
                "4. If you're uncertain if something is an issue, DO NOT comment on it\n"
                "5. The codebase uses Google Test framework - test functions and assertions are intentionally structured\n"
                "6. Threshold variables like _IDExtsnRulePct_ are defined elsewhere and should not be questioned\n"
                "7. Functions that begin with 'test' or have names like 'testDoEXTWKS' are intentionally designed test functions\n"
                "8. EXPECT_EQ and similar assertions are standard test patterns and should not be questioned\n"
                "9. When a test function fails, the FAIL() << fail_message pattern is standard and intentional\n"
                "10. Form reference checks using R() function (e.g., R(311), R(313)) in EXPECT_EQ statements are verifying that calculated values match values in form references, which is correct methodology\n"
                "11. Try-catch blocks that call test functions are standard test patterns and not an issue\n"
                
                "IMPORTANT FORMATTING: For each ACTUAL issue found, write a separate paragraph starting with 'Line <line_number>: ' followed by your comment.\n"
                "MAKE SEPARATE COMMENTS for different issues - DO NOT combine multiple issues into one comment.\n"
                "If a file contains no significant issues, DO NOT add any comments for that file.\n"
                "Example format for issues:\n"
                "Line 42: Logical error: The loop condition 'i <= array.size()' will cause out-of-bounds access on the last iteration. Should be 'i < array.size()' instead.\n\n"
                "Line 78: Potential null pointer dereference: 'ptr' is not checked for nullptr before being accessed.\n\n"
            ),
            "workflow_id": "0a654593-da34-4dfe-a6ed-9c8506e31b73",  # OpenArena Chain workflow ID
            "is_persistence_allowed": False,
            "modelparams": {
                "openai_gpt-4o": {
                    "temperature": "0.7",
                    "top_p": "1",
                    "max_tokens": "16384",
                    "enable_reasoning": "true",                    "system_prompt": (
                        "You are a senior Software Developer with 20+ years of experience reviewing code changes for a team of skilled professionals. "
                        "You understand that over-commenting on trivial matters is counter-productive. "
                        "Focus ONLY on significant issues in the code that could cause actual bugs, serious performance problems, or major maintainability challenges. "
                        "Do not comment on code that already follows best practices or working code that doesn't need improvements. "
                        "For test files, assume the testing methodology is intentional unless there's a critical flaw. "
                        "When reviewing code with macros (like NLTZ, WD, LO, _IDExtsnRulePct_), assume these are well-tested utility functions or defined thresholds. "
                        "Do not comment on Google Test framework patterns like try-catch blocks with FAIL() statements, EXPECT_EQ assertions, or test data setup functions. "
                        "Assume all functions that begin with 'test' or have 'test' in their name are properly designed test functions. "
                        "If you find no substantial issues, it is perfectly acceptable and preferable to provide NO comments. "
                        "Only flag issues that experienced developers would truly need help spotting. "
                        "When in doubt, assume the code is correct rather than making a potentially incorrect or trivial comment."
                    )
                }
            }
        }
        
        # Add retry logic for API timeouts
        max_retries = 2
        retry_count = 0
        retry_delay = 5  # seconds
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    log_activity(f"Retry attempt {retry_count}/{max_retries} for OpenArena API call...")
                    
                # Make the API request
                log_activity("Sending request to OpenArena API...")
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
                        model_answer.get('openai_gpt-4o', '') or
                        model_answer.get('vertexai_gemini-2.5-pro', '') or
                        model_answer.get('anthropic_direct.claude-v4-sonnet', '') or
                        model_answer.get('vertexai_palm-2', '')
                    )
                    
                    if not feedback:
                        log_activity("⚠️ Received empty feedback despite 200 status")
                        if retry_count < max_retries:
                            retry_count += 1
                            time.sleep(retry_delay)
                            continue
                        else:
                            log_activity("⚠️ Empty response received after all retries.")
                            return "Line 1: No specific issues detected in the code changes.", 0.0, 0
                    
                    log_activity("💬 AI Code Review Feedback received.")
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
                    
                    log_activity(f"📊 Token usage: {total_tokens} tokens (Prompt: {prompt_tokens}, Completion: {completion_tokens})")
                    log_activity(f"💰 Est. cost: ${cost_usd:.5f} (Input: ${(prompt_tokens/1000)*0.003:.5f}, Output: ${(completion_tokens/1000)*0.015:.5f})")
                    return feedback, cost_usd, total_tokens
                
                elif response.status_code in [504, 408, 502, 503]:  # Timeout and server errors
                    if retry_count < max_retries:
                        log_activity(f"⚠️ OpenArena API timeout/error: {response.status_code}, {response.text}")
                        log_activity(f"Waiting {retry_delay} seconds before retry...")
                        retry_count += 1
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        log_activity(f"❌ Maximum retries reached. Could not get response from OpenArena API.")
                        return f"API Error ({response.status_code}): Could not process review after {max_retries} retries.", 0.0, 0
                        
                else:
                    log_activity(f"⚠️ OpenArena API Error: {response.status_code}, {response.text}")
                    return f"API Error ({response.status_code}): Could not process review.", 0.0, 0
                    
            except Exception as e:
                if retry_count < max_retries:
                    log_activity(f"🚨 API call failed with error: {e}. Retrying in {retry_delay} seconds...")
                    retry_count += 1
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    log_activity(f"🚨 Failed to review code after {max_retries} retries: {e}")
                    return f"Error: {str(e)}", 0.0, 0
        
        return "Error: Failed to get a response from the API after multiple attempts", 0.0, 0
    
    except Exception as e:
        log_activity(f"❌ Unexpected error in review_code function: {str(e)}")
        return f"Error: {str(e)}", 0.0, 0
    
    return ""  # Fallback return if all retries fail

# 💬 Post comments on GitHub PR
def post_comments_on_pr(pr, comments, filename, modified_lines):
    """
    Post comments on a GitHub PR with improved line detection and comment parsing.
    This function parses AI-generated comments and posts them to the appropriate lines in the PR.
    """
    added_comments = set()
    commits = list(pr.get_commits())
    latest_commit = commits[-1]

    # Process comments - split long multi-line comments into individual line comments
    parsed_comments = []
    
    # Join all comments into a single string for processing
    all_comments_text = "\n".join([c.strip() for c in comments if c.strip()])
    
    # Enhanced regex pattern to better capture individual line comments
    # This pattern handles:
    # 1. Standard "Line X: comment" format
    # 2. Captures multi-line comments for a single line
    # 3. Handles comments that might contain line numbers in their content
    line_pattern = re.compile(r'Line\s+(\d+)\s*:\s*(.*?)(?=\n\s*Line\s+\d+\s*:|$)', re.DOTALL)
    matches = line_pattern.findall(all_comments_text)
    
    log_activity(f"Found {len(matches)} parsed comments using primary pattern")
    
    for line_num, content in matches:
        try:
            line_number = int(line_num)
            comment_content = f"Line {line_num}: {content.strip()}"
            parsed_comments.append((line_number, comment_content))
        except ValueError:
            log_activity(f"⚠️ Invalid line number format: {line_num}")
            continue
    
    # If no matches were found, try alternative parsing approaches
    if not parsed_comments and all_comments_text:
        log_activity("⚠️ Could not parse individual line comments. Trying alternative parsing...")
        
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
                    comment_content = block.strip()
                    parsed_comments.append((line_number, comment_content))
                except ValueError:
                    continue
        
        log_activity(f"Found {len(parsed_comments)} parsed comments using alternative pattern")
        
        # If still no parsed comments, try processing each original comment individually
        if not parsed_comments:
            log_activity("⚠️ Still no structured comments. Checking each line individually...")
            for line_content in comments:
                line_content = line_content.strip()
                if not line_content:
                    continue
                    
                # Try to extract line number from beginning of the comment
                matches = re.findall(r'^Line\s+(\d+):', line_content)
                if matches:
                    try:
                        line_number = int(matches[0])
                        parsed_comments.append((line_number, line_content))
                    except ValueError:
                        continue
    
    log_activity(f"Final count: {len(parsed_comments)} parsed comments ready to post")
    
    # Sort comments by line number for more organized posting
    parsed_comments.sort(key=lambda x: x[0])
    
    # Post each comment to GitHub
    for line_position, line_content in parsed_comments:
        # Check if this is a modified line in the PR
        # For added/modified lines, line_position is positive
        # For removed lines, we'd use negative line numbers in our modified_lines dictionary
        
        # First check if this exact line number is in the modified lines
        line_exists = line_position in modified_lines
        
        # If not found, try to find the nearest modified line
        if not line_exists:
            # Get all positive line numbers (added/modified lines)
            positive_lines = [l for l in modified_lines.keys() if l > 0]
            if positive_lines:
                # Find the closest modified line (prefer lines after the comment line)
                closest_lines = sorted(positive_lines, key=lambda l: abs(l - line_position))
                if closest_lines:
                    closest_line = closest_lines[0]
                    # Use the closest line if within a reasonable distance (e.g., 5 lines)
                    if abs(closest_line - line_position) <= 5:
                        log_activity(f"⚙️ Adjusting comment from line {line_position} to closest modified line {closest_line}")
                        line_position = closest_line
                        line_exists = True

        # Skip if we can't find a suitable line to attach the comment to
        if not line_exists:
            log_activity(f"⚠️ Skipping comment for invalid line {line_position} in {filename}. Not found in diff.")
            continue

        # Skip duplicate comments
        if line_content in added_comments:
            log_activity(f"⚠️ Skipping duplicate comment at line {line_position}")
            continue

        try:
            pr.create_review_comment(
                body=line_content,
                commit=latest_commit,
                path=filename,
                line=line_position,
                side="RIGHT"  # Always use RIGHT side to place comments on the new version
            )
            added_comments.add(line_content)
            log_activity(f"✅ Commented on PR #{pr.number}, file {filename}, line {line_position}: {line_content[:50]}...")
        except Exception as e:
            log_activity(f"🚨 Error posting comment on PR #{pr.number}, file {filename}, line {line_position}: {e}")
            # Try with default line if there was an error
            try:
                # Fall back to the first line if we can't post to the specific line
                if modified_lines:
                    default_line = next((l for l in modified_lines.keys() if l > 0), None)
                    if default_line and default_line != line_position:
                        log_activity(f"⚠️ Retrying comment on fallback line {default_line}")
                        pr.create_review_comment(
                            body=f"[Originally for line {line_position}] {line_content}",
                            commit=latest_commit,
                            path=filename,
                            line=default_line,
                            side="RIGHT"
                        )
                        added_comments.add(line_content)
                        log_activity(f"✅ Posted comment to fallback line {default_line}")
            except Exception as fallback_error:
                log_activity(f"🚨 Fallback also failed: {fallback_error}")

    return added_comments

# Function to create HTML report of comments for browser viewing
def create_comments_html_report(comments, pr_url, repo_name, pr_number):
    """Create an HTML file with all review comments for viewing in a browser"""
    # Group comments by file
    comments_by_file = {}
    for comment in comments:
        filename = comment["file"]
        if filename not in comments_by_file:
            comments_by_file[filename] = []
        comments_by_file[filename].append(comment)
    
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
            .content {{ margin-top: 5px; white-space: pre-wrap; }}
            .pr-link {{ margin-bottom: 20px; }}
            .pr-link a {{ color: #0078D7; text-decoration: none; }}
            .pr-link a:hover {{ text-decoration: underline; }}
            .summary {{ margin-top: 20px; padding: 15px; background: #e6f3ff; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>AI Code Review Report</h1>
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
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    report_file = os.path.join(reports_dir, f"review_report_{repo_name.replace('/', '_')}_PR{pr_number}_{timestamp}.html")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log_activity(f"💾 HTML report saved to: {report_file}")
    
    # Store the latest report path globally
    global latest_report_path
    latest_report_path = report_file
    
    # Enable the view report button
    if view_report_button:
        view_report_button.configure(state="normal")
    
    # Open the report in the browser
    webbrowser.open(f"file://{report_file}")
    log_activity(f"🌐 Opening review report in browser...")

def main(repo_name, pr_number, post_comments=True):
    total_files_in_pr = 0
    reviewed_files_count = 0
    all_posted_comments_total_count = 0
    all_comments = []  # Store all comments for potential viewing
    total_cost = 0.0
    total_tokens = 0
    pr_url = None
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

        current_file_num = 0
        for file in files_to_review:
            current_file_num += 1
            log_activity(f"Processing file {current_file_num}/{total_files_in_pr}: {file.filename}")
            
            if progress_bar:
                progress_bar.set(float(current_file_num) / total_files_in_pr)
                root.update_idletasks()

            # Check if the file matches any of the ignore patterns
            if any(fnmatch.fnmatch(file.filename, pattern) for pattern in ignore_patterns):
                log_activity(f"🔍 Skipping file: {file.filename} (matches ignore patterns)")
                continue
            
            reviewed_files_count +=1 # Count as reviewed even if no comments are made, but processing attempted

            diff = file.patch
            log_activity(f"\\n🔍 Reviewing the code for file: {file.filename}\\n{'-'*60}")            # Extract exact modified lines
            modified_lines = get_modified_lines_from_patch(diff)
            
            # Log raw diff for debugging if needed
            if not modified_lines:
                log_activity(f"Raw patch for debugging:\n{diff[:500]}{'...' if len(diff) > 500 else ''}")
                
            # Convert extracted lines into a formatted string for AI review
            diff_text = "\\n".join([f"{line_num}: {content}" for line_num, content in modified_lines.items()])
            
            # Debug output to see what changes were detected
            if modified_lines:
                added_count = sum(1 for k in modified_lines.keys() if k > 0)
                removed_count = sum(1 for k in modified_lines.keys() if k < 0)
                log_activity(f"Found {len(modified_lines)} modified lines in {file.filename} ({added_count} added/modified, {removed_count} removed)")
                log_activity(f"Sample of changes (up to 5 lines):")
                for i, (line_num, content) in enumerate(modified_lines.items()):
                    if i >= 5: break  # Limit to first 5 lines
                    line_type = "Added/Modified" if line_num > 0 else "Removed"
                    line_display = abs(line_num)
                    log_activity(f"  {line_type} line {line_display}: {content[:50]}{'...' if len(content) > 50 else ''}")
            else:
                log_activity(f"⚠️ No modified lines detected in {file.filename} patch")
            
            if not diff_text.strip():
                log_activity(f"No reviewable changes found in {file.filename} after parsing patch.")
                continue            # 🚀 Send modified lines to AI
            review_result = review_code(diff_text, openarena_token)
            
            if isinstance(review_result, tuple) and len(review_result) >= 3:
                comments_text, file_cost, file_tokens = review_result
            else:
                comments_text = review_result
                file_cost = 0.0
                file_tokens = 0
                
            if not comments_text:
                log_activity(f"❌ No AI feedback for {file.filename}")
                continue
                
            # If we received valid feedback but no token count (API limitation),
            # estimate tokens based on the text length (1 token ≈ 4 chars for English text)
            if file_tokens == 0 and comments_text:
                # Estimate input tokens from diff size (roughly)
                estimated_input_tokens = len(diff_text) // 4
                # Estimate output tokens from comments size
                estimated_output_tokens = len(comments_text) // 4
                # Calculate estimated cost
                estimated_cost = calculate_claude_cost(estimated_input_tokens, estimated_output_tokens)
                log_activity(f"⚠️ No token data from API. Estimating based on text length.")
                log_activity(f"📊 Estimated tokens - Input: {estimated_input_tokens}, Output: {estimated_output_tokens}")
                log_activity(f"💰 Estimated cost: ${estimated_cost:.5f}")
                file_cost = estimated_cost
                file_tokens = estimated_input_tokens + estimated_output_tokens
                
            # Track accumulated costs
            total_cost += file_cost
            total_tokens += file_tokens# 💬 Process AI feedback comments            # No need for separate filtering - filtering is now built into the AI query
            comment_lines = comments_text.split('\\n')
            
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
            else:                # Log the comments without posting
                log_activity(f"💬 Comments for {file.filename} (not posted to GitHub):")
                for line in comment_lines:
                    if line.strip():
                        log_activity(f"   {line}")
                # Count the comments even though they're not posted
                all_posted_comments_total_count += len([line for line in comment_lines if line.strip()])
        
        if all_posted_comments_total_count > 0: # Check if any comments were found across all files
            summary_message = f"✅ AI code review complete. Reviewed {reviewed_files_count}/{total_files_in_pr} files. A total of {all_posted_comments_total_count} comments were generated."
            
            # Post summary comment only if posting is enabled
            if post_comments:
                summary_comment = f"{summary_message} Please check and resolve."
                pr.create_issue_comment(summary_comment)
                log_activity(f"\\n🚀 Posted summary issue comment on PR #{pr.number}: {summary_comment}")
            else:
                log_activity(f"\\n📝 {summary_message} (Comments were not posted to GitHub)")
                
            # Create an HTML report for viewing in browser if not posting to GitHub
            if not post_comments and all_comments:
                create_comments_html_report(all_comments, pr_url, repo_name, pr_number)
                
        elif reviewed_files_count > 0: # Files were reviewed but no comments made
            log_activity(f"\\nℹ️ AI code review complete. Reviewed {reviewed_files_count}/{total_files_in_pr} files. No specific issues found by AI requiring comments.")
        else: # No files were reviewed (e.g. all ignored or empty PR)
            log_activity(f"\\nℹ️ No files were reviewed in PR #{pr.number}.")        # Status update handled by run_code_review after this function returns        log_activity(f"🎉 Code review process by AI has been completed. Check PR for details.")
        log_activity(f"💰💰 COST SUMMARY 💰💰")
        log_activity(f"💲 Total estimated cost: ${total_cost:.5f} for {total_tokens} tokens")
        
        # Calculate the input/output cost breakdown (assuming 70/30 split if not detailed)
        input_tokens = int(total_tokens * 0.7)
        output_tokens = total_tokens - input_tokens
        input_cost = (input_tokens / 1000) * 0.003
        output_cost = (output_tokens / 1000) * 0.015
        log_activity(f"📊 Breakdown: Input ${input_cost:.5f} + Output ${output_cost:.5f}")
        log_activity(f"📝 Claude 4 Sonnet pricing: $0.003/1K input tokens, $0.015/1K output tokens")
    except Exception as e:
        log_activity(f"🚨 Error in main function: {e}")
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
            mode_switch.configure(text=f"{'🌙' if new_mode == 'Dark' else '☀️'} {new_mode} Mode")
        except Exception as e:
            print(f"Error updating mode switch: {e}")

customtkinter.set_appearance_mode("Dark")  # Default to Dark mode
customtkinter.set_default_color_theme(os.path.join(os.path.dirname(__file__), "blue.json"))  # Use custom blue theme for professional look

root = customtkinter.CTk() # New CustomTkinter root
root.title("AI Code Review Tool")
root.geometry("800x700") # Adjusted initial geometry, will be resizable

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
        "✨ Release Notes (v2.0.0) ✨\n\n"
        "🎨 Modern UI\n"
        "   • Sleek customtkinter interface with professional blue theme\n"
        "   • Improved layout and enhanced visual elements\n"
        "   • Added background image for improved aesthetics\n\n"
        "📊 Enhanced Features\n"
        "   • Detailed activity logging with real-time updates\n"
        "   • Progress tracking with visual indicators\n"
        "   • Performance metrics and cost estimation\n\n"
        "🔧 Usability Improvements\n"
        "   • Dark/Light mode toggle switch\n"
        "   • One-click PR viewing on GitHub\n"
        "   • Streamlined menu organization\n\n"
        "🚀 Ready to transform your code review process!"
    )
    dialog = customtkinter.CTkToplevel(root)
    dialog.title("Release Notes")
    dialog.geometry("450x400")  # Increased size to fit enhanced content
    dialog.resizable(False, False)
    dialog.grab_set()
    
    # Make dialog modal
    dialog.transient(root)
    dialog.focus_set()
    
    # Content frame
    content_frame = customtkinter.CTkFrame(dialog)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Notes text - using a text widget instead of label for better text handling
    notes_text = customtkinter.CTkTextbox(content_frame, height=300, width=400)
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
        "🤖 AI Code Review Tool 🚀\n\n"
        "💡 What it does:\n"
        "This intelligent application leverages advanced AI to automatically review "
        "code changes in GitHub pull requests. It analyzes modifications, posts helpful "
        "comments, and generates comprehensive review metrics to improve code quality.\n\n"
        "✅ Benefits:\n"
        "• Faster code reviews with consistent quality\n"
        "• Early detection of potential issues\n"
        "• Improved code standards across your team\n"
        "• Time savings for developers and reviewers\n\n"
        "🛠️ Built with pride by the Ultratax Team, 2025"
    )
    dialog = customtkinter.CTkToplevel(root)
    dialog.title("About")
    dialog.geometry("500x400")  # Increased size for enhanced content
    dialog.resizable(False, False)
    dialog.grab_set()
    
    # Make dialog modal
    dialog.transient(root)
    dialog.focus_set()
    
    # Content frame
    content_frame = customtkinter.CTkFrame(dialog)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # About text - using a text widget instead of label for better text handling
    about_text = customtkinter.CTkTextbox(content_frame, height=300, width=450)
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
    webbrowser.open('mailto:velavalapalli.harishsarma@thomsonreuters.com')

# Create standard menu bar (like in the second image)
menu_bar = tk.Menu(root)
root.configure(menu=menu_bar)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New Review", command=lambda: file_menu_callback("New Review"))
file_menu.add_command(label="View Latest Report", command=lambda: open_latest_report())
file_menu.add_separator()
file_menu.add_command(label="Release Notes", command=show_release_notes)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=show_about)
help_menu.add_command(label="Support", command=show_contact)

# File Menu callback function (used in lambda above)
def clear_activity_log():
    """Clear the content of the activity log textbox"""
    if activity_log_textbox:
        activity_log_textbox.delete("1.0", tk.END)
        log_activity("Activity log cleared")

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
        status_message.set("")
        if time_taken_label:
            time_taken_label.configure(text="Time Taken: -")
        if cost_label:
            cost_label.configure(text="Est. Cost: -")
        if view_pr_button:
            view_pr_button.configure(state="disabled")

# --- MAIN UI LAYOUT ---
# Controls (left)
left_frame = customtkinter.CTkFrame(content_frame)
left_frame.grid(row=0, column=0, padx=(10,5), pady=(5,10), sticky="nsew")
left_frame.grid_columnconfigure(0, weight=1)

# --- Settings Frame ---
settings_frame = customtkinter.CTkFrame(left_frame)
settings_frame.grid(row=0, column=0, padx=10, pady=(0,10), sticky="ew")
settings_frame.grid_columnconfigure(0, weight=1)
settings_frame.grid_columnconfigure(1, weight=0)

app_info_label = customtkinter.CTkLabel(
    settings_frame, 
    text=f"AI Code Review Tool v{APP_VERSION}", 
    font=customtkinter.CTkFont(size=14, weight="bold")
)
app_info_label.grid(row=0, column=0, padx=10, pady=5)

# Theme selector with a toggle switch
theme_frame = customtkinter.CTkFrame(settings_frame)
theme_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")

# Create mode switch
# Create the button as a global variable
global mode_switch
mode_switch = customtkinter.CTkButton(
    theme_frame, 
    text="🌙 Dark Mode" if customtkinter.get_appearance_mode() == "Dark" else "☀️ Light Mode",
    command=change_appearance_mode_event,
    width=120,
    height=28
)
mode_switch.pack(side="right", padx=5)

# --- Input Fields Frame ---
input_frame = customtkinter.CTkFrame(left_frame)
input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
input_frame.grid_columnconfigure(1, weight=1)
header_label = customtkinter.CTkLabel(input_frame, text="🤖 AI Code Review Tool", font=customtkinter.CTkFont(size=20, weight="bold"))
header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), padx=10)

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
gh_token_label = customtkinter.CTkLabel(input_frame, text="GitHub Token:")
gh_token_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)
github_token_entry = customtkinter.CTkEntry(input_frame, show="*", placeholder_text="Enter GitHub PAT")
github_token_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
create_ctk_info_button(input_frame, 1, 2, "Enter your GitHub personal access token. Required for GitHub API access.")

# OpenArena Token
oa_token_label = customtkinter.CTkLabel(input_frame, text="OpenArena Token:")
oa_token_label.grid(row=2, column=0, sticky='w', padx=10, pady=5)
openarena_token_entry = customtkinter.CTkEntry(input_frame, show="*", placeholder_text="Enter OpenArena API Token")
openarena_token_entry.grid(row=2, column=1, pady=5, padx=10, sticky="ew")
create_ctk_info_button(input_frame, 2, 2, "Enter your OpenArena token for AI API authentication.")

# OpenArena Link
openarena_link_label = customtkinter.CTkLabel(input_frame, text="OpenArena Platform Link", text_color="blue", cursor="hand2", font=customtkinter.CTkFont(underline=True))
openarena_link_label.grid(row=3, column=0, columnspan=3, pady=(0, 10), padx=10, sticky='w')
openarena_link_label.bind("<Button-1>", open_openarena_link)

# Repository Name
repo_label = customtkinter.CTkLabel(input_frame, text="Repository Name:")
repo_label.grid(row=4, column=0, sticky='w', padx=10, pady=5)

# Create a frame to hold the combobox and integrate it with customtkinter
repo_frame = customtkinter.CTkFrame(input_frame, fg_color="transparent")
repo_frame.grid(row=4, column=1, pady=5, padx=10, sticky="ew")
repo_frame.grid_columnconfigure(0, weight=1)  # Make the combobox expand

# Load recent repositories
recent_repos = load_recent_repos()

# Create a standard ttk Combobox for repository selection
repo_combobox = ttk.Combobox(repo_frame, values=recent_repos)
repo_combobox.pack(fill='x', expand=True)

# Set placeholder text if no repos exist
if recent_repos:
    repo_combobox.set("")  # Empty by default, user needs to select
else:
    repo_combobox.set("owner/repo-name")  # Placeholder text

# For compatibility with existing code
repo_name_entry = repo_combobox

create_ctk_info_button(input_frame, 4, 2, "Select or enter repository name (e.g., 'owner/repo').")

# Pull Request Number
pr_label = customtkinter.CTkLabel(input_frame, text="Pull Request No.:")
pr_label.grid(row=5, column=0, sticky='w', padx=10, pady=5)
pr_number_entry = customtkinter.CTkEntry(input_frame, placeholder_text="Enter PR number")
pr_number_entry.grid(row=5, column=1, pady=5, padx=10, sticky="ew")
create_ctk_info_button(input_frame, 5, 2, "Enter the pull request number.")

# Add a checkbox for posting comments option
post_comments_var = tk.BooleanVar(value=True)
post_comments_checkbox = customtkinter.CTkCheckBox(
    input_frame, 
    text="Post comments to PR", 
    variable=post_comments_var, 
    onvalue=True, 
    offvalue=False
)
post_comments_checkbox.grid(row=6, column=0, columnspan=2, sticky='w', padx=10, pady=5)
create_ctk_info_button(input_frame, 6, 2, "When unchecked, comments will be shown in the log but not posted to GitHub PR.")


# --- Control Buttons Frame ---
controls_frame = customtkinter.CTkFrame(left_frame)
controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
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
progress_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
progress_frame.grid_columnconfigure(0, weight=1)

progress_bar = customtkinter.CTkProgressBar(progress_frame)
progress_bar.grid(row=0, column=0, pady=(0,10), padx=10, sticky="ew")
progress_bar.set(0)


# View buttons frame
view_buttons_frame = customtkinter.CTkFrame(left_frame)
view_buttons_frame.grid(row=4, column=0, padx=10, pady=(0,10), sticky="ew")
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
    if latest_report_path and os.path.exists(latest_report_path):
        webbrowser.open(f"file://{latest_report_path}")
    else:
        # Look for most recent report in the reports directory
        reports_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "reports")
        if os.path.exists(reports_dir):
            reports = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir) if f.startswith("review_report_") and f.endswith(".html")]
            if reports:
                latest_report = max(reports, key=os.path.getmtime)
                webbrowser.open(f"file://{latest_report}")
                return
        messagebox.showinfo("No Report", "No review report found. Run a code review without posting comments to generate a report.")

view_report_button = customtkinter.CTkButton(
    view_buttons_frame, 
    text="View Report in Browser", 
    command=open_latest_report, 
    state="disabled"
)
view_report_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


# --- Status and Footer Frame ---
status_footer_frame = customtkinter.CTkFrame(left_frame)
status_footer_frame.grid(row=5, column=0, padx=10, pady=(10,0), sticky="ew")
status_footer_frame.grid_columnconfigure(0, weight=1) # For centering status message

status_message = tk.StringVar()
status_label = customtkinter.CTkLabel(status_footer_frame, textvariable=status_message, font=customtkinter.CTkFont(size=12))
status_label.grid(row=0, column=0, columnspan=2, pady=(0,5))

version_label_bottom = customtkinter.CTkLabel(status_footer_frame, text=f"Version {APP_VERSION}", font=customtkinter.CTkFont(size=10))
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
    text="Activity Log:", 
    font=customtkinter.CTkFont(size=12, weight="bold")
)
activity_log_title_label.grid(row=0, column=0, sticky="w")

# Clear button for activity log
clear_log_button = customtkinter.CTkButton(
    activity_log_title_frame, 
    text="Clear", 
    command=clear_activity_log, 
    width=60, 
    height=24,
    font=customtkinter.CTkFont(size=10)
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
except Exception as e:
    print(f"Error during token loading on startup: {e}")
    messagebox.showerror("Token Loading Error", 
                       "There was an error loading saved tokens. You may need to re-enter them.\n\n"
                       f"Error details: {str(e)}")

# Theme is now set via customtkinter.set_appearance_mode("Dark") at initialization

# Run the Tkinter event loop (now CustomTkinter)
root.mainloop()