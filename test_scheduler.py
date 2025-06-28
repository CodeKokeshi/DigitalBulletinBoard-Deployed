#!/usr/bin/env python3
"""
Test script to check runtime scheduler status
Run this to see if your website should be live right now
"""

import os
from datetime import datetime
import pytz
from runtime_scheduler import scheduler

def test_scheduler():
    print("=== Digital Bulletin Board - Runtime Scheduler Test ===")
    print()
    
    # Get current time in Philippine timezone
    ph_tz = pytz.timezone('Asia/Manila')
    current_time_ph = datetime.now(ph_tz)
    current_time_utc = datetime.now(pytz.UTC)
    
    print(f"Current time (Philippines): {current_time_ph.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Current time (UTC): {current_time_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()
    
    # Get scheduler info
    schedule_info = scheduler.get_schedule_info()
    
    print("=== Schedule Configuration ===")
    print(f"Timezone: {schedule_info['timezone']}")
    print(f"Operating Hours: {schedule_info['start_time']} - {schedule_info['end_time']}")
    print(f"Schedule Type: {schedule_info['schedule_type']}")
    print(f"Daily Hours: {schedule_info['daily_hours']}")
    print(f"Monthly Hours: {schedule_info['monthly_hours']}")
    print()
    
    print("=== Current Status ===")
    if schedule_info['is_running']:
        print("✅ Website is LIVE - Currently running!")
    else:
        print("❌ Website is DOWN - Currently in maintenance mode")
        print(f"Next runtime: {schedule_info['next_runtime']}")
    print()
    
    # Environment variables check
    print("=== Environment Variables ===")
    print(f"TIMEZONE: {os.environ.get('TIMEZONE', 'Not set (using default)')}")
    print(f"RUNTIME_START_HOUR: {os.environ.get('RUNTIME_START_HOUR', 'Not set (using default)')}")
    print(f"RUNTIME_END_HOUR: {os.environ.get('RUNTIME_END_HOUR', 'Not set (using default)')}")
    print(f"RUNTIME_WEEKDAYS_ONLY: {os.environ.get('RUNTIME_WEEKDAYS_ONLY', 'Not set (using default)')}")

if __name__ == "__main__":
    test_scheduler()
