import pytz
import datetime
import contextlib
from random import randint
from selenium import webdriver
from whatsappcloud import Whatsapp
from time import sleep, perf_counter
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

driverpath = "C:\\Users\\Administrator\\Documents\\WhatsApp Status Checker\\assest\\driver\\chromedriver.exe"

service = Service(executable_path=driverpath)
options = Options()
options.add_argument("--disable-gpu")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(r'user-data-dir=C:\BoT Chrome Profile')
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", 'enable-logging'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--profile-directory=BoT Profile')
bot = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(bot, 30)
action = ActionChains(bot)
bot.maximize_window()

wa = Whatsapp("Temp STR in WA Obj", preview_url=False)
timeZones: list = pytz.all_timezones  # All Time zone

bot.get("https://web.whatsapp.com")
try:
    # Giving it time to load up "Whatsapp" Text and wait until it disabled.
    sleep(2)
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, '//div[@class="_26aja _1dEQH"]')))
    print("\nLogging in ...💿")
    wait.until(EC.invisibility_of_element(
        (By.XPATH, '//div[@class="_2dfCc"]')))
    print("Logged in successfully.✌")
except TimeoutException:
    print("Took too long to login.")
    wa.text("Took too long to login.")
    bot.quit()

statusUploaderName: str = "ConatctName" # As it is saved on your phone(Case Sensitive)
barsXpath: str = '//div[@class="sZBni"]'
ppsXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_2EU3r"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]'
ppXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_2EU3r"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]//parent::div'


def gmtTime():
    return datetime.datetime.now(
    pytz.timezone("Africa/Lagos")).strftime("%H : %M : %S")


def checkstatusTypeMsg():
    
    try: # Image Status
        bot.find_element(By.XPATH, '//div[@class="_26Q83"]//img')
        return {"imgStatusValue": True}
    except NoSuchElementException:
        try: # Video Status
            bot.find_element(By.XPATH, '//div[@class="_26Q83"]//video')
            return {"videoStatusValue": True}
        except NoSuchElementException:
            try:
                try: # Text Status
                    bot.find_element(By.XPATH, '//div[contains(@class, "_3KpnX")]')
                    return {"txtStatusValue": True}
                except NoSuchElementException:# OLD WHATSAPP MSG
                    bot.find_element(By.XPATH, '//div[@class="_3Rxrh"]')
                    return {"old_messageValue": True}
            except NoSuchElementException as e:
                print(f"Neither can Image/Video/Text/'Old whatsapp' be found.\n{e}")


def runCode():

    search_field = bot.find_element(By.XPATH, '//div[@data-testid="chat-list-search"]')
    search_field.clear()
    search_field.send_keys(statusUploaderName)
    sleep(5)

    while True:
        statusTypeMsg: str = ""
        with contextlib.suppress(Exception):
            # Status Circle around profile picture
            bot.find_element(By.XPATH, ppsXpath)

            # Click Profile Picture to view Status
            bot.find_element(By.XPATH, ppXpath).click()
            
            unviewed_status: int = len(bot.find_elements(By.XPATH, '//div[@class="_3f8oh _1A2HZ"]')) + 1
            total_status: int = len(bot.find_elements(By.XPATH, '//div[@class="sZBni"]'))
            viewed_status: int = total_status - unviewed_status
            loop_range: list = range(1, unviewed_status+1)
            block_line: str = "-"*38    
            statusTypeMsg += f"{statusUploaderName}\
                \nUnviewed Statues is/are {unviewed_status} out of {total_status}.\n"

            for status_idx in loop_range:
                if status_idx == 1: print(statusTypeMsg[:-1])

                sleep(1)
                    
                # Wait for loading icon to be disabled
                wait.until(EC.invisibility_of_element_located(
                    (By.XPATH, '//div[@class="_1xAJD EdAF7 loading"]')))
                
                # Click the pause button
                bot.find_element(
                    By.XPATH, '//span[@data-icon="status-media-controls-pause"]').click()

                check_Status: dict = checkstatusTypeMsg()

                try:
                    if check_Status["imgStatusValue"]:
                        print(f"{status_idx}. Status is an Image.")
                        statusTypeMsg += f"{status_idx}. Status is an Image.\n"
                except KeyError:
                    try:
                        if check_Status["videoStatusValue"]:
                            print(f"{status_idx}. Status is a Video.")
                            statusTypeMsg += f"{status_idx}. Status is a Video.\n"
                            sleep(1)
                    except KeyError: 
                        try:
                            if check_Status["txtStatusValue"]:
                                print(f"{status_idx}. Status is a Text.")
                                statusTypeMsg += f"{status_idx}. Status is a Text.\n"
                        except KeyError:
                            try: 
                                if check_Status["old_messageValue"]:
                                    print(f"{status_idx}. Status is an Old Whatsapp Version.")
                                    statusTypeMsg += f"{status_idx}. Status is an Old Whatsapp Version.\n"
                            except KeyError as e: 
                                print(f'Failed! -> {e}')
                finally:
                    if status_idx != loop_range[-1]:
                        viewed_status += 1

                        # Click Next Status
                        bot.find_elements(By.XPATH, barsXpath)[ 
                            viewed_status].click()
                    else: # Exit status
                        print(block_line)
                        bot.find_element(By.XPATH, '//span[@data-icon="x-viewer"]').click()

            # Send to MySelf
            wa.text(f"{statusTypeMsg}\n{statusUploaderName} at {gmtTime()}.")
        
        
if __name__ == "__main__":
    try:
        runCode()
    except Exception as e:
        print(f"Main Exception\n{e}")
        wa.text("Window Closed 🤦‍♀️")
