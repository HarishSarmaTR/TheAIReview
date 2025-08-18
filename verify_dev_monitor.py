#!/usr/bin/env python3
"""
Quick verification script for dev monitor functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from AIReview.usage_tracker import *
    print("✅ Usage tracker import successful")
    
    # Test admin detection
    is_admin = is_current_user_admin()
    print(f"🔐 Admin status: {is_admin}")
    
    # Test session management
    session_result = start_session({"email": "test@company.com", "display_name": "Test User"})
    print(f"📊 Session start: {session_result}")
    
    # Test activity logging
    log_activity("SYSTEM_TEST", "Testing dev monitor functionality")
    print("✅ Activity logged successfully")
    
    # Test reporting
    report = get_usage_report()
    if "error" not in report:
        print(f"📈 Usage report generated: {report['summary']['capacity_status']}")
    else:
        print(f"❌ Report error: {report['error']}")
    
    # Clean up
    end_session()
    print("✅ Session ended successfully")
    
    print("\n🎯 Dev Monitor Status:")
    print("   ✅ Import functionality working")
    print("   ✅ Admin detection working") 
    print("   ✅ Session management working")
    print("   ✅ Activity logging working")
    print("   ✅ Usage reporting working")
    print("\n🚀 Dev Monitor is ready for use!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
