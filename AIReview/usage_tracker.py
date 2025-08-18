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

# Configuration - DEVELOPER/ADMIN ONLY ACCESS
USAGE_LOG_FILE = "usage_log.json"
ACCESS_CONTROL_FILE = "access_control.json"
ADMIN_USERS = ["6126175", "harish.sarma", "velavalapalli.harishsarma@thomsonreuters.com"]  # Developer access only

# Enhanced capacity settings for enterprise usage tracking
MAX_SESSIONS_IN_MEMORY = 10000  # Keep up to 10,000 sessions (suitable for monthly exports)
ARCHIVE_THRESHOLD = 8000  # When to start archiving old data
MONTHLY_ARCHIVE_ENABLED = True  # Enable automatic monthly archiving

class UsageTracker:
    def __init__(self):
        self.current_session = None
        self.initialize_access_control()
    
    def initialize_access_control(self):
        """Initialize access control file with developer-only permissions"""
        if not os.path.exists(ACCESS_CONTROL_FILE):
            default_config = {
                "admin_users": ADMIN_USERS,
                "allowed_users": [],  # Empty means open access for regular users
                "require_approval": False,
                "usage_tracking": True,
                "detailed_logging": True,
                "developer_only_reports": True,  # Only developers can see usage reports
                "log_all_access": True,  # Log all access attempts for monitoring
                "security_notice": "Usage tracking is for developer monitoring only"
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
        
        # Enhanced capacity management for enterprise usage tracking
        if len(usage_logs) > MAX_SESSIONS_IN_MEMORY:
            # Implement intelligent data management
            if MONTHLY_ARCHIVE_ENABLED:
                self.archive_old_sessions(usage_logs)
            
            # After archiving, keep the most recent sessions
            usage_logs = usage_logs[-ARCHIVE_THRESHOLD:]
            print(f"[USAGE TRACKER] Archived old sessions, keeping {len(usage_logs)} recent sessions")
        
        # Save back to file
        try:
            with open(USAGE_LOG_FILE, 'w') as f:
                json.dump(usage_logs, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save usage log: {e}")
            
    def archive_old_sessions(self, usage_logs):
        """Archive old sessions by month for long-term storage"""
        try:
            current_date = datetime.datetime.now()
            archive_folder = "usage_archives"
            
            # Create archive folder if it doesn't exist
            if not os.path.exists(archive_folder):
                os.makedirs(archive_folder)
            
            # Group sessions by month
            monthly_data = {}
            sessions_to_keep = []
            
            for session in usage_logs:
                try:
                    session_date = datetime.datetime.fromisoformat(session.get('start_time', ''))
                    
                    # Keep sessions from current month
                    if session_date.year == current_date.year and session_date.month == current_date.month:
                        sessions_to_keep.append(session)
                    else:
                        # Archive older sessions
                        month_key = f"{session_date.year}-{session_date.month:02d}"
                        if month_key not in monthly_data:
                            monthly_data[month_key] = []
                        monthly_data[month_key].append(session)
                except:
                    # If date parsing fails, keep the session
                    sessions_to_keep.append(session)
            
            # Save archived sessions to monthly files
            for month_key, month_sessions in monthly_data.items():
                archive_file = os.path.join(archive_folder, f"usage_archive_{month_key}.json")
                
                # Load existing archive if it exists
                existing_archive = []
                if os.path.exists(archive_file):
                    try:
                        with open(archive_file, 'r') as f:
                            existing_archive = json.load(f)
                    except:
                        existing_archive = []
                
                # Add new sessions to archive (avoid duplicates)
                existing_session_ids = {s.get('session_id') for s in existing_archive}
                new_sessions = [s for s in month_sessions if s.get('session_id') not in existing_session_ids]
                
                if new_sessions:
                    combined_archive = existing_archive + new_sessions
                    
                    # Save archived data
                    with open(archive_file, 'w') as f:
                        json.dump(combined_archive, f, indent=2)
                    
                    print(f"[ARCHIVE] Archived {len(new_sessions)} sessions to {archive_file}")
            
            # Update the main log to keep only current month sessions
            usage_logs.clear()
            usage_logs.extend(sessions_to_keep)
            
        except Exception as e:
            print(f"[WARNING] Archiving failed: {e}")
            
    def get_comprehensive_usage_report(self, include_archives=True):
        """Generate comprehensive report including archived data for monthly exports"""
        report_data = {
            "generated_at": datetime.datetime.now().isoformat(),
            "report_type": "comprehensive" if include_archives else "current",
            "current_sessions": [],
            "archived_sessions": {},
            "summary": {}
        }
        
        # Load current sessions
        if os.path.exists(USAGE_LOG_FILE):
            try:
                with open(USAGE_LOG_FILE, 'r') as f:
                    report_data["current_sessions"] = json.load(f)
            except Exception as e:
                print(f"Error loading current sessions: {e}")
        
        # Load archived sessions if requested
        if include_archives and os.path.exists("usage_archives"):
            archive_folder = "usage_archives"
            for archive_file in os.listdir(archive_folder):
                if archive_file.startswith("usage_archive_") and archive_file.endswith(".json"):
                    month_key = archive_file.replace("usage_archive_", "").replace(".json", "")
                    archive_path = os.path.join(archive_folder, archive_file)
                    
                    try:
                        with open(archive_path, 'r') as f:
                            report_data["archived_sessions"][month_key] = json.load(f)
                    except Exception as e:
                        print(f"Error loading archive {archive_file}: {e}")
        
        # Generate comprehensive summary
        all_sessions = report_data["current_sessions"].copy()
        for monthly_sessions in report_data["archived_sessions"].values():
            all_sessions.extend(monthly_sessions)
        
        # Calculate summary statistics
        unique_users = set()
        total_reviews = 0
        unique_repos = set()
        user_activity = {}
        monthly_stats = {}
        
        for session in all_sessions:
            # Extract user information
            system_user = session.get("system_info", {}).get("system_user", "Unknown")
            sso_user = session.get("user_info", {}).get("email", "")
            display_name = session.get("user_info", {}).get("display_name", system_user)
            
            # Track unique users
            unique_users.add(system_user)
            if sso_user:
                unique_users.add(sso_user)
            
            # Accumulate totals
            session_reviews = session.get("reviews_conducted", 0)
            total_reviews += session_reviews
            session_repos = session.get("repositories_accessed", [])
            unique_repos.update(session_repos)
            
            # Track per-user activity
            user_key = sso_user if sso_user else system_user
            if user_key not in user_activity:
                user_activity[user_key] = {
                    "display_name": display_name,
                    "session_count": 0,
                    "review_count": 0,
                    "last_active": None,
                    "repositories": set()
                }
            
            user_activity[user_key]["session_count"] += 1
            user_activity[user_key]["review_count"] += session_reviews
            user_activity[user_key]["repositories"].update(session_repos)
            
            # Update last active time
            start_time = session.get("start_time")
            if start_time and (not user_activity[user_key]["last_active"] or start_time > user_activity[user_key]["last_active"]):
                user_activity[user_key]["last_active"] = start_time
            
            # Monthly statistics
            try:
                session_date = datetime.datetime.fromisoformat(start_time)
                month_key = f"{session_date.year}-{session_date.month:02d}"
                if month_key not in monthly_stats:
                    monthly_stats[month_key] = {
                        "sessions": 0,
                        "reviews": 0,
                        "unique_users": set(),
                        "repositories": set()
                    }
                monthly_stats[month_key]["sessions"] += 1
                monthly_stats[month_key]["reviews"] += session_reviews
                monthly_stats[month_key]["unique_users"].add(user_key)
                monthly_stats[month_key]["repositories"].update(session_repos)
            except:
                pass
        
        # Convert sets to lists for JSON serialization
        for user, activity in user_activity.items():
            activity["repositories"] = list(activity["repositories"])
        
        for month, stats in monthly_stats.items():
            stats["unique_users"] = len(stats["unique_users"])
            stats["repositories"] = list(stats["repositories"])
        
        report_data["summary"] = {
            "total_sessions": len(all_sessions),
            "unique_users": list(unique_users),
            "total_reviews": total_reviews,
            "repositories_accessed": list(unique_repos),
            "user_activity": user_activity,
            "monthly_statistics": monthly_stats,
            "capacity_info": {
                "current_sessions_count": len(report_data["current_sessions"]),
                "archived_months": len(report_data["archived_sessions"]),
                "total_capacity": f"Up to {MAX_SESSIONS_IN_MEMORY:,} sessions",
                "archive_enabled": MONTHLY_ARCHIVE_ENABLED
            }
        }
        
        return report_data
    
    def end_session(self):
        """End the current session"""
        if self.current_session:
            self.current_session["end_time"] = datetime.datetime.now().isoformat()
            self.log_activity("SESSION_END", "User session ended")
            self.current_session = None
    
    def get_usage_report(self):
        """Generate a usage report for admin review (current sessions only)"""
        if not os.path.exists(USAGE_LOG_FILE):
            return {"error": "No usage data available"}
        
        try:
            with open(USAGE_LOG_FILE, 'r') as f:
                usage_logs = json.load(f)
        except Exception as e:
            return {"error": f"Error reading usage log: {e}"}
        
        # Calculate summary statistics
        total_sessions = len(usage_logs)
        unique_users = set()
        total_reviews = 0
        unique_repos = set()
        user_activity = {}
        recent_sessions = []
        
        for log in usage_logs:
            # Extract user information
            system_user = log.get("system_info", {}).get("system_user", "Unknown")
            sso_user = log.get("user_info", {}).get("email", "")
            display_name = log.get("user_info", {}).get("display_name", system_user)
            
            # Track unique users
            unique_users.add(system_user)
            if sso_user:
                unique_users.add(sso_user)
            
            # Accumulate totals
            session_reviews = log.get("reviews_conducted", 0)
            total_reviews += session_reviews
            session_repos = log.get("repositories_accessed", [])
            unique_repos.update(session_repos)
            
            # Track per-user activity
            user_key = sso_user if sso_user else system_user
            if user_key not in user_activity:
                user_activity[user_key] = {
                    "display_name": display_name,
                    "session_count": 0,
                    "review_count": 0,
                    "last_active": None,
                    "repositories": set()
                }
            
            user_activity[user_key]["session_count"] += 1
            user_activity[user_key]["review_count"] += session_reviews
            user_activity[user_key]["repositories"].update(session_repos)
            
            # Update last active time
            start_time = log.get("start_time")
            if start_time and (not user_activity[user_key]["last_active"] or start_time > user_activity[user_key]["last_active"]):
                user_activity[user_key]["last_active"] = start_time
            
            # Keep recent sessions for detailed view
            if len(recent_sessions) < 20:  # Keep last 20 sessions
                recent_sessions.append({
                    "user": display_name,
                    "start_time": start_time,
                    "end_time": log.get("end_time", "Ongoing"),
                    "reviews": session_reviews,
                    "repositories": session_repos
                })
        
        # Convert sets to lists for JSON serialization
        for user, activity in user_activity.items():
            activity["repositories"] = list(activity["repositories"])
        
        report = {
            "report_type": "current_sessions",
            "generated_at": datetime.datetime.now().isoformat(),
            "summary": {
                "total_sessions": total_sessions,
                "unique_users": len(unique_users),
                "total_reviews": total_reviews,
                "unique_repositories": len(unique_repos),
                "capacity_status": f"{total_sessions:,} / {MAX_SESSIONS_IN_MEMORY:,} sessions",
                "archive_status": "Enabled" if MONTHLY_ARCHIVE_ENABLED else "Disabled"
            },
            "user_activity": user_activity,
            "recent_sessions": recent_sessions[::-1],  # Most recent first
            "repositories_accessed": list(unique_repos)
        }
        
        return report

    def is_current_user_admin(self):
        """Check if current user is admin (for UI visibility control)"""
        try:
            with open(ACCESS_CONTROL_FILE, 'r') as f:
                config = json.load(f)
        except:
            return False
        
        system_user = getpass.getuser()
        admin_users = config.get("admin_users", [])
        
        if system_user in admin_users:
            return True
        
        # Check SSO email if available in current session
        if self.current_session and self.current_session.get('user_info'):
            email = self.current_session['user_info'].get('email')
            if email and email in admin_users:
                return True
        
        return False

# Global instance
usage_tracker = UsageTracker()

# Main application interface functions
def start_session(user_info=None):
    """Initialize usage tracking for the application"""
    return usage_tracker.start_session(user_info)

def log_activity(action, details="", repo_name=None, pr_number=None):
    """Log an activity with optional context"""
    return usage_tracker.log_activity(action, details, repo_name, pr_number)

def end_session():
    """End the current tracking session"""
    return usage_tracker.end_session()

def get_usage_report():
    """Get current session usage report (admin only)"""
    return usage_tracker.get_usage_report()

def get_comprehensive_report(include_archives=True):
    """Get comprehensive usage report including archived data (admin only)"""
    return usage_tracker.get_comprehensive_usage_report(include_archives)

def is_current_user_admin():
    """Check if current user is admin (for UI visibility control)"""
    return usage_tracker.is_current_user_admin()
