import os
from datetime import datetime, time, timedelta
import pytz
from fastapi import HTTPException
from fastapi.responses import HTMLResponse

class RuntimeScheduler:
    def __init__(self, timezone="UTC"):
        """
        Initialize runtime scheduler
        
        Args:
            timezone: Timezone string (e.g., "UTC", "US/Eastern", "Asia/Manila")
        """
        self.timezone = pytz.timezone(timezone)
        
        # Default schedule: Run 8 AM to 10 PM (14 hours)
        # This uses only ~420 hours per month instead of 720
        self.start_time = time(8, 0)   # 8:00 AM
        self.end_time = time(22, 0)    # 10:00 PM
        
        # Override with environment variables if set
        start_hour = int(os.environ.get("RUNTIME_START_HOUR", "8"))
        end_hour = int(os.environ.get("RUNTIME_END_HOUR", "22"))
        
        self.start_time = time(start_hour, 0)
        self.end_time = time(end_hour, 0)
        
        # Portfolio mode: weekdays only
        self.weekdays_only = os.environ.get("RUNTIME_WEEKDAYS_ONLY", "false").lower() == "true"
    
    def is_runtime_allowed(self) -> bool:
        """Check if current time is within allowed runtime hours"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        
        # Check weekdays only mode (perfect for portfolio!)
        if self.weekdays_only:
            # Monday = 0, Sunday = 6
            if now.weekday() >= 5:  # Saturday (5) or Sunday (6)
                return False
        
        if self.start_time <= self.end_time:
            # Normal case: 8 AM to 10 PM
            return self.start_time <= current_time <= self.end_time
        else:
            # Overnight case: 10 PM to 8 AM
            return current_time >= self.start_time or current_time <= self.end_time
    
    def get_next_runtime(self) -> str:
        """Get next allowed runtime as string"""
        now = datetime.now(self.timezone)
        
        if self.is_runtime_allowed():
            return "Currently running"
        
        # Calculate next start time
        if now.time() < self.start_time:
            # Same day
            next_start = now.replace(
                hour=self.start_time.hour, 
                minute=self.start_time.minute, 
                second=0, 
                microsecond=0
            )
        else:
            # Next day
            next_start = now.replace(
                hour=self.start_time.hour, 
                minute=self.start_time.minute, 
                second=0, 
                microsecond=0
            ) + timedelta(days=1)
        
        # If weekdays only, adjust to next weekday
        if self.weekdays_only:
            while next_start.weekday() >= 5:  # Skip weekends
                next_start += timedelta(days=1)
        
        return next_start.strftime("%Y-%m-%d %H:%M %Z")
    
    def get_schedule_info(self) -> dict:
        """Get schedule information"""
        schedule_type = "Weekdays Only" if self.weekdays_only else "Daily"
        daily_hours = self._calculate_daily_hours()
        monthly_hours = daily_hours * (22 if self.weekdays_only else 30)  # 22 weekdays per month
        
        return {
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M"),
            "timezone": str(self.timezone),
            "schedule_type": schedule_type,
            "is_running": self.is_runtime_allowed(),
            "next_runtime": self.get_next_runtime(),
            "daily_hours": daily_hours,
            "monthly_hours": monthly_hours
        }
    
    def _calculate_daily_hours(self) -> float:
        """Calculate daily runtime hours"""
        if self.start_time <= self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            return (end_minutes - start_minutes) / 60
        else:
            # Overnight schedule
            return 24 - self._calculate_daily_hours()

# Global scheduler instance
scheduler = RuntimeScheduler(timezone=os.environ.get("TIMEZONE", "UTC"))

def check_runtime_allowed():
    """Middleware to check if runtime is allowed"""
    if not scheduler.is_runtime_allowed():
        schedule_info = scheduler.get_schedule_info()
        maintenance_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scheduled Maintenance</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }}
                .clock {{ font-size: 3em; margin: 20px 0; }}
                .schedule {{ font-size: 1.2em; margin: 20px 0; }}
                .next-time {{ 
                    background: rgba(255,255,255,0.2); 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin: 20px 0;
                }}
                .badge {{ 
                    background: rgba(255,255,255,0.3); 
                    padding: 5px 10px; 
                    border-radius: 15px; 
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌙 Digital Bulletin Board</h1>
                <div class="clock">💤</div>
                <h2>Scheduled Maintenance</h2>
                <p>The bulletin board is currently offline for scheduled maintenance.</p>
                
                <div class="schedule">
                    <span class="badge">{schedule_info['schedule_type']}</span><br><br>
                    <strong>Operating Hours:</strong><br>
                    {schedule_info['start_time']} - {schedule_info['end_time']} {schedule_info['timezone']}
                </div>
                
                <div class="next-time">
                    <strong>Next Available:</strong><br>
                    {schedule_info['next_runtime']}
                </div>
                
                <p>This helps conserve server resources and ensures optimal performance during peak hours.</p>
                <p><em>Monthly usage: {schedule_info['monthly_hours']:.0f} hours (within free tier limits)</em></p>
                <p>Thank you for your understanding! 🙏</p>
            </div>
        </body>
        </html>
        """
        raise HTTPException(
            status_code=503, 
            detail=maintenance_html,
            headers={"Content-Type": "text/html"}
        )
