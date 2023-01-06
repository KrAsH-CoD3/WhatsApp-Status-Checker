import datetime
from random import randint
import pytz
from whatsappcloud import Whatsapp
from selenium import webdriver
from time import sleep, perf_counter
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, \
    NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException, \
    StaleElementReferenceException, InvalidSessionIdException

driverpath = "C:\\Users\\Administrator\\Documents\\Boss\\assest\\driver\\chromedriver.exe"
# driverpath = "C:\\Users\\Administrator\\Documents\\Boss\\assest\\driver\\geckodriver.exe"
# driverpath = "C:\\Users\\LmAo\\Documents\\AAA Testing\\Boss\\assest\\driver\\chromedriver.exe" # 127.0.0.1

service = Service(executable_path=driverpath)
options = Options()
# options.headless = True
options.add_argument("--disable-gpu")
options.add_argument('--disable-blink-features=AutomationControlled') # Check what did is 
# options.add_argument("--disable-infobars")
options.add_argument(r'user-data-dir=C:\BoT Chrome Profile')
# options.add_argument('user-data-dir=C:\\Users\\LmAo\\AppData\\Local\\Google\\Chrome\\User Data\\Default') # 127.0.0.1
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", 'enable-logging'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--profile-directory=BoT Profile')
# options.add_experimental_option("debuggerAddress", "localhost:9222") # for using existing opened Chrome instance
bot = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(bot, 30)
action = ActionChains(bot)
bot.maximize_window()


wa = Whatsapp("Temp STR in WA Obj", preview_url=False)
timeZones = pytz.all_timezones  # All Time zone
# chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\BoT Chrome Profile" "--profile-directory=BoT Profile" https://bot.incolumitas.com/#browserData

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

start = int(perf_counter())
output_TimeStart = int(perf_counter())
imgStatusValue, videoStatusValue, txtStatusValue, old_messageValue = [False for _ in range(4)]

statusUploaderName:str = "OG Yungtee" # Ijk Kazmpire NaijaTwitterSavage Crypto Base
barsXpath:str = '//div[@class="sZBni"]'
ppsXpath:str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::div[@class="_2EU3r"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]'
ppXpath:str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::div[@class="_2EU3r"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]//parent::div'


def gmtTime(): 
    return datetime.datetime.now(
    pytz.timezone("Africa/Lagos")).strftime("%H : %M : %S")


def checkstatusTypeMsg():  # sourcery skip: do-not-use-bare-except, extract-duplicate-method, inline-variable
    global imgStatusValue, videoStatusValue, txtStatusValue, old_messageValue
    
    try: # Image Status
        bot.find_element(By.XPATH, '//div[@class="_26Q83"]//img')
        imgStatusValue = True
        return {"imgStatusValue": imgStatusValue}
    except Exception:
        try: # Video Status
            bot.find_element(By.XPATH, '//div[@class="_26Q83"]//video')
            videoStatusValue = True
            return {"videoStatusValue": videoStatusValue}
        except:
            try:
                try: # If it contain any of the Text Status Type
                    bot.find_element(By.XPATH, '//div[contains(@class, "_3KpnX")]')
                    txtStatusValue = True
                    return {"txtStatusValue": txtStatusValue}
                except:# Check if the status type is OLD WHATSAPP MSG
                    old_message = bot.find_element(
                        By.XPATH, '//div[@class="_3Rxrh"]')
                    old_messageValue = True
                    return {"old_messageValue": old_messageValue}
            except:
                print("Neither can Image/Video/Text and even 'Old whatsapp' could be found.")


def runCode():
    global counter, output_TimeStart, imgStatusValue, videoStatusValue, txtStatusValue, old_messageValue

    search_field = bot.find_element(By.XPATH, '//div[@data-testid="chat-list-search"]')
    search_field.clear()
    search_field.send_keys(statusUploaderName)
    sleep(5)
    
    while True:
        statusTypeMsg: str = ""
        try:
            # Status Circle around profile picture
            bot.find_element(By.XPATH, ppsXpath)

            # Click Profile Picture to view Status
            bot.find_element(By.XPATH, ppXpath).click()
            sleep(1)

            unviewed_status: int = len(bot.find_elements(By.XPATH, '//div[@class="_3f8oh _1A2HZ"]')) + 1
            total_status: int = len(bot.find_elements(By.XPATH, '//div[@class="sZBni"]'))
            viewed_status: int = total_status - unviewed_status
            loop_range: list = range(1, unviewed_status+1)
            statusTypeMsg += f"\n{statusUploaderName}\nUnviewed Statues is/are {unviewed_status} out of {total_status}.\n\n"

            for status_idx in loop_range:
                check_Status = checkstatusTypeMsg()
                try:
                    if imgStatusValue == check_Status["imgStatusValue"]:
                        if status_idx == 1: # First status
                            print(
                                f"Viewed {status_idx} out of {unviewed_status}.")
                        if status_idx != loop_range[-1]:  # Not the last
                            print(f"{status_idx}. Status is an Image.")
                            statusTypeMsg += f"{status_idx}. Status is an Image.\n"

                            # Click the pause button
                            bot.find_element(
                                By.XPATH, '//div[@class="lyrceosr bx7g2weo i94gqilv bmot90v7 lxozqee9"]').click()

                            # Click next Status
                            bot.find_elements(By.XPATH, barsXpath)[
                                viewed_status+1].click()
                        else:  # Last Status is an Image.
                            print(
                                f"{status_idx}. Status is an Image.")
                            statusTypeMsg += f"{status_idx}. Status is an Image.\n"
                            
                            # Click the pause button
                            bot.find_element(
                                By.XPATH, '//div[@class="lyrceosr bx7g2weo i94gqilv bmot90v7 lxozqee9"]').click()

                        # Return the value to False to not always excecute this if the first viewed status is an image
                        imgStatusValue = False
                except:
                    try:
                        if videoStatusValue == check_Status["videoStatusValue"]:
                            if status_idx == 1: # First status
                                print(f"Viewed {status_idx} out of {unviewed_status}.")
                            if status_idx != loop_range[-1]:  # Not the last Status
                                print(f"{status_idx}. Status is a Video.")
                                statusTypeMsg += f"{status_idx}. Status is a Video.\n"

                                # Wait for loading icon to disabled
                                try:
                                    wait.until(EC.invisibility_of_element_located(
                                        (By.XPATH, '//div[@class="_1xAJD EdAF7 loading"]')))
                                    sleep(1)
                                except: # Passing cus the loading icon is disabled.
                                    pass
                                finally:
                                    # Click the pause button
                                    bot.find_element(
                                        By.XPATH, '//div[@class="lyrceosr bx7g2weo i94gqilv bmot90v7 lxozqee9"]').click()
                                    sleep(1)

                                    # Click Next Status
                                    bot.find_elements(By.XPATH, barsXpath)[
                                        viewed_status+1].click()
                            else:  # Last Status
                                print(
                                    f"{status_idx}. Status is a Video.")
                                statusTypeMsg += f"{status_idx}. Status is a Video.\n"

                                try:
                                    wait.until(EC.invisibility_of_element_located(
                                        (By.XPATH, '//div[@class="_1xAJD EdAF7 loading"]')))
                                except: # Passing cus the loading icon is disabled.
                                    pass
                                finally:
                                    # Click the pause button
                                    bot.find_element(
                                        By.XPATH, '//div[@class="lyrceosr bx7g2weo i94gqilv bmot90v7 lxozqee9"]').click()
                                    sleep(1)
                            # Return the value to False to not always excecute this if the first viewed status is an Video
                            videoStatusValue = False
                    except: 
                        try:
                            if txtStatusValue == check_Status["txtStatusValue"]: 
                                if status_idx == 1: # First status
                                    print(
                                        f"Viewed {status_idx} out of {unviewed_status}.")                                                 
                                if status_idx != loop_range[-1]:  # Not last Status
                                    print(f"{status_idx}. Status is Just a Text.")
                                    statusTypeMsg += f"{status_idx}. Status is a Text.\n"

                                    # Click the pause button
                                    bot.find_element(
                                        By.XPATH, '//div[@class="lyrceosr bx7g2weo i94gqilv bmot90v7 lxozqee9"]').click()

                                    # Click next status
                                    bot.find_elements(By.XPATH, barsXpath)[
                                        viewed_status+1].click()
                                else:  # Last Status is a Text.
                                    print(f"{status_idx}. Status is a Text.")
                                    statusTypeMsg += f"{status_idx}. Status is a Text.\n"
                                    # Click the pause button
                                    bot.find_element(
                                        By.XPATH, '//div[@class="lyrceosr bx7g2weo i94gqilv bmot90v7 lxozqee9"]').click()
                                # Return the value to False to not always excecute this if the first viewed status is an Text
                                txtStatusValue = False
                        except:
                            try: 
                                if old_messageValue == check_Status["old_messageValue"]:
                                    if status_idx != loop_range[-1]:  # Not the last status
                                        print(
                                            f"{status_idx}. Status is an Old Whatsapp Version.")
                                        statusTypeMsg += f"{status_idx}. Status is an Old Whatsapp Version.\n"

                                        # Click the pause button
                                        bot.find_element(
                                            By.XPATH, '//div[@class="lyrceosr bx7g2weo i94gqilv bmot90v7 lxozqee9"]').click()
                                        # sleep(1)

                                        # Click next status
                                        bot.find_elements(By.XPATH, barsXpath)[
                                            viewed_status+1].click()
                                    else:  # Last Status
                                        print(
                                            f"{status_idx}. Status is an Old Whatsapp Version.")
                                        statusTypeMsg += f"{status_idx}. Status is an Old Whatsapp Version.\n"

                                        # Click the pause button
                                        bot.find_element(
                                            By.XPATH, '//div[@class="lyrceosr bx7g2weo i94gqilv bmot90v7 lxozqee9"]').click()
                                    print(
                                        f"Viewed {status_idx} out of {unviewed_status}.\nStatus is an Old Whatsapp Version.")
                                    # Return the value to False to not always excecute this if the first viewed status is an Text
                                    old_messageValue = False
                            except Exception as e: 
                                print(f'Failed {e}')
                finally:
                    if status_idx != loop_range[-1]: # Increment Viewed Status
                        viewed_status += 1
                    else: # Exit status
                        bot.find_element(By.XPATH, '//span[@data-icon="x-viewer"]').click()

            # Send to MySelf
            wa.text(f"{statusTypeMsg}\n{statusUploaderName} at {gmtTime()}")
        
        except Exception:
            pass #  Cus No Status Found
        
        
if __name__ == "__main__":
    try:
        runCode()
    except Exception as e:
        print(f"Main While Exception\n{e}")
        wa.text("Window Closed 🤦‍♀️")