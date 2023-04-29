import pytz
import contextlib
from datetime import datetime
from selenium import webdriver
from time import sleep, perf_counter
from os import environ as env_variable
from selenium.webdriver.common.by import By
from art import tprint, set_default, text2art
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from python_whatsapp_bot import Whatsapp, Inline_list, List_item
from selenium.common.exceptions import TimeoutException, NoSuchElementException

NUMBER: str = env_variable.get("MY_NUMBER")  # Your WhatsApp Number e.g: 234xxxxxxxxxx
NUM_ID: str = env_variable.get("NUM_ID")  # Your Number ID
TOKEN: str =  env_variable.get("TOKEN")  # Token


set_default("fancy99")
tprint("WhatsApp Status Viewer", 'rectangles')
tprint('\nDo you want to get notified about status or view them automatically?\n\
Enter "Y" to get notified or "N" to view them automatically: ')

answer: str = input('===> ').strip().upper()

input_count: int = 1
while True:
    if answer not in {"YES", "NO", "Y", "N"}:
        print(text2art('\nYou had one job to do! "Y" or "N"', "fancy56")); print('🥱')
        tprint('Do you want to get notified about status or view them automatically?')
        answer: str = input(text2art('Enter "Y" to get notified or "N" to view them automatically: ')).upper()
    else:
        if answer in ("N", "NO"): break
        while True:
            with contextlib.suppress(ValueError):
                if input_count == 1:
                    reminderTime: int = int(input(text2art('\nHow often do you want to be notified?\n1. Enter "1" for 30 Mins\n2. Enter "2" for 1 Hour\n3. Enter "3" for 3 Hours\n4. Enter "4" for 6 Hours\nI want: ')))
                else: 
                    print(text2art('\nYou have to choose between "1", "2", "3" or "4"', "fancy56"))#; print('', end="")
                    reminderTime: int = int(input('🥱 ===> '))
                if reminderTime in {1, 2, 3, 4}: break
            input_count += 1
        break

timezone: str = "Africa/Lagos"  # Your timezone
statusUploaderName: str = "ContactName" # As it is saved on your phone(Case Sensitive)
ppsXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]'
ppXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]//parent::div'
barsXpath: str = '//div[@class="g0rxnol2 qq0sjtgm jxacihee l7jjieqr egv1zj2i ppled2lx gj5xqxfh om6y7gxh"]'
barXpath: str =  '//div[@class="lhggkp7q qq0sjtgm tkdu00h0 ln8gz9je ppled2lx ss1fofi6 o7z9b2jg"]'
barVA_Xpath: str =  '//div[@class="lhggkp7q qq0sjtgm tkdu00h0 ln8gz9je ppled2lx ss1fofi6 o7z9b2jg velocity-animating"]'
driverpath: str = "C:\\Users\\Administrator\\Documents\\WhatsApp Status Checker\\assest\\driver\\chromedriver.exe"
img_status_xpath: str = '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//img'
video_status_xpath: str = '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//video'
text_status_xpath: str = '//div[@data-testid="status-v3-text"]'
audio_status_xpath: str = '//div[@class="g0rxnol2 ggj6brxn"]'

service = Service(executable_path=driverpath)
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-first-run")
options.add_argument('--disable-dev-shm-usage')
options.add_argument(r'--profile-directory=BoT Profile')
options.add_argument(r'user-data-dir=C:\BoT Chrome Profile')
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", 'enable-logging'])
options.add_argument('--disable-blink-features=AutomationControlled')


bot = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(bot, 60)
wait3secs = WebDriverWait(bot, 3)
action = ActionChains(bot)
bot.set_window_position(676, 0)
wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)

bot.get("https://web.whatsapp.com")


gmtTime: str = lambda tz: datetime.now(
    pytz.timezone(tz)).strftime("%H : %M : %S")

try:
    print(text2art("\nLogging in..."), "💿")
    login_count: int = 1
    while True:
        try:
            bot.find_element(By.XPATH, '//div[@data-testid="chat-list-search"]')
            break
        except NoSuchElementException:  # Log in page (Scan QRCode)
            with contextlib.suppress(TimeoutException):
                wait3secs.until(EC.visibility_of_element_located(
                    (By.XPATH, '//div[@class="_3AjBo"]')))  # WhatsApp list login instructions
                if login_count == 1:
                    print(text2art("Please scan the QRCODE to log in"), "🔑")
                    login_count += 1
                wait3secs.until(EC.invisibility_of_element(
                    (By.XPATH, '//div[@class="_3AjBo"]')))  # WhatsApp list login instructions
                wait3secs.until(EC.visibility_of_element_located(
                    (By.XPATH, '//div[@class="_1dEQH _26aja"]'))) # WhatsApp: Text
                wait3secs.until(EC.invisibility_of_element(
                    (By.XPATH, '//div[@class="_2dfCc"]')))  # Loading your chat
                break
    print(text2art("Logged in successfully."), "✌")
    tprint(f'Logged in at {gmtTime(timezone)}\n')
except TimeoutException:
    wa_bot.send_message(NUMBER, 'Took too long to login.', reply_markup=Inline_list("Show list", \
        list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job 🤞")]))
    bot.quit()

search_field = bot.find_element(By.XPATH, '//div[@data-testid="chat-list-search"]')
search_field.clear()
search_field.send_keys(statusUploaderName)
while True:
    with contextlib.suppress(TimeoutException):
        WebDriverWait(bot, 3).until(EC.invisibility_of_element_located(  # SEARCH BAR LOADING SVG ICON
            (By.XPATH, '//*[local-name()="svg" and @class="gdrnme8s hbnrezoj f8mos8ky tkmeqcnu b9fczbqn"]')))
        sleep(5)
        break

checkStatus = lambda : bot.find_element(By.XPATH, ppsXpath)  # Status Circle around profile picture

def checkStatusType() -> dict:
    try: # Image Status
        bot.find_element(By.XPATH, img_status_xpath)
        return {"imgStatusValue": True}
    except NoSuchElementException:
        try: # Video Status
            bot.find_element(By.XPATH, video_status_xpath)
            return {"videoStatusValue": True}
        except NoSuchElementException:
            try: # Text Status
                bot.find_element(By.XPATH, text_status_xpath)
                return {"txtStatusValue": True}
            except NoSuchElementException:
                try:
                    try:  # Audio Status
                        bot.find_element(By.XPATH, audio_status_xpath)
                        return {"audioStatusValue": True}
                    except NoSuchElementException: # OLD WHATSAPP MSG
                            bot.find_element(By.XPATH, '//div[@class="lhggkp7q qq0sjtgm tkdu00h0 ln8gz9je ppled2lx"]')
                            return {"old_messageValue": True}
                except NoSuchElementException:
                    tprint("Neither can Image/Video/Text/'Old whatsapp' be found.")

def reminderFn(ttime_diff: float, sstart: float) -> float:
    if (
       reminderTime == 1 and ttime_diff >= 1_800  # Every 30 Mins
       or reminderTime == 2 and ttime_diff >= 3_600  # Every 1 Hour
       or reminderTime == 3 and ttime_diff >= 10_800  # Every 3 Hours
       or reminderTime == 4 and ttime_diff >= 21_600  # Every 6 Hours
    ): return float("{:.2f}".format(perf_counter()))
    else: return sstart

def getNotified() -> None:
    start = float("{:.2f}".format(perf_counter()))
    while True:
        with contextlib.suppress(NoSuchElementException):
            checkStatus()
            time_diff = float("{:.2f}".format(perf_counter())) - start
            
            if time_diff <= 0.2:
                tprint(f"\n{statusUploaderName} has a status.\n{gmtTime(timezone)}")
                wa_bot.send_message(NUMBER, f"{statusUploaderName} has a status.\n{gmtTime(timezone)}", reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("GGs 🤞")]))
            else:
                start = reminderFn(time_diff, start)  # Reset time

def autoViewStatus(statusTypeMsg: str = "") -> None:
    status_links: list = []
    while True:
        with contextlib.suppress(Exception):
            checkStatus()
            bot.find_element(By.XPATH, ppXpath).click()  # Click Profile Picture to view Status
            unviewed_status: int = len(bot.find_elements(By.XPATH, '//div[contains(@class, "mjomr7am")]')) + 1
            total_status: int = len(bot.find_elements(By.XPATH, barsXpath))
            block_line: str = "-"*38
            loop_range: list = range(1, unviewed_status+1)
            viewed_status: int = total_status - unviewed_status
            statusTypeMsg += f"{statusUploaderName}\nUnviewed Statues is/are {unviewed_status} out of {total_status}.\n"
            for status_idx in loop_range:
                if status_idx == 1: tprint(statusTypeMsg[:-1])

                sleep(1)

                check_Status: dict = checkStatusType()

                try:
                    if check_Status["imgStatusValue"]:
                        tprint(f"{status_idx}. Status is an Image.")
                        statusTypeMsg += f"{status_idx}. Status is an Image.\n"
                except KeyError:
                    try:
                        if check_Status["videoStatusValue"]:
                            loading_icon: bool = True
                            while True:
                                with contextlib.suppress(TimeoutException):
                                    try:
                                        bot.find_element(By.XPATH, barXpath)
                                    except NoSuchElementException:
                                        bot.find_element(By.XPATH, barVA_Xpath)
                                        style_value = bot.find_element(By.XPATH, barVA_Xpath).get_attribute("style")
                                        video_progress = style_value.split("(")[1].split(")")[0][1:-1]
                                        if all([(0 <= float(video_progress) <= 30), loading_icon, total_status > 1]): # Not the only Status
                                            bot.find_elements(By.XPATH, barsXpath)[viewed_status+1].click()
                                            sleep(3)
                                            bot.find_elements(By.XPATH, barsXpath)[viewed_status].click()
                                    finally:
                                        WebDriverWait(bot, 0.1).until(EC.invisibility_of_element_located(
                                            (By.XPATH, '//button[@class="icon-media-disabled"]')))
                                        loading_icon = False
                                        break
                            # Click the pause button
                            bot.find_element(
                                By.XPATH, '//span[@data-icon="status-media-controls-pause"]').click()
                            sleep(3) # .5

                            tprint(f"{status_idx}. Status is a Video.")
                            statusTypeMsg += f"{status_idx}. Status is a Video.\n"
                    except KeyError: 
                        try:
                            if check_Status["txtStatusValue"]:
                                tprint(f"{status_idx}. Status is a Text.")
                                statusTypeMsg += f"{status_idx}. Status is a Text.\n"
                        except KeyError:
                            try:
                                if check_Status["audioStatusValue"]:
                                    tprint(f"{status_idx}. Status is an Audio.")
                                    statusTypeMsg += f"{status_idx}. Status is an Audio.\n"
                            except KeyError:
                                try: 
                                    if check_Status["old_messageValue"]:
                                        tprint(f"{status_idx}. Status is an Old Whatsapp Version.")
                                        statusTypeMsg += f"{status_idx}. Status is an Old Whatsapp Version.\n"
                                except KeyError as e: 
                                    tprint(f'Failed! -> {e}')
                finally:
                    if status_idx != loop_range[-1]:
                        viewed_status += 1

                        # Click Next Status
                        bot.find_elements(By.XPATH, barsXpath)[ 
                            viewed_status].click()
                    else: # Exit status
                        bot.find_element(By.XPATH, '//span[@data-icon="x-viewer"]').click()
                        tprint(block_line)

                        # Send to Self
                        wa_bot.send_message(NUMBER, f"{statusTypeMsg}\n{statusUploaderName} at {gmtTime(timezone)}.", \
                            reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job")]))
                        statusTypeMsg: str = ""

                
if __name__ == "__main__":
    try:
        if answer in ["Y", "YES"]: getNotified()
        elif answer in ["N", "NO"]: autoViewStatus()
    except Exception as e:
        tprint(f"Main Exception\n{e}")
        wa_bot.send_message(NUMBER, "Window Closed 🤦‍♀️", reply_markup=Inline_list("Show list", \
            list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job 🤞")]))
        