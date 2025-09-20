"""
Utility functions and helper methods
"""

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime
from time import sleep
import pytz

from vars import bars_xpath, status_exit_xpath, scrolled_viewed_person_xpath


def wait_for(bot: WebDriver, seconds: int) -> WebDriverWait:
    """Create WebDriverWait instance with specified timeout"""
    return WebDriverWait(bot, seconds)


def gmtTime(tz: str) -> str:
    """Get current time in specified timezone formatted as HH:MM:SS AM/PM"""
    return datetime.now(pytz.timezone(tz)).strftime("%I:%M:%S %p")


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
