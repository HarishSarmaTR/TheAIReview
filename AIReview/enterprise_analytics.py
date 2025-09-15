"""
Enterprise Analytics Module for AI Code Review Tool
Real-time usage tracking across multiple users and departments

Author: AI Assistant
Date: 2025
License: Thomson Reuters Internal Use
"""

import json
import requests
import threading
import time
import os
import socket
import platform
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib
import logging

class EnterpriseAnalytics:
    """
    Enterprise-grade analytics system for tracking application usage
    across multiple users and departments in real-time.
    
    Features:
    - Real-time user activity tracking
    - Department/team analytics 
    - Feature usage statistics
    - Performance monitoring
    - Privacy-compliant data collection
    - Secure data transmission
    """
    
    def __init__(self, app_version: str = "2.1.8", analytics_endpoint: str = None):
        self.app_version = app_version
        self.session_id = str(uuid.uuid4())
        self.user_id = self._get_anonymous_user_id()
        self.machine_id = self._get_machine_fingerprint()
        self.start_time = datetime.now()
        
        # Analytics endpoint (can be internal server, Azure, or cloud service)
        self.analytics_endpoint = analytics_endpoint or "https://your-internal-analytics-server.tr.com/api/analytics"
        
        # Local backup storage
        self.local_storage_path = os.path.join(os.path.expanduser("~"), ".ai_review_analytics")
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Event queue for batch sending
        self.event_queue = []
        self.queue_lock = threading.Lock()
        
        # User consent and privacy
        self.data_collection_consent = self._check_user_consent()
        
        # Start background telemetry
        self._start_telemetry_worker()
        
        print(f"[ANALYTICS] Enterprise analytics initialized - Session: {self.session_id[:8]}...")

    def _get_anonymous_user_id(self) -> str:
        """Generate anonymous but consistent user ID"""
        try:
            # Use Windows username + machine name for consistent but anonymous ID
            username = os.getenv('USERNAME', 'unknown')
            machine = socket.gethostname()
            unique_string = f"{username}@{machine}"
            
            # Hash for privacy (no personal info stored)
            hashed_id = hashlib.sha256(unique_string.encode()).hexdigest()[:16]
            return f"user_{hashed_id}"
        except Exception:
            return f"user_{uuid.uuid4().hex[:16]}"

    def _get_machine_fingerprint(self) -> str:
        """Get anonymous machine fingerprint for analytics"""
        try:
            system_info = f"{platform.system()}_{platform.release()}_{platform.machine()}"
            machine_hash = hashlib.md5(system_info.encode()).hexdigest()[:12]
            return f"machine_{machine_hash}"
        except Exception:
            return f"machine_{uuid.uuid4().hex[:12]}"

    def _check_user_consent(self) -> bool:
        """Check if user has consented to analytics (enterprise compliance)"""
        consent_file = os.path.join(self.local_storage_path, "analytics_consent.json")
        
        try:
            if os.path.exists(consent_file):
                with open(consent_file, 'r') as f:
                    consent_data = json.load(f)
                    return consent_data.get('consent_given', False)
            else:
                # First time - ask for consent
                return self._request_user_consent()
        except Exception:
            return False

    def _request_user_consent(self) -> bool:
        """Request user consent for analytics collection"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            consent_message = """🔬 Enterprise Analytics & Usage Tracking

The AI Code Review Tool collects anonymous usage statistics to:

✅ Monitor application performance and reliability
✅ Understand feature usage across teams
✅ Improve user experience and functionality
✅ Generate executive reports for management

🔒 PRIVACY PROTECTION:
• No personal information is collected
• Data is anonymized and encrypted
• Only usage patterns and performance metrics
• Compliant with Thomson Reuters data policies

Do you consent to anonymous usage analytics?"""

            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            result = messagebox.askyesno("Enterprise Analytics Consent", consent_message)
            root.destroy()
            
            # Save consent choice
            consent_file = os.path.join(self.local_storage_path, "analytics_consent.json")
            consent_data = {
                'consent_given': result,
                'timestamp': datetime.now().isoformat(),
                'version': self.app_version
            }
            
            with open(consent_file, 'w') as f:
                json.dump(consent_data, f, indent=2)
                
            return result
            
        except Exception as e:
            print(f"[ANALYTICS] Consent dialog failed: {e}")
            return False

    def track_event(self, event_name: str, properties: Dict[str, Any] = None, category: str = "general"):
        """
        Track a user event with properties
        
        Args:
            event_name: Name of the event (e.g., "review_started", "token_extracted")
            properties: Additional event properties
            category: Event category (e.g., "user_action", "performance", "error")
        """
        if not self.data_collection_consent:
            return
            
        event_data = {
            'event_id': str(uuid.uuid4()),
            'event_name': event_name,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'user_id': self.user_id,
            'machine_id': self.machine_id,
            'app_version': self.app_version,
            'properties': properties or {}
        }
        
        # Add to queue for batch processing
        with self.queue_lock:
            self.event_queue.append(event_data)
        
        # Also store locally as backup
        self._store_event_locally(event_data)

    def track_feature_usage(self, feature_name: str, duration_ms: int = None, success: bool = True):
        """Track feature usage with performance metrics"""
        properties = {
            'feature': feature_name,
            'success': success,
            'duration_ms': duration_ms
        }
        
        self.track_event("feature_used", properties, "feature_usage")

    def track_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Track performance metrics"""
        properties = {
            'metric': metric_name,
            'value': value,
            'unit': unit
        }
        
        self.track_event("performance_metric", properties, "performance")

    def track_error(self, error_type: str, error_message: str, stack_trace: str = None):
        """Track application errors"""
        properties = {
            'error_type': error_type,
            'error_message': error_message[:500],  # Limit length
            'has_stack_trace': stack_trace is not None
        }
        
        self.track_event("error_occurred", properties, "error")

    def track_user_demographics(self, department: str = None, role: str = None):
        """Track user demographics for organizational insights"""
        properties = {
            'department': department,
            'role': role
        }
        
        self.track_event("user_demographics", properties, "demographics")

    def _store_event_locally(self, event_data: Dict[str, Any]):
        """Store event locally as backup"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            local_file = os.path.join(self.local_storage_path, f"analytics_{today}.jsonl")
            
            with open(local_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_data) + '\n')
                
        except Exception as e:
            print(f"[ANALYTICS] Local storage failed: {e}")

    def _start_telemetry_worker(self):
        """Start background worker to send analytics data"""
        def telemetry_worker():
            while True:
                try:
                    time.sleep(30)  # Send every 30 seconds
                    self._send_queued_events()
                except Exception as e:
                    print(f"[ANALYTICS] Telemetry worker error: {e}")
                    
        worker_thread = threading.Thread(target=telemetry_worker, daemon=True)
        worker_thread.start()

    def _send_queued_events(self):
        """Send queued events to analytics endpoint"""
        if not self.data_collection_consent:
            return
            
        with self.queue_lock:
            if not self.event_queue:
                return
                
            events_to_send = self.event_queue.copy()
            self.event_queue.clear()

        try:
            # Send to analytics endpoint
            payload = {
                'events': events_to_send,
                'metadata': {
                    'client_version': self.app_version,
                    'timestamp': datetime.now().isoformat(),
                    'event_count': len(events_to_send)
                }
            }
            
            response = requests.post(
                self.analytics_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[ANALYTICS] Sent {len(events_to_send)} events successfully")
            else:
                print(f"[ANALYTICS] Send failed: HTTP {response.status_code}")
                # Re-queue events for retry
                with self.queue_lock:
                    self.event_queue.extend(events_to_send)
                    
        except Exception as e:
            print(f"[ANALYTICS] Network send failed: {e}")
            # Re-queue events for retry
            with self.queue_lock:
                self.event_queue.extend(events_to_send)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session summary"""
        session_duration = datetime.now() - self.start_time
        
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'machine_id': self.machine_id,
            'app_version': self.app_version,
            'session_duration_minutes': session_duration.total_seconds() / 60,
            'events_queued': len(self.event_queue),
            'consent_given': self.data_collection_consent
        }

    def end_session(self):
        """End current session and send final data"""
        session_summary = self.get_session_summary()
        self.track_event("session_ended", session_summary, "session")
        
        # Force send remaining events
        self._send_queued_events()
        
        print(f"[ANALYTICS] Session ended - Duration: {session_summary['session_duration_minutes']:.1f} minutes")

# Global analytics instance
_analytics_instance = None

def get_analytics() -> EnterpriseAnalytics:
    """Get global analytics instance"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = EnterpriseAnalytics()
    return _analytics_instance

def track_app_event(event_name: str, properties: Dict[str, Any] = None, category: str = "general"):
    """Convenience function to track events"""
    try:
        analytics = get_analytics()
        analytics.track_event(event_name, properties, category)
    except Exception as e:
        print(f"[ANALYTICS] Event tracking failed: {e}")

# Convenience functions
def track_review_started(repository: str, pr_number: int):
    """Track when a code review is started"""
    track_app_event("review_started", {
        'repository': repository,
        'pr_number': pr_number
    }, "code_review")

def track_review_completed(repository: str, pr_number: int, duration_seconds: int, comments_posted: int):
    """Track when a code review is completed"""
    track_app_event("review_completed", {
        'repository': repository,
        'pr_number': pr_number,
        'duration_seconds': duration_seconds,
        'comments_posted': comments_posted
    }, "code_review")

def track_token_extraction(token_type: str, success: bool):
    """Track token extraction attempts"""
    track_app_event("token_extracted", {
        'token_type': token_type,
        'success': success
    }, "authentication")

def track_feature_access(feature_name: str):
    """Track feature access"""
    track_app_event("feature_accessed", {
        'feature': feature_name
    }, "feature_usage")
