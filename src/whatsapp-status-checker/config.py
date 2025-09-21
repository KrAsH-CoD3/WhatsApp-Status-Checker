from os import environ as env_variable
from dotenv import load_dotenv

load_dotenv()

# CallMeBot API Configuration
NUMBER: str = env_variable.get("MY_NUMBER")  # Your WhatsApp Number with country code e.g: +1234567890
CALLMEBOT_APIKEY: str = env_variable.get("CALLMEBOT_APIKEY")  # CallMeBot API Key

status_uploader_name: str = "contact_name" # As it is saved on your phone(Case Sensitive)
timezone: str = "Africa/Lagos"  # Your timezone #TODO: Use specified timezone else Automatically get it