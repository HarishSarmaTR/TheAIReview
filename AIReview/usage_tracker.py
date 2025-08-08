#!/usr/bin/env python3
"""
Usage Tracker Module for AI Review Tool
Tracks who is using the tool and provides access control
"""

import json
import os
import datetime
import getpass
import platform
import hashlib
import socket
from pathlib import Path

# Configuration
USAGE_LOG_FILE = "usage_log.json"
ACCESS_CONTROL_FILE = "access_control.json"
ADMIN_USERS = ["6126175", "harish.sarma"]  # Add your authorized usernames/emails

class UsageTracker:
    def __init__(self):
        self.current_session = None
        self.initialize_access_control()
    
    def initialize_access_control(self):
        """Initialize access control file if it doesn't exist"""
        if not os.path.exists(ACCESS_CONTROL_FILE):
            default_config = {
                "admin_users": ADMIN_USERS,
                "allowed_users": [],  # Empty means no restrictions
                "require_approval": False,
                "usage_tracking": True,
                "detailed_logging": True
            }
            with open(ACCESS_CONTROL_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    def get_system_info(self):
        """Get comprehensive system information"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
        except:
            hostname = "unknown"
            ip_address = "unknown"
        
        return {
            "system_user": getpass.getuser(),
            "hostname": hostname,
            "ip_address": ip_address,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "working_directory": str(Path.cwd())
        }
    
    def check_access_permission(self, user_info=None):
        """Check if current user has permission to use the tool"""
        try:
            with open(ACCESS_CONTROL_FILE, 'r') as f:
                config = json.load(f)
        except:
            # If config file is corrupted, allow access but log the issue
            self.log_usage("ERROR", "Access control file corrupted, allowing access")
            return True, "Access control file error - proceeding"
        
        system_info = self.get_system_info()
        current_user = system_info["system_user"]
        
        # Check if user is admin
        if current_user in config.get("admin_users", []):
            return True, f"Admin access granted for {current_user}"
        
        # Check if SSO user is admin (if available)
        if user_info and user_info.get('email'):
            if user_info['email'] in config.get("admin_users", []):
                return True, f"Admin access granted for {user_info['email']}"
        
        # If no restrictions (empty allowed_users list), allow access
        allowed_users = config.get("allowed_users", [])
        if not allowed_users and not config.get("require_approval", False):
            return True, "Open access mode - no restrictions"
        
        # Check if user is in allowed list
        if current_user in allowed_users:
            return True, f"Access granted for authorized user {current_user}"
        
        if user_info and user_info.get('email') and user_info['email'] in allowed_users:
            return True, f"Access granted for authorized user {user_info['email']}"
        
        # Access denied
        return False, f"Access denied for user {current_user}. Please contact administrator."
    
    def start_session(self, user_info=None):
        """Start a new usage tracking session"""
        # Check access permission first
        has_access, message = self.check_access_permission(user_info)
        
        if not has_access:
            raise PermissionError(message)
        
        system_info = self.get_system_info()
        
        self.current_session = {
            "session_id": self.generate_session_id(),
            "start_time": datetime.datetime.now().isoformat(),
            "system_info": system_info,
            "user_info": user_info or {},
            "access_message": message,
            "activities": [],
            "reviews_conducted": 0,
            "repositories_accessed": set(),
            "pr_numbers_reviewed": set()
        }
        
        self.log_usage("SESSION_START", f"User session started: {system_info['system_user']}")
        return True, message
    
    def generate_session_id(self):
        """Generate a unique session ID"""
        timestamp = datetime.datetime.now().isoformat()
        user = getpass.getuser()
        return hashlib.md5(f"{timestamp}_{user}".encode()).hexdigest()[:16]
    
    def log_activity(self, activity_type, details, repo_name=None, pr_number=None):
        """Log a specific activity within the current session"""
        if not self.current_session:
            return  # No active session
        
        activity = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": activity_type,
            "details": details,
            "repo_name": repo_name,
            "pr_number": pr_number
        }
        
        self.current_session["activities"].append(activity)
        
        # Update session statistics
        if activity_type == "CODE_REVIEW":
            self.current_session["reviews_conducted"] += 1
            if repo_name:
                self.current_session["repositories_accessed"].add(repo_name)
            if pr_number:
                self.current_session["pr_numbers_reviewed"].add(pr_number)
        
        # Convert sets to lists for JSON serialization
        session_copy = self.current_session.copy()
        session_copy["repositories_accessed"] = list(session_copy["repositories_accessed"])
        session_copy["pr_numbers_reviewed"] = list(session_copy["pr_numbers_reviewed"])
        
        # Save to usage log
        self.save_usage_log(session_copy)
    
    def log_usage(self, event_type, message):
        """Log general usage events"""
        if self.current_session:
            self.log_activity("SYSTEM", f"{event_type}: {message}")
    
    def save_usage_log(self, session_data):
        """Save usage data to log file"""
        usage_logs = []
        
        # Load existing logs
        if os.path.exists(USAGE_LOG_FILE):
            try:
                with open(USAGE_LOG_FILE, 'r') as f:
                    usage_logs = json.load(f)
            except:
                usage_logs = []
        
        # Update or add current session
        session_id = session_data["session_id"]
        
        # Find and update existing session or add new one
        updated = False
        for i, log in enumerate(usage_logs):
            if log.get("session_id") == session_id:
                usage_logs[i] = session_data
                updated = True
                break
        
        if not updated:
            usage_logs.append(session_data)
        
        # Keep only last 100 sessions to prevent file from growing too large
        usage_logs = usage_logs[-100:]
        
        # Save back to file
        try:
            with open(USAGE_LOG_FILE, 'w') as f:
                json.dump(usage_logs, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save usage log: {e}")
    
    def end_session(self):
        """End the current session"""
        if self.current_session:
            self.current_session["end_time"] = datetime.datetime.now().isoformat()
            self.log_activity("SESSION_END", "User session ended")
            self.current_session = None
    
    def get_usage_report(self):
        """Generate a usage report for admin review"""
        if not os.path.exists(USAGE_LOG_FILE):
            return "No usage data available"
        
        try:
            with open(USAGE_LOG_FILE, 'r') as f:
                usage_logs = json.load(f)
        except:
            return "Error reading usage log"
        
        report = []
        report.append("=== AI REVIEW TOOL USAGE REPORT ===\n")
        
        # Summary statistics
        total_sessions = len(usage_logs)
        unique_users = set()
        total_reviews = 0
        unique_repos = set()
        
        for log in usage_logs:
            if log.get("system_info", {}).get("system_user"):
                unique_users.add(log["system_info"]["system_user"])
            if log.get("user_info", {}).get("email"):
                unique_users.add(log["user_info"]["email"])
            
            total_reviews += log.get("reviews_conducted", 0)
            unique_repos.update(log.get("repositories_accessed", []))
        
        report.append(f"Total Sessions: {total_sessions}")
        report.append(f"Unique Users: {len(unique_users)}")
        report.append(f"Total Code Reviews: {total_reviews}")
        report.append(f"Unique Repositories: {len(unique_repos)}")
        report.append("\n=== RECENT SESSIONS ===\n")
        
        # Recent session details (last 20)
        recent_sessions = usage_logs[-20:]
        for session in recent_sessions:
            start_time = session.get("start_time", "Unknown")
            user = session.get("system_info", {}).get("system_user", "Unknown")
            sso_user = session.get("user_info", {}).get("email", "")
            reviews = session.get("reviews_conducted", 0)
            repos = session.get("repositories_accessed", [])
            
            user_display = f"{user}" + (f" ({sso_user})" if sso_user else "")
            report.append(f"Session: {start_time}")
            report.append(f"  User: {user_display}")
            report.append(f"  Reviews: {reviews}")
            report.append(f"  Repositories: {', '.join(repos) if repos else 'None'}")
            report.append("")
        
        return "\n".join(report)
    
    def is_admin(self, user_info=None):
        """Check if current user is admin"""
        try:
            with open(ACCESS_CONTROL_FILE, 'r') as f:
                config = json.load(f)
        except:
            return False
        
        system_user = getpass.getuser()
        admin_users = config.get("admin_users", [])
        
        if system_user in admin_users:
            return True
        
        if user_info and user_info.get('email') and user_info['email'] in admin_users:
            return True
        
        return False

# Global instance
usage_tracker = UsageTracker()

def start_tracking_session(user_info=None):
    """Initialize usage tracking for the application"""
    return usage_tracker.start_session(user_info)

def log_review_activity(repo_name, pr_number, details):
    """Log a code review activity"""
    usage_tracker.log_activity("CODE_REVIEW", details, repo_name, pr_number)

def log_system_activity(activity_type, message):
    """Log general system activity"""
    usage_tracker.log_usage(activity_type, message)

def end_tracking_session():
    """End the current tracking session"""
    usage_tracker.end_session()

def get_usage_report():
    """Get usage report (admin only)"""
    return usage_tracker.get_usage_report()

def is_admin_user(user_info=None):
    """Check if user has admin privileges"""
    return usage_tracker.is_admin(user_info)
