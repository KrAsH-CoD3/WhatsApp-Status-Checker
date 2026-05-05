"""
Status Handler classes implementing Strategy Pattern for different WhatsApp status types
"""

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from ..utils.helpers import wait_for, handle_status_not_loaded
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from abc import ABC, abstractmethod
from typing import Optional, Dict
from art import tprint
from ..vars import (
    loading_icon_in_status_xpath, pause_btn_xpath, 
    playing_bar_xpath, paused_bar_xpath
)


class StatusHandler(ABC):
    """Abstract base class for handling different status types"""
    
    MAX_LOAD_ATTEMPTS = 3
    LOAD_CHECK_TIMEOUT = 0.5  # seconds to wait per loading icon check
    PAUSE_BTN_TIMEOUT = 2.0   # seconds to wait for pause button clickability
    
    def __init__(self, bot: WebDriver, phone_number: str, api_key: str, contact_name: str):
        self.bot = bot
        self.phone_number = phone_number
        self.api_key = api_key
        self.contact_name = contact_name
    
    @abstractmethod
    def handle(self, status_idx: int, **kwargs) -> str:
        """Handle the specific status type and return status message"""
        pass
    
    def _is_loading(self) -> bool:
        """Check if the loading icon is currently visible"""
        try:
            wait_for(self.bot, self.LOAD_CHECK_TIMEOUT).until(
                EC.invisibility_of_element_located(
                    (By.XPATH, loading_icon_in_status_xpath)))
            return False
        except (TimeoutException, NoSuchElementException):
            return True
    
    def wait_for_load(self, total_status: int, viewed_status: int, media_type: str = "media"):
        """Wait for the status to fully load.
        
        To prevent unnecessary back-and-forth spamming, we only force a reload 
        if the status has played past 30% but the loading icon is still visible.
        Otherwise, we wait patiently for normal buffering.
        """
        while self._is_loading():
            progress = self._get_status_progress()
            
            if progress is not None and progress > 30:
                # Bug state: it's playing (past 30%) but loading icon remains
                handle_status_not_loaded(self.bot, total_status, viewed_status)
    
    def _get_status_progress(self) -> Optional[float]:
        """Extract status progress from status bar style attribute"""
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
    
    def click_pause(self):
        """Pause the status playback. Safe to call even if already paused."""
        try:
            pause_btn = wait_for(self.bot, self.PAUSE_BTN_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, pause_btn_xpath)))
            pause_btn.click()
        except (NoSuchElementException, TimeoutException):
            return  # Already paused or no pause button (e.g. text status)


class ImageStatusHandler(StatusHandler):
    """Handler for image status types"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        total_status = kwargs.get('total_status', 1)
        viewed_status = kwargs.get('viewed_status', 0)
        
        self.wait_for_load(total_status, viewed_status, media_type="image")
        self.click_pause()
        
        msg = f"{status_idx}. Status is an Image."
        tprint(msg)
        return msg + '\n'


class VideoStatusHandler(StatusHandler):
    """Handler for video status types"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        total_status = kwargs.get('total_status', 1)
        viewed_status = kwargs.get('viewed_status', 0)
        
        self.wait_for_load(total_status, viewed_status, media_type="video")
        self.click_pause()
        
        msg = f"{status_idx}. Status is a Video."
        tprint(msg)
        return msg + '\n'


class TextStatusHandler(StatusHandler):
    """Handler for text status types"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        # Text statuses don't load media, but pause to prevent auto-advance
        self.click_pause()
        msg = f"{status_idx}. Status is a Text."
        tprint(msg)
        return msg + '\n'


class AudioStatusHandler(StatusHandler):
    """Handler for audio status types"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        total_status = kwargs.get('total_status', 1)
        viewed_status = kwargs.get('viewed_status', 0)
        
        self.wait_for_load(total_status, viewed_status, media_type="audio")
        self.click_pause()
        
        msg = f"{status_idx}. Status is an Audio."
        tprint(msg)
        return msg + '\n'


class OldMessageStatusHandler(StatusHandler):
    """Handler for old WhatsApp version messages"""
    
    def handle(self, status_idx: int, **kwargs) -> str:
        self.click_pause()
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
    
    # Get the first active status type from the check_status dict
    active_type = next((k for k, v in check_status.items() if v), None)
    
    if handler_cls := handler_map.get(active_type):
        return handler_cls(bot, phone_number, api_key, contact_name)
        
    return None
