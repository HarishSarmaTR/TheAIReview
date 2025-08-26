#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FILE: AIReview.py

"""
Author: Velavalapalli Harish Sarma (velavalapalli.harishsarma@thomsonreuters.com)
"""

import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Button
import customtkinter # Added customtkinter
import sys
import os
import re
import requests
import webbrowser
import urllib.parse  # For URL encoding email content
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

# Import usage tracking
try:
    from usage_tracker import start_session, log_activity, end_session, get_usage_report, get_comprehensive_report, is_current_user_admin
    HAS_USAGE_TRACKING = True
except ImportError:
    HAS_USAGE_TRACKING = False
    print("Usage tracking module not found. Running without usage tracking.")

# Import GitHub token extractor
try:
    from github_token_extractor import get_github_token_smart, get_github_token_interactive, load_github_token_from_file, create_github_token_instructions
    HAS_GITHUB_EXTRACTOR = True
except ImportError:
    HAS_GITHUB_EXTRACTOR = False
    print("GitHub token extractor not found. Manual token entry required.")

# Import update checker
try:
    from update_checker import check_for_updates_startup, check_for_updates_manual
    HAS_UPDATE_CHECKER = True
except ImportError:
    HAS_UPDATE_CHECKER = False
    print("Update checker not found. Manual update checking required.")

def is_current_user_admin():
    """Check if the current user is an admin - for UI visibility control"""
    try:
        user_info = get_authenticated_user_info()
        admin_identifiers = ["6126175", "harish.sarma", "velavalapalli.harishsarma@thomsonreuters.com"]
        
        # Check system user
        if user_info.get('system_user') in admin_identifiers:
            log_activity(f"[ADMIN CHECK] Admin access granted via system user: {user_info.get('system_user')}")
            return True
        
        # Check SSO email
        if user_info.get('email') and any(admin_id in user_info['email'].lower() for admin_id in admin_identifiers):
            log_activity(f"[ADMIN CHECK] Admin access granted via SSO email: {user_info.get('email')}")
            return True
        
        # Check display name
        if user_info.get('display_name') and "harish" in user_info['display_name'].lower():
            log_activity(f"[ADMIN CHECK] Admin access granted via display name: {user_info.get('display_name')}")
            return True
        
        # Final check using usage tracker admin function
        if HAS_USAGE_TRACKING:
            try:
                if is_current_user_admin():
                    log_activity(f"[ADMIN CHECK] Admin access granted via usage tracker")
                    return True
            except:
                pass
        
        # Regular user detected
        log_activity(f"[SECURITY] Regular user detected: {user_info.get('display_name', 'Unknown')} - admin features hidden")
        return False
    except Exception as e:
        log_activity(f"[ERROR] Admin check failed: {e} - defaulting to regular user")
        return False

def show_usage_report():
    """Show usage report - ADMIN ONLY feature for monitoring tool usage"""
    if not HAS_USAGE_TRACKING:
        messagebox.showinfo("Usage Tracking", "Usage tracking module is not available.")
        return
    
    try:
        # Strict admin check - only allow specific authorized users
        user_info = get_authenticated_user_info()
        
        # Check if user is admin using multiple criteria
        is_admin = False
        admin_identifiers = ["6126175", "harish.sarma", "velavalapalli.harishsarma@thomsonreuters.com"]
        
        # Check system user
        if user_info.get('system_user') in admin_identifiers:
            is_admin = True
        
        # Check SSO email
        if user_info.get('email') and any(admin_id in user_info['email'].lower() for admin_id in admin_identifiers):
            is_admin = True
        
        # Check display name
        if user_info.get('display_name') and "harish" in user_info['display_name'].lower():
            is_admin = True
        
        # Final check using usage tracker admin function
        if HAS_USAGE_TRACKING:
            try:
                is_admin = is_admin or is_current_user_admin()
            except:
                pass
        
        if not is_admin:
            log_activity(f"[SECURITY] Unauthorized usage report access attempt by {user_info.get('display_name', 'Unknown')}")
            messagebox.showerror(
                "Access Denied - Developer Only Feature", 
                "❌ This feature is restricted to the developer only.\n\n"
                "Usage tracking and reporting is for administrative monitoring purposes.\n"
                "Contact the developer if you need access to usage statistics."
            )
            return
        
        log_activity(f"[ADMIN] Usage report accessed by authorized admin: {user_info.get('display_name', 'Unknown')}")
        
        # Get usage report
        report = get_usage_report()
        if not report or 'error' in report:
            messagebox.showinfo("Usage Report", f"No usage data available: {report.get('error', 'Unknown error')}")
            return
        
        # Create report window
        report_window = Toplevel(root)
        report_window.title("🔒 AI Review Tool - Usage Report (Developer Only)")
        report_window.geometry("900x700")
        report_window.configure(bg="#2b2b2b")
        
        # Add security warning header
        security_frame = tk.Frame(report_window, bg="#dc3545", height=40)
        security_frame.pack(fill=tk.X, padx=0, pady=0)
        security_frame.pack_propagate(False)
        
        security_label = tk.Label(security_frame, 
                                 text="🔒 CONFIDENTIAL - DEVELOPER/ADMIN ONLY - DO NOT SHARE", 
                                 bg="#dc3545", fg="white", 
                                 font=("Arial", 10, "bold"))
        security_label.pack(expand=True)
        
        # Create scrollable text widget
        frame = tk.Frame(report_window, bg="#2b2b2b")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, bg="#1e1e1e", fg="#ffffff", font=("Consolas", 9))
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Format and insert report
        report_text = f"""🔒 AI REVIEW TOOL - CONFIDENTIAL USAGE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {user_info.get('display_name', 'Admin')}
{'='*80}

⚠️  IMPORTANT: This report contains confidential usage data for monitoring purposes.
    Do not share this information with unauthorized personnel.

📊 USAGE SUMMARY:
{'='*50}
• Total Sessions: {report.get('total_sessions', 0)}
• Active Users: {len(report.get('unique_users', []))}
• Total Reviews Conducted: {report.get('total_reviews', 0)}
• Repositories Accessed: {len(report.get('repositories_accessed', []))}

👥 USER ACTIVITY BREAKDOWN:
{'='*50}"""
        
        # Add detailed user activity
        if 'user_activity' in report and report['user_activity']:
            for user, activity in report['user_activity'].items():
                report_text += f"""
📋 User: {activity.get('display_name', user)}
   • System ID: {user}
   • Sessions: {activity.get('session_count', 0)}
   • Reviews: {activity.get('review_count', 0)}
   • Last Active: {activity.get('last_active', 'N/A')}
   • Repositories: {', '.join(activity.get('repositories', []))}
"""
        else:
            report_text += "\nNo user activity data available."
        
        # Add repository usage
        if 'repositories_accessed' in report and report['repositories_accessed']:
            report_text += f"\n\n📁 REPOSITORY ACCESS LOG:\n{'='*50}\n"
            for repo in report['repositories_accessed']:
                report_text += f"• {repo}\n"
        
        # Add recent sessions (last 10 for security)
        if 'recent_sessions' in report and report['recent_sessions']:
            report_text += f"\n\n🕒 RECENT SESSIONS (Last 10):\n{'='*50}\n"
            for session in report['recent_sessions'][:10]:
                user = session.get('user_info', {}).get('display_name', 'Unknown')
                start_time = session.get('start_time', 'N/A')
                reviews = session.get('reviews_conducted', 0)
                repos = session.get('repositories_accessed', [])
                report_text += f"{start_time} - {user} ({reviews} reviews) - {', '.join(repos)}\n"
        
        # Add footer warning
        report_text += f"""

{'='*80}
🔒 CONFIDENTIALITY NOTICE:
This report contains sensitive usage information and should be treated as confidential.
Access is logged and monitored. Do not distribute without authorization.

Report generated for: {user_info.get('display_name', 'Admin')}
Generation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}"""
        
        text_widget.insert(tk.END, report_text)
        text_widget.configure(state=tk.DISABLED)
        
        # Add export button with security warning
        button_frame = tk.Frame(report_window, bg="#2b2b2b")
        button_frame.pack(pady=5)
        
        export_button = tk.Button(button_frame, text="📁 Export Report (Secure)", 
                                 command=lambda: export_usage_report_secure(report, user_info),
                                 bg="#FFA500", fg="white", font=("Arial", 10))
        export_button.pack(side=tk.LEFT, padx=5)
        
        close_button = tk.Button(button_frame, text="🔒 Close", 
                                command=report_window.destroy,
                                bg="#DC3545", fg="white", font=("Arial", 10))
        close_button.pack(side=tk.LEFT, padx=5)
        
    except Exception as e:
        log_activity(f"[ERROR] Failed to generate usage report: {e}")
        messagebox.showerror("Error", f"Failed to generate usage report: {e}")

def export_usage_report_secure(report_data, user_info):
    """Export usage report with security logging - ADMIN ONLY"""
    try:
        from tkinter import filedialog
        
        # Add security metadata to export
        secure_report = {
            "export_metadata": {
                "exported_by": user_info.get('display_name', 'Unknown'),
                "exported_at": datetime.now().isoformat(),
                "export_purpose": "Administrative monitoring",
                "confidentiality": "RESTRICTED - DO NOT SHARE"
            },
            "usage_data": report_data
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Usage Report (Confidential)",
            initialname=f"usage_report_confidential_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(secure_report, f, indent=2, default=str)
            
            # Log the export action
            log_activity(f"[SECURITY] Usage report exported by {user_info.get('display_name', 'Unknown')} to {filename}")
            
            messagebox.showinfo("Export Complete", 
                              f"✅ Confidential usage report exported to:\n{filename}\n\n"
                              "⚠️ This file contains sensitive data - handle with care!")
            
    except Exception as e:
        log_activity(f"[ERROR] Failed to export secure usage report: {e}")
        messagebox.showerror("Export Error", f"Failed to export report: {e}")

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
                
                log_activity(f"+ SSO user info loaded: {user_info['display_name']}")
            else:
                log_activity("ℹ️ No SSO user info found, using system username")
                user_info['display_name'] = user_info['system_user']
        else:
            # Fallback to system username
            user_info['display_name'] = user_info['system_user']
            log_activity(f"[USER] Using system username: {user_info['display_name']}")
            
    except Exception as e:
        log_activity(f"[ERROR] Could not get SSO user info: {e}")
        user_info['display_name'] = user_info['system_user']
    
    return user_info

def setup_welcome_section():
    """Setup compact welcome section with user greeting"""
    global welcome_section_frame
    
    # Create compact welcome section frame
    welcome_section_frame = customtkinter.CTkFrame(left_frame, corner_radius=8)
    welcome_section_frame.grid(row=1, column=0, padx=4, pady=1, sticky="ew")
    welcome_section_frame.grid_columnconfigure(0, weight=1)  # Welcome message takes most space
    welcome_section_frame.grid_columnconfigure(1, weight=0)  # Dark mode button stays right

    # Welcome message label - compact
    root.welcome_label = customtkinter.CTkLabel(
        welcome_section_frame, 
        text="Welcome! 👋", 
        font=customtkinter.CTkFont(size=12, weight="bold"),
        text_color="#DC8400"  # Orange color for welcome message
    )
    root.welcome_label.grid(row=0, column=0, pady=2, padx=8, sticky="w")
    
    # Create compact Dark Mode toggle button
    global mode_switch
    current_mode = customtkinter.get_appearance_mode()
    
    # Create a compact toggle button
    mode_switch = customtkinter.CTkButton(
        welcome_section_frame,
        text="🌙" if current_mode == "Dark" else "☀️",
        command=toggle_dark_mode,
        width=60,
        height=22,
        corner_radius=11,  # Rounded corners for toggle look
        fg_color=("#3B8ED0", "#1F6AA5") if current_mode == "Dark" else ("#DBDBDB", "#ABABAB"),
        hover_color=("#36719F", "#144870") if current_mode == "Dark" else ("#C7C7C7", "#949494"),
        text_color="white" if current_mode == "Dark" else "black",
        font=customtkinter.CTkFont(size=12)
    )
    mode_switch.grid(row=0, column=1, padx=4, sticky="e")  # Place on the right side
    
    # Update welcome message with new user info
    update_welcome_message()

def update_welcome_message():
    """Update the welcome message with authenticated user info"""
    try:
        user_info = get_authenticated_user_info()
        
        # Create a more informative welcome message
        if user_info['first_name']:
            welcome_text = f"Welcome {user_info['first_name']}!"
        elif user_info['display_name']:
            welcome_text = f"Welcome {user_info['display_name']}!"
        else:
            welcome_text = f"Welcome {user_info['system_user']}!"
            
        # Update the welcome label if it exists
        if hasattr(root, 'welcome_label') and root.welcome_label:
            root.welcome_label.configure(text=welcome_text)
            log_activity(f"[UI] Welcome message updated: {welcome_text}")
        
        # Log user session info
        if user_info['email']:
            log_activity(f"[USER] User session: {user_info['email']}")
        else:
            log_activity(f"[USER] User session: {user_info['system_user']} (system)")
            
        return user_info
        
    except Exception as e:
        log_activity(f"[ERROR] Error updating welcome message: {e}")
        return None

def extract_github_token_interactive():
    """Open GitHub token creation page for manual token setup"""
    try:
        log_activity("🔧 Preparing GitHub token setup with SSO instructions...")
        
        # Show comprehensive pre-setup instructions first
        pre_instructions = """🔐 GitHub Token Setup Instructions

IMPORTANT: Please follow these steps in order:

📋 STEP 1 - Navigate to Token Settings:
   🌐 Go to GitHub Settings → Developer settings
   🔑 Click "Personal access tokens" 
   📝 Select "Tokens (classic)" (as shown in the red arrow)

🆕 STEP 2 - Create Token:
   ➕ Click "Generate new token (classic)"
   📝 Note: "AI Review Tool Token"
   ⏰ Expiration: 90 days (recommended)
   ✅ Permissions: Check "repo" (Full control of repositories)

🔐 STEP 3 - SSO Authorization (CRITICAL):
   ⚙️ After creating token, you'll see "Configure SSO" button
   🔗 Click "Configure SSO" next to your organization
   ✅ Click "Authorize" to grant SSO access
   ⚠️ Without SSO authorization, the token won't work!

🔒 STEP 4 - Security:
   📋 Copy the token immediately (shown only once!)
   🔐 Store it securely - it will be encrypted locally

Click OK to open GitHub token creation page..."""
        
        result = messagebox.askokcancel("GitHub Token Setup - Read Instructions", pre_instructions)
        
        if not result:
            log_activity("[CANCELLED] User cancelled GitHub token setup")
            return
        
        # Open GitHub token creation page in browser
        github_token_url = "https://github.com/settings/tokens/new"
        webbrowser.open(github_token_url)
        log_activity("[BROWSER] GitHub token creation page opened in browser")
        
        # Show post-opening reminder
        post_instructions = """[BROWSER] GitHub Token Page Opened

Quick Reminder:

1. [NAV] Navigate: Personal access tokens > Tokens (classic)
2. [CREATE] Create: Generate new token (classic)
3. [CONFIG] Configure: Note="AI Review Tool", Expiration=90 days
4. [PERMS] Permissions: Check "repo" scope
5. [GEN] Generate: Click "Generate token"
6. [SSO] SSO: Click "Configure SSO" -> "Authorize" (REQUIRED!)
7. [COPY] Copy: Save the token (shown only once!)
8. [PASTE] Paste: Enter token in the field below

Without SSO authorization, your token will not work with organization repositories!"""
        
        messagebox.showinfo("GitHub Token - Next Steps", post_instructions)
        log_activity("[INFO] GitHub token setup instructions provided")
        
    except Exception as e:
        log_activity(f"? Error opening GitHub token page: {e}")
        messagebox.showerror("Error", f"Failed to open GitHub token page:\n{e}")

def show_token_creation_dialog():
    """Show comprehensive dialog about GitHub token creation with SSO requirements"""
    message = """[SETUP] No existing GitHub token found.

[IMPORTANT] Token must be SSO-authorized to work with organization repositories!

The setup process includes:
� Creating a Personal Access Token (classic)
� Configuring SSO authorization 
� Authorizing access to your organization

Click OK to open GitHub with detailed step-by-step instructions."""
    
    result = messagebox.askokcancel("GitHub Token Setup Required", message)
    
    if result:
        extract_github_token_interactive()
    else:
        log_activity("[CANCELLED] User cancelled GitHub token setup")

def create_new_github_token():
    """Simply redirect to GitHub token creation page"""
    extract_github_token_interactive()

def prompt_for_existing_token():
    """Prompt user to enter an existing GitHub token"""
    from tkinter import simpledialog
    
    instructions = """Please paste your GitHub Personal Access Token below.

[IMPORTANT] Make sure your token is SSO-authorized!
If you get authentication errors, check that you've clicked 
"Configure SSO" -> "Authorize" after creating the token.

If you don't have a token, click Cancel and use the "Get" button."""
    
    messagebox.showinfo("GitHub Token Setup", instructions)
    
    token = simpledialog.askstring(
        "Enter GitHub Token",
        "Paste your SSO-authorized GitHub Personal Access Token:",
        show='*'  # Hide the token input
    )
    
    if token and token.strip():
        # Simple validation - just check length and format
        if len(token.strip()) >= 40 and token.strip().startswith(('ghp_', 'github_pat_')):
            github_token_entry.delete(0, tk.END)
            github_token_entry.insert(0, token.strip())
            log_activity("? GitHub token entered successfully!")
            
            # Show SSO reminder
            sso_reminder = """? Token saved successfully!

[SSO] SSO Reminder: If you encounter authentication errors when accessing 
organization repositories, verify that your token has SSO authorization:

1. Go to GitHub Settings -> Developer settings -> Personal access tokens
2. Find your token and check for "Configure SSO" button
3. Click "Configure SSO" and "Authorize" for your organization

Your token is now encrypted and stored locally."""
            
            messagebox.showinfo("Token Saved - SSO Reminder", sso_reminder)
        else:
            log_activity("? Invalid GitHub token format")
            messagebox.showerror("Invalid Token", 
                "The token format appears invalid. GitHub tokens should:\n"
                "� Be at least 40 characters long\n"
                "- Start with 'ghp_' or 'github_pat_'\n\n"
                "Please check and try again.\n\n"
                "[NOTE] Don't forget to authorize SSO after creating the token!")
    else:
        log_activity("[ERROR] No token provided")
        messagebox.showinfo("Cancelled", "No token was provided.")
    """Extract GitHub token using the interactive extractor"""
    if not HAS_GITHUB_EXTRACTOR:
        messagebox.showinfo("GitHub Token Extractor", 
            "GitHub token extraction module not available.\n\n"
            "Please create a token manually:\n"
            "1. Go to GitHub Settings ? Developer settings ? Personal access tokens\n"
            "2. Click 'Generate new token'\n"
            "3. Select 'repo' scope\n"
            "4. Copy and paste the token here")
        return
    
    # Disable button during extraction
    try:
        # Find the GitHub extract button and disable it
        for widget in github_frame.winfo_children():
            if isinstance(widget, customtkinter.CTkButton) and widget.cget("text") == "Get":
                widget.configure(state="disabled", text="Getting...")
                root.update_idletasks()
                break
    except:
        pass
    
    try:
        log_activity("[EXTRACT] Starting GitHub token extraction process...")
        log_activity("[CHECK] Checking for existing GitHub tokens...")
        
        # Run token extraction in a separate thread
        def extraction_thread():
            try:
                # Use smart token retrieval that checks existing sources first
                token = get_github_token_smart()
                
                # Update UI in main thread
                def update_ui():
                    if token:
                        github_token_entry.delete(0, tk.END)
                        github_token_entry.insert(0, token)
                        log_activity("? GitHub token retrieved successfully!")
                        messagebox.showinfo("Success", 
                            "GitHub token retrieved and saved successfully!\n\n"
                            "The token has been added to the GitHub Token field.")
                    else:
                        log_activity("[NOT_FOUND] No existing valid token found")
                        # Show user choice dialog
                        show_token_creation_dialog()
                    
                    # Re-enable button
                    try:
                        for widget in github_frame.winfo_children():
                            if isinstance(widget, customtkinter.CTkButton):
                                widget.configure(state="normal", text="Get")
                                break
                    except:
                        pass
                
                root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    log_activity(f"? Error during GitHub token extraction: {e}")
                    messagebox.showerror("Error", f"GitHub token extraction failed:\n{e}")
                    try:
                        for widget in github_frame.winfo_children():
                            if isinstance(widget, customtkinter.CTkButton):
                                widget.configure(state="normal", text="Get")
                                break
                    except:
                        pass
                
                root.after(0, show_error)
        
        # Start extraction in background thread
        thread = threading.Thread(target=extraction_thread, daemon=True)
        thread.start()
        
    except Exception as e:
        log_activity(f"? Error starting GitHub token extraction: {e}")
        messagebox.showerror("Error", f"Failed to start GitHub token extraction:\n{e}")
        try:
            for widget in github_frame.winfo_children():
                if isinstance(widget, customtkinter.CTkButton):
                    widget.configure(state="normal", text="Get")
                    break
        except:
            pass

def extract_openarena_token_with_user_info():
    """Extract OpenArena token and user info using TR SSO authentication"""
    url = "https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/11d87e9a-6dcd-4926-80ea-e9fdd07f7e9b"
    
    # Disable button during extraction
    extract_token_button.configure(state="disabled", text="Extracting...")
    root.update_idletasks()
    
    try:
        log_activity("[AUTH] Starting TR SSO authentication with user info...")
        log_activity("[BROWSER] Please complete SSO authentication when browser opens...")
        
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
                        log_activity("? OpenArena token extracted successfully!")
                        
                        # Update welcome message with new user info
                        update_welcome_message()
                        
                        if user_info:
                            if user_info.get('display_name'):
                                log_activity(f"[AUTH] User authenticated: {user_info['display_name']}")
                            if user_info.get('email'):
                                log_activity(f"[EMAIL] Email: {user_info['email']}")
                            if user_info.get('first_name'):
                                log_activity(f"[WELCOME] Welcome {user_info['first_name']}!")
                        
                        success_msg = f"Token extracted successfully!"
                        if user_info and user_info.get('display_name'):
                            success_msg += f"\nAuthenticated as: {user_info['display_name']}"
                        if user_info and user_info.get('email'):
                            success_msg += f"\nEmail: {user_info['email']}"
                            
                        messagebox.showinfo("Success", success_msg)
                        
                        # Save token
                        if save_token_to_file(token):
                            log_activity("[SAVE] Token saved to file for future use")
                    else:
                        log_activity("[ERROR] Failed to extract OpenArena token")
                        messagebox.showerror("Error", "Failed to extract token. Please try manual entry.")
                    
                    # Re-enable button
                    extract_token_button.configure(state="normal", text="Get-Token")
                
                root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    log_activity(f"? Error during extraction: {e}")
                    messagebox.showerror("Error", f"Extraction failed: {e}")
                    extract_token_button.configure(state="normal", text="Get-Token")
                
                root.after(0, show_error)
        
        # Start extraction in background thread
        thread = threading.Thread(target=extraction_thread, daemon=True)
        thread.start()
        
    except Exception as e:
        log_activity(f"? Error starting extraction: {e}")
        messagebox.showerror("Error", f"Failed to start extraction: {e}")
        extract_token_button.configure(state="normal", text="Get-Token")

def restore_user_data():
    """Restore user data from backup if needed"""
    try:
        # Placeholder for user data restoration logic
        log_activity("[RESTORE] User data restoration checked")
    except Exception as e:
        log_activity(f"[ERROR] Error checking user data restoration: {e}")

def backup_user_data():
    """Backup user data for future updates"""
    try:
        # Placeholder for user data backup logic
        log_activity("[BACKUP] User data backup completed")
    except Exception as e:
        log_activity(f"[ERROR] Error backing up user data: {e}")

def setup_enhanced_header():
    """Setup enhanced header with welcome message"""
    # This function is now handled by setup_welcome_section()
    pass

# Enhanced startup sequence
def enhanced_startup_sequence():
    """Enhanced startup sequence with user authentication and data restoration"""
    try:
        # Start usage tracking session first
        if HAS_USAGE_TRACKING:
            try:
                user_info = get_authenticated_user_info()
                has_access, access_message = start_session(user_info)
                log_activity(f"* Access Control: {access_message}")
                
                # Check if user is admin and show admin info
                if is_current_user_admin():
                    log_activity("* Admin privileges detected - full access granted")
                    # You can uncomment the next line to see usage report on startup
                    # log_activity(f"[REPORT] Usage Report:\n{get_usage_report()}")
                
            except PermissionError as e:
                # Access denied - show error and exit
                log_activity(f"? Access Denied: {e}")
                messagebox.showerror("Access Denied", 
                    f"You do not have permission to use this tool.\n\n{e}\n\n"
                    "Please contact the administrator for access.")
                root.quit()
                return
            except Exception as e:
                log_activity(f"[ERROR] Usage tracking error: {e}")
        
        # Restore user data if needed
        restore_user_data()
        
        # Load AI settings from file
        load_ai_settings()
        
        # Setup modern UI first (creates the entry fields)
        setup_modern_ui()
        
        # Setup welcome section
        setup_welcome_section()
        
        # Migrate token file if needed
        migrate_token_file()
        
        # Load tokens (now that UI elements exist)
        load_tokens()
        load_openarena_token_on_startup()
        
        # Update welcome message (will load SSO user info if available)
        root.after(1000, update_welcome_message)
        
        # Update repository combobox with recent repositories
        root.after(1500, update_repo_combobox)
        
        # Check for updates (non-blocking, after UI is ready)
        if HAS_UPDATE_CHECKER:
            root.after(3000, lambda: check_for_updates_startup(APP_VERSION))
        
        # Backup user data for future updates
        root.after(2000, backup_user_data)
        
    except Exception as e:
        print(f"Error during enhanced startup: {e}")
        # Even if there's an error, make sure UI is set up
        try:
            if github_token_entry is None:  # UI not set up yet
                setup_modern_ui()
                setup_welcome_section()
        except:
            pass
        log_activity(f"[WARNING] Startup warning: {str(e)}")
        # Don't show error dialog as it might prevent UI from appearing

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
latest_report_path = None  # Store the latest report path for the View Report button
repo_combobox = None  # Combobox for repository selection

# Global variables for AI settings UI elements
temperature_entry = None
top_p_entry = None
max_tokens_entry = None
system_prompt_textbox = None
workflow_entry = None
filter_comments_var = None

# Global variables for UI frames and buttons
github_frame = None
extract_token_button = None
current_window_height = 640  # Further reduced for better footer visibility


TOKEN_FILE = "tokens.txt"

# Define the version as a static date-based version
APP_VERSION = "2.1.5" # Updated with improved update notification UI and eliminated duplicate popups
                      # Versioning format: Major.Minor.Patch
                      # Major: Significant changes or new features
                      # Minor: Backward-compatible changes or improvements
                      # Patch: Bug fixes or minor changes
                      
# File to store recently used repositories
RECENT_REPOS_FILE = "recent_repos.json"
# Maximum number of repositories to remember
MAX_RECENT_REPOS = 10

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
    
    # First try to load from the encrypted token file
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
                        
                        # Only update UI fields if they exist
                        if github_token_entry is not None:
                            github_token_entry.insert(0, github_token)
                        if openarena_token_entry is not None:
                            openarena_token_entry.insert(0, openarena_token)
                        print("Tokens loaded successfully.")
                    except Exception as e:
                        print(f"Error decrypting tokens: {str(e)}")
                        messagebox.showerror("Token Error", f"Could not decrypt tokens. The token file may be corrupted or was created with a different encryption key.\nError: {str(e)}")
                        # Handle the error by backing up the problematic token file
                        backup_file = f"{TOKEN_FILE}.bak"
                        if os.path.exists(backup_file):
                            try:
                                os.remove(backup_file)
                            except:
                                pass  # Ignore if can't remove backup
                        try:
                            os.rename(TOKEN_FILE, backup_file)
                            print(f"Renamed corrupted token file to {backup_file}")
                        except Exception as rename_error:
                            print(f"Could not rename token file: {rename_error}")
                else:
                    print("Token file does not contain enough tokens.")
        except Exception as e:
            print(f"Error loading tokens: {str(e)}")
            # Don't show error dialog during startup as it might interfere with UI creation
    
    # If GitHub token wasn't loaded and we have the GitHub extractor, try loading from its file
    if HAS_GITHUB_EXTRACTOR and (not github_token or not github_token.strip()):
        try:
            extracted_token = load_github_token_from_file()
            if extracted_token and github_token_entry is not None:
                github_token_entry.delete(0, tk.END)
                github_token_entry.insert(0, extracted_token)
                print("GitHub token loaded from extractor file")
                log_activity("[TOKEN] GitHub token loaded from extractor file")
        except Exception as e:
            print(f"Could not load GitHub token from extractor: {e}")

def load_openarena_token_on_startup():
    """Try to load OpenArena token from TokenExtraction module on startup"""
    if HAS_TOKEN_EXTRACTION:
        try:
            saved_token = load_token_from_file()
            if saved_token and openarena_token_entry is not None and not openarena_token_entry.get():
                openarena_token_entry.insert(0, saved_token)
                log_activity("[TOKEN] OpenArena token loaded from TokenExtraction file")
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
    
    # Update the combobox if it exists
    update_repo_combobox()

def handle_repo_selection(choice):
    """Handle repository selection from dropdown - automatically save to recent repos"""
    if choice and '/' in choice:
        add_recent_repo(choice)
        log_activity(f"[REPO] Repository selected: {choice}")

def add_custom_repository():
    """No longer needed - combobox is editable"""
    pass

def update_repo_combobox():
    """Update the repository combobox with recent repositories"""
    try:
        # Load recent repositories and merge with defaults
        recent_repos = load_recent_repos()
        default_repos = ["tr/cs-prof_tax-us-cstax-1040ST-AL", "tr/cs-prof_tax-us-cstax-1040ST-IL", "tr/cs-prof_tax-us-cstax-1040ST-NE"]
        
        # Combine recent repos with defaults (recent first)
        all_repos = []
        for repo in recent_repos:
            if repo not in all_repos:
                all_repos.append(repo)
        for repo in default_repos:
            if repo not in all_repos:
                all_repos.append(repo)
        
        # Update the dropdown values if it exists - need to find the dropdown via the frame
        # This is a simplified approach since we can't easily reference the dropdown directly
        log_activity(f"[REPOS] Repository list updated with {len(all_repos)} repositories")
            
    except Exception as e:
        print(f"Error updating repository combobox: {e}")

def run_code_review():
    global github_token, openarena_token, last_pr_url
    
    # Enhanced usage tracking - Start session at the beginning
    user_info = get_authenticated_user_info()
    if HAS_USAGE_TRACKING:
        try:
            success, message = start_session(user_info)
            if not success:
                log_activity(f"[ACCESS DENIED] {message}")
                messagebox.showerror("Access Denied", message)
                return
            log_activity(f"[TRACKING] {message}")
        except Exception as e:
            log_activity(f"[WARNING] Usage tracking failed: {e}")
    
    github_token = github_token_entry.get()
    openarena_token = openarena_token_entry.get()
    repo_name = repo_combobox.get()  # Use combobox instead of entry
    pr_number = pr_number_entry.get()
    post_comments = post_comments_var.get()  # Get checkbox state
    
    if not (github_token and openarena_token and repo_name and pr_number):
        messagebox.showerror("Input Error", "Please fill in all fields.")
        if HAS_USAGE_TRACKING:
            log_activity("SYSTEM_ERROR", "Input validation failed - missing required fields")
            end_session()
        return
    
    # Enhanced logging for tracking
    log_activity(f"[REVIEW START] Repository: {repo_name}, PR: {pr_number}, User: {user_info.get('display_name', 'Unknown')}")
    log_activity("[INFO] ⚠️ Usage monitoring is active for administrative purposes")
    
    if HAS_USAGE_TRACKING:
        log_activity("CODE_REVIEW", f"Starting code review for {repo_name} PR #{pr_number}", repo_name, pr_number)
    
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
        filtering = ai_settings.get("filter_comments", False)  # Fixed: Use False as default
        noise_reduction = ai_settings.get("reduce_noise", True)
        log_activity(f"[CONFIG] AI Settings: Temp={temp}, Top-P={top_p}, Max-Tokens={max_tok}, Filtering={'On' if filtering else 'Off'}, Noise Reduction={'On' if noise_reduction else 'Off'}")
    else:
        filtering = ai_settings.get("filter_comments", False)  # Fixed: Use False as default
        noise_reduction = ai_settings.get("reduce_noise", True)
        log_activity(f"[CONFIG] AI Settings: Filtering={'On' if filtering else 'Off'}, Noise Reduction={'On' if noise_reduction else 'Off'}")
    
    # Update status via activity log and status label
    log_activity("Starting code review...")
    
    # Log review activity for usage tracking
    if HAS_USAGE_TRACKING:
        log_activity("CODE_REVIEW", f"Starting code review for {repo_name} PR #{pr_number}", repo_name, pr_number)
    
    status_message.set("Running code review...")
    if progress_bar:
        progress_bar.set(0)
        if progress_percentage_label:
            progress_percentage_label.configure(text="🔄 Initializing...")
    if time_taken_label:
        time_taken_label.configure(text="⏱️ Time: -")
    if cost_label:
        cost_label.configure(text="💰 Cost: -")
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
        time_taken_label.configure(text=f"⏱️ Time: {minutes:02d}:{seconds:02d} min")
    if cost_label:
        if total_cost > 0:
            cost_label.configure(text=f"💰 Cost: ${total_cost:.4f}")
        else:
            # Even if API reports 0 cost, provide an estimate based on response length
            if all_posted_comments_count > 0:
                # Rough estimate: $0.01 per comment as a minimum
                min_cost = all_posted_comments_count * 0.01
                cost_label.configure(text=f"💰 Min. Cost: ${min_cost:.4f}")
            else:
                cost_label.configure(text=f"💰 Cost: ${total_cost:.4f}")
    review_button.configure(state="normal")
    
    if reviewed_files_count > 0:
        log_activity(f"Code review completed. Reviewed {reviewed_files_count}/{total_files} files. Posted {all_posted_comments_count} comments.")
        status_message.set("Completed ✅")
        
        # Enhanced completion tracking
        if HAS_USAGE_TRACKING:
            log_activity("CODE_REVIEW_COMPLETE", f"Completed review - {reviewed_files_count} files, {all_posted_comments_count} comments, ${total_cost:.4f}", repo_name, pr_number)
            end_session()
        
        messagebox.showinfo("Success", f"Code review completed successfully! Reviewed {reviewed_files_count}/{total_files} files.")
        last_pr_url = pr_url
        
        # Save the repository to the recently used list
        add_recent_repo(repo_name)
        if view_pr_button:
            view_pr_button.configure(state="normal")
    elif total_files == 0:
        log_activity("No files found in the PR to review.")
        status_message.set("No files to review")
        
        if HAS_USAGE_TRACKING:
            log_activity("SYSTEM_INFO", "No files found in PR to review")
            end_session()
        
        messagebox.showinfo("Info", "No files found in the PR to review.")
        last_pr_url = None
        if view_pr_button:
            view_pr_button.configure(state="disabled")
    else:
        log_activity("Code review finished. No comments were posted or an error occurred.")
        status_message.set("Finished (No comments/Error)")
        
        if HAS_USAGE_TRACKING:
            log_activity("SYSTEM_WARNING", "Review completed but no comments generated or error occurred")
            end_session()
        
        messagebox.showwarning("Warning", "Code review finished, but no comments were posted or an error occurred during the process.")
        last_pr_url = pr_url
        if view_pr_button:
            view_pr_button.configure(state="normal" if pr_url else "disabled")


# Function to log messages to the activity log and print to console
def log_activity(message):
    try:
        # Handle Unicode characters by encoding them properly
        if isinstance(message, str):
            # Replace problematic Unicode characters with ASCII equivalents for better compatibility
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
        else:
            safe_message = str(message)
        
        # Properly format message for printing (replace literal \n with newlines)
        formatted_message = safe_message.replace('\\n', '\n')
        print(formatted_message) # Keep console logging with proper newlines
        
        if activity_log_textbox:
            # Add timestamp with date to the message for GUI display
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamped_message = f"[{timestamp}] {safe_message}"
            # For the GUI, we add a proper newline character
            activity_log_textbox.insert(tk.END, timestamped_message + "\n")
            activity_log_textbox.see(tk.END) # Scroll to the end
    except Exception as e:
        # Fallback if there are still encoding issues
        fallback_message = f"Log message with encoding issue: {repr(message)}"
        print(fallback_message)
        if activity_log_textbox:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            activity_log_textbox.insert(tk.END, f"[{timestamp}] {fallback_message}\n")
            activity_log_textbox.see(tk.END)
    root.update_idletasks()


# Extract exact modified lines from the patch
def get_modified_lines_from_patch(patch_text):
    """
    Parse a git diff patch to extract added and removed lines.
    Enhanced to handle large files and new files correctly.
    For new files (starting with @@ -0,0), all lines are considered as added.
    For modified files, both added and removed lines are tracked.
    
    Returns a dictionary where:
    - Keys > 0 are added/modified lines (line number in new file)
    - Keys < 0 are removed lines (-line number in old file)
    - Values are the content of those lines
    """
    modified_lines = {}
    current_new_line = None
    current_old_line = None
    is_new_file = False
    
    if not patch_text: # Added safety check
        return modified_lines

    # Handle newline escapes in patch text and normalize line endings
    cleaned_patch = patch_text.replace('\\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
    
    # Enhanced new file detection - check multiple patterns
    if any(pattern in cleaned_patch for pattern in ["@@ -0,0 ", "new file mode", "index 0000000.."]):
        is_new_file = True
        log_activity(f"[DEBUG] Detected new file in patch")
    
    # Split into lines and process
    lines = cleaned_patch.split('\n')
    
    for i, line in enumerate(lines):
        # Match the hunk header to get line numbers
        hunk_match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if hunk_match:
            old_start = int(hunk_match.group(1))
            old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
            new_start = int(hunk_match.group(3))
            new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1
            
            current_old_line = old_start
            current_new_line = new_start
            
            # Enhanced new file detection
            if old_start == 0 and old_count == 0:
                is_new_file = True
                log_activity(f"[DEBUG] New file confirmed by hunk header: @@ -{old_start},{old_count} +{new_start},{new_count} @@")
            
            continue

        if current_new_line is None:
            continue

        # Process different line types
        if line.startswith('+++') or line.startswith('---'):
            # Skip file headers
            continue
        elif line.startswith('diff ') or line.startswith('index '):
            # Skip diff metadata
            continue
        elif line.startswith('+') and not line.startswith('+++'):
            # Added line
            content = line[1:]  # Keep original spacing/indentation
            modified_lines[current_new_line] = content
            current_new_line += 1
            
            # For new files, this is expected behavior
            if is_new_file:
                log_activity(f"[DEBUG] New file line {current_new_line-1}: {content[:50]}{'...' if len(content) > 50 else ''}")
                
        elif line.startswith('-') and not line.startswith('---'):
            # Removed line (only for existing files)
            if not is_new_file and current_old_line is not None:
                content = line[1:]  # Keep original spacing/indentation
                modified_lines[-current_old_line] = content
                current_old_line += 1
        elif line.startswith(' '):
            # Context line - increment both counters
            if current_new_line is not None:
                current_new_line += 1
            if current_old_line is not None and not is_new_file:
                current_old_line += 1
        elif line.strip() == '' and i < len(lines) - 1:
            # Empty line in the middle of patch - might be context
            if current_new_line is not None:
                current_new_line += 1
            if current_old_line is not None and not is_new_file:
                current_old_line += 1
    
    # Enhanced logging for debugging
    if is_new_file:
        added_lines = len([k for k in modified_lines.keys() if k > 0])
        log_activity(f"[DEBUG] New file processed: {added_lines} lines added")
    else:
        added_lines = len([k for k in modified_lines.keys() if k > 0])
        removed_lines = len([k for k in modified_lines.keys() if k < 0])
        log_activity(f"[DEBUG] Modified file processed: {added_lines} lines added, {removed_lines} lines removed")
            
    return modified_lines

# Send modified lines to AI for review
def filter_review_comments(comments, filename):
    """
    Filter review comments based on specified rules.
    
    Only filter out comments that are genuinely not useful while preserving 
    valuable feedback about code quality, security, and maintainability.
    """
    if not comments:
        return comments
    
    # Only filter if filtering is explicitly enabled in settings
    if not ai_settings.get("filter_comments", False):
        return comments
    
    filtered_comments = []
    
    # Only filter out very specific date-related false positives
    # but keep legitimate concerns about date handling
    overly_specific_date_keywords = [
        'ccmmddyy format is', 'ccmmddyy is correct', '20123100 is valid',
        'base_date is correct', 'gadateannual is correct'
    ]
    
    # Only filter out extremely speculative language if noise reduction is enabled
    noise_keywords = [
        'you might possibly want to maybe consider', 
        'this could potentially maybe be',
        'it might possibly be worth considering perhaps'
    ] if ai_settings.get("reduce_noise", False) else []
    
    for comment in comments:
        comment_lower = comment.lower()
        
        # Only filter out very specific false positive patterns
        is_false_positive = any(keyword in comment_lower for keyword in overly_specific_date_keywords)
        
        # Only filter extremely speculative comments
        is_overly_speculative = ai_settings.get("reduce_noise", False) and any(keyword in comment_lower for keyword in noise_keywords)
        
        if is_false_positive:
            log_activity(f"[FILTER] Filtered out false positive: {comment[:100]}...")
            continue
            
        if is_overly_speculative:
            log_activity(f"[FILTER] Filtered out overly speculative comment: {comment[:100]}...")
            continue
            
        # Keep all other comments - they're likely valuable feedback
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
            "query": f"""Review the following MODIFIED CODE LINES ONLY and provide line-specific feedback.

IMPORTANT: These are the ONLY lines that were changed in this PR. Focus your review on these specific changes and their immediate impact.

MODIFIED LINES TO REVIEW:
{diff}

CRITICAL REQUIREMENTS:
1. ONLY review the lines shown above - these are the actual changes made in this PR
2. ONLY provide feedback on real code issues in these specific changed lines
3. For each issue found, use EXACTLY this format: 'Line <number>: [SEVERITY] Description'
4. If no issues found in the changed lines, respond with: 'Line 0: [INFO] No reviewable issues found in modified lines'
5. Use severity levels: [CRITICAL], [HIGH], [MEDIUM], [LOW], [INFO]
6. Focus on: logic errors, security vulnerabilities, performance issues, maintainability problems
7. DO NOT comment on: date literals (20241231, etc.), standard patterns, or unchanged surrounding code

EXAMPLES OF CORRECT FORMAT:
Line 42: [HIGH] Memory leak: Allocated pointer not freed in error path
Line 78: [MEDIUM] Consider using const reference to avoid unnecessary copying
Line 105: [LOW] Variable name could be more descriptive

Provide your review now:""",
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
        return "🚨 Critical"
    
    # High priority issues
    elif any(word in content_lower for word in [
        'logic error', 'incorrect', 'bug', 'failure', 'exception', 'error',
        'undefined behavior', 'infinite loop', 'resource leak', 'null pointer dereference',
        'segmentation fault', 'deadlock', 'race condition', 'buffer overflow',
        'memory leak', 'potential security', 'potential vulnerability'
    ]):
        return "⚠️ High"
    
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
            log_activity(f"❌ Invalid line number format: {line_num}")
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
                    ai_comment = f"[AI] **AI Code Review**\n\n{block.strip()}"
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
                        ai_comment = f"[AI] **AI Code Review**\n\n{line_content}"
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
                            fallback_content = f"[AI] **AI Code Review** (originally for line {line_position})\n\n{line_content}"
                            
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
                        general_comment = f"[AI] **AI Code Review for {filename} (line {line_position}):**\n\n{line_content}"
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
            "severity": severity,
            "code_snippet": comment.get("code_snippet", "")  # Include code snippet
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
            .code-snippet {{ margin-top: 8px; padding: 8px; background: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 12px; white-space: pre-wrap; color: #333; }}
            .snippet-label {{ font-size: 11px; color: #666; margin-bottom: 3px; font-weight: bold; }}
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
            # Build code snippet section if available
            code_snippet_html = ""
            if comment.get("code_snippet") and comment["code_snippet"].strip():
                code_snippet_html = f"""
                <div class="snippet-label">📝 Code Context:</div>
                <div class="code-snippet">{comment["code_snippet"]}</div>"""
            
            html_content += f"""
            <div class="comment">
                <div class="line-number">Line {comment["line_number"]}</div>
                <div class="severity">Severity: {comment["severity"]}</div>
                <div class="content">{comment["content"]}</div>{code_snippet_html}
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
        
        # Define tool file patterns to skip (as requested by user)
        tool_file_patterns = [
            "*/tool/*",      # Any file in a 'tool' directory
            "**/tool/**",    # Any file in any 'tool' subdirectory  
            "*/tools/*",     # Also skip 'tools' directories
            "**/tools/**"    # Any file in any 'tools' subdirectory
        ]

        files_to_review = list(pr.get_files())
        total_files_in_pr = len(files_to_review)
        log_activity(f"Found {total_files_in_pr} files in PR #{pr.number}.")
        
        # Log all files for debugging
        log_activity(f"[DEBUG] All files in PR:")
        for i, file in enumerate(files_to_review, 1):
            log_activity(f"[DEBUG] {i}. {file.filename}")
        
        
        if progress_bar:
            progress_bar.set(0) # Initialize progress bar
            if progress_percentage_label:
                progress_percentage_label.configure(text="0%")

        current_file_num = 0
        for file in files_to_review:
            current_file_num += 1
            log_activity(f"Processing file {current_file_num}/{total_files_in_pr}: {file.filename}")
            
            try:
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
                
                # Check if the file is a tool file (as requested by user)
                if any(fnmatch.fnmatch(file.filename, pattern) for pattern in tool_file_patterns):
                    log_activity(f"[SKIP] Skipping tool file: {file.filename} (tool files don't need code review)")
                    continue
                
                # Enhanced file size and type checking
                file_status = file.status
                file_changes = file.changes
                file_additions = file.additions
                file_deletions = file.deletions
                
                log_activity(f"[INFO] File details - Status: {file_status}, Changes: {file_changes}, Additions: {file_additions}, Deletions: {file_deletions}")
                
                # Handle large files with chunking approach
                MAX_CHANGES_PER_REVIEW = 500  # Configurable limit
                if file_changes > MAX_CHANGES_PER_REVIEW:
                    log_activity(f"[LARGE FILE] File {file.filename} has {file_changes} changes, which exceeds the limit of {MAX_CHANGES_PER_REVIEW}")
                    log_activity(f"[LARGE FILE] Will attempt to process in chunks or skip if too large")
                    
                    # For very large files, we might want to skip or process differently
                    if file_changes > 2000:  # Very large file threshold
                        log_activity(f"[SKIP] File {file.filename} is too large ({file_changes} changes) for effective AI review")
                        continue
                
                # Special handling for new files
                if file_status == "added":
                    log_activity(f"[NEW FILE] Detected new file: {file.filename}")
                    
                    # For new files, check if they're too large
                    if file_additions > 1000:
                        log_activity(f"[LARGE NEW FILE] New file {file.filename} has {file_additions} lines")
                        log_activity(f"[LARGE NEW FILE] Will review first 500 lines for new file overview")
                        # We'll handle this in the patch processing
                
                reviewed_files_count += 1 # Count as reviewed even if no comments are made, but processing attempted

                diff = file.patch
                if not diff:
                    log_activity(f"[SKIP] No patch data available for {file.filename}")
                    # For new files without patch, try to get content differently
                    if file_status == "added":
                        log_activity(f"[NEW FILE] Attempting to get content for new file {file.filename}")
                        try:
                            # Get file content from GitHub
                            file_content = repo.get_contents(file.filename, ref=pr.head.sha)
                            if hasattr(file_content, 'decoded_content'):
                                content = file_content.decoded_content.decode('utf-8')
                                # Create a pseudo-diff for new files
                                lines = content.split('\n')
                                
                                # Limit review to first portion of very large new files
                                if len(lines) > 500:
                                    lines = lines[:500]
                                    log_activity(f"[NEW FILE] Reviewing first 500 lines of large new file {file.filename}")
                                
                                pseudo_diff = '\n'.join([f"+{line}" for line in lines])
                                diff = f"@@ -0,0 +1,{len(lines)} @@\n{pseudo_diff}"
                                log_activity(f"[NEW FILE] Created pseudo-diff for new file {file.filename} ({len(lines)} lines)")
                            else:
                                log_activity(f"[SKIP] Could not decode content for new file {file.filename}")
                                continue
                        except Exception as content_error:
                            log_activity(f"[ERROR] Could not get content for new file {file.filename}: {content_error}")
                            continue
                    else:
                        continue
                    
                # Extract exact modified lines with error handling
                try:
                    modified_lines = get_modified_lines_from_patch(diff)
                except Exception as patch_error:
                    log_activity(f"[ERROR] Failed to parse patch for {file.filename}: {patch_error}")
                    modified_lines = {}
                
                # Log raw diff for debugging if needed
                if not modified_lines:
                    log_activity(f"[DEBUG] No modified lines extracted from patch")
                    log_activity(f"Raw patch for debugging:\n{diff[:500]}{'...' if len(diff) > 500 else ''}")
                    
                # Handle large file chunking for review
                if len(modified_lines) > MAX_CHANGES_PER_REVIEW:
                    log_activity(f"[CHUNKING] File {file.filename} has {len(modified_lines)} modified lines, processing in chunks")
                    
                    # Split modified lines into chunks
                    positive_lines = {k: v for k, v in modified_lines.items() if k > 0}
                    chunks = []
                    chunk_size = MAX_CHANGES_PER_REVIEW // 2  # Smaller chunks for better processing
                    
                    sorted_lines = sorted(positive_lines.items())
                    for i in range(0, len(sorted_lines), chunk_size):
                        chunk = dict(sorted_lines[i:i + chunk_size])
                        chunks.append(chunk)
                    
                    log_activity(f"[CHUNKING] Split into {len(chunks)} chunks for processing")
                    
                    # Process each chunk
                    for chunk_idx, chunk_lines in enumerate(chunks, 1):
                        log_activity(f"[CHUNKING] Processing chunk {chunk_idx}/{len(chunks)} for {file.filename}")
                        
                        # Convert chunk to diff text format
                        chunk_diff_text = "\n".join([f"{line_num}: {content}" for line_num, content in chunk_lines.items()])
                        
                        if chunk_diff_text.strip():
                            # Process this chunk
                            chunk_review_result = review_code(chunk_diff_text, openarena_token)
                            
                            # Handle chunk review result (similar to existing logic)
                            if chunk_review_result and isinstance(chunk_review_result, tuple) and len(chunk_review_result) >= 2:
                                chunk_comments, chunk_cost = chunk_review_result[:2]
                                chunk_tokens = chunk_review_result[2] if len(chunk_review_result) >= 3 else 0
                                
                                total_cost += chunk_cost
                                total_tokens += chunk_tokens
                                
                                if chunk_comments and chunk_comments.strip():
                                    chunk_comment_lines = chunk_comments.split('\n')
                                    
                                    # Process chunk comments (similar to existing logic)
                                    for line in chunk_comment_lines:
                                        if line and line.strip():
                                            # Extract line number and add to all_comments
                                            line_number = "N/A"
                                            line_match = re.search(r'Line\s+(\d+)\s*:', str(line))
                                            if line_match:
                                                line_number = line_match.group(1)
                                            
                                            code_snippet = ""
                                            if line_number != "N/A" and line_number.isdigit():
                                                line_num = int(line_number)
                                                if line_num in chunk_lines:
                                                    code_snippet = chunk_lines[line_num]
                                            
                                            all_comments.append({
                                                "file": file.filename,
                                                "line_number": line_number,
                                                "content": str(line),
                                                "code_snippet": code_snippet,
                                                "chunk": f"{chunk_idx}/{len(chunks)}"  # Mark as chunked
                                            })
                    
                    # Skip the normal processing for chunked files
                    continue
                    
                # Convert extracted lines into a formatted string for AI review
                try:
                    diff_text = "\n".join([f"{line_num}: {content}" for line_num, content in modified_lines.items()])
                except Exception as format_error:
                    log_activity(f"[ERROR] Failed to format diff text for {file.filename}: {format_error}")
                    continue
            
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
                
                # Safely handle the review result
                if review_result is None:
                    log_activity(f"[ERROR] review_code returned None for {file.filename}")
                    continue
                elif isinstance(review_result, tuple) and len(review_result) >= 3:
                    comments_text, file_cost, file_tokens = review_result
                elif isinstance(review_result, tuple) and len(review_result) == 2:
                    comments_text, file_cost = review_result
                    file_tokens = 0
                elif isinstance(review_result, str):
                    comments_text = review_result
                    file_cost = 0.0
                    file_tokens = 0
                else:
                    log_activity(f"[ERROR] Unexpected review_result type for {file.filename}: {type(review_result)}")
                    continue
                    
                if not comments_text or comments_text == "":
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
                comment_lines = comments_text.split('\n')  # Fixed: Use actual newline character
                log_activity(f"[DEBUG] Found {len(comment_lines)} raw comment lines for {file.filename}")
                
                # Apply additional filtering to catch any date-related comments that slipped through (if enabled)
                if ai_settings.get("filter_comments", False):  # Fixed: Use False as default to match ai_settings
                    comment_lines_before = len(comment_lines)
                    comment_lines = filter_review_comments(comment_lines, file.filename)
                    log_activity(f"[DEBUG] Filtering reduced comments from {comment_lines_before} to {len(comment_lines)} for {file.filename}")
                
                # Store the comments for this file (for potential browser viewing)
                if comment_lines:
                    valid_comments = [line for line in comment_lines if line and line.strip()]
                    log_activity(f"[DEBUG] Adding {len(valid_comments)} valid comments to all_comments for {file.filename}")
                    
                    for line in valid_comments:
                        try:
                            # Enhanced line number extraction with multiple patterns
                            line_number = "N/A"
                            
                            # Try primary pattern: "Line X:"
                            line_match = re.search(r'Line\s+(\d+)\s*:', str(line))
                            if line_match:
                                line_number = line_match.group(1)
                            else:
                                # Try alternative patterns if primary fails
                                # Pattern for "Line X " without colon
                                alt_match = re.search(r'Line\s+(\d+)\s+', str(line))
                                if alt_match:
                                    line_number = alt_match.group(1)
                                else:
                                    # If this is a meaningful comment but no line number, use the first modified line as fallback
                                    if any(keyword in str(line).lower() for keyword in ['error', 'bug', 'issue', 'problem', 'warning', 'critical', 'high', 'medium', 'low']):
                                        # Get the first modified line number for this file as a fallback
                                        positive_lines = [l for l in modified_lines.keys() if l > 0]
                                        if positive_lines:
                                            line_number = str(min(positive_lines))
                                            log_activity(f"[DEBUG] Used fallback line {line_number} for comment: {str(line)[:50]}...")
                            
                            # Log what we extracted for debugging
                            if line_number != "N/A":
                                log_activity(f"[DEBUG] Extracted line {line_number} from: {str(line)[:80]}...")
                            else:
                                log_activity(f"[DEBUG] No line number found in: {str(line)[:80]}...")
                            
                            # Get code snippet for this line (as requested by user)
                            code_snippet = ""
                            if line_number != "N/A" and line_number.isdigit():
                                try:
                                    line_num = int(line_number)
                                    if line_num in modified_lines:
                                        code_snippet = modified_lines[line_num]
                                    else:
                                        # Try to get nearby modified lines for context
                                        nearby_lines = [l for l in modified_lines.keys() if abs(l - line_num) <= 2 and l > 0]
                                        if nearby_lines:
                                            closest_line = min(nearby_lines, key=lambda x: abs(x - line_num))
                                            code_snippet = f"(Near line {closest_line}): {modified_lines[closest_line]}"
                                except (ValueError, KeyError):
                                    pass
                            
                            all_comments.append({
                                "file": file.filename, 
                                "line_number": line_number,
                                "content": str(line),
                                "code_snippet": code_snippet  # Add code snippet for HTML report
                            })
                        except Exception as e:
                            log_activity(f"[ERROR] Failed to process comment line: {e}")
                            # Add the comment anyway with N/A line number
                            all_comments.append({
                                "file": file.filename, 
                                "line_number": "N/A",
                                "content": str(line) if line else "",
                                "code_snippet": ""  # No code snippet for failed parsing
                            })
                else:
                    log_activity(f"[DEBUG] No valid comments to add for {file.filename}")
                
                # Post comments if enabled - FIX: Only post if post_comments is True
                if post_comments and comment_lines:
                    posted_comments_for_file = post_comments_on_pr(pr, comment_lines, file.filename, modified_lines)
                    all_posted_comments_total_count += len(posted_comments_for_file)
                    log_activity(f"[POSTED] Posted {len(posted_comments_for_file)} comments to GitHub for {file.filename}")
                else:
                    # Count the comments without posting but don't log content to keep activity log clean
                    comment_count = len([line for line in comment_lines if line.strip()])
                    if comment_count > 0:
                        if post_comments:
                            log_activity(f"[INFO] Found {comment_count} comments for {file.filename} but none were posted")
                        else:
                            log_activity(f"[GENERATED] Found {comment_count} AI comments for {file.filename} (not posted - checkbox unchecked)")
                        all_posted_comments_total_count += comment_count
                        
            except Exception as file_error:
                log_activity(f"[ERROR] Error processing file {file.filename}: {file_error}")
                log_activity(f"[ERROR] Continuing with next file...")
                # Don't let individual file errors crash the entire review process
                continue
        
        # Enhanced summary with skip reasons
        skipped_files = total_files_in_pr - reviewed_files_count
        if skipped_files > 0:
            log_activity(f"\n[SKIP SUMMARY] {skipped_files} files were skipped:")
            log_activity(f"[SKIP SUMMARY] - Tool files (*/tool/*, */tools/*) are automatically skipped")
            log_activity(f"[SKIP SUMMARY] - Project files (*.vcxproj, *.vcxproj.filters) are skipped")
            log_activity(f"[SKIP SUMMARY] - Files without patch data are skipped")
            log_activity(f"[SKIP SUMMARY] - Files with API errors are skipped but logged")
        
        # Generate summary message based on results
        if post_comments and all_posted_comments_total_count > 0:
            summary_message = f"? AI code review complete. Reviewed {reviewed_files_count}/{total_files_in_pr} files. A total of {all_posted_comments_total_count} comments were posted to GitHub PR."
            pr.create_issue_comment(summary_message)
            log_activity(f"\n[SUMMARY] Posted AI summary issue comment on PR #{pr.number}: {summary_message}")
        elif not post_comments and all_posted_comments_total_count > 0:
            summary_message = f"🎯 AI code review complete. Reviewed {reviewed_files_count}/{total_files_in_pr} files. A total of {all_posted_comments_total_count} comments were generated (not posted to GitHub - see HTML report)."
            log_activity(f"\n[SUMMARY] {summary_message}")
        elif all_posted_comments_total_count > 0:
            summary_message = f"🎯 AI code review complete. Reviewed {reviewed_files_count}/{total_files_in_pr} files. A total of {all_posted_comments_total_count} comments were generated."
            log_activity(f"\n[SUMMARY] {summary_message}")
        elif reviewed_files_count > 0:
            summary_message = f"🎯 AI code review complete. Reviewed {reviewed_files_count}/{total_files_in_pr} files. No specific issues found by AI requiring comments."
            log_activity(f"\n{summary_message}")
        else:
            summary_message = f"[INFO] No files were reviewed in PR #{pr.number}."
            log_activity(f"\n{summary_message}")
            
        # Create an HTML report for viewing in browser if comments exist
        log_activity(f"[DEBUG] Report generation: Found {len(all_comments)} total comments")
        if all_comments:
            log_activity(f"[REPORT] Generating HTML report with {len(all_comments)} comments...")
            create_comments_html_report(all_comments, pr_url, repo_name, pr_number)
            log_activity(f"[REPORT] HTML report generation completed")
        else:
            log_activity(f"[DEBUG] No HTML report generated - no comments found")
            # List why no comments were found
            if reviewed_files_count == 0:
                log_activity(f"[DEBUG] Reason: No files were reviewed")
            elif all_posted_comments_total_count == 0:
                log_activity(f"[DEBUG] Reason: No comments were generated by AI")
            else:
                log_activity(f"[DEBUG] Reason: Comments were generated but not stored in all_comments list")
            
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
def toggle_dark_mode():
    """Toggle between dark and light mode with custom button styling"""
    global mode_switch
    
    # Get current mode and toggle
    current_mode = customtkinter.get_appearance_mode()
    new_mode = "Light" if current_mode == "Dark" else "Dark"
    
    # Set the new appearance mode
    customtkinter.set_appearance_mode(new_mode)
    log_activity(f"[THEME] Switched to {new_mode} mode")
    
    # Update the button appearance to reflect the current mode
    if mode_switch:
        if new_mode == "Dark":
            mode_switch.configure(
                text="🌙 Dark",
                fg_color=("#3B8ED0", "#1F6AA5"),
                hover_color=("#36719F", "#144870"),
                text_color="white"
            )
        else:
            mode_switch.configure(
                text="☀️ Light", 
                fg_color=("#DBDBDB", "#ABABAB"),
                hover_color=("#C7C7C7", "#949494"),
                text_color="black"
            )

def change_appearance_mode_event():
    # Get the current state of the toggle checkbox
    if 'mode_switch' in globals() and mode_switch is not None:
        try:
            # If checkbox is checked, use Dark mode; if unchecked, use Light mode
            new_mode = "Dark" if mode_switch.get() else "Light"
        except Exception:
            # Fallback: toggle between current modes
            current_mode = customtkinter.get_appearance_mode()
            new_mode = "Light" if current_mode == "Dark" else "Dark"
    else:
        # Fallback: toggle between current modes
        current_mode = customtkinter.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
    
    # Set the new appearance mode
    customtkinter.set_appearance_mode(new_mode)
    log_activity(f"[THEME] Switched to {new_mode} mode")


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
root.title(f"AI Code Review Tool v{APP_VERSION}")
root.geometry(f"1200x{current_window_height}") # Optimized window height for better UI layout
root.minsize(1000, 580)  # Reduced minimum height for compact layout



# Set the application icon
try:
    # Try to load the icon from multiple possible locations
    icon_locations = [
        os.path.join(os.path.dirname(__file__), "ai.ico"),  # Same directory as script
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai.ico"),  # Parent directory
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "ai.ico"),  # Parent/images
        "ai.ico",  # Current working directory
        "../ai.ico",  # Relative parent
        "../images/ai.ico",  # Relative parent/images
    ]
    
    # If running from PyInstaller bundle, add bundle paths
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
        icon_locations.extend([
            os.path.join(bundle_dir, "ai.ico"),
            os.path.join(bundle_dir, "images", "ai.ico"),
            os.path.join(bundle_dir, "AIReview", "ai.ico"),
        ])
    
    icon_found = False
    for icon_path in icon_locations:
        if os.path.exists(icon_path):
            try:
                # Use absolute path for better compatibility
                abs_icon_path = os.path.abspath(icon_path)
                root.iconbitmap(abs_icon_path)
                log_activity(f"[ICON] Application icon loaded from: {abs_icon_path}")
                icon_found = True
                break
            except Exception as icon_error:
                log_activity(f"[WARN] Failed to load icon from {icon_path}: {icon_error}")
                continue
    
    if not icon_found:
        log_activity("⚠️ Application icon not found in any location, using default")
        # Try alternative method for CustomTkinter
        try:
            # Some systems prefer wm_iconbitmap
            parent_icon = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai.ico")
            if os.path.exists(parent_icon):
                root.wm_iconbitmap(os.path.abspath(parent_icon))
                log_activity(f"🎨 Icon set using wm_iconbitmap: {parent_icon}")
                icon_found = True
        except Exception as wm_error:
            log_activity(f"⚠️ wm_iconbitmap also failed: {wm_error}")
            
except Exception as e:
    log_activity(f"❌ Could not set application icon: {e}")
    # Try one final fallback
    try:
        root.iconbitmap(default="")  # Use system default
    except:
        pass

# Configure grid weights for responsive layout
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)  # Equal weight for both sides
root.grid_rowconfigure(0, weight=1)

# Create regular frame for left side (no scrolling needed with compact layout)
left_frame = customtkinter.CTkFrame(root, width=350)
left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
left_frame.grid_columnconfigure(0, weight=1)

right_frame = customtkinter.CTkFrame(root)
right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_rowconfigure(1, weight=1)

# Global variables for UI elements
github_token_entry = None
openarena_token_entry = None
repo_combobox = None  # Changed from repo_name_entry to repo_combobox
pr_number_entry = None
post_comments_var = None
review_button = None
extract_token_button = None
activity_log_textbox = None
progress_bar = None
progress_percentage_label = None
time_taken_label = None
cost_label = None
view_pr_button = None
view_report_button = None
status_message = None
mode_switch = None
latest_report_path = None

# AI Settings variables
temperature_entry = None
top_p_entry = None
max_tokens_entry = None
system_prompt_textbox = None
workflow_entry = None
filter_comments_var = None

# AI settings with defaults (Enhanced for better review quality)
ai_settings = {
    "temperature": "0.3",    # Lower temperature for more consistent, focused reviews
    "top_p": "0.9",         # Slightly more focused than 1.0
    "max_tokens": "16384",   # Sufficient for detailed reviews
    "workflow_id": "7c41c3ab-c214-4394-ba38-9da289975d85",
    "system_prompt": """You are an expert code reviewer with deep knowledge of software engineering best practices. Your goal is to provide thorough, constructive feedback that helps improve code quality, security, and maintainability.

ANALYZE THE CODE FOR:

[CRITICAL] **CRITICAL ISSUES** (Always flag these):
1. Logic errors, bugs, or incorrect implementations
2. Security vulnerabilities and input validation issues
3. Memory leaks, null pointer dereferences, buffer overflows
4. Race conditions, deadlocks, or concurrency issues
5. Performance bottlenecks or inefficient algorithms
6. Error handling gaps or improper exception management

[QUALITY] **CODE QUALITY ISSUES** (Flag when significant):
1. Code duplication or violating DRY principle
2. Complex functions that should be broken down
3. Poor variable/function naming that affects readability
4. Missing const qualifiers where appropriate
5. Inconsistent coding patterns within the file
6. Hard-coded values that should be configurable

[BEST] **BEST PRACTICES** (Suggest improvements):
1. Missing documentation for complex logic
2. Opportunity to use more efficient data structures
3. Better error messages or logging
4. Code that could benefit from modern language features
5. Suggestions for better maintainability

[IGNORE] **IGNORE THESE** (Don't comment on):
- 8-digit date literals in CCMMDDYY format (20010123, 20123100, etc.)
- Standard date arithmetic with known date constants
- Well-established test patterns (EXPECT_EQ, test fixtures)
- Standard include statements and namespace usage
- Minor formatting inconsistencies

[FORMAT] **RESPONSE FORMAT**:
- For each issue, start with 'Line <number>: [SEVERITY] Description'
- Use severity levels: [CRITICAL], [HIGH], [MEDIUM], [LOW]
- Be specific about the problem and suggest concrete solutions
- Provide separate comments for each distinct issue
- If code looks good, it's fine to provide fewer or no comments

Provide actionable, professional feedback that helps developers write better code.""",
    "filter_comments": False,  # Disabled aggressive filtering
    "reduce_noise": False      # Disabled noise reduction to preserve feedback
}

default_system_prompt = """You are an expert code reviewer with deep knowledge of software engineering best practices. Your goal is to provide thorough, constructive feedback that helps improve code quality, security, and maintainability.

ANALYZE THE CODE FOR:

[CRITICAL] **CRITICAL ISSUES** (Always flag these):
1. Logic errors, bugs, or incorrect implementations
2. Security vulnerabilities and input validation issues
3. Memory leaks, null pointer dereferences, buffer overflows
4. Race conditions, deadlocks, or concurrency issues
5. Performance bottlenecks or inefficient algorithms
6. Error handling gaps or improper exception management

[QUALITY] **CODE QUALITY ISSUES** (Flag when significant):
1. Code duplication or violating DRY principle
2. Complex functions that should be broken down
3. Poor variable/function naming that affects readability
4. Missing const qualifiers where appropriate
5. Inconsistent coding patterns within the file
6. Hard-coded values that should be configurable

[BEST] **BEST PRACTICES** (Suggest improvements):
1. Missing documentation for complex logic
2. Opportunity to use more efficient data structures
3. Better error messages or logging
4. Code that could benefit from modern language features
5. Suggestions for better maintainability

[IGNORE] **IGNORE THESE** (Don't comment on):
- 8-digit date literals in CCMMDDYY format (20010123, 20123100, etc.)
- Standard date arithmetic with known date constants
- Well-established test patterns (EXPECT_EQ, test fixtures)
- Standard include statements and namespace usage
- Minor formatting inconsistencies

[FORMAT] **RESPONSE FORMAT**:
- For each issue, start with 'Line <number>: [SEVERITY] Description'
- Use severity levels: [CRITICAL], [HIGH], [MEDIUM], [LOW]
- Be specific about the problem and suggest concrete solutions
- Provide separate comments for each distinct issue
- If code looks good, it's fine to provide fewer or no comments

**Example responses:**
Line 42: [CRITICAL] Potential buffer overflow: Array access with index 'i' without bounds checking.

Line 78: [HIGH] Memory leak: Allocated pointer 'buffer' is not freed in error path.

Line 105: [MEDIUM] Consider using const reference to avoid unnecessary copying of large object.

Provide actionable, professional feedback that helps developers write better code."""

def show_ai_settings():
    """Show AI Settings configuration window"""
    global temperature_entry, top_p_entry, max_tokens_entry, system_prompt_textbox, workflow_entry, filter_comments_var
    
    # Create AI Settings window
    settings_window = customtkinter.CTkToplevel(root)
    settings_window.title("AI Settings")
    settings_window.geometry("700x550")
    settings_window.transient(root)
    settings_window.grab_set()
    
    # Configure grid
    settings_window.grid_columnconfigure(1, weight=1)
    
    # Title
    title_label = customtkinter.CTkLabel(settings_window, text="AI Configuration Settings", 
                                       font=customtkinter.CTkFont(size=18, weight="bold"))
    title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,10), sticky="w")
    
    # Temperature
    temp_label = customtkinter.CTkLabel(settings_window, text="Temperature (0.0 - 2.0):")
    temp_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
    
    temp_entry = customtkinter.CTkEntry(settings_window, placeholder_text="0.7")
    temp_entry.insert(0, ai_settings.get("temperature", "0.7"))
    temp_entry.grid(row=1, column=1, padx=20, pady=5, sticky="ew")
    
    # Top-p
    top_p_label = customtkinter.CTkLabel(settings_window, text="Top-p (0.0 - 1.0):")
    top_p_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
    
    top_p_entry = customtkinter.CTkEntry(settings_window, placeholder_text="1.0")
    top_p_entry.insert(0, ai_settings.get("top_p", "1.0"))
    top_p_entry.grid(row=2, column=1, padx=20, pady=5, sticky="ew")
    
    # Max Tokens
    max_tokens_label = customtkinter.CTkLabel(settings_window, text="Max Tokens (1 - 200000):")
    max_tokens_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
    
    max_tokens_entry = customtkinter.CTkEntry(settings_window, placeholder_text="16384")
    max_tokens_entry.insert(0, ai_settings.get("max_tokens", "16384"))
    max_tokens_entry.grid(row=3, column=1, padx=20, pady=5, sticky="ew")
    
    # Workflow ID
    workflow_label = customtkinter.CTkLabel(settings_window, text="Workflow ID:")
    workflow_label.grid(row=4, column=0, padx=20, pady=5, sticky="w")
    
    workflow_entry = customtkinter.CTkEntry(settings_window, placeholder_text="Workflow ID")
    workflow_entry.insert(0, ai_settings.get("workflow_id", "7c41c3ab-c214-4394-ba38-9da289975d85"))
    workflow_entry.grid(row=4, column=1, padx=20, pady=5, sticky="ew")
    
    # Reduce Noise option (now handles date-related comments filtering automatically)
    reduce_noise_var = customtkinter.BooleanVar(value=ai_settings.get("reduce_noise", True))
    reduce_noise_checkbox = customtkinter.CTkCheckBox(settings_window, text="[FILTER] Reduce noise (focus on substantial issues, auto-filters date/format comments)", variable=reduce_noise_var)
    reduce_noise_checkbox.grid(row=5, column=0, columnspan=2, padx=20, pady=5, sticky="w")
    
    # System Prompt
    prompt_label = customtkinter.CTkLabel(settings_window, text="System Prompt:")
    prompt_label.grid(row=6, column=0, columnspan=2, padx=20, pady=(10,5), sticky="w")
    
    system_prompt_textbox = customtkinter.CTkTextbox(settings_window, height=150)
    system_prompt_textbox.insert("1.0", ai_settings.get("system_prompt", default_system_prompt))
    system_prompt_textbox.grid(row=7, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
    
    # Buttons
    button_frame = customtkinter.CTkFrame(settings_window)
    button_frame.grid(row=8, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
    # Grid configuration will be set later after the functions are defined
    
    def save_settings():
        try:
            ai_settings["temperature"] = temp_entry.get() or "0.7"
            ai_settings["top_p"] = top_p_entry.get() or "1.0"
            ai_settings["max_tokens"] = max_tokens_entry.get() or "16384"
            ai_settings["workflow_id"] = workflow_entry.get() or "7c41c3ab-c214-4394-ba38-9da289975d85"
            ai_settings["system_prompt"] = system_prompt_textbox.get("1.0", "end-1c") or default_system_prompt
            ai_settings["reduce_noise"] = reduce_noise_var.get()
            
            # Save to file
            try:
                with open("ai_settings.json", "w") as f:
                    json.dump(ai_settings, f, indent=2)
                log_activity("[SUCCESS] AI settings saved successfully")
            except Exception as e:
                log_activity(f"[ERROR] Could not save AI settings to file: {e}")
            
            messagebox.showinfo("Success", "AI settings saved successfully!")
            settings_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {e}")
    
    def reset_settings():
        temp_entry.delete(0, tk.END)
        temp_entry.insert(0, "0.7")
        top_p_entry.delete(0, tk.END)
        top_p_entry.insert(0, "1.0")
        max_tokens_entry.delete(0, tk.END)
        max_tokens_entry.insert(0, "16384")
        workflow_entry.delete(0, tk.END)
        workflow_entry.insert(0, "7c41c3ab-c214-4394-ba38-9da289975d85")
        system_prompt_textbox.delete("1.0", tk.END)
        system_prompt_textbox.insert("1.0", default_system_prompt)
        reduce_noise_var.set(True)
    
    def test_ai_connection():
        """Test the AI connection with current settings"""
        try:
            # Get current settings from the dialog
            temp = temp_entry.get() or "0.7"
            top_p = top_p_entry.get() or "1.0"
            max_tokens = max_tokens_entry.get() or "16384"
            workflow_id = workflow_entry.get() or "7c41c3ab-c214-4394-ba38-9da289975d85"
            
            # Get OpenArena token from main window
            if not openarena_token_entry or not openarena_token_entry.get():
                messagebox.showerror("Test Failed", "Please enter an OpenArena token first in the main window.")
                return
            
            token = openarena_token_entry.get()
            
            # Show testing message
            test_btn.configure(text="Testing...", state="disabled")
            settings_window.update()
            
            # Test payload
            test_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept-Encoding': 'gzip, deflate',
                'User-Agent': 'AICodeReviewTool-Test',
                'Connection': 'keep-alive'
            }
            
            test_payload = {
                "query": "Test connection: Please respond with 'Connection successful'",
                "workflow_id": workflow_id,
                "is_persistence_allowed": False,
                "modelparams": {
                    "anthropic_direct.claude-v4-sonnet": {
                        "temperature": temp,
                        "top_p": top_p,
                        "max_tokens": max_tokens
                    }
                }
            }
            
            import requests
            response = requests.post(
                "https://aiopenarena.gcs.int.thomsonreuters.com/v1/inference",
                headers=test_headers,
                json=test_payload,
                timeout=30
            )
            
            # Re-enable button
            test_btn.configure(text="Test AI Connection", state="normal")
            
            if response.status_code == 200:
                ai_response = response.json()
                result = ai_response.get('result', {})
                answer = result.get('answer', {})
                feedback = (
                    answer.get('anthropic_direct.claude-v4-sonnet', '') or
                    answer.get('openai_gpt-4o', '') or
                    answer.get('vertexai_gemini-2.5-pro', '') or
                    "No response content"
                )
                
                # Show success with some response details
                cost_info = result.get('cost', {})
                token_usage = cost_info.get('token_usage', {})
                total_tokens = token_usage.get('total_tokens', 0)
                
                success_msg = f"? AI Connection Test Successful!\n\n"
                success_msg += f"Response: {feedback[:100]}{'...' if len(feedback) > 100 else ''}\n\n"
                success_msg += f"Settings Used:\n"
                success_msg += f"� Temperature: {temp}\n"
                success_msg += f"� Top-p: {top_p}\n"
                success_msg += f"� Max Tokens: {max_tokens}\n"
                success_msg += f"� Workflow: {workflow_id[:20]}...\n"
                if total_tokens > 0:
                    success_msg += f"� Tokens Used: {total_tokens}"
                
                messagebox.showinfo("Connection Test Successful", success_msg)
                
            elif response.status_code == 401:
                messagebox.showerror("Test Failed", "? Authentication failed.\n\nThe OpenArena token is invalid or expired.\nPlease check your token.")
            else:
                messagebox.showerror("Test Failed", f"? Connection test failed.\n\nStatus Code: {response.status_code}\nResponse: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            test_btn.configure(text="Test AI Connection", state="normal")
            messagebox.showerror("Test Failed", "? Connection test timed out.\n\nThe AI service may be temporarily unavailable.")
        except Exception as e:
            test_btn.configure(text="Test AI Connection", state="normal")
            messagebox.showerror("Test Failed", f"? Connection test failed.\n\nError: {str(e)}")
    
    # Update button frame to have 4 columns
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    button_frame.grid_columnconfigure(3, weight=1)
    
    save_btn = customtkinter.CTkButton(button_frame, text="Save", command=save_settings)
    save_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
    reset_btn = customtkinter.CTkButton(button_frame, text="Reset to Defaults", command=reset_settings)
    reset_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    test_btn = customtkinter.CTkButton(button_frame, text="Test AI Connection", command=test_ai_connection)
    test_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
    
    cancel_btn = customtkinter.CTkButton(button_frame, text="Cancel", command=settings_window.destroy)
    cancel_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

def show_help():
    """Show Help/About window"""
    help_window = customtkinter.CTkToplevel(root)
    help_window.title("Help & About")
    help_window.geometry("500x400")
    help_window.transient(root)
    help_window.grab_set()
    
    # Title
    title_label = customtkinter.CTkLabel(help_window, text="AI Code Review Tool", 
                                       font=customtkinter.CTkFont(size=20, weight="bold"))
    title_label.pack(pady=(20,10))
    
    # Version
    version_label = customtkinter.CTkLabel(help_window, text=f"Version: {APP_VERSION}", 
                                         font=customtkinter.CTkFont(size=14))
    version_label.pack(pady=5)
    
    # Description
    desc_text = customtkinter.CTkTextbox(help_window, height=200)
    desc_text.pack(padx=20, pady=10, fill="both", expand=True)
    
    help_content = f"""🚀 AI Code Review Tool v{APP_VERSION}

✨ OVERVIEW
This cutting-edge application provides AI-powered code review for GitHub pull requests using OpenArena's Claude 4 Sonnet model, delivering intelligent insights to enhance code quality and development workflows.

🎯 KEY FEATURES
• 🔍 Automated GitHub PR analysis with smart file detection
• 🧠 AI-powered code review comments with severity classification
• 🔐 Secure token management with encryption
• 📊 Beautiful HTML report generation with analytics
• 🔑 SSO authentication support for enterprise environments
• ⚙️ Fully customizable AI settings and prompts

📋 QUICK START GUIDE
1. 🔑 Enter your GitHub personal access token
2. 🎫 Get or enter your OpenArena token  
3. 📁 Specify the repository (owner/repo format)
4. 🔢 Enter the PR number to review
5. 🚀 Click "Start Review" to begin analysis

🎯 SMART ANALYSIS
The tool intelligently analyzes all modified files in your PR and generates contextual AI comments highlighting potential issues, security vulnerabilities, performance improvements, and best practice suggestions.

👥 DEVELOPMENT TEAM
Built with ❤️ by Thomson Reuters • UltraTax Team
© 2025 Thomson Reuters - Licensed for internal use only

🔧 Need help? Use the feedback feature to contact our engineering team!"""
    
    desc_text.insert("1.0", help_content)
    desc_text.configure(state="disabled")
    
    # Close button
    close_btn = customtkinter.CTkButton(help_window, text="Close", command=help_window.destroy)
    close_btn.pack(pady=10)

def show_feedback():
    """Show feedback submission window"""
    feedback_window = customtkinter.CTkToplevel(root)
    feedback_window.title("Submit Feedback")
    feedback_window.geometry("650x650")  # Increased height from 500 to 650
    feedback_window.transient(root)
    feedback_window.grab_set()
    feedback_window.resizable(True, True)  # Allow resizing if needed
    
    # Title
    title_label = customtkinter.CTkLabel(feedback_window, text="📧 Submit Feedback", 
                                       font=customtkinter.CTkFont(size=20, weight="bold"))
    title_label.pack(pady=(20,10))
    
    # Subtitle
    subtitle_label = customtkinter.CTkLabel(feedback_window, 
                                          text="Help us improve the AI Code Review Tool",
                                          font=customtkinter.CTkFont(size=14))
    subtitle_label.pack(pady=5)
    
    # Feedback type selection
    type_frame = customtkinter.CTkFrame(feedback_window)
    type_frame.pack(padx=20, pady=10, fill="x")
    
    type_label = customtkinter.CTkLabel(type_frame, text="Feedback Type:")
    type_label.pack(anchor="w", padx=10, pady=(10,5))
    
    feedback_type = customtkinter.CTkOptionMenu(type_frame, 
                                               values=["Bug Report", "Feature Request", "UI/UX Improvement", "Performance Issue", "General Feedback"])
    feedback_type.pack(padx=10, pady=(0,10), fill="x")
    feedback_type.set("General Feedback")
    
    # Priority selection
    priority_label = customtkinter.CTkLabel(type_frame, text="Priority:")
    priority_label.pack(anchor="w", padx=10, pady=(5,5))
    
    priority = customtkinter.CTkOptionMenu(type_frame, 
                                          values=["Low", "Medium", "High", "Critical"])
    priority.pack(padx=10, pady=(0,10), fill="x")
    priority.set("Medium")
    
    # Feedback text area
    text_label = customtkinter.CTkLabel(feedback_window, text="Detailed Feedback:")
    text_label.pack(anchor="w", padx=20, pady=(10,5))
    
    feedback_text = customtkinter.CTkTextbox(feedback_window, height=180)  # Increased from 150 to 180
    feedback_text.pack(padx=20, pady=5, fill="both", expand=True)
    feedback_text.insert("1.0", "Please describe your feedback in detail...")
    
    # User info frame
    user_frame = customtkinter.CTkFrame(feedback_window)
    user_frame.pack(padx=20, pady=10, fill="x")
    user_frame.grid_columnconfigure(1, weight=1)
    
    # Email (optional)
    email_label = customtkinter.CTkLabel(user_frame, text="Email (optional):")
    email_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    email_entry = customtkinter.CTkEntry(user_frame, placeholder_text="your.email@tr.com")
    email_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    
    def submit_feedback():
        """Submit feedback by opening Outlook with pre-filled email to engineering team"""
        try:
            # Get feedback data
            feedback_type_value = feedback_type.get()
            priority_value = priority.get()
            feedback_content = feedback_text.get("1.0", "end-1c")
            user_email = email_entry.get()
            current_user = os.getenv('USERNAME', 'Unknown')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Engineering team email addresses
            engineering_team = [
                "Velavalapalli.HarishSarma@thomsonreuters.com",
                "Ravi.Bitra@thomsonreuters.com",
                "kalyani.kandunuri@thomsonreuters.com"
            ]
            
            # Create email recipients string
            to_emails = ";".join(engineering_team)
            
            # Create email subject
            subject = f"AI Code Review Tool Feedback - {feedback_type_value} ({priority_value} Priority)"
            
            # Create email body with structured content
            body = f"""Hi Team,

I have feedback for the AI Code Review Tool:

FEEDBACK DETAILS:
================
Type: {feedback_type_value}
Priority: {priority_value}
Submitted by: {current_user}
Contact Email: {user_email if user_email else 'Not provided'}
App Version: {APP_VERSION}
Date/Time: {timestamp}

FEEDBACK CONTENT:
================
{feedback_content}

Please review and consider this feedback for future improvements.

Best regards,
{current_user}

---
This email was generated automatically by the AI Code Review Tool feedback system.
"""
            
            # Encode the email components for URL
            subject_encoded = urllib.parse.quote(subject)
            body_encoded = urllib.parse.quote(body)
            to_encoded = urllib.parse.quote(to_emails)
            
            # Create Outlook mailto URL
            mailto_url = f"mailto:{to_encoded}?subject={subject_encoded}&body={body_encoded}"
            
            # Also save feedback locally as backup
            feedback_data = {
                "timestamp": timestamp,
                "type": feedback_type_value,
                "priority": priority_value,
                "feedback": feedback_content,
                "email": user_email,
                "app_version": APP_VERSION,
                "user": current_user,
                "sent_to": engineering_team
            }
            
            feedback_file = "feedback_submissions.json"
            feedbacks = []
            
            if os.path.exists(feedback_file):
                try:
                    with open(feedback_file, "r") as f:
                        feedbacks = json.load(f)
                except:
                    feedbacks = []
            
            feedbacks.append(feedback_data)
            
            with open(feedback_file, "w") as f:
                json.dump(feedbacks, f, indent=2)
            
            # Open Outlook with pre-filled email
            try:
                webbrowser.open(mailto_url)
                log_activity(f"[EMAIL] Opened Outlook with feedback email to engineering team")
                
                # Show success message
                success_window = customtkinter.CTkToplevel(feedback_window)
                success_window.title("Feedback Email Opened")
                success_window.geometry("450x250")
                success_window.transient(feedback_window)
                success_window.grab_set()
                
                success_label = customtkinter.CTkLabel(success_window, 
                                                     text="[EMAIL] Outlook Email Opened!",
                                                     font=customtkinter.CTkFont(size=16, weight="bold"))
                success_label.pack(pady=20)
                
                info_label = customtkinter.CTkLabel(success_window, 
                                                  text=f"An email has been prepared in Outlook with:\n\n" +
                                                       f"To: {', '.join(engineering_team)}\n" +
                                                       f"Subject: {feedback_type_value} Feedback\n\n" +
                                                       f"Please review and send the email.",
                                                  font=customtkinter.CTkFont(size=12))
                info_label.pack(pady=10)
                
                ok_btn = customtkinter.CTkButton(success_window, text="OK", 
                                               command=lambda: [success_window.destroy(), feedback_window.destroy()])
                ok_btn.pack(pady=20)
                
            except Exception as e:
                # Fallback if Outlook opening fails
                log_activity(f"[ERROR] Failed to open Outlook: {e}")
                messagebox.showinfo("Email Addresses", 
                                   f"Could not open Outlook automatically.\n\n" +
                                   f"Please send your feedback manually to:\n" +
                                   f"{chr(10).join(engineering_team)}\n\n" +
                                   f"Subject: {subject}\n\n" +
                                   f"Your feedback has also been saved locally.")
                feedback_window.destroy()
            
        except Exception as e:
            log_activity(f"[ERROR] Failed to submit feedback: {e}")
            messagebox.showerror("Error", f"Failed to prepare feedback email: {str(e)}")
            
            log_activity(f"[FEEDBACK] Feedback submitted: {feedback_data['type']} - {feedback_data['priority']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit feedback: {str(e)}")
    
    # Buttons frame
    button_frame = customtkinter.CTkFrame(feedback_window)
    button_frame.pack(padx=20, pady=(15, 20), fill="x")  # Increased top padding from 10 to 15, bottom to 20
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    
    cancel_btn = customtkinter.CTkButton(button_frame, text="Cancel", 
                                       command=feedback_window.destroy,
                                       height=32)  # Made buttons taller
    cancel_btn.grid(row=0, column=0, padx=5, pady=8, sticky="ew")  # Increased pady from 5 to 8
    
    submit_btn = customtkinter.CTkButton(button_frame, text="📧 Send Email to Team", 
                                       command=submit_feedback,
                                       height=32)  # Made buttons taller
    submit_btn.grid(row=0, column=1, padx=5, pady=8, sticky="ew")  # Increased pady from 5 to 8

def load_ai_settings():
    """Load AI settings from file"""
    try:
        if os.path.exists("ai_settings.json"):
            with open("ai_settings.json", "r") as f:
                saved_settings = json.load(f)
                ai_settings.update(saved_settings)
                log_activity("[CONFIG] AI settings loaded from file")
    except Exception as e:
        log_activity(f"[WARN] Could not load AI settings: {e}")

def setup_modern_ui():
    """Setup the modern UI with all controls"""
    global github_token_entry, openarena_token_entry, repo_combobox, pr_number_entry
    global post_comments_var, review_button, extract_token_button, activity_log_textbox
    global progress_bar, progress_percentage_label, time_taken_label, cost_label
    global view_pr_button, view_report_button, status_message, github_frame
    
    def open_user_guide():
        """Open the user guide HTML file in the browser"""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_root = os.path.dirname(script_dir)
            
            # Try revolutionary version first (user's preference), then fall back to others
            guide_options = [
                "user_guide_revolutionary.html",
                "user_guide_professional.html",
                "user_guide_spectacular.html", 
                "user_guide_v2.html",
                "user_guide.html"
            ]
            
            for guide_name in guide_options:
                user_guide_path = os.path.join(project_root, "docs", guide_name)
                if os.path.exists(user_guide_path):
                    # Use file:// protocol for local files
                    file_url = f"file:///{user_guide_path.replace(os.sep, '/')}"
                    webbrowser.open(file_url)
                    log_activity(f"[INFO] Opened user guide: {guide_name}")
                    return
            
            # If none found, try fallback locations
            for guide_name in guide_options:
                fallback_paths = [
                    os.path.join(script_dir, "..", "docs", guide_name),
                    os.path.join(script_dir, "docs", guide_name),
                    f"docs/{guide_name}"
                ]
                
                for path in fallback_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
                        webbrowser.open(file_url)
                        log_activity(f"[INFO] Opened user guide from fallback: {guide_name}")
                        return
            
            log_activity("[ERROR] User guide file not found in any expected location")
            messagebox.showerror("Error", "User guide file not found. Please check if docs/user_guide.html exists.")
        except Exception as e:
            log_activity(f"[ERROR] Failed to open user guide: {e}")
            messagebox.showerror("Error", f"Failed to open user guide: {e}")
    
    # Create menu bar
    menubar = tk.Menu(root)
    root.configure(menu=menubar)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Save Tokens", command=save_tokens)
    file_menu.add_command(label="Clear Tokens", command=clear_tokens)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    
    # Settings menu
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="AI Settings", command=show_ai_settings)
    settings_menu.add_command(label="Toggle Dark/Light Mode", command=change_appearance_mode_event)
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=show_help)
    help_menu.add_command(label="User Guide", command=open_user_guide)
    help_menu.add_separator()
    help_menu.add_command(label="📧 Email Feedback to Team", command=show_feedback)
    if HAS_UPDATE_CHECKER:
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates", command=lambda: check_for_updates_manual(APP_VERSION))
    

    
    # App Title Section with compact styling
    title_frame = customtkinter.CTkFrame(left_frame, corner_radius=8, border_width=1, border_color="#0078D7")
    title_frame.grid(row=0, column=0, padx=4, pady=1, sticky="ew")
    title_frame.grid_columnconfigure(0, weight=1)
    
    # Main title with reduced size for better space management
    app_title = customtkinter.CTkLabel(title_frame, text="🤖 AI Code Review Tool", 
                                     font=customtkinter.CTkFont(size=14, weight="bold"),
                                     text_color="#0078D7")
    app_title.grid(row=0, column=0, pady=1)
    
    # Combined subtitle and version for space efficiency
    subtitle = customtkinter.CTkLabel(title_frame, text=f"Claude 4 Sonnet ✨ v{APP_VERSION}", 
                                    font=customtkinter.CTkFont(size=10),
                                    text_color="#666666")
    subtitle.grid(row=1, column=0, pady=(0,1))

    # Setup token section with compact design and hints
    token_frame = customtkinter.CTkFrame(left_frame, corner_radius=8)
    token_frame.grid(row=2, column=0, padx=4, pady=1, sticky="ew")
    token_frame.grid_columnconfigure(1, weight=1)
    
    # Section header - compact
    token_header = customtkinter.CTkLabel(token_frame, text="🔑 Tokens", 
                                        font=customtkinter.CTkFont(size=13, weight="bold"),
                                        text_color="#0078D7")
    token_header.grid(row=0, column=0, columnspan=2, padx=6, pady=2, sticky="w")
    
    # GitHub Token with compact styling and hint
    github_label = customtkinter.CTkLabel(token_frame, text="GitHub:", font=customtkinter.CTkFont(size=12))
    github_label.grid(row=1, column=0, padx=6, pady=2, sticky="w")
    
    # GitHub token frame with entry and button
    github_frame = customtkinter.CTkFrame(token_frame, corner_radius=6)
    github_frame.grid(row=1, column=1, padx=6, pady=2, sticky="ew")
    github_frame.grid_columnconfigure(0, weight=1)
    
    github_token_entry = customtkinter.CTkEntry(github_frame, show="*", width=120, height=24,
                                               placeholder_text="Personal access token...")
    github_token_entry.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
    
    # Add GitHub token extraction button if module is available
    if HAS_GITHUB_EXTRACTOR:
        github_extract_button = customtkinter.CTkButton(github_frame, text="Get", 
                                                       command=extract_github_token_interactive, 
                                                       width=50, height=24, corner_radius=6,
                                                       font=customtkinter.CTkFont(size=11),
                                                       fg_color="#6f42c1", hover_color="#5a32a3")
        github_extract_button.grid(row=0, column=1, padx=3, pady=3)
    
    # OpenArena Token section with compact design
    openarena_label = customtkinter.CTkLabel(token_frame, text="OpenArena:", font=customtkinter.CTkFont(size=12))
    openarena_label.grid(row=2, column=0, padx=6, pady=2, sticky="w")
    
    openarena_frame = customtkinter.CTkFrame(token_frame, corner_radius=6)
    openarena_frame.grid(row=2, column=1, padx=6, pady=2, sticky="ew")
    openarena_frame.grid_columnconfigure(0, weight=1)
    
    openarena_token_entry = customtkinter.CTkEntry(openarena_frame, show="*", width=120, height=24,
                                                  placeholder_text="API token...")
    openarena_token_entry.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
    
    extract_token_button = customtkinter.CTkButton(openarena_frame, text="Get", 
                                                  command=extract_openarena_token_with_user_info, 
                                                  width=50, height=24, corner_radius=6,
                                                  font=customtkinter.CTkFont(size=11),
                                                  fg_color="#28A745", hover_color="#218838")
    extract_token_button.grid(row=0, column=1, padx=3, pady=3)
    
    # Repository section with improved combobox design
    repo_frame = customtkinter.CTkFrame(left_frame, corner_radius=8)
    repo_frame.grid(row=3, column=0, padx=4, pady=1, sticky="ew")
    repo_frame.grid_columnconfigure(1, weight=1)
    
    # Section header - compact
    repo_header = customtkinter.CTkLabel(repo_frame, text="📁 Repository", 
                                       font=customtkinter.CTkFont(size=13, weight="bold"),
                                       text_color="#0078D7")
    repo_header.grid(row=0, column=0, columnspan=2, padx=6, pady=2, sticky="w")
    
    repo_label = customtkinter.CTkLabel(repo_frame, text="Repo:", font=customtkinter.CTkFont(size=12))
    repo_label.grid(row=1, column=0, padx=6, pady=2, sticky="w")
    
    # Load recent repositories and merge with defaults
    recent_repos = load_recent_repos()
    default_repos = ["tr/cs-prof_tax-us-cstax-1040ST-AL", "tr/cs-prof_tax-us-cstax-1040ST-IL", "tr/cs-prof_tax-us-cstax-1040ST-NE"]
    
    # Combine recent repos with defaults (recent first)
    all_repos = []
    for repo in recent_repos:
        if repo not in all_repos:
            all_repos.append(repo)
    for repo in default_repos:
        if repo not in all_repos:
            all_repos.append(repo)
    
    # Create a simple repository input with entry field and dropdown
    repo_input_frame = customtkinter.CTkFrame(repo_frame, fg_color="transparent")
    repo_input_frame.grid(row=1, column=1, padx=6, pady=2, sticky="ew")
    repo_input_frame.grid_columnconfigure(0, weight=1)
    
    # Main entry field for typing repositories (larger and more standard)
    repo_combobox = customtkinter.CTkEntry(
        repo_input_frame,
        placeholder_text="Type repository (owner/repo)...",
        width=300,
        height=32,
        font=customtkinter.CTkFont(size=12),
        border_width=2
    )
    repo_combobox.grid(row=0, column=0, padx=(0, 5), sticky="ew")
    repo_combobox.insert(0, "tr/cs-prof_tax-us-cstax-1040ST-IL")  # Default value
    
    # Quick select dropdown with larger size
    repo_dropdown = customtkinter.CTkOptionMenu(
        repo_input_frame,
        values=all_repos if all_repos else default_repos,
        width=100,
        height=32,
        font=customtkinter.CTkFont(size=11),
        dynamic_resizing=False,
        command=lambda choice: (repo_combobox.delete(0, 'end'), repo_combobox.insert(0, choice), handle_repo_selection(choice))
    )
    repo_dropdown.grid(row=0, column=1, sticky="e")
    repo_dropdown.set("Quick Select")
    
    # Bind event to save manually typed repositories
    def on_repo_change(event=None):
        typed_repo = repo_combobox.get().strip()
        if typed_repo and '/' in typed_repo:
            add_recent_repo(typed_repo)
    
    repo_combobox.bind("<Return>", on_repo_change)
    repo_combobox.bind("<FocusOut>", on_repo_change)
    
    pr_label = customtkinter.CTkLabel(repo_frame, text="PR #:", font=customtkinter.CTkFont(size=12))
    pr_label.grid(row=2, column=0, padx=6, pady=2, sticky="w")
    
    pr_number_entry = customtkinter.CTkEntry(repo_frame, placeholder_text="e.g., 123", 
                                           width=200, height=32,
                                           font=customtkinter.CTkFont(size=12))
    pr_number_entry.grid(row=2, column=1, padx=6, pady=2, sticky="ew")
    
    # Combined options and buttons section for space efficiency
    action_frame = customtkinter.CTkFrame(left_frame, corner_radius=8)
    action_frame.grid(row=4, column=0, padx=4, pady=1, sticky="ew")
    action_frame.grid_columnconfigure(0, weight=1)
    action_frame.grid_columnconfigure(1, weight=1)
    action_frame.grid_columnconfigure(2, weight=1)
    
    # Options header
    options_header = customtkinter.CTkLabel(action_frame, text="⚙️ Options & Actions", 
                                          font=customtkinter.CTkFont(size=13, weight="bold"),
                                          text_color="#0078D7")
    options_header.grid(row=0, column=0, columnspan=3, padx=6, pady=2, sticky="w")
    
    post_comments_var = customtkinter.BooleanVar(value=True)
    post_comments_checkbox = customtkinter.CTkCheckBox(action_frame, text="💬 Post comments to PR (uncheck for review-only mode)", 
                                                      variable=post_comments_var,
                                                      font=customtkinter.CTkFont(size=11),
                                                      checkbox_width=14, checkbox_height=14)
    post_comments_checkbox.grid(row=1, column=0, columnspan=3, padx=6, pady=2, sticky="w")
    
    # Compact action buttons
    review_button = customtkinter.CTkButton(action_frame, text="🚀 Review", 
                                          command=run_code_review, 
                                          height=28, corner_radius=6,
                                          font=customtkinter.CTkFont(size=12, weight="bold"),
                                          fg_color="#0078D7", hover_color="#106ebe")
    review_button.grid(row=2, column=0, padx=3, pady=4, sticky="ew")
    
    save_tokens_button = customtkinter.CTkButton(action_frame, text="💾 Save", 
                                               command=save_tokens, 
                                               height=28, corner_radius=6,
                                               font=customtkinter.CTkFont(size=12),
                                               fg_color="#28A745", hover_color="#218838")
    save_tokens_button.grid(row=2, column=1, padx=3, pady=4, sticky="ew")
    
    clear_tokens_button = customtkinter.CTkButton(action_frame, text="🗑️ Clear", 
                                                 command=clear_tokens, 
                                                 height=28, corner_radius=6,
                                                 font=customtkinter.CTkFont(size=12),
                                                 fg_color="#DC3545", hover_color="#c82333")
    clear_tokens_button.grid(row=2, column=2, padx=3, pady=4, sticky="ew")
    
    # Combined status and analytics section for space efficiency
    status_frame = customtkinter.CTkFrame(left_frame, corner_radius=8)
    status_frame.grid(row=5, column=0, padx=4, pady=1, sticky="ew")
    status_frame.grid_columnconfigure(0, weight=1)
    status_frame.grid_columnconfigure(1, weight=1)
    
    # Section header
    status_header = customtkinter.CTkLabel(status_frame, text="📊 Status", 
                                         font=customtkinter.CTkFont(size=13, weight="bold"),
                                         text_color="#0078D7")
    status_header.grid(row=0, column=0, columnspan=2, padx=6, pady=2, sticky="w")
    
    status_message = customtkinter.StringVar(value="✅ Ready")
    status_display = customtkinter.CTkLabel(status_frame, textvariable=status_message,
                                          font=customtkinter.CTkFont(size=12))
    status_display.grid(row=1, column=0, columnspan=2, padx=6, pady=2, sticky="w")
    
    # Compact progress bar
    progress_bar = customtkinter.CTkProgressBar(status_frame, height=8, corner_radius=4)
    progress_bar.grid(row=2, column=0, columnspan=2, padx=6, pady=2, sticky="ew")
    progress_bar.set(0)
    
    # Compact view buttons
    view_frame = customtkinter.CTkFrame(left_frame, corner_radius=8)
    view_frame.grid(row=6, column=0, padx=4, pady=1, sticky="ew")
    view_frame.grid_columnconfigure(0, weight=1)
    view_frame.grid_columnconfigure(1, weight=1)
    
    # Results section with improved header
    view_header = customtkinter.CTkLabel(view_frame, text="📊 Results", 
                                       font=customtkinter.CTkFont(size=12, weight="bold"),
                                       text_color="#0078D7")
    view_header.grid(row=0, column=0, columnspan=2, padx=6, pady=2, sticky="w")
    
    view_pr_button = customtkinter.CTkButton(view_frame, text="🔗 View PR", 
                                           command=view_last_pr, state="disabled",
                                           height=24, corner_radius=6,
                                           font=customtkinter.CTkFont(size=11),
                                           fg_color="#6F42C1", hover_color="#5a379c")
    view_pr_button.grid(row=1, column=0, padx=3, pady=2, sticky="ew")
    
    view_report_button = customtkinter.CTkButton(view_frame, text="📄 Report", 
                                               command=view_latest_report, state="disabled",
                                               height=24, corner_radius=6,
                                               font=customtkinter.CTkFont(size=11),
                                               fg_color="#17A2B8", hover_color="#138496")
    view_report_button.grid(row=1, column=1, padx=3, pady=2, sticky="ew")
    
    # Add usage report button ONLY for admin users (completely hidden from regular users)
    if is_current_user_admin():
        usage_report_button = customtkinter.CTkButton(view_frame, text="👨‍💻 Dev Monitor", 
                                                     command=show_usage_report,
                                                     height=24, corner_radius=6,
                                                     font=customtkinter.CTkFont(size=11),
                                                     fg_color="#DC3545", hover_color="#c82333")
        usage_report_button.grid(row=2, column=0, columnspan=2, padx=3, pady=2, sticky="ew")
        log_activity("[ADMIN UI] Dev Monitor button visible - admin user detected")
    else:
        log_activity("[SECURITY] Dev Monitor button hidden - regular user")
    
    # Compact footer with better visibility
    footer_frame = customtkinter.CTkFrame(left_frame, corner_radius=6, height=32)
    footer_frame.grid(row=7, column=0, padx=4, pady=(1,2), sticky="ew")
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_propagate(False)  # Maintain fixed height

    footer_label = customtkinter.CTkLabel(footer_frame, text="Thomson Reuters • UltraTax Team © 2025", 
                                        font=customtkinter.CTkFont(size=10),
                                        text_color="#666666")
    footer_label.grid(row=0, column=0, pady=6)
    
    # Right side - Activity log with clear button
    log_header_frame = customtkinter.CTkFrame(right_frame, corner_radius=8, border_width=1, border_color="#0078D7")
    log_header_frame.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
    log_header_frame.grid_columnconfigure(0, weight=1)
    
    log_label = customtkinter.CTkLabel(log_header_frame, text="📝 Activity Log", 
                                     font=customtkinter.CTkFont(size=14, weight="bold"),
                                     text_color="#0078D7")
    log_label.grid(row=0, column=0, padx=8, pady=6, sticky="w")
    
    # Add Clear Log button
    clear_log_button = customtkinter.CTkButton(log_header_frame, text="🧹 Clear", 
                                             command=clear_activity_log, 
                                             width=70, height=24,
                                             font=customtkinter.CTkFont(size=10),
                                             fg_color="#DC3545", hover_color="#c82333")
    clear_log_button.grid(row=0, column=1, padx=8, pady=6, sticky="e")
    
    activity_log_textbox = customtkinter.CTkTextbox(right_frame, corner_radius=8, border_width=1,
                                                  font=customtkinter.CTkFont(family="Consolas", size=11))
    activity_log_textbox.grid(row=1, column=0, padx=4, pady=(0,4), sticky="nsew")
    
    # Analytics section below Activity Log
    analytics_frame = customtkinter.CTkFrame(right_frame, corner_radius=8, border_width=1, border_color="#0078D7")
    analytics_frame.grid(row=2, column=0, padx=4, pady=4, sticky="ew")
    analytics_frame.grid_columnconfigure(0, weight=1)
    analytics_frame.grid_columnconfigure(1, weight=1)
    analytics_frame.grid_columnconfigure(2, weight=1)
    
    # Analytics section header with better layout
    analytics_header = customtkinter.CTkLabel(analytics_frame, text="📈 Review Analytics", 
                                            font=customtkinter.CTkFont(size=12, weight="bold"),
                                            text_color="#0078D7")
    analytics_header.grid(row=0, column=0, columnspan=3, padx=8, pady=(4,1), sticky="")
    
    # Time and Cost labels with proper headings
    time_taken_label = customtkinter.CTkLabel(analytics_frame, text="⏰ Time: 0s", 
                                            font=customtkinter.CTkFont(size=11, weight="bold"),
                                            text_color="#0078D7")
    time_taken_label.grid(row=1, column=0, padx=6, pady=(2,4), sticky="w")
    
    cost_label = customtkinter.CTkLabel(analytics_frame, text="💰 Cost: $0.00", 
                                      font=customtkinter.CTkFont(size=11, weight="bold"),
                                      text_color="#28A745")
    cost_label.grid(row=1, column=2, padx=6, pady=(2,4), sticky="e")

def clear_activity_log():
    """Clear the activity log"""
    if activity_log_textbox:
        activity_log_textbox.delete("1.0", "end")
        log_activity("🧹 Activity log cleared")

def view_last_pr():
    """Open the last reviewed PR in browser"""
    global last_pr_url
    if last_pr_url:
        webbrowser.open(last_pr_url)
        log_activity(f"[INFO] Opened PR in browser: {last_pr_url}")
    else:
        messagebox.showinfo("Info", "No PR URL available to view.")

def view_latest_report():
    """Open the latest HTML report in browser"""
    global latest_report_path
    if latest_report_path and os.path.exists(latest_report_path):
        webbrowser.open(f"file://{latest_report_path}")
        log_activity(f"[INFO] Opened report in browser: {latest_report_path}")
    else:
        messagebox.showinfo("Info", "No report available to view.")

# Initialize the application
try:
    # Run enhanced startup sequence
    enhanced_startup_sequence()
    
    log_activity(">> AI Code Review Tool started successfully!")
    log_activity(f">> Version: {APP_VERSION}")
    log_activity(">> Ready to review your code!")
    
except Exception as e:
    print(f"Error during startup: {e}")
    log_activity(f"[ERROR] Startup error: {e}")

# Run the application
if __name__ == "__main__":
    root.mainloop()

