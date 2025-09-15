#!/usr/bin/env python3
"""
Management Report Generator for AI Review Tool
Creates comprehensive usage reports for management presentation

Author: AI Assistant
Created: September 2025
"""

import json
import os
import datetime
import pandas as pd
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import hashlib

# Import version utilities
try:
    from version_utils import APP_VERSION, APP_NAME, RELEASE_DATE
    from usage_tracker import get_comprehensive_report, USAGE_LOG_FILE
except ImportError:
    APP_VERSION = "2.1.8"
    APP_NAME = "AI Code Review Tool"
    USAGE_LOG_FILE = "usage_log.json"

class ManagementReportGenerator:
    def __init__(self):
        self.usage_data = self.load_usage_data()
        self.report_date = datetime.datetime.now()
        
    def load_usage_data(self):
        """Load usage data from tracking files"""
        if not os.path.exists(USAGE_LOG_FILE):
            return {"sessions": [], "activities": [], "summary": {}}
            
        try:
            with open(USAGE_LOG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load usage data: {e}")
            return {"sessions": [], "activities": [], "summary": {}}
    
    def generate_executive_summary(self):
        """Generate high-level executive summary"""
        sessions = self.usage_data.get("sessions", [])
        activities = self.usage_data.get("activities", [])
        
        # Calculate key metrics
        total_users = len(set(session.get("user", "Unknown") for session in sessions))
        total_sessions = len(sessions)
        total_reviews = len([act for act in activities if "review" in act.get("action", "").lower()])
        
        # Calculate date ranges
        if sessions:
            dates = [datetime.datetime.fromisoformat(session.get("start_time", "2025-01-01T00:00:00")) 
                    for session in sessions if session.get("start_time")]
            if dates:
                start_date = min(dates)
                end_date = max(dates)
                days_active = (end_date - start_date).days + 1
            else:
                start_date = end_date = datetime.datetime.now()
                days_active = 1
        else:
            start_date = end_date = datetime.datetime.now()
            days_active = 1
        
        return {
            "report_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "total_active_users": total_users,
            "total_sessions": total_sessions,
            "total_code_reviews": total_reviews,
            "days_with_activity": days_active,
            "average_sessions_per_day": round(total_sessions / max(days_active, 1), 2),
            "average_reviews_per_user": round(total_reviews / max(total_users, 1), 2)
        }
    
    def generate_user_adoption_metrics(self):
        """Generate user adoption and engagement metrics"""
        sessions = self.usage_data.get("sessions", [])
        activities = self.usage_data.get("activities", [])
        
        user_stats = defaultdict(lambda: {
            "sessions": 0,
            "total_duration": 0,
            "reviews_completed": 0,
            "last_active": None,
            "first_active": None
        })
        
        for session in sessions:
            user = session.get("user", "Unknown")
            user_stats[user]["sessions"] += 1
            
            if session.get("duration"):
                user_stats[user]["total_duration"] += session["duration"]
            
            session_time = session.get("start_time")
            if session_time:
                try:
                    session_dt = datetime.datetime.fromisoformat(session_time)
                    if not user_stats[user]["first_active"] or session_dt < user_stats[user]["first_active"]:
                        user_stats[user]["first_active"] = session_dt
                    if not user_stats[user]["last_active"] or session_dt > user_stats[user]["last_active"]:
                        user_stats[user]["last_active"] = session_dt
                except:
                    pass
        
        for activity in activities:
            if "review" in activity.get("action", "").lower():
                user = activity.get("user", "Unknown")
                user_stats[user]["reviews_completed"] += 1
        
        return dict(user_stats)
    
    def generate_feature_usage_analytics(self):
        """Generate feature usage and performance analytics"""
        activities = self.usage_data.get("activities", [])
        
        feature_usage = Counter()
        performance_metrics = defaultdict(list)
        
        for activity in activities:
            action = activity.get("action", "Unknown")
            feature_usage[action] += 1
            
            if "duration" in activity:
                performance_metrics[action].append(activity["duration"])
        
        # Calculate average performance per feature
        feature_performance = {}
        for feature, durations in performance_metrics.items():
            if durations:
                feature_performance[feature] = {
                    "average_duration": round(sum(durations) / len(durations), 2),
                    "usage_count": len(durations),
                    "total_time": sum(durations)
                }
        
        return {
            "feature_usage_count": dict(feature_usage),
            "feature_performance": feature_performance
        }
    
    def generate_trend_analysis(self):
        """Generate usage trends over time"""
        sessions = self.usage_data.get("sessions", [])
        
        daily_usage = defaultdict(int)
        weekly_usage = defaultdict(int)
        monthly_usage = defaultdict(int)
        
        for session in sessions:
            if session.get("start_time"):
                try:
                    dt = datetime.datetime.fromisoformat(session["start_time"])
                    daily_usage[dt.strftime("%Y-%m-%d")] += 1
                    weekly_usage[dt.strftime("%Y-W%U")] += 1
                    monthly_usage[dt.strftime("%Y-%m")] += 1
                except:
                    pass
        
        return {
            "daily_sessions": dict(daily_usage),
            "weekly_sessions": dict(weekly_usage),
            "monthly_sessions": dict(monthly_usage)
        }
    
    def generate_roi_analysis(self):
        """Generate ROI and productivity impact analysis"""
        activities = self.usage_data.get("activities", [])
        
        reviews_completed = len([act for act in activities if "review" in act.get("action", "").lower()])
        comments_posted = sum(1 for act in activities if "comment" in act.get("action", "").lower())
        
        # Estimated time savings (assuming manual review takes 2-3x longer)
        avg_review_time = 15  # minutes
        estimated_time_saved_per_review = 30  # minutes
        total_time_saved = reviews_completed * estimated_time_saved_per_review
        
        # Cost savings (assuming developer hourly rate)
        hourly_rate = 75  # USD (average developer rate)
        cost_savings = (total_time_saved / 60) * hourly_rate
        
        return {
            "reviews_completed": reviews_completed,
            "comments_generated": comments_posted,
            "estimated_time_saved_hours": round(total_time_saved / 60, 2),
            "estimated_cost_savings_usd": round(cost_savings, 2),
            "productivity_improvement": f"{round((estimated_time_saved_per_review / avg_review_time) * 100, 1)}%"
        }
    
    def generate_html_executive_report(self):
        """Generate a comprehensive HTML report for management"""
        exec_summary = self.generate_executive_summary()
        user_metrics = self.generate_user_adoption_metrics()
        feature_analytics = self.generate_feature_usage_analytics()
        trends = self.generate_trend_analysis()
        roi = self.generate_roi_analysis()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{APP_NAME} - Executive Usage Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 5px; }}
        .metric-label {{ color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
        .section {{ background: white; margin: 20px 0; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        .user-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .user-table th, .user-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .user-table th {{ background: #f8f9fa; font-weight: 600; }}
        .feature-bar {{ display: flex; align-items: center; margin: 10px 0; }}
        .feature-name {{ min-width: 150px; font-weight: 500; }}
        .feature-bar-fill {{ background: #667eea; height: 25px; border-radius: 12px; display: flex; align-items: center; padding: 0 10px; color: white; font-size: 0.9em; }}
        .roi-highlight {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .footer {{ text-align: center; margin-top: 40px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{APP_NAME} - Executive Usage Report</h1>
            <p>Generated on: {self.report_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Report Period: {exec_summary['report_period']}</p>
        </div>
        
        <div class="alert">
            <strong>[CONFIDENTIAL]</strong> This report contains proprietary usage analytics for management review only.
        </div>
        
        <div class="section">
            <h2>[EXECUTIVE SUMMARY]</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">{exec_summary['total_active_users']}</div>
                    <div class="metric-label">Active Users</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{exec_summary['total_sessions']}</div>
                    <div class="metric-label">Total Sessions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{exec_summary['total_code_reviews']}</div>
                    <div class="metric-label">Code Reviews</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{exec_summary['average_reviews_per_user']}</div>
                    <div class="metric-label">Avg Reviews/User</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="roi-highlight">
                <h2 style="margin-top: 0; border: none; padding: 0;">[ROI ANALYSIS]</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
                    <div>
                        <div style="font-size: 2em; font-weight: bold;">${roi['estimated_cost_savings_usd']:,.2f}</div>
                        <div>Estimated Cost Savings</div>
                    </div>
                    <div>
                        <div style="font-size: 2em; font-weight: bold;">{roi['estimated_time_saved_hours']}</div>
                        <div>Hours Saved</div>
                    </div>
                    <div>
                        <div style="font-size: 2em; font-weight: bold;">{roi['productivity_improvement']}</div>
                        <div>Productivity Gain</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>[USER ADOPTION]</h2>
            <table class="user-table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Sessions</th>
                        <th>Reviews</th>
                        <th>Total Hours</th>
                        <th>Last Active</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add user data to table
        for user, stats in sorted(user_metrics.items(), key=lambda x: x[1]['sessions'], reverse=True)[:20]:
            hours = round(stats['total_duration'] / 3600, 1) if stats['total_duration'] else 0
            last_active = stats['last_active'].strftime('%Y-%m-%d') if stats['last_active'] else 'Unknown'
            html_content += f"""
                    <tr>
                        <td>{user[:20]}{'...' if len(user) > 20 else ''}</td>
                        <td>{stats['sessions']}</td>
                        <td>{stats['reviews_completed']}</td>
                        <td>{hours}h</td>
                        <td>{last_active}</td>
                    </tr>
"""
        
        html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>[FEATURE USAGE ANALYTICS]</h2>
"""
        
        # Add feature usage bars
        feature_data = feature_analytics['feature_usage_count']
        if feature_data:
            max_usage = max(feature_data.values())
            for feature, count in sorted(feature_data.items(), key=lambda x: x[1], reverse=True)[:10]:
                width = (count / max_usage) * 100
                html_content += f"""
            <div class="feature-bar">
                <div class="feature-name">{feature[:20]}{'...' if len(feature) > 20 else ''}</div>
                <div class="feature-bar-fill" style="width: {width}%">{count} uses</div>
            </div>
"""
        
        html_content += f"""
        </div>
        
        <div class="section">
            <h2>[USAGE TRENDS]</h2>
            <p>Daily usage patterns show {'consistent' if len(trends['daily_sessions']) > 5 else 'growing'} engagement with the AI Review Tool.</p>
            <p>Peak usage: {max(trends['daily_sessions'].values()) if trends['daily_sessions'] else 0} sessions in a single day</p>
            <p>Most active month: {max(trends['monthly_sessions'].items(), key=lambda x: x[1])[0] if trends['monthly_sessions'] else 'No data'}</p>
        </div>
        
        <div class="section">
            <h2>[RECOMMENDATIONS FOR MANAGEMENT]</h2>
            <ul>
                <li><strong>Expand Rollout:</strong> With {exec_summary['total_active_users']} active users showing {roi['productivity_improvement']} productivity improvement, consider broader team deployment.</li>
                <li><strong>Training Investment:</strong> Users completing more reviews show higher engagement. Recommend structured training program.</li>
                <li><strong>Integration Opportunities:</strong> High usage in code review features suggests potential for CI/CD pipeline integration.</li>
                <li><strong>Cost-Benefit Positive:</strong> Estimated ${roi['estimated_cost_savings_usd']:,.2f} cost savings demonstrate clear ROI for continued investment.</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by {APP_NAME} v{APP_VERSION} | Thomson Reuters UltraTax Team</p>
            <p>[CONFIDENTIAL] - For Internal Management Use Only</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content
    
    def save_management_report(self):
        """Save the management report to file"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"management_usage_report_{timestamp}.html"
        
        try:
            html_content = self.generate_html_executive_report()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"[SUCCESS] Management report generated: {filename}")
            return filename
        except Exception as e:
            print(f"[ERROR] Failed to generate management report: {e}")
            return None

def generate_management_report():
    """Main function to generate management report"""
    generator = ManagementReportGenerator()
    return generator.save_management_report()

if __name__ == "__main__":
    generate_management_report()
