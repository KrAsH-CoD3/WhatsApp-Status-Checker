from os import environ as env_variable
from dotenv import load_dotenv
from typing import Optional
load_dotenv()

# CallMeBot API Configuration
NUMBER: str = env_variable.get("MY_NUMBER")  # Your WhatsApp Number with country code e.g: +1234567890
CALLMEBOT_APIKEY: str = env_variable.get("CALLMEBOT_APIKEY")  # CallMeBot API Key

status_uploader_name: str = "contact_name" # As it is saved on your phone(Case Sensitive)
# Your timezone (None for auto-detection from IP)
timezone: Optional[str] = None # Example: "Africa/Lagos", Specify your timezone manually