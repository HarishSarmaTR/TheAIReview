#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FILE: enhanced_tracking.py

"""
Enhanced Multi-Method Tracking System for AI Review Tool
Combines local, email, and cloud tracking for maximum visibility
"""

import json
import os
from datetime import datetime
import requests
import hashlib
import platform
import getpass
from version_utils import APP_VERSION, APP_NAME, RELEASE_DATE

class EnhancedTracker:
    def __init__(self):
        self.tracking_methods = {
            "local": True,      # Always works
            "email": True,      # Daily reports
            "cloud": True,      # Real-time dashboard
            "network": True     # Network share tracking
        }
        
        # File locations
        self.local_file = "enhanced_usage.json"
        self.network_path = "\\\\shared-drive\\ai-review-tracking\\usage_data.json"  # Update with your network path
        self.webhook_url = "https://webhook.site/#!/your-unique-id"  # Update with your webhook
        
    def track_event(self, event_type, details=None):
        """Track event using all available methods"""
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "version": APP_VERSION,
            "app_name": APP_NAME,
            "release_date": RELEASE_DATE,
            "user": getpass.getuser(),
            "hostname": platform.node(),
            "platform": platform.platform(),
            "details": details or {},
            "session_id": self.get_session_id()
        }
        
        # Method 1: Local tracking (always works)
        self.track_local(event_data)
        
        # Method 2: Network share tracking (if available)
        self.track_network(event_data)
        
        # Method 3: Cloud webhook tracking (if internet available)
        self.track_cloud(event_data)
        
        # Method 4: Email aggregation (daily summary)
        self.track_email(event_data)
        
        print(f"[TRACKING] ✅ Event '{event_type}' tracked via multiple methods")
    
    def track_local(self, event_data):
        """Track to local JSON file"""
        try:
            # Read existing data
            if os.path.exists(self.local_file):
                with open(self.local_file, "r") as f:
                    data = json.load(f)
            else:
                data = {"events": []}
            
            # Add new event
            data["events"].append(event_data)
            
            # Keep only last 1000 events to prevent file bloat
            if len(data["events"]) > 1000:
                data["events"] = data["events"][-1000:]
            
            # Save back
            with open(self.local_file, "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[TRACKING] Local tracking failed: {e}")
    
    def track_network(self, event_data):
        """Track to network share (for enterprise environments)"""
        try:
            if os.path.exists(os.path.dirname(self.network_path)):
                # Read existing network data
                if os.path.exists(self.network_path):
                    with open(self.network_path, "r") as f:
                        data = json.load(f)
                else:
                    data = {"events": []}
                
                # Add event
                data["events"].append(event_data)
                
                # Save to network
                with open(self.network_path, "w") as f:
                    json.dump(data, f, indent=2)
                    
        except Exception as e:
            print(f"[TRACKING] Network tracking failed: {e}")
    
    def track_cloud(self, event_data):
        """Track to cloud webhook for real-time monitoring"""
        try:
            response = requests.post(
                self.webhook_url.replace("#!/", ""),
                json=event_data,
                timeout=5
            )
            if response.status_code == 200:
                print(f"[TRACKING] ☁️ Cloud tracking successful")
        except Exception as e:
            print(f"[TRACKING] Cloud tracking failed: {e}")
    
    def track_email(self, event_data):
        """Aggregate for daily email reports"""
        try:
            email_file = f"email_tracking_{datetime.now().strftime('%Y-%m-%d')}.json"
            
            if os.path.exists(email_file):
                with open(email_file, "r") as f:
                    data = json.load(f)
            else:
                data = {"date": datetime.now().strftime('%Y-%m-%d'), "events": []}
            
            data["events"].append(event_data)
            
            with open(email_file, "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[TRACKING] Email tracking failed: {e}")
    
    def get_session_id(self):
        """Generate session ID"""
        return hashlib.md5(f"{datetime.now().date()}{getpass.getuser()}".encode()).hexdigest()[:8]
    
    def generate_live_dashboard(self):
        """Generate live HTML dashboard"""
        try:
            with open(self.local_file, "r") as f:
                data = json.load(f)
            
            events = data.get("events", [])
            
            # Generate simple HTML dashboard
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Review Tool - Live Usage Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .event {{ background: #e8f4f8; padding: 8px; margin: 5px 0; border-left: 3px solid #007acc; }}
    </style>
</head>
<body>
    <h1>🤖 AI Review Tool - Live Dashboard</h1>
    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="metric">
        <h3>📊 Current Stats</h3>
        <p>Total Events Today: {len([e for e in events if e.get('timestamp', '').startswith(datetime.now().strftime('%Y-%m-%d'))])}</p>
        <p>Active Users: {len(set(e.get('user', 'unknown') for e in events[-50:]))}</p>
        <p>Current Version: {APP_VERSION}</p>
    </div>
    
    <div class="metric">
        <h3>🕒 Recent Activity (Last 10 events)</h3>
"""
            
            for event in events[-10:]:
                html += f"""
        <div class="event">
            <strong>{event.get('timestamp', 'N/A')}</strong> - 
            {event.get('user', 'Unknown')} - 
            {event.get('event', 'Unknown')} 
            (v{event.get('version', 'Unknown')})
        </div>
"""
            
            html += """
    </div>
</body>
</html>
"""
            
            # Save dashboard
            with open("live_dashboard.html", "w") as f:
                f.write(html)
                
            print(f"[DASHBOARD] 📊 Live dashboard updated: live_dashboard.html")
            
        except Exception as e:
            print(f"[DASHBOARD] Failed to generate dashboard: {e}")

# Global enhanced tracker
enhanced_tracker = EnhancedTracker()

# Easy integration functions
def track_app_start():
    enhanced_tracker.track_event("APP_START")
    enhanced_tracker.generate_live_dashboard()

def track_code_review(repo, pr, details):
    enhanced_tracker.track_event("CODE_REVIEW", {
        "repo": repo,
        "pr": pr,
        "files_reviewed": details.get("files", 0),
        "comments_posted": details.get("comments", 0),
        "cost": details.get("cost", 0.0)
    })
    enhanced_tracker.generate_live_dashboard()

def track_feature_use(feature, details=None):
    enhanced_tracker.track_event("FEATURE_USE", {"feature": feature, "details": details})
    enhanced_tracker.generate_live_dashboard()
