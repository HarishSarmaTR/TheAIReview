#!/usr/bin/env python3
"""
Auto Update Checker Module
Checks for new versions of the AI Review Tool from GitHub releases
"""

import json
import os
import requests
import subprocess
import tempfile
from datetime import datetime, timedelta
import webbrowser
from tkinter import messagebox
import tkinter as tk
from version_utils import APP_VERSION
import customtkinter

UPDATE_CHECK_FILE = "last_update_check.json"
UPDATE_NOTIFICATION_FILE = "update_notifications.json"
GITHUB_API_URL = "https://api.github.com/repos/HarishSarmaTR/TheAIReview/releases/latest"
CHECK_INTERVAL_DAYS = 1  # Check for updates daily

class UpdateChecker:
    def __init__(self, current_version="2.1.4"):
        self.current_version = current_version
        self.update_check_file = UPDATE_CHECK_FILE
        self.notification_file = UPDATE_NOTIFICATION_FILE
    
    def should_check_for_updates(self):
        """Check if enough time has passed since last update check"""
        try:
            if not os.path.exists(self.update_check_file):
                return True
            
            with open(self.update_check_file, 'r') as f:
                data = json.load(f)
            
            last_check = datetime.fromisoformat(data.get('last_check', '2025-01-01'))
            time_since_check = datetime.now() - last_check
            
            return time_since_check.days >= CHECK_INTERVAL_DAYS
            
        except Exception as e:
            print(f"Error checking update schedule: {e}")
            return True
    
    def save_last_check_time(self):
        """Save the current time as the last update check time"""
        try:
            data = {
                'last_check': datetime.now().isoformat(),
                'current_version': self.current_version
            }
            with open(self.update_check_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving update check time: {e}")
    
    def parse_version(self, version_string):
        """Parse version string into comparable tuple"""
        try:
            # Remove 'v' prefix if present and split by dots
            clean_version = version_string.lstrip('vV')
            parts = clean_version.split('.')
            return tuple(int(part) for part in parts)
        except Exception:
            return (0, 0, 0)
    
    def is_newer_version(self, latest_version):
        """Compare version numbers to see if latest is newer than current"""
        current_tuple = self.parse_version(self.current_version)
        latest_tuple = self.parse_version(latest_version)
        return latest_tuple > current_tuple
    
    def check_for_updates(self, show_no_update_message=False):
        """
        Check GitHub releases for newer versions
        Returns: (has_update, latest_version, download_url, release_notes)
        """
        try:
            print("🔄 Checking for updates...")
            
            # Make request to GitHub API
            response = requests.get(GITHUB_API_URL, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Failed to check for updates: HTTP {response.status_code}")
                return False, None, None, None
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('vV')
            release_notes = release_data.get('body', '')
            download_url = release_data.get('html_url', '')
            
            # Find the .exe asset if available
            exe_download_url = None
            for asset in release_data.get('assets', []):
                if asset.get('name', '').endswith('.exe'):
                    exe_download_url = asset.get('browser_download_url')
                    break
            
            if exe_download_url:
                download_url = exe_download_url
            
            print(f"📊 Current version: {self.current_version}")
            print(f"📊 Latest version: {latest_version}")
            
            # Save the check time
            self.save_last_check_time()
            
            if self.is_newer_version(latest_version):
                print(f"✅ New version available: {latest_version}")
                return True, latest_version, download_url, release_notes
            else:
                print("✅ You have the latest version")
                if show_no_update_message:
                    messagebox.showinfo("Update Check", f"You have the latest version ({self.current_version})")
                return False, latest_version, download_url, release_notes
                
        except Exception as e:
            print(f"❌ Error checking for updates: {e}")
            if show_no_update_message:
                messagebox.showerror("Update Check", f"Failed to check for updates: {str(e)}")
            return False, None, None, None
    
    def has_been_notified(self, version):
        """Check if user has already been notified about this version"""
        try:
            if not os.path.exists(self.notification_file):
                return False
            
            with open(self.notification_file, 'r') as f:
                data = json.load(f)
            
            notified_versions = data.get('notified_versions', [])
            return version in notified_versions
            
        except Exception:
            return False
    
    def mark_as_notified(self, version):
        """Mark a version as having been notified to the user"""
        try:
            data = {'notified_versions': []}
            
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'r') as f:
                    data = json.load(f)
            
            if 'notified_versions' not in data:
                data['notified_versions'] = []
            
            if version not in data['notified_versions']:
                data['notified_versions'].append(version)
                
                # Keep only last 5 versions to prevent file bloat
                data['notified_versions'] = data['notified_versions'][-5:]
            
            with open(self.notification_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving notification status: {e}")
    
    def download_update(self, download_url, filename):
        """Download the update file"""
        try:
            print(f"📥 Downloading update from: {download_url}")
            
            # Create a temporary directory for downloads
            download_dir = tempfile.gettempdir()
            file_path = os.path.join(download_dir, filename)
            
            # Download the file
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get total file size for progress (if available)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(file_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"📥 Download progress: {progress:.1f}%", end='\r')
            
            print(f"\n✅ Download completed: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def show_update_notification(self, latest_version, download_url, release_notes):
        """Show modern update notification dialog to user"""
        try:
            # Create a custom update dialog window
            update_window = customtkinter.CTkToplevel()
            update_window.title("Update Available")
            update_window.geometry("500x450")
            update_window.resizable(False, False)
            
            # Configure window
            update_window.configure(fg_color=("#f0f0f0", "#2b2b2b"))
            
            # Center the window
            update_window.transient()
            update_window.grab_set()
            
            # Header frame with icon and title
            header_frame = customtkinter.CTkFrame(update_window, corner_radius=0, fg_color=("#0078D7", "#0078D7"))
            header_frame.pack(fill="x", padx=0, pady=0)
            
            header_label = customtkinter.CTkLabel(
                header_frame, 
                text="🚀 Update Available", 
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=15)
            
            # Main content frame
            content_frame = customtkinter.CTkFrame(update_window, corner_radius=8)
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Version info frame
            version_frame = customtkinter.CTkFrame(content_frame, corner_radius=8, fg_color=("#e8f4fd", "#1a1a1a"))
            version_frame.pack(fill="x", padx=15, pady=15)
            
            current_label = customtkinter.CTkLabel(
                version_frame, 
                text=f"📦 Current Version: {self.current_version}",
                font=customtkinter.CTkFont(size=14)
            )
            current_label.pack(pady=(10, 5))
            
            latest_label = customtkinter.CTkLabel(
                version_frame, 
                text=f"✨ Latest Version: {latest_version}",
                font=customtkinter.CTkFont(size=14, weight="bold"),
                text_color=("#0078D7", "#4da6ff")
            )
            latest_label.pack(pady=(0, 10))
            
            # Release notes section
            if release_notes and release_notes.strip():
                notes_label = customtkinter.CTkLabel(
                    content_frame, 
                    text="📝 What's New:",
                    font=customtkinter.CTkFont(size=14, weight="bold")
                )
                notes_label.pack(anchor="w", padx=15, pady=(0, 5))
                
                # Truncate release notes for display
                short_notes = release_notes[:150] + "..." if len(release_notes) > 150 else release_notes
                
                notes_text = customtkinter.CTkTextbox(
                    content_frame, 
                    height=80,
                    corner_radius=8,
                    font=customtkinter.CTkFont(size=12)
                )
                notes_text.pack(fill="x", padx=15, pady=(0, 15))
                notes_text.insert("1.0", short_notes)
                notes_text.configure(state="disabled")
            
            # Button frame
            button_frame = customtkinter.CTkFrame(content_frame, corner_radius=8, fg_color="transparent")
            button_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            # Download button
            download_btn = customtkinter.CTkButton(
                button_frame,
                text="📥 Download & Install",
                command=lambda: self.handle_update_download(update_window, download_url, latest_version),
                font=customtkinter.CTkFont(size=14, weight="bold"),
                height=40,
                corner_radius=8,
                fg_color=("#0078D7", "#0078D7"),
                hover_color=("#106ebe", "#106ebe")
            )
            download_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            # Later button
            later_btn = customtkinter.CTkButton(
                button_frame,
                text="⏰ Later",
                command=update_window.destroy,
                font=customtkinter.CTkFont(size=14),
                height=40,
                corner_radius=8,
                fg_color=("#6c757d", "#6c757d"),
                hover_color=("#5a6268", "#5a6268")
            )
            later_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
            
            # Footer with Thomson Reuters and UltraTax branding
            footer_frame = customtkinter.CTkFrame(content_frame, corner_radius=8, fg_color=("#f8f9fa", "#1a1a1a"))
            footer_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            thomson_label = customtkinter.CTkLabel(
                footer_frame,
                text="Thomson Reuters",
                font=customtkinter.CTkFont(size=10, weight="bold"),
                text_color=("#6c757d", "#adb5bd")
            )
            thomson_label.pack(side="left", padx=10, pady=5)
            
            separator_label = customtkinter.CTkLabel(
                footer_frame,
                text="•",
                font=customtkinter.CTkFont(size=10),
                text_color=("#6c757d", "#adb5bd")
            )
            separator_label.pack(side="left")
            
            ultratax_label = customtkinter.CTkLabel(
                footer_frame,
                text="UltraTax Team",
                font=customtkinter.CTkFont(size=10, weight="bold"),
                text_color=("#6c757d", "#adb5bd")
            )
            ultratax_label.pack(side="left", padx=(0, 10), pady=5)
            
            copyright_label = customtkinter.CTkLabel(
                footer_frame,
                text="© 2025",
                font=customtkinter.CTkFont(size=10),
                text_color=("#6c757d", "#adb5bd")
            )
            copyright_label.pack(side="right", padx=10, pady=5)
            
            # Mark this version as notified regardless of user choice
            self.mark_as_notified(latest_version)
            
            # Focus and wait
            update_window.focus_set()
            update_window.wait_window()
            
        except Exception as e:
            print(f"❌ Error showing update notification: {e}")
            print(f"📋 Update available: {latest_version}")
            print(f"🔗 Download URL: {download_url}")
    
    def handle_update_download(self, window, download_url, latest_version):
        """Handle the download process from the custom dialog"""
        window.destroy()
        
        # Extract filename from download_url
        filename = os.path.basename(download_url)
        if not filename.endswith('.exe'):
            filename = f"AIReviewTool_V{latest_version}.exe"
        
        # Download the update file
        downloaded_file = self.download_update(download_url, filename)
        
        if downloaded_file:
            # Show custom download complete dialog
            self.show_download_complete_dialog(downloaded_file)
        else:
            # Show custom download failed dialog
            self.show_download_failed_dialog(download_url)
    
    def show_download_complete_dialog(self, downloaded_file):
        """Show custom download complete dialog"""
        try:
            # Create download complete dialog
            complete_window = customtkinter.CTkToplevel()
            complete_window.title("Download Complete")
            complete_window.geometry("550x400")  # Made larger
            complete_window.resizable(False, False)
            
            # Configure window
            complete_window.configure(fg_color=("#f0f0f0", "#2b2b2b"))
            complete_window.transient()
            complete_window.grab_set()
            
            # Header with checkmark
            header_frame = customtkinter.CTkFrame(complete_window, corner_radius=0, fg_color=("#28a745", "#28a745"))
            header_frame.pack(fill="x")
            
            header_label = customtkinter.CTkLabel(
                header_frame,
                text="✅ Download Complete",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=15)
            
            # Content frame
            content_frame = customtkinter.CTkFrame(complete_window, corner_radius=8)
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Success message
            success_label = customtkinter.CTkLabel(
                content_frame,
                text="Update downloaded successfully!",
                font=customtkinter.CTkFont(size=16, weight="bold")
            )
            success_label.pack(pady=(20, 15))
            
            # File path info with proper wrapping
            path_frame = customtkinter.CTkFrame(content_frame, corner_radius=8, fg_color=("#e8f4fd", "#1a1a1a"))
            path_frame.pack(fill="x", padx=15, pady=(0, 20))
            
            path_title = customtkinter.CTkLabel(
                path_frame,
                text="📁 File Location:",
                font=customtkinter.CTkFont(size=12, weight="bold")
            )
            path_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            path_label = customtkinter.CTkLabel(
                path_frame,
                text=downloaded_file,
                font=customtkinter.CTkFont(size=11),
                wraplength=500,  # Increased wrap length
                justify="left"
            )
            path_label.pack(anchor="w", padx=15, pady=(0, 10))
            
            # Question section
            question_frame = customtkinter.CTkFrame(content_frame, corner_radius=8, fg_color="transparent")
            question_frame.pack(fill="x", padx=15, pady=(0, 20))
            
            question_label = customtkinter.CTkLabel(
                question_frame,
                text="Would you like to run the installer now?",
                font=customtkinter.CTkFont(size=15, weight="bold")
            )
            question_label.pack(pady=(0, 8))
            
            # Note
            note_label = customtkinter.CTkLabel(
                question_frame,
                text="(Note: This will close the current application)",
                font=customtkinter.CTkFont(size=12),
                text_color=("#6c757d", "#adb5bd")
            )
            note_label.pack(pady=(0, 15))
            
            # Button frame
            button_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            # Yes button
            yes_btn = customtkinter.CTkButton(
                button_frame,
                text="✅ Yes, Install Now",
                command=lambda: self.run_installer(complete_window, downloaded_file),
                font=customtkinter.CTkFont(size=14, weight="bold"),
                height=45,  # Made taller
                fg_color=("#28a745", "#28a745"),
                hover_color=("#218838", "#218838")
            )
            yes_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
            
            # No button  
            no_btn = customtkinter.CTkButton(
                button_frame,
                text="⏰ Install Later",
                command=lambda: self.save_for_later(complete_window, downloaded_file),
                font=customtkinter.CTkFont(size=14),
                height=45,  # Made taller
                fg_color=("#6c757d", "#6c757d"),
                hover_color=("#5a6268", "#5a6268")
            )
            no_btn.pack(side="right", fill="x", expand=True, padx=(8, 0))
            
            complete_window.focus_set()
            complete_window.wait_window()
            
        except Exception as e:
            print(f"❌ Error showing download complete dialog: {e}")
    
    def run_installer(self, window, downloaded_file):
        """Run the installer and close the application"""
        window.destroy()
        try:
            print(f"🚀 Running installer: {downloaded_file}")
            subprocess.Popen([downloaded_file])
            print("✅ Installer started. Closing application.")
            os._exit(0)
        except Exception as e:
            print(f"❌ Failed to run installer: {e}")
            self.show_error_dialog(f"Failed to run installer: {e}\n\nPlease run the installer manually from:\n{downloaded_file}")
    
    def save_for_later(self, window, downloaded_file):
        """Save for later and close dialog"""
        window.destroy()
        print(f"📁 Update saved for later: {downloaded_file}")
    
    def show_download_failed_dialog(self, download_url):
        """Show custom download failed dialog"""
        try:
            # Create download failed dialog
            failed_window = customtkinter.CTkToplevel()
            failed_window.title("Download Failed")
            failed_window.geometry("400x250")
            failed_window.resizable(False, False)
            
            # Configure window
            failed_window.configure(fg_color=("#f0f0f0", "#2b2b2b"))
            failed_window.transient()
            failed_window.grab_set()
            
            # Header with error icon
            header_frame = customtkinter.CTkFrame(failed_window, corner_radius=0, fg_color=("#dc3545", "#dc3545"))
            header_frame.pack(fill="x")
            
            header_label = customtkinter.CTkLabel(
                header_frame,
                text="❌ Download Failed",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=15)
            
            # Content frame
            content_frame = customtkinter.CTkFrame(failed_window, corner_radius=8)
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Error message
            error_label = customtkinter.CTkLabel(
                content_frame,
                text="Failed to download update automatically.\nOpening download page in browser...",
                font=customtkinter.CTkFont(size=14),
                justify="center"
            )
            error_label.pack(pady=30)
            
            # OK button
            ok_btn = customtkinter.CTkButton(
                content_frame,
                text="OK",
                command=lambda: self.open_browser_and_close(failed_window, download_url),
                font=customtkinter.CTkFont(size=14),
                height=40,
                fg_color=("#0078D7", "#0078D7")
            )
            ok_btn.pack(pady=20)
            
            failed_window.focus_set()
            failed_window.wait_window()
            
        except Exception as e:
            print(f"❌ Error showing download failed dialog: {e}")
            webbrowser.open(download_url)
    
    def open_browser_and_close(self, window, download_url):
        """Open browser and close dialog"""
        window.destroy()
        webbrowser.open(download_url)
        print(f"🌐 Opened download page: {download_url}")
    
    def show_error_dialog(self, error_message):
        """Show custom error dialog"""
        try:
            error_window = customtkinter.CTkToplevel()
            error_window.title("Error")
            error_window.geometry("500x200")
            error_window.resizable(False, False)
            error_window.configure(fg_color=("#f0f0f0", "#2b2b2b"))
            error_window.transient()
            error_window.grab_set()
            
            # Content
            content_frame = customtkinter.CTkFrame(error_window, corner_radius=8)
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            error_label = customtkinter.CTkLabel(
                content_frame,
                text=error_message,
                font=customtkinter.CTkFont(size=12),
                wraplength=450,
                justify="center"
            )
            error_label.pack(expand=True)
            
            ok_btn = customtkinter.CTkButton(
                content_frame,
                text="OK",
                command=error_window.destroy,
                height=35
            )
            ok_btn.pack(pady=10)
            
            error_window.focus_set()
            error_window.wait_window()
            
        except Exception as e:
            print(f"❌ Error showing error dialog: {e}")
    
    def check_and_notify_updates(self, force_check=False):
        """Main method to check for updates and notify user if needed"""
        try:
            # Check if we should perform an update check
            if not force_check and not self.should_check_for_updates():
                print("⏰ Skipping update check (too soon since last check)")
                return
            
            # Check for updates
            has_update, latest_version, download_url, release_notes = self.check_for_updates()
            
            if has_update and latest_version:
                # Check if we've already notified about this version
                if not self.has_been_notified(latest_version):
                    self.show_update_notification(latest_version, download_url, release_notes)
                else:
                    print(f"📋 Update {latest_version} available (already notified)")
            
        except Exception as e:
            print(f"❌ Error in update check process: {e}")

def check_for_updates_manual(current_version=None):
    """Manual update check function that can be called from menu"""
    if current_version is None:
        current_version = APP_VERSION
    checker = UpdateChecker(current_version)
    has_update, latest_version, download_url, release_notes = checker.check_for_updates(show_no_update_message=True)
    
    if has_update and latest_version:
        checker.show_update_notification(latest_version, download_url, release_notes)

def check_for_updates_startup(current_version=None):
    """Startup update check function"""
    if current_version is None:
        current_version = APP_VERSION
    checker = UpdateChecker(current_version)
    checker.check_and_notify_updates()

if __name__ == "__main__":
    # Test the update checker
    checker = UpdateChecker()
    checker.check_and_notify_updates(force_check=True)
