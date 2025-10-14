"""
Utility functions and helper methods
"""

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime
from typing import Optional
from time import sleep
import requests
import pytz
import json

from vars import bars_xpath, status_exit_xpath, scrolled_viewed_person_xpath

# Global cache for timezone and current time
_timezone_cache: Optional[str] = None
_current_time_cache: Optional[str] = None
_cache_timestamp: Optional[float] = None
CACHE_DURATION = 86_400  # Cache for 24 hours


def wait_for(bot: WebDriver, seconds: int) -> WebDriverWait:
    """Create WebDriverWait instance with specified timeout"""
    return WebDriverWait(bot, seconds)


def get_timezone_from_ip() -> str:
    """Get timezone based on IP geolocation"""
    try:
        # Using ipapi.co for timezone detection (free service)
        response = requests.get("https://ipapi.co/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            timezone = data.get('timezone')
            if timezone:
                return timezone
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        pass
    
    # Fallback to UTC if IP detection fails
    return "UTC"


def get_cached_time(tz: Optional[str] = None) -> str:
    """Get current time with caching to avoid repeated function calls"""
    from time import time
    
    global _timezone_cache, _current_time_cache, _cache_timestamp
    
    current_time = time()
    
    if tz is None:
        if _timezone_cache is None:
            _timezone_cache = get_timezone_from_ip()
        effective_timezone = _timezone_cache
    else:
        effective_timezone = tz
    
    # Check if cache is valid
    if (_current_time_cache is not None and 
        _cache_timestamp is not None and 
        current_time - _cache_timestamp < CACHE_DURATION):
        return _current_time_cache
    
    # Update cache
    _current_time_cache = datetime.now(pytz.timezone(effective_timezone)).strftime("%I:%M:%S %p")
    _cache_timestamp = current_time
    
    return _current_time_cache


def gmt_time(tz: Optional[str] = None) -> str:
    """Get current time in specified timezone formatted as HH:MM:SS AM/PM
    
    Args:
        tz: Timezone string (e.g., 'America/New_York'). If None, auto-detects from IP.
    
    Returns:
        Formatted time string (HH:MM:SS AM/PM)
    """
    return get_cached_time(tz)


def _backnforward(bot: WebDriver, viewed_status: int):
    """Go backward and forward to get 'blob' in url"""
    bot.find_elements(By.XPATH, bars_xpath)[viewed_status-1].click()
    sleep(.2)
    bot.find_elements(By.XPATH, bars_xpath)[viewed_status].click()


def _forwardnback(bot: WebDriver, viewed_status: int):
    """Go forward and backward to get 'blob' in url"""
    bot.find_elements(By.XPATH, bars_xpath)[viewed_status+1].click()
    sleep(.2)
    bot.find_elements(By.XPATH, bars_xpath)[viewed_status].click()


def _close_status(bot: WebDriver):
    """Close status view"""
    bot.find_element(By.XPATH, status_exit_xpath).click()


def handle_status_not_loaded(bot: WebDriver, total_status: int, viewed_status: int):
    """Handle cases where status is not properly loaded"""
    unviewed_status: int = total_status - viewed_status

    if total_status == 1:  # Only one status
        _close_status(bot)
        sleep(3)
        _click_profile_picture(bot)
    else:  # Multiple statuses
        if unviewed_status == 1:  # Only one new status uploaded
            _backnforward(bot, viewed_status)
        else:
            _forwardnback(bot, viewed_status)


def _click_profile_picture(bot: WebDriver):
    """Click profile picture to view status"""
    from vars import profile_picture_img_xpath, default_profile_picture_xpath
    
    try:
        bot.find_element(By.XPATH, profile_picture_img_xpath).click()
    except NoSuchElementException:
        bot.find_element(By.XPATH, default_profile_picture_xpath).click()


def scroll(bot: WebDriver, contact_name: str) -> None:
    """Scroll to find contact in status list"""
    from vars import status_list_page_xpath
    
    bot.find_element(By.XPATH, status_list_page_xpath).click()  # Enter Status Screen
    status_container_xpath: str = '//*[@class="g0rxnol2 ggj6brxn m0h2a7mj lb5m6g5c lzi2pvmc ag5g9lrv jhwejjuw ny7g4cd4"]'

    vertical_ordinate: int = 0
    while True:
        try:
            vertical_ordinate += 2500
            status_container = bot.find_element(By.XPATH, status_container_xpath)
            viewed_circle_xpath: str = f'//span[@title="{contact_name}"]//ancestor::div[@class="lhggkp7q ln8gz9je rx9719la"]\
                            //*[local-name()="circle" and @class="j9ny8kmf"]'  # UNVIEWED
            bot.execute_script(
                "arguments[0].scrollTop = arguments[1]", status_container, vertical_ordinate)
            statusPoster = bot.find_element(By.XPATH, viewed_circle_xpath)
            bot.execute_script('arguments[0].scrollIntoView();', statusPoster)
            break
        except NoSuchElementException:
            try:
                viewed_circle_xpath: str = f'//span[@title="{contact_name}"]//ancestor::div[@class="lhggkp7q ln8gz9je rx9719la"]\
                                //*[local-name()="circle" and @class="i2tfkqu4"]'  # VIEWED
                statusPoster = bot.find_element(By.XPATH, viewed_circle_xpath)
                bot.execute_script('arguments[0].scrollIntoView();', statusPoster)
                break
            except NoSuchElementException:
                continue


def reminderFn(ttime_diff: float, sstart: float, reminder_time: int) -> float:
    """Calculate reminder time based on configured interval"""
    if (
       reminder_time == 1 and ttime_diff >= 1_800  # Every 30 Mins
       or reminder_time == 2 and ttime_diff >= 3_600  # Every 1 Hour
       or reminder_time == 3 and ttime_diff >= 10_800  # Every 3 Hours
       or reminder_time == 4 and ttime_diff >= 21_600  # Every 6 Hours
    ):
        from time import perf_counter
        return float("{:.2f}".format(perf_counter()))
    else:
        return sstart
