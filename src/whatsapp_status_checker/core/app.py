"""
WhatsApp Status Checker Application
"""

from ..utils import get_time, calculate_next_reminder_time, initialize_timezone
from ..config import NUMBER, CALLMEBOT_APIKEY, STATUS_UPLOADER_NAME, TIMEZONE
from .status_handlers import status_handler, VideoStatusHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
from .whatsapp_operations import WhatsAppOperations
from .webdriver_manager import BotManager
from urllib3.exceptions import ProtocolError
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    # NoSuchWindowException,
    WebDriverException
)
from callmebot import send_message
from art import tprint, text2art
from time import perf_counter
from ..vars import driverpath
from typing import Optional
import contextlib
import pyautogui
import threading


class WhatsAppStatusChecker:
    """Main application controller for WhatsApp Status Checker"""
    
    def __init__(self, 
        phone_number: Optional[str] = None,
        api_key: Optional[str] = None,
        status_uploader_name: Optional[str] = None,
        timezone: Optional[str] = None
    ):
        self.phone_number = phone_number or NUMBER
        self.api_key = api_key or CALLMEBOT_APIKEY
        self.status_uploader_name = status_uploader_name or STATUS_UPLOADER_NAME
        self.timezone = timezone or TIMEZONE
        
        self.bot = None
        self.whatsapp_ops = None
        self.stop_event = None
        self.bot_manager = None
    
    def initialize(self):
        """Initialize all application components"""
        from ..utils import ensure_chromedriver
        from art import set_default
        
        
        ensure_chromedriver()
        set_default("fancy99")
        
        self.detected_timezone = initialize_timezone(self.timezone)
        self.bot = BotManager().start_chrome(driverpath)
        self.whatsapp_ops = WhatsAppOperations(self.bot)
        self.stop_event = threading.Event()
        self.bot.set_window_position(676, 0)
        self.bot.set_window_size(700, 730)
        pyautogui.FAILSAFE = False
        pyautogui.press('esc')
    
    def get_user_choice(self) -> tuple[str, Optional[int]]:
        """Get user choice for notification vs auto-view mode"""
        tprint("Whatsapp Status Checker", 'rectangles')
        tprint('\nDo you want to get notified about status or view them automatically?\n\
Enter "Y" to get notified or "N" to view them automatically: ')
        # answer = input('===> ').strip().upper()
        answer = "N"
        
        input_count = 1
        reminder_time = None
        
        while True:
            if answer not in {"YES", "NO", "Y", "N"}:
                print(text2art('\nYou had one job to do! "Y" or "N"', "fancy56"))
                print('🥱')
                tprint('Do you want to get notified about status or view them automatically?')
                answer = input(text2art('Enter "Y" to get notified or "N" to view them automatically: ')).upper()
            else:
                if answer in ("N", "NO"):
                    break
                    
                # Get reminder time for notification mode
                while True:
                    with contextlib.suppress(ValueError):
                        if input_count == 1:
                            reminder_time = int(input(text2art('\nHow often do you want to be notified?\n1. Enter "1" for 30 Mins\n2. Enter "2" for 1 Hour\n3. Enter "3" for 3 Hours\n4. Enter "4" for 6 Hours\nI want: ')))
                        else: 
                            print(text2art('\nYou have to choose between "1", "2", "3" or "4"', "fancy56"))
                            reminder_time = int(input('🥱 ===> '))
                        if reminder_time in {1, 2, 3, 4}:
                            break
                    input_count += 1
                break
        
        return answer, reminder_time
    
    def monitor_notifications(self, reminder_time: int):
        """Monitor contact for status updates and send notifications"""
        start = float("{:.2f}".format(perf_counter()))
        while True:
            try:
                self.whatsapp_ops.wait_for_status_and_click()
                time_diff = float("{:.2f}".format(perf_counter())) - start
                timezone = get_time()
                
                if time_diff <= 0.2:
                    tprint(f"\n{self.status_uploader_name} has a status.\n{timezone}")
                    message = f"🔔 *{self.status_uploader_name}* has a new status!\n📅 {timezone}"
                    message = self.format_message(message)
                    send_message(message, self.phone_number, self.api_key)
                else:
                    start = calculate_next_reminder_time(time_diff, start, reminder_time)
            except (TimeoutException, NoSuchElementException):
                continue
    
    def auto_view_status(self, message: str = "") -> Optional[str]:
        """Main function to automatically view and process WhatsApp statuses"""
        self.whatsapp_ops.open_whatsapp()
        self.whatsapp_ops.search_contact(self.status_uploader_name)
        
        while True:
            # Wait for status and click profile picture
            while True:
                try:
                    self.whatsapp_ops.wait_for_status_and_click()
                    break
                except (TimeoutException, NoSuchElementException): 
                    continue
            
            # Get status information
            status_info = self.whatsapp_ops.get_status_info()
            total_status = status_info['total_status']
            unviewed_status = status_info['unviewed_status']
            viewed_status = status_info['viewed_status']
            
            block_line = "-" * 38
            loop_range = range(1, unviewed_status + 1)
            is_more_than_one_status = unviewed_status > 1

            message += f'{self.status_uploader_name}\nUnviewed Status update' + \
                ("s are " if is_more_than_one_status else " is ") + \
                f'{unviewed_status} out of {total_status}.\n'
            
            status_type_xpaths = self.whatsapp_ops.get_status_type_xpaths()
            
            for status_idx in loop_range:
                if status_idx == 1: 
                    tprint(message[:-1])
                
                self.stop_event.clear()
                executor = ThreadPoolExecutor(max_workers=5)
                tasks = [executor.submit(self.whatsapp_ops.check_status_type, xpath, self.stop_event) for xpath in status_type_xpaths]

                check_status = None
                for future in as_completed(tasks):
                    check_status = future.result()
                    if check_status is not None:
                        break

                executor.shutdown(wait=False)

                # Use simple factory pattern to handle the detected status type
                if check_status is not None:
                    handler = status_handler(
                        check_status, self.bot, 
                        self.phone_number, self.api_key, 
                        self.status_uploader_name
                    )
                    if handler is not None:
                        if isinstance(handler, VideoStatusHandler):
                            msg = handler.handle(
                                status_idx, 
                                total_status=total_status, 
                                viewed_status=viewed_status
                            )
                        else:
                            msg = handler.handle(status_idx)
                        message += msg
                    else:
                        tprint(f'Unknown status type detected: {check_status}')
                else:
                    tprint(f'Failed to detect status type for status {status_idx}')
                
                # Handle status navigation
                if status_idx != loop_range[-1]:
                    viewed_status += 1
                    check_status = None
                    self.whatsapp_ops.navigate_to_next_status(viewed_status)
                else:  # Status view completed, Exit status
                    self.whatsapp_ops.exit_status_view(self.status_uploader_name)
                    tprint(block_line)
        
            # Send to Self
            message = self.format_message(message)
            send_message(message, self.phone_number, self.api_key)
                        
            message = "" # Reset message
    
    def format_message(self, message: str) -> str:
        """Format message to bold the contact name"""
        return message.replace(self.status_uploader_name, f"*{self.status_uploader_name}*")

    def run(self):
        """Main application run method"""
        try:
            self.initialize()
            answer, reminder_time = self.get_user_choice()
            
            if answer in ["Y", "YES"]: 
                self.monitor_notifications(reminder_time)
            elif answer in ["N", "NO"]: 
                self.auto_view_status()
                
        except KeyboardInterrupt:
            print("Keyboard Interrupt!")
        except NoSuchElementException as e:
            print(f"Element not found!: {e}")
        except WebDriverException as e:
            print(f"Webdriver Chrome Browser Closed!: {e}")
        except ProtocolError as e:
            print(f"Protocol Error!: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print("Program ended!")


