import pytz
import contextlib
from time import sleep
from random import randint
from datetime import datetime
from selenium import webdriver
from whatsappcloud import Whatsapp
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
options.add_argument('--disable-dev-shm-usage')
options.add_argument(r'--profile-directory=BoT Profile')
options.add_argument(r'user-data-dir=C:\BoT Chrome Profile')
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", 'enable-logging'])
options.add_argument('--disable-blink-features=AutomationControlled')
bot = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(bot, 60)
action = ActionChains(bot)
bot.set_window_position(676, 0)

wa = Whatsapp("Temp STR in WA Object", preview_url=False)
timeZones: list = pytz.all_timezones  # All Time zone

bot.get("https://web.whatsapp.com")
try:
    # Giving it time to load up "Whatsapp" Text and wait until it disabled.
    sleep(2)
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, '//div[@class="_1dEQH _26aja"]'))) # WhatsApp Text
    print("\nLogging in ...💿")
    wait.until(EC.invisibility_of_element(
        (By.XPATH, '//div[@class="_2dfCc"]')))
    print("Logged in successfully.✌")
except TimeoutException:
    print("Took too long to login.")
    wa.text("Took too long to login.")
    bot.quit()

timezone: str = "Africa/Lagos"
statusUploaderName: str = "ContactName" # As it is saved on your phone(Case Sensitive)
barsXpath: str = '//div[@class="g0rxnol2 qq0sjtgm jxacihee l7jjieqr egv1zj2i ppled2lx gj5xqxfh om6y7gxh"]'
ppsXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]'
ppXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]//parent::div'

def gmtTime(tz) -> str:
    """
    Information
    -----------
    For some reason, the returned value for some African Timezone from
    the datetime module are 6 hours late which made me revalidate it to 
    the correct time.
    """
    temp_gmtTime: list = datetime.now(
    pytz.timezone(tz)).strftime("%H : %M : %S").split(":")
    hrs: int = int(temp_gmtTime[0])
    if hrs in range(17):
        return f"{hrs + 6} : {temp_gmtTime[1]} : {temp_gmtTime[2]}"
    elif hrs in range(18, 24):
        if hrs == 18:
            return f"00 : {temp_gmtTime[1]} : {temp_gmtTime[2]}"
        elif hrs == 19:
            return f"01 : {temp_gmtTime[1]} : {temp_gmtTime[2]}"
        elif hrs == 20:
            return f"02 : {temp_gmtTime[1]} : {temp_gmtTime[2]}"
        elif hrs == 21:
            return f"03 : {temp_gmtTime[1]} : {temp_gmtTime[2]}"
        elif hrs == 22:
            return f"04 : {temp_gmtTime[1]} : {temp_gmtTime[2]}"
        elif hrs == 23:
            return f"05: {temp_gmtTime[1]} : {temp_gmtTime[2]}"

print(gmtTime(timezone))

def checkstatusTypeMsg() -> dict:
    try: # Image Status
        bot.find_element(By.XPATH, '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//img')
        return {"imgStatusValue": True}
    except NoSuchElementException:
        try: # Video Status
            bot.find_element(By.XPATH, '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//video')
            return {"videoStatusValue": True}
        except NoSuchElementException:
            try: # Text Status
                bot.find_element(By.XPATH, '//div[@data-testid="status-v3-text"]')
                return {"txtStatusValue": True}
            except NoSuchElementException:
                try:
                    try:  # Audio Status
                        bot.find_element(By.XPATH, '//div[@class="g0rxnol2 ggj6brxn"]')
                        return {"audioStatusValue": True}
                    except NoSuchElementException: # OLD WHATSAPP MSG
                            bot.find_element(By.XPATH, '//div[@class="lhggkp7q qq0sjtgm tkdu00h0 ln8gz9je ppled2lx"]')
                            return {"old_messageValue": True}
                except NoSuchElementException:
                    print("Neither can Image/Video/Text/'Old whatsapp' be found.")


def runCode() -> None:

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
            
            unviewed_status: int = len(bot.find_elements(By.XPATH, '//div[contains(@class, "mjomr7am")]')) + 1
            total_status: int = len(bot.find_elements(By.XPATH, barsXpath))
            viewed_status: int = total_status - unviewed_status
            loop_range: list = range(1, unviewed_status+1)
            block_line: str = "-"*38    
            statusTypeMsg += f"{statusUploaderName}\
                \nUnviewed Statues is/are {unviewed_status} out of {total_status}.\n"

            for status_idx in loop_range:
                if status_idx == 1: print(statusTypeMsg[:-1])

                sleep(1)
                    
                check_Status: dict = checkstatusTypeMsg()

                try:
                    if check_Status["imgStatusValue"]:
                        print(f"{status_idx}. Status is an Image.")
                        statusTypeMsg += f"{status_idx}. Status is an Image.\n"
                except KeyError:
                    try:
                        if check_Status["videoStatusValue"]:
                            # Wait for loading icon to be disabled
                            wait.until(EC.invisibility_of_element_located(
                                (By.XPATH, '//div[@class="_1xAJD EdAF7 loading"]')))
                            sleep(7)

                            # Click the pause button
                            bot.find_element(
                                By.XPATH, '//span[@data-icon="status-media-controls-pause"]').click()

                            print(f"{status_idx}. Status is a Video.")
                            statusTypeMsg += f"{status_idx}. Status is a Video.\n"
                    except KeyError: 
                        try:
                            if check_Status["txtStatusValue"]:
                                print(f"{status_idx}. Status is a Text.")
                                statusTypeMsg += f"{status_idx}. Status is a Text.\n"
                        except KeyError:
                            try:
                                if check_Status["audioStatusValue"]:
                                    print(f"{status_idx}. Status is an Audio.")
                                    statusTypeMsg += f"{status_idx}. Status is an Audio.\n"
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
            wa.text(f"{statusTypeMsg}\n{statusUploaderName} at {gmtTime(timezone)}.")
        
        
if __name__ == "__main__":
    try:
        runCode()
    except Exception as e:
        print(f"Main Exception\n{e}")
        wa.text("Window Closed 🤦‍♀️")
