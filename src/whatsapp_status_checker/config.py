from os import environ as env_variable
from dotenv import load_dotenv
from typing import Optional
load_dotenv()

# CallMeBot API Configuration
NUMBER: Optional[str] = env_variable.get("MY_NUMBER")  # Your WhatsApp Number with country code e.g: +1234567890
CALLMEBOT_APIKEY: Optional[str] = env_variable.get("CALLMEBOT_APIKEY")  # CallMeBot API Key

STATUS_UPLOADER_NAME: Optional[str] = env_variable.get("STATUS_UPLOADER_NAME") # As it is saved on your phone(Case Sensitive)
TIMEZONE: Optional[str] = env_variable.get("TIMEZONE") # Example: "Africa/Lagos", Specify your timezone manually
REMINDER_TIME: Optional[str] = env_variable.get("REMINDER_TIME")  # Notification interval: 1=30min, 2=1hr, 3=3hrs, 4=6hrs
HEADLESS: Optional[str] = env_variable.get("HEADLESS")  # Run browser without GUI: True/False
AUTO_VIEW: Optional[str] = env_variable.get("AUTO_VIEW")  # Auto-view statuses (True) or notify only (False)
SCREEN_WIDTH: Optional[str] = env_variable.get("SCREEN_WIDTH")  # Browser viewport width in pixels e.g: 800
SCREEN_HEIGHT: Optional[str] = env_variable.get("SCREEN_HEIGHT")  # Browser viewport height in pixels e.g: 800