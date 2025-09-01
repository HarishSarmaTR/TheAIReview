#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FILE: email_tracker.py

"""
Email-Based Usage Tracking - Sends daily usage reports via email
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from version_utils import APP_VERSION

class EmailUsageTracker:
    def __init__(self):
        self.usage_file = "daily_usage.json"
        self.admin_email = "velavalapalli.harishsarma@thomsonreuters.com"  # Your email
        
    def log_usage(self, event_type, details):
        """Log usage event to daily file"""
        usage_data = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "version": APP_VERSION,
            "user": os.getenv("USERNAME", "unknown"),
            "details": details
        }
        
        # Read existing data
        try:
            with open(self.usage_file, "r") as f:
                data = json.load(f)
        except:
            data = {"date": datetime.now().strftime("%Y-%m-%d"), "events": []}
        
        # Add new event
        data["events"].append(usage_data)
        
        # Save back
        with open(self.usage_file, "w") as f:
            json.dump(data, f, indent=2)
        
        # Check if should send daily report
        self.check_and_send_daily_report()
    
    def check_and_send_daily_report(self):
        """Send daily report if it's a new day"""
        try:
            with open("last_report_date.txt", "r") as f:
                last_report = f.read().strip()
        except:
            last_report = ""
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        if last_report != today:
            self.send_daily_report()
            with open("last_report_date.txt", "w") as f:
                f.write(today)
    
    def send_daily_report(self):
        """Send daily usage report via email"""
        try:
            # Read usage data
            with open(self.usage_file, "r") as f:
                data = json.load(f)
            
            # Create report
            report = self.generate_report(data)
            
            # Send email (using Outlook/Exchange)
            msg = MIMEMultipart()
            msg['From'] = self.admin_email
            msg['To'] = self.admin_email
            msg['Subject'] = f"AI Review Tool - Daily Usage Report {data['date']}"
            
            msg.attach(MIMEText(report, 'plain'))
            
            # For Thomson Reuters, you might need to use internal SMTP
            # server = smtplib.SMTP('your-internal-smtp-server.tr.com', 587)
            # server.send_message(msg)
            
            print(f"[EMAIL TRACKER] Daily report prepared for {data['date']}")
            
        except Exception as e:
            print(f"[EMAIL TRACKER] Error sending report: {e}")
    
    def generate_report(self, data):
        """Generate formatted usage report"""
        events = data.get("events", [])
        
        report = f"""
🤖 AI REVIEW TOOL - DAILY USAGE REPORT
Date: {data.get('date', 'Unknown')}
=====================================

📊 SUMMARY:
• Total Events: {len(events)}
• Users Active: {len(set(e.get('user', 'unknown') for e in events))}
• Versions Used: {len(set(e.get('version', 'unknown') for e in events))}

📋 EVENT BREAKDOWN:
"""
        
        # Group events by type
        event_types = {}
        for event in events:
            event_type = event.get('event', 'unknown')
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append(event)
        
        for event_type, type_events in event_types.items():
            report += f"\n{event_type.upper()}: {len(type_events)} events\n"
            for event in type_events[:5]:  # Show first 5
                report += f"  • {event.get('timestamp', 'N/A')} - {event.get('user', 'Unknown')}\n"
            if len(type_events) > 5:
                report += f"  ... and {len(type_events) - 5} more\n"
        
        return report

# Global email tracker
email_tracker = EmailUsageTracker()

# Easy integration functions
def track_via_email(event_type, details=None):
    email_tracker.log_usage(event_type, details or {})
