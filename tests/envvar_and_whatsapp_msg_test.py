from os import environ as env_variable
from callmebot import send_message
from dotenv import load_dotenv

load_dotenv()

NUMBER: str = env_variable.get("MY_NUMBER")
CALLMEBOT_APIKEY: str = env_variable.get("CALLMEBOT_APIKEY")

# Test CallMeBot API
message = "This is a test message to confirm CallMeBot API is working 🤖✨"
success, response = send_message(message, NUMBER, CALLMEBOT_APIKEY)

if success:
    print("✅ CallMeBot API test successful!")
else:
    print(f"❌ CallMeBot API test failed: {response}")
        
