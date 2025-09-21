"""
WhatsApp Status Checker Application Controller
Handles the main application logic and flow
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    NoSuchWindowException, 
    WebDriverException
)
from time import perf_counter
from typing import Optional
import contextlib
import pyautogui
import threading

from art import tprint, text2art
from urllib3.exceptions import ProtocolError

from .whatsapp_notifier import CallMeBotClient
from . import create_status_handler, VideoStatusHandler, BotManager, WhatsAppOperations
from utils import gmtTime, reminderFn
from vars import driverpath


class WhatsAppStatusApp:
    """Main application controller for WhatsApp Status Checker"""
    
    def __init__(self, phone_number: str, api_key: str, status_uploader_name: str, timezone: str):
        self.phone_number = phone_number
        self.api_key = api_key
        self.status_uploader_name = status_uploader_name
        self.timezone = timezone
        
        # Application components
        self.bot = None
        self.wa_bot = None
        self.whatsapp_ops = None
        self.stop_event = None
        self.bot_manager = None
    
    def initialize(self):
        """Initialize all application components"""
        self.bot_manager = BotManager(driverpath)
        self.bot = self.bot_manager.start_chrome()
        self.bot.set_window_size(700, 730)
        self.bot.set_window_position(676, 0)
        self.wa_bot = CallMeBotClient(self.phone_number, self.api_key)
        self.whatsapp_ops = WhatsAppOperations(self.bot, self.timezone)
        pyautogui.FAILSAFE = False
        pyautogui.press('esc')
        self.stop_event = threading.Event()
    
    def get_user_choice(self) -> tuple[str, Optional[int]]:
        """Get user choice for notification vs auto-view mode"""
        tprint("WhatsApp Status Viewer", 'rectangles')
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
                
                if time_diff <= 0.2:
                    tprint(f"\n{self.status_uploader_name} has a status.\n{gmtTime(self.timezone)}")
                    self.wa_bot.send_simple_notification(self.status_uploader_name, gmtTime(self.timezone))
                else:
                    start = reminderFn(time_diff, start, reminder_time)
            except (TimeoutException, NoSuchElementException):
                continue
    
    def auto_view_status(self, status_type_msg: str = "") -> Optional[str]:
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
            status_type_msg += f"{self.status_uploader_name}\nUnviewed Status update" + ("s" if is_more_than_one_status else "") + f" {unviewed_status} out of {total_status}.\n"
            
            # Initialize status handler factory
            status_factory = StatusHandlerFactory(self.bot, self.wa_bot, self.status_uploader_name)
            status_type_xpaths = self.whatsapp_ops.get_status_type_xpaths()
            
            for status_idx in loop_range:
                if status_idx == 1: 
                    tprint(status_type_msg[:-1])
                
                # Detect status type using ThreadPoolExecutor
                self.stop_event.clear()
                executor = ThreadPoolExecutor(max_workers=5)
                tasks = [executor.submit(self.whatsapp_ops.check_status_type, xpath, self.stop_event) for xpath in status_type_xpaths]

                check_status = None
                for future in as_completed(tasks):
                    check_status = future.result()
                    if check_status is not None:
                        break

                executor.shutdown(wait=False)

                # Use Strategy Pattern to handle the detected status type
                if check_status is not None:
                    handler = create_status_handler(check_status, self.bot, self.wa_bot, self.status_uploader_name)
                    if handler is not None:
                        if isinstance(handler, VideoStatusHandler):
                            msg = handler.handle(status_idx, total_status=total_status, viewed_status=viewed_status)
                        else:
                            msg = handler.handle(status_idx)
                        status_type_msg += msg
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
            self.wa_bot.send_status_notification(
                self.status_uploader_name,
                status_type_msg,
                gmtTime(self.timezone)
            )
            
            status_type_msg = ""
    
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
        except NoSuchElementException:
            print("Element not found!")
        except WebDriverException:
            print("Webdriver Chrome Browser Closed!")
        except ProtocolError:
            print("Protocol Error!")
        except Exception as e:
            print("An error occurred:", e)
        finally:
            print("Program ended!")
