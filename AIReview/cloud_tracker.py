#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FILE: cloud_tracker.py

"""
Enhanced Cloud-Based Usage Tracking for AI Review Tool
Sends usage data to a centralized tracking service
"""

import requests
import json
from datetime import datetime
import hashlib
import platform
import getpass
from version_utils import APP_VERSION

class CloudUsageTracker:
    def __init__(self):
        # Use a simple webhook service like webhook.site or your own endpoint
        self.tracking_endpoint = "https://webhook.site/your-unique-id"  # Replace with your endpoint
        self.session_id = self.generate_session_id()
        self.user_fingerprint = self.get_user_fingerprint()
        
    def generate_session_id(self):
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        user = getpass.getuser()
        return hashlib.md5(f"{timestamp}{user}".encode()).hexdigest()[:16]
    
    def get_user_fingerprint(self):
        """Create anonymous but unique user fingerprint"""
        system_info = f"{platform.node()}{getpass.getuser()}{platform.platform()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:12]
    
    def track_session_start(self):
        """Track when user starts the application"""
        data = {
            "event": "session_start",
            "session_id": self.session_id,
            "user_fingerprint": self.user_fingerprint,
            "version": APP_VERSION,
            "timestamp": datetime.now().isoformat(),
            "platform": platform.platform(),
            "hostname": platform.node()
        }
        self.send_tracking_data(data)
    
    def track_code_review(self, repo_name, pr_number, review_details):
        """Track when user performs a code review"""
        data = {
            "event": "code_review",
            "session_id": self.session_id,
            "user_fingerprint": self.user_fingerprint,
            "version": APP_VERSION,
            "timestamp": datetime.now().isoformat(),
            "repo_name": repo_name,
            "pr_number": pr_number,
            "review_details": {
                "files_reviewed": review_details.get("files_count", 0),
                "comments_posted": review_details.get("comments_count", 0),
                "ai_cost": review_details.get("cost", 0.0)
            }
        }
        self.send_tracking_data(data)
    
    def track_feature_usage(self, feature_name, details=None):
        """Track when user uses specific features"""
        data = {
            "event": "feature_usage",
            "session_id": self.session_id,
            "user_fingerprint": self.user_fingerprint,
            "version": APP_VERSION,
            "timestamp": datetime.now().isoformat(),
            "feature": feature_name,
            "details": details or {}
        }
        self.send_tracking_data(data)
    
    def send_tracking_data(self, data):
        """Send tracking data to cloud endpoint"""
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"AIReviewTool/{APP_VERSION}"
            }
            
            response = requests.post(
                self.tracking_endpoint,
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[TRACKING] ✅ Event '{data['event']}' tracked successfully")
            else:
                print(f"[TRACKING] ⚠️ Failed to track event: {response.status_code}")
                
        except Exception as e:
            print(f"[TRACKING] ❌ Error sending tracking data: {e}")
            # Fallback to local logging
            self.fallback_local_tracking(data)
    
    def fallback_local_tracking(self, data):
        """Fallback to local file tracking if cloud fails"""
        try:
            with open("usage_fallback.json", "a") as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            print(f"[TRACKING] Failed local fallback: {e}")

# Global tracker instance
cloud_tracker = CloudUsageTracker()

# Easy-to-use functions for integration
def track_app_start():
    cloud_tracker.track_session_start()

def track_review(repo, pr, details):
    cloud_tracker.track_code_review(repo, pr, details)

def track_feature(feature, details=None):
    cloud_tracker.track_feature_usage(feature, details)
