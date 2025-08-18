#!/usr/bin/env python3
"""
Auto Update Checker Module
Checks for new versions of the AI Review Tool from GitHub releases
"""

import json
import os
import requests
from datetime import datetime, timedelta
import webbrowser
from tkinter import messagebox

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
    
    def show_update_notification(self, latest_version, download_url, release_notes):
        """Show update notification to user"""
        try:
            # Create a truncated version of release notes for the dialog
            short_notes = release_notes[:200] + "..." if len(release_notes) > 200 else release_notes
            
            message = f"""A new version of AI Review Tool is available!

Current Version: {self.current_version}
Latest Version: {latest_version}

What's New:
{short_notes}

Would you like to download the update?"""
            
            result = messagebox.askyesno("Update Available", message)
            
            if result:
                # Open download URL in browser
                webbrowser.open(download_url)
                print(f"🌐 Opened download page: {download_url}")
            
            # Mark this version as notified regardless of user choice
            self.mark_as_notified(latest_version)
            
        except Exception as e:
            print(f"Error showing update notification: {e}")
    
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

def check_for_updates_manual():
    """Manual update check function that can be called from menu"""
    checker = UpdateChecker("2.1.4")
    has_update, latest_version, download_url, release_notes = checker.check_for_updates(show_no_update_message=True)
    
    if has_update and latest_version:
        checker.show_update_notification(latest_version, download_url, release_notes)

def check_for_updates_startup(current_version="2.1.4"):
    """Startup update check function"""
    checker = UpdateChecker(current_version)
    checker.check_and_notify_updates()

if __name__ == "__main__":
    # Test the update checker
    checker = UpdateChecker()
    checker.check_and_notify_updates(force_check=True)
