from os import environ as env_variable
from python_whatsapp_bot import Whatsapp, Inline_list, List_item
from dotenv import load_dotenv

load_dotenv()

NUMBER: str = env_variable.get("MY_NUMBER")  # Your WhatsApp Number e.g: 234xxxxxxxxxx
NUM_ID: str = env_variable.get("NUM_ID")  # Your Number ID
TOKEN: str =  env_variable.get("TOKEN")  # Token

wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)
wa_bot.send_message(NUMBER, "This is a test message to confirm env variables are read 🤦.", reply_markup=Inline_list("Show list", \
  list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job 🤞")]))
        
