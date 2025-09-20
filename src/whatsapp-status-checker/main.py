from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException, WebDriverException
from concurrent.futures import ThreadPoolExecutor, as_completed
from python_whatsapp_bot import Whatsapp, Inline_list, List_item
from art import tprint, set_default, text2art
from urllib3.exceptions import ProtocolError
from time import perf_counter
from typing import Optional
import contextlib
import pyautogui
import threading

# Local imports
from core import StatusHandlerFactory, VideoStatusHandler, BotManager, WhatsAppOperations
from utils import ensure_chromedriver, gmtTime, reminderFn
from vars import *
from config import *


ensure_chromedriver() # Handle ChromeDriver

set_default("fancy99")
tprint("WhatsApp Status Viewer", 'rectangles')
tprint('\nDo you want to get notified about status or view them automatically?\n\
Enter "Y" to get notified or "N" to view them automatically: ')

# Global variables for bot and WhatsApp operations
bot = None
wa_bot = None
whatsapp_ops = None
stop_event = None

def getNotified() -> None:
    """Monitor contact for status updates and send notifications"""
    global whatsapp_ops, wa_bot
    start = float("{:.2f}".format(perf_counter()))
    while True:
        try:
            whatsapp_ops.wait_for_status_and_click()
            time_diff = float("{:.2f}".format(perf_counter())) - start
            
            if time_diff <= 0.2:
                tprint(f"\n{status_uploader_name} has a status.\n{gmtTime(timezone)}")
                wa_bot.send_message(NUMBER, f"{status_uploader_name} has a status.\n{gmtTime(timezone)}", 
                    reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("GGs 🤞")]))
            else:
                start = reminderFn(time_diff, start, reminderTime)  # Reset time
        except (TimeoutException, NoSuchElementException):
            continue

def autoViewStatus(statusTypeMsg: str = "", status_uploader_name: str = status_uploader_name) -> Optional[str]:
    """Main function to automatically view and process WhatsApp statuses"""
    global bot, wa_bot, whatsapp_ops, stop_event
    
    whatsapp_ops.open_whatsapp()
    whatsapp_ops.search_contact(status_uploader_name)
    
    total_status: int = 1
    while True:
        # Wait for status and click profile picture
        while True:
            try:
                whatsapp_ops.wait_for_status_and_click()
                break
            except (TimeoutException, NoSuchElementException): 
                continue
        
        # Get status information
        status_info = whatsapp_ops.get_status_info()
        total_status = status_info['total_status']
        unviewed_status = status_info['unviewed_status']
        viewed_status = status_info['viewed_status']
        
        block_line: str = "-"*38
        loop_range: list = range(1, unviewed_status+1)
        is_more_than_one_status: bool = unviewed_status > 1
        statusTypeMsg += f"{status_uploader_name}\nUnviewed Status update" + ("s" if is_more_than_one_status else "") + f" {unviewed_status} out of {total_status}.\n"
        
        # Initialize status handler factory
        status_factory = StatusHandlerFactory(bot, wa_bot, status_uploader_name)
        statusType_xpaths = whatsapp_ops.get_status_type_xpaths()
        
        for status_idx in loop_range:
            if status_idx == 1: 
                tprint(statusTypeMsg[:-1])
            
            # Detect status type using ThreadPoolExecutor
            stop_event.clear()
            executor = ThreadPoolExecutor(max_workers=5)
            tasks = [executor.submit(whatsapp_ops.check_status_type, xpath, stop_event) for xpath in statusType_xpaths]

            check_status = None
            for future in as_completed(tasks):
                check_status = future.result()
                if check_status is not None:
                    break

            executor.shutdown(wait=False)

            # Use Strategy Pattern to handle the detected status type
            if check_status is not None:
                handler = status_factory.get_handler(check_status)
                if handler is not None:
                    if isinstance(handler, VideoStatusHandler):
                        msg = handler.handle(status_idx, total_status=total_status, viewed_status=viewed_status)
                    else:
                        msg = handler.handle(status_idx)
                    statusTypeMsg += msg
                else:
                    tprint(f'Unknown status type detected: {check_status}')
            else:
                tprint(f'Failed to detect status type for status {status_idx}')
            
            # Handle status navigation
            if status_idx != loop_range[-1]:
                viewed_status += 1
                check_status = None
                whatsapp_ops.navigate_to_next_status(viewed_status)
            else: # Status view completed, Exit status
                whatsapp_ops.exit_status_view(status_uploader_name)
                tprint(block_line)
    
        # Send to Self
        wa_bot.send_message(
            NUMBER, 
            f"{statusTypeMsg}\n{status_uploader_name} at {gmtTime(timezone)}.",
            reply_markup=Inline_list(
                "Show list",
                list_items=[
                    List_item("Nice one 👌"), 
                    List_item("Thanks ✨"), 
                    List_item("Great Job")
                ]
            )
        )
        
        statusTypeMsg: str = ""



if __name__ == "__main__":

    # answer: str = input('===> ').strip().upper()
    answer: str = "N"

    input_count: int = 1
    while True:
        if answer not in {"YES", "NO", "Y", "N"}:
            print(text2art('\nYou had one job to do! "Y" or "N"', "fancy56")); print('🥱')
            tprint('Do you want to get notified about status or view them automatically?')
            answer: str = input(text2art('Enter "Y" to get notified or "N" to view them automatically: ')).upper()
        else:
            if answer in ("N", "NO"): break
            while True:
                with contextlib.suppress(ValueError):
                    if input_count == 1:
                        reminderTime: int = int(input(text2art('\nHow often do you want to be notified?\n1. Enter "1" for 30 Mins\n2. Enter "2" for 1 Hour\n3. Enter "3" for 3 Hours\n4. Enter "4" for 6 Hours\nI want: ')))
                    else: 
                        print(text2art('\nYou have to choose between "1", "2", "3" or "4"', "fancy56"))#; print('', end="")
                        reminderTime: int = int(input('🥱 ===> '))
                    if reminderTime in {1, 2, 3, 4}: break
                input_count += 1
            break
    


    def initialize_app():
        """Initialize the application components"""
        global bot, wa_bot, whatsapp_ops, stop_event
        
        bot_manager = BotManager(driverpath)
        bot = bot_manager.start_chrome()
        bot.set_window_size(700, 730)
        bot.set_window_position(676, 0)
        wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)
        whatsapp_ops = WhatsAppOperations(bot, timezone)
        pyautogui.FAILSAFE = False
        pyautogui.press('esc')
        stop_event = threading.Event()
        return bot_manager

    try:
        bot_manager = initialize_app()

        if answer in ["Y", "YES"]: 
            getNotified()
        elif answer in ["N", "NO"]: 
            autoViewStatus()
    except KeyboardInterrupt as e:
        print("Keyboard Interrupt")
    except (NoSuchWindowException, WebDriverException, ProtocolError) as e:
        print("Webdriver Chrome Browser Closed!")
    finally:
        print("Program ended!")
