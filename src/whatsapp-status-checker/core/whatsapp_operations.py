"""
WhatsApp-specific operations and status detection logic
"""

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from typing import Optional, Dict, List
from art import tprint, text2art
from time import sleep
import contextlib

from vars import (
    login_instructions_xpath, profile_picture_status_xpath, profile_picture_img_xpath,
    default_profile_picture_xpath, search_field_xpath, bars_xpath, unviewed_status_xpath,
    status_exit_xpath, img_status_xpath, video_status_xpath, text_status_xpath,
    audio_status_xpath, oldMessage_status_xpath, status_uploader_name
)
from utils.helpers import wait_for


class WhatsAppOperations:
    """Handles WhatsApp web operations and status detection"""
    
    def __init__(self, bot: WebDriver, timezone: str):
        self.bot = bot
        self.timezone = timezone
    
    def open_whatsapp(self) -> None:
        """Open WhatsApp Web and handle login process"""
        wait_until_whatsapp_login_instructions_disappear = lambda: wait_for(self.bot, 3).until(
            EC.visibility_of_element_located((By.XPATH, login_instructions_xpath)))

        self.bot.get("https://web.whatsapp.com/")

        try:
            print(text2art("\nLogging in..."), "💿")
            login_count: int = 1
            while True:
                try:
                    self.bot.find_element(By.XPATH, '//div[@id="pane-side"]')
                    break
                except NoSuchElementException:  # Log in page (Scan QRCode)
                    with contextlib.suppress(TimeoutException):
                        wait_until_whatsapp_login_instructions_disappear()

                        if login_count == 1:
                            print(text2art("Please scan the QRCODE to log in"), "🔑")
                            login_count += 1

                        wait_until_whatsapp_login_instructions_disappear()

                        wait_for(self.bot, 3).until(EC.visibility_of_element_located(
                            (By.XPATH, '//div[@class="_1dEQH _26aja"]'))) # WhatsApp: Text
                        wait_for(self.bot, 3).until(EC.invisibility_of_element(
                            (By.XPATH, '//div[@class="x1c3i2sq x14ug900 xk82a7y x1sy10c2"]')))  # Loading your chats
                        wait_for(self.bot, 3).until(EC.invisibility_of_element(
                            (By.XPATH, '//div[@class="_3HbCE"]'))) # Loading [%]
                        break
            print(text2art("Logged in successfully."), "✌")
            from utils.helpers import gmtTime
            tprint(f'Logged in at {gmtTime(self.timezone)}\n')
        except TimeoutException:
            from python_whatsapp_bot import Inline_list, List_item
            from vars import NUMBER
            # This would need wa_bot instance - consider refactoring
            print('Took too long to login.')
            self.bot.quit()
    
    def search_contact(self, contact_name: str) -> None:
        """Search for a specific contact"""
        search_field: WebElement = self.bot.find_element(By.XPATH, search_field_xpath)
        search_field.send_keys(contact_name)
    
    def wait_for_status_and_click(self) -> None:
        """Wait for status circle to appear and click profile picture"""
        wait_for(self.bot, 60).until(EC.visibility_of_element_located(
            (By.XPATH, profile_picture_status_xpath)))
        self.bot.find_element(By.XPATH, profile_picture_status_xpath)
        sleep(5)
        self._click_profile_picture()
    
    def _click_profile_picture(self) -> None:
        """Click profile picture to view status"""
        try:
            self.bot.find_element(By.XPATH, profile_picture_img_xpath).click()
        except NoSuchElementException: 
            self.bot.find_element(By.XPATH, default_profile_picture_xpath).click()
    
    def get_status_info(self) -> Dict[str, int]:
        """Get information about statuses (total, unviewed, viewed)"""
        bars: List[WebElement] = self.bot.find_elements(By.XPATH, bars_xpath)
        unviewed_status: int = len(self.bot.find_elements(By.XPATH, unviewed_status_xpath)) + 1
        total_status: int = len(bars)
        viewed_status: int = total_status - unviewed_status
        
        return {
            'total_status': total_status,
            'unviewed_status': unviewed_status,
            'viewed_status': viewed_status
        }
    
    def navigate_to_next_status(self, viewed_status: int) -> None:
        """Navigate to the next status"""
        self.bot.find_elements(By.XPATH, bars_xpath)[viewed_status].click()
    
    def exit_status_view(self, contact_name: str) -> None:
        """Exit from status viewing mode"""
        try:
            self.bot.find_element(By.XPATH, status_exit_xpath).click()
        except NoSuchElementException: # Status already exited
            sleep(3)
            with contextlib.suppress(NoSuchElementException): 
                # Check if it has truely exited by confirming if the page is on 'contact_name' search page
                self.bot.find_element(By.XPATH, f'//span[@title="{contact_name}"]//span')
                self.bot.find_element(By.XPATH, '//div[@title="Status"]').send_keys(Keys.ESCAPE)
    
    def check_status_type(self, xpath: str, stop_event) -> Optional[Dict[str, bool]]:
        """Check what type of status is currently displayed"""
        while not stop_event.is_set():
            with contextlib.suppress(NoSuchElementException, TimeoutException):
                wait_for(self.bot, .1).until(EC.presence_of_element_located((By.XPATH, xpath)))

                if '//video' in xpath:
                    stop_event.set()
                    return {"videoStatusValue": True}
                elif 'x5yr21d"]//img' in xpath:
                    element: WebElement = self.bot.find_element(By.XPATH, xpath)
                    if element.get_attribute('alt') == '':
                        stop_event.set()
                        return {"imgStatusValue": True}
                elif 'background-color: rgb' in xpath:
                    stop_event.set()
                    return {"txtStatusValue": True}
                elif 'FixMeAudio' in xpath:
                    stop_event.set()
                    return {"audioStatusValue": True}
                elif 'x1vvkbs x47corl")]' in xpath:
                    stop_event.set()
                    return {"old_messageValue": True}  # Very rare
        return None
    
    def get_status_type_xpaths(self) -> List[str]:
        """Get list of XPath expressions for different status types"""
        return [
            img_status_xpath, 
            video_status_xpath, 
            text_status_xpath, 
            audio_status_xpath, 
            oldMessage_status_xpath
        ]
