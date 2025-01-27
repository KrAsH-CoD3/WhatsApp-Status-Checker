from os import environ as env_variable
from dotenv import load_dotenv

load_dotenv()

NUMBER: str = env_variable.get("MY_NUMBER")  # Your WhatsApp Number e.g: 234xxxxxxxxxx
NUM_ID: str = env_variable.get("NUM_ID")  # Your Number ID
TOKEN: str =  env_variable.get("TOKEN")  # Token

status_uploader_name: str = "contact_name" # As it is saved on your phone(Case Sensitive)
timezone: str = "Africa/Lagos"  # Your timezone #TODO: Use specified timezone else Automatically get it