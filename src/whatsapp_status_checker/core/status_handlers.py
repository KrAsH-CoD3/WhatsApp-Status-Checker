"""
Status Handler classes implementing Strategy Pattern for different WhatsApp status types
"""

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from ..utils.helpers import wait_for, handle_status_not_loaded
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from abc import ABC, abstractmethod
from callmebot import send_message
from typing import Optional, Dict
from art import tprint
from ..vars import (
    loading_icon_in_status_xpath, pause_btn_xpath, playing_bar_xpath, 
    paused_bar_xpath, NUMBER, #_status_not_loaded
)
import contextlib
import sys


class StatusHandler(ABC):
    """Abstract base class for handling different status types"""
    
    def __init__(self, bot: WebDriver, phone_number: str, api_key: str, contact_name: str):
        self.bot = bot
        self.phone_number = phone_number
        self.api_key = api_key
        self.contact_name = contact_name
    
    @abstractmethod
    def handle(self, status_idx: int, **kwargs) -> str:
        """Handle the specific status type and return status message"""
        pass
    
    def click_pause(self):
        """Helper method to pause status"""
        try:
            wait_for(self.bot, .5).until(EC.invisibility_of_element_located(
                (By.XPATH, loading_icon_in_status_xpath)))
            self.bot.find_element(By.XPATH, pause_btn_xpath).click()
        except(NoSuchElementException, TimeoutException): 
            return  # ALREADY PAUSED


class ImageStatusHandler(StatusHandler):
    """Handler for image status types"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        self.click_pause()
        msg = f"{status_idx}. Status is an Image."
        tprint(msg)
        return msg + '\n'


class VideoStatusHandler(StatusHandler):
    """Handler for video status types with complex loading logic"""
    
    def __init__(self, bot: WebDriver, phone_number: str, api_key: str, contact_name: str, max_attempts: int = 3):
        super().__init__(bot, phone_number, api_key, contact_name)
        self.max_attempts = max_attempts
    
    def handle(self, status_idx: int, **kwargs) -> str:
        total_status = kwargs.get('total_status', 1)
        viewed_status = kwargs.get('viewed_status', 0)
        return self._process_video_status(status_idx, total_status, viewed_status)
    
    def _process_video_status(self, status_idx: int, total_status: int, viewed_status: int) -> str:
        """Process video status with loading detection and retry logic"""
        loading_icon = True
        attempts = 0
        
        while True:
            with contextlib.suppress(TimeoutException):
                wait_for(self.bot, .1).until(EC.invisibility_of_element_located(
                    (By.XPATH, loading_icon_in_status_xpath)))
                loading_icon = False
            
            video_progress = self._get_video_progress()
            if video_progress is None:
                continue
            
            # Handle video loading detection
            if not self._is_video_loaded(loading_icon, video_progress, total_status, viewed_status, attempts):
                attempts += 1
                if attempts >= self.max_attempts:
                    self._send_loading_failure_message()
                    sys.exit()
                continue
            
            try:
                self.click_pause()
            except NoSuchElementException:
                pass  # ALREADY PAUSED
            
            msg = f"{status_idx}. Status is a Video."
            tprint(msg)
            return msg + '\n'
    
    def _get_video_progress(self) -> Optional[float]:
        """Extract video progress from status bar style attribute"""
        try:
            playing_status = self.bot.find_element(By.XPATH, playing_bar_xpath)
            style_value = playing_status.get_attribute("style")
        except NoSuchElementException:
            try:
                paused_status = self.bot.find_element(By.XPATH, paused_bar_xpath)
                style_value = paused_status.get_attribute("style")
            except NoSuchElementException:
                return None
        
        try:
            return float(style_value.split("(")[1].split(")")[0][1:-1])
        except (IndexError, ValueError):
            return None
    
    def _is_video_loaded(self, loading_icon: bool, video_progress: float, 
                        total_status: int, viewed_status: int, attempts: int) -> bool:
        """Check if video is properly loaded"""
        try:
            wait_for(self.bot, .5).until(EC.invisibility_of_element_located(
                (By.XPATH, loading_icon_in_status_xpath)))
            return True  # Video is loaded
        except (TimeoutException, NoSuchElementException):
            if loading_icon and (0 <= video_progress <= 30):
                handle_status_not_loaded(self.bot, total_status, viewed_status)
                return False
            return True  # Assume loaded if we can't detect loading icon
    
    def _send_loading_failure_message(self):
        """Send failure message when video can't be loaded after max attempts"""
        error_message = f"Unable to load {self.contact_name}'s video status. Use a better internet i guess."
        message = f"⚠️ Error with *{self.contact_name}*'s status:\n{error_message}"
        send_message(message, self.phone_number, self.api_key)


class TextStatusHandler(StatusHandler):
    """Handler for text status types"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        self.click_pause()
        msg = f"{status_idx}. Status is a Text."
        tprint(msg)
        return msg + '\n'


class AudioStatusHandler(StatusHandler):
    """Handler for audio status types"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        msg = f"{status_idx}. Status is an Audio."
        tprint(msg)
        return msg + '\n'


class OldMessageStatusHandler(StatusHandler):
    """Handler for old WhatsApp version messages"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        msg = f"{status_idx}. Status is an Old Whatsapp Version."
        tprint(msg)
        return msg + '\n'


def status_handler(
    check_status: Dict[str, bool], 
    bot: WebDriver, 
    phone_number: str, 
    api_key: str, 
    contact_name: str
) -> Optional[StatusHandler]:
    """Create the appropriate status handler based on status type"""
    handler_map = {
        "imgStatusValue": ImageStatusHandler,
        "videoStatusValue": VideoStatusHandler,
        "txtStatusValue": TextStatusHandler,
        "audioStatusValue": AudioStatusHandler,
        "old_messageValue": OldMessageStatusHandler
    }
    
    for status_type, handler in handler_map.items():
        if check_status.get(status_type, False):
            return handler(bot, phone_number, api_key, contact_name)
    return None
