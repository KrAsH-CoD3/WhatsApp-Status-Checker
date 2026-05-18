"""
Utility functions and helper methods
"""

from datetime import datetime
from typing import Optional
from time import sleep
import requests
import pytz
import json



def get_timezone_from_ip() -> str:
    """Get timezone based on IP geolocation"""
    try:
        response = requests.get("http://lumtest.com/myip.json", timeout=30)
        if response.status_code == 200:
            data: dict[str, dict[str, str]] = response.json()
            timezone: str = data.get('geo').get('tz')
            if timezone:
                return timezone
    except (requests.RequestException, json.JSONDecodeError, KeyError, AttributeError):
        pass
    
    # Fallback to GMT if IP detection fails
    return "GMT"


def initialize_timezone(tz: Optional[str] = None) -> str:
    """Initialize timezone once at application startup"""
    global _detected_timezone
    
    if tz is not None:
        _detected_timezone = tz
    else:
        _detected_timezone = get_timezone_from_ip()
    
    return _detected_timezone


def get_time() -> str:
    """Get current time in the initialized timezone formatted as HH:MM:SS AM/PM
    
    Returns:
        Formatted time string (HH:MM:SS AM/PM)
    """
    global _detected_timezone

    if _detected_timezone is None:
        # Fallback if not initialized
        _detected_timezone = get_timezone_from_ip()
    
    return datetime.now(pytz.timezone(_detected_timezone)).strftime("%I:%M:%S %p")




def calculate_next_reminder_time(ttime_diff: float, sstart: float, reminder_time: int) -> float:
    """Calculate next reminder time based on configured interval"""
    if (
       reminder_time == 1 and ttime_diff >= 1_800  # Every 30 Mins
       or reminder_time == 2 and ttime_diff >= 3_600  # Every 1 Hour
       or reminder_time == 3 and ttime_diff >= 10_800  # Every 3 Hours
       or reminder_time == 4 and ttime_diff >= 21_600  # Every 6 Hours
    ):
        from time import perf_counter
        return float("{:.2f}".format(perf_counter()))
    else:
        return sstart
