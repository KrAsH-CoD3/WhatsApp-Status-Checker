import pytz
import contextlib
from datetime import datetime
from selenium import webdriver
from time import sleep, perf_counter
from os import environ as env_variable
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from python_whatsapp_bot import Whatsapp, Inline_keyboard, Inline_list, List_item

NUMBER: str = env_variable.get("MY_NUMBER")  # Your Number e.g: 234xxxxxxxxxx
NUM_ID: str = env_variable.get("NUM_ID")  # Your Number ID
TOKEN: str =  env_variable.get("TOKEN")  # Token

answer = input('\nDo you want to get notified about status or view them automatically?\n\
Enter "Y" to get notified or "N" to view them automatically: ').upper()

while True:
    if answer in {"Y", "N"}:
        if answer == "N": break
        while True:
            try:
                reminderTime = int(input("\nHow often do you want to be notified?\n1. Enter \"1\" for 30 Mins\n2. Enter \"2\" for 1 Hour\n3. Enter \"3\" for 3 Hours\n4. Enter \"4\" for 6 Hours\nI want: "))
                if reminderTime in {1, 2, 3, 4}: break
            except ValueError: 
                print("\nYou have to choose between \"1\", \"2\", \"3\" or \"4\" 🥱".upper())
                continue
        break
    else:
        print("\nYou had one job to do! \"Y\" or \"N\" 🥱".upper())
        answer = input('\nDo you want to get notified about status or view them automatically?\n\
        Enter "Y" to get notified or "N" to view them automatically: ').upper()


timezone: str = "Africa/Lagos"
statusUploaderName: str = "Ijk" # As it is saved on your phone(Case Sensitive)
ppsXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]'
ppXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]//parent::div'
barsXpath: str = '//div[@class="g0rxnol2 qq0sjtgm jxacihee l7jjieqr egv1zj2i ppled2lx gj5xqxfh om6y7gxh"]'
driverpath = "C:\\Users\\Administrator\\Documents\\WhatsApp Status Checker\\assest\\driver\\chromedriver.exe"

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
action = ActionChains(bot)
bot.set_window_position(676, 0)
wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)

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
    wa_bot.send_message(NUMBER, 'Took too long to login.', reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("GGs 🤞")]))
    bot.quit()

gmtTime: str = lambda tz: datetime.now(
    pytz.timezone(tz)).strftime("%H : %M : %S")
print(gmtTime(timezone))

search_field = bot.find_element(By.XPATH, '//div[@data-testid="chat-list-search"]')
search_field.clear()
search_field.send_keys(statusUploaderName)
sleep(5)

checkStatus = lambda : bot.find_element(By.XPATH, ppsXpath)  # Status Circle around profile picture

def checkStatusType() -> dict:
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
    
def autoViewStatus(statusTypeMsg: str = "") -> None:
    while True:
        with contextlib.suppress(Exception):
            checkStatus()
            bot.find_element(By.XPATH, ppXpath).click()  # Click Profile Picture to view Status
            unviewed_status: int = len(bot.find_elements(By.XPATH, '//div[contains(@class, "mjomr7am")]')) + 1
            total_status: int = len(bot.find_elements(By.XPATH, barsXpath))
            viewed_status: int = total_status - unviewed_status
            loop_range: list = range(1, unviewed_status+1)
            block_line: str = "-"*38  
            statusTypeMsg += f"{statusUploaderName}\nUnviewed Statues is/are {unviewed_status} out of {total_status}.\n"
            for status_idx in loop_range:
                if status_idx == 1: print(statusTypeMsg[:-1])

                sleep(1)
                    
                check_Status: dict = checkStatusType()

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
                            sleep(7)  # Longer sleep (making sure the view is registered) 

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

            # Send to Self
            wa_bot.send_message(NUMBER, f"{statusTypeMsg}\n{statusUploaderName} at {gmtTime(timezone)}.", reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("GGs 🤞")]))

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
                wa_bot.send_message(NUMBER, f"{statusUploaderName} has a status.\n{gmtTime(timezone)}", reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("GGs 🤞")]))
            else:
                start = reminderFn(time_diff, start)  # Reset time

                
if __name__ == "__main__":
    try:
        if answer == "Y": getNotified()
        elif answer == "N": autoViewStatus()
    except Exception as e:
        print(f"Main Exception\n{e}")
        wa_bot.send_message(NUMBER, "Window Closed 🤦‍♀️", reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("GGs 🤞")]))
        