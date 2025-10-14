"""
WhatsApp Status Checker
"""

from config import NUMBER, CALLMEBOT_APIKEY, status_uploader_name, timezone
from core.app_controller import WhatsAppStatusApp
from utils import ensure_chromedriver
from art import set_default


def main():
    # Setup
    ensure_chromedriver()
    set_default("fancy99")
    
    # Create and run application
    app = WhatsAppStatusApp(NUMBER, CALLMEBOT_APIKEY, status_uploader_name, timezone)
    app.run()

if __name__ == "__main__":
    main()