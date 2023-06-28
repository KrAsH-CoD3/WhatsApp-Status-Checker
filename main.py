from datetime import datetime
from selenium import webdriver
from typing import Optional, Dict
import contextlib, pyautogui, pytz
from time import sleep, perf_counter
from os import environ as env_variable
from selenium.webdriver.common.by import By
from art import tprint, set_default, text2art
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor, as_completed
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
pause_btn_xpath:str = '//span[@data-icon="status-media-controls-pause"]'
statusUploaderName: str = "ContactName" # As it is saved on your phone(Case Sensitive)
ppsXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]'
ppXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]//parent::div'
barsXpath: str = '//div[@class="g0rxnol2 qq0sjtgm jxacihee l7jjieqr egv1zj2i ppled2lx gj5xqxfh om6y7gxh"]'
barXpath: str =  '//div[@class="lhggkp7q qq0sjtgm tkdu00h0 ln8gz9je ppled2lx ss1fofi6 o7z9b2jg"]'
driverpath: str = "C:\\Users\\Administrator\\Documents\\WhatsApp Status Checker\\assest\\driver\\chromedriver.exe"
barVA_Xpath: str =  '//div[@class="lhggkp7q qq0sjtgm tkdu00h0 ln8gz9je ppled2lx ss1fofi6 o7z9b2jg velocity-animating"]'
scrolled_viewed_person_xpath :str = f'//span[@title="{statusUploaderName}" and \
    @class="ggj6brxn gfz4du6o r7fjleex g0rxnol2 lhj4utae le5p0ye3 _11JPr"]'
tempStatusThumbnail: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::div[@class="_1AHcd"]//\
    div[@class="t3g6t33p sxl192xd qnwaluaf g9p5wyxn i0tg5vk9 aoogvgrq o2zu3hjb gfz4du6o r7fjleex lniyxyh2 qssinsw9 rx2toazg"]'
img_status_xpath: str = '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//img'
video_status_xpath: str = '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//video'
text_status_xpath: str = '//div[@data-testid="status-v3-text"]'
audio_status_xpath: str = '//div[@class="ajgl1lbb"]'
oldMessage_status_xpath: str = '//div[contains(@class, "qfejxiq4 b6f1x6w7 m62443ks")]'
caption_xpath: str = '//div[@class="tvsr5v2h mz6luxmp clw8hvz5 p2tfx3a3 holukk2e cw3vfol9"]//\
    span[@class="_11JPr" and @dir="auto" and @aria-label]'
read_more_caption_xpath: str = f'{caption_xpath}//following-sibling::strong'

service = Service(executable_path=driverpath)
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-first-run")
options.add_argument("--single-process")
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
bot.set_window_size(700, 730)
bot.set_window_position(676, 0)
wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)
pyautogui.FAILSAFE = False
pyautogui.press('esc')

gmtTime: str = lambda tz: datetime.now(
    pytz.timezone(tz)).strftime("%H : %M : %S")

checkStatus = lambda : bot.find_element(By.XPATH, ppsXpath)  # Status Circle around profile picture

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
                wa_bot.send_message(NUMBER, f"{statusUploaderName} has a status.\n{gmtTime(timezone)}", \
                    reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("GGs 🤞")]))
            else:
                start = reminderFn(time_diff, start)  # Reset time

def open_WhatsApp()-> None:

    bot.get("https://web.whatsapp.com")


    try:
        print(text2art("\nLogging in..."), "💿")
        login_count: int = 1
        while True:
            try:  # 
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
                    wait3secs.until(EC.invisibility_of_element(
                        (By.XPATH, '//div[@class="_3HbCE"]'))) # Loading [%]
                    break
        print(text2art("Logged in successfully."), "✌")
        tprint(f'Logged in at {gmtTime(timezone)}\n')
    except TimeoutException:
        wa_bot.send_message(NUMBER, 'Took too long to login.', reply_markup=Inline_list("Show list", \
            list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job 🤞")]))
        bot.quit()

def scroll(personName) -> None:

    bot.find_element(By.XPATH, '//div[@title="Status"]').click()  # Enter Status Screen
    status_container_xpath: str = '//*[@class="g0rxnol2 ggj6brxn m0h2a7mj lb5m6g5c lzi2pvmc ag5g9lrv jhwejjuw ny7g4cd4"]'

    vertical_ordinate: int = 0
    while True:
        with contextlib.suppress(NoSuchElementException):
            try:
                vertical_ordinate += 2500
                status_container = bot.find_element(By.XPATH, status_container_xpath)
                viewed_circle_xpath: str = f'//span[@title="{personName}"]//ancestor::div[@class="lhggkp7q ln8gz9je rx9719la"]\
                                //*[local-name()="circle" and @class="j9ny8kmf"]'  # UNVIEWED
                bot.execute_script(
                    "arguments[0].scrollTop = arguments[1]", status_container, vertical_ordinate)
                statusPoster = bot.find_element(By.XPATH, viewed_circle_xpath)
                bot.execute_script('arguments[0].scrollIntoView();', statusPoster)
                break
            except NoSuchElementException:
                viewed_circle_xpath: str = f'//span[@title="{personName}"]//ancestor::div[@class="lhggkp7q ln8gz9je rx9719la"]\
                                //*[local-name()="circle" and @class="i2tfkqu4"]'  # VIEWED
                statusPoster = bot.find_element(By.XPATH, viewed_circle_xpath)
                bot.execute_script('arguments[0].scrollIntoView();', statusPoster)
                break
            #  REMOVE EXCEPTION BLOCK AFTER GETTING WHETHER IT VIEWED OR NOT

def checkStatusType(xpath) -> Optional[Dict[str, bool]]:
    global kill
    while kill != True:
        with contextlib.suppress(NoSuchElementException, TimeoutException):
            WebDriverWait(bot, .1).until(EC.presence_of_element_located((By.XPATH, xpath)))
            # bot.find_element(By.XPATH, xpath)
            if 'r7fjleex"]//img' in xpath:
                kill = True
                return {"imgStatusValue": True}
            elif 'r7fjleex"]//video' in xpath:
                kill = True
                return {"videoStatusValue": True}
            elif 'status-v3-text"]' in xpath:
                kill = True
                return {"txtStatusValue": True}
            elif 'FixMeAudio' in xpath:
            # elif 'ajgl1lbb"]' in xpath:
                kill = True
                return {"audioStatusValue": True}
            elif 'b6f1x6w7 m62443ks")]' in xpath:
                kill = True
                return {"old_messageValue": True}  # Returning this is very rare

def autoViewStatus(
    statusTypeMsg: str = "", 
    statusUploaderName: str = statusUploaderName, 
    ) -> Optional[Dict[str, str]]:
    
    def _backnforward():
        # Go backward and forward to get 'blob' in url
        bot.find_elements(By.XPATH, barsXpath)[viewed_status-1].click(); sleep(1)
        bot.find_elements(By.XPATH, barsXpath)[viewed_status].click(); sleep(1)

    def click_pause():
        while True:
            try:
                wait.until(EC.invisibility_of_element_located(
                    (By.XPATH, '//button[@class="icon-media-disabled"]')))
                bot.find_element(By.XPATH, pause_btn_xpath).click()
                sleep(3)
                break
            except TimeoutException: ...
            except NoSuchElementException: break  # ALREADY PAUSED

    def img_txt_pause():
        try:
            WebDriverWait(bot, 1).until(EC.invisibility_of_element_located(
                (By.XPATH, '//button[@class="icon-media-disabled"]')))
            bot.find_element(By.XPATH, pause_btn_xpath).click()
        except Exception: return
        # except (TimeoutException, NoSuchElementException): return
        ##  Add StaleElement to the above(Fix this)
    
    global kill
    kill = False

    open_WhatsApp()

    search_field = bot.find_element(By.XPATH, '//div[@data-testid="chat-list-search"]')
    search_field.send_keys(statusUploaderName)

    counter = 0
    total_status: int  = 1
    while True:
        counter += 1
        while True:
            try:
                wait.until(EC.invisibility_of_element_located(  # SEARCH BAR LOADING SVG ICON
                    (By.XPATH, '//*[local-name()="svg" and @class="gdrnme8s hbnrezoj f8mos8ky tkmeqcnu b9fczbqn"]')))
                bot.find_element(By.XPATH, ppsXpath)  # Status Circle around profile picture
                sleep(5)
                bot.find_element(By.XPATH, ppXpath).click()  # Click Profile Picture to view Status
                break
            except (TimeoutException, NoSuchElementException): continue
            ######     DEBUGGING PURPOSE     ######
            # except TimeoutException: continue  # STARTING FROM THE
            # except NoSuchElementException:     # TIMEOUTEXECPTION TO
            #     if counter > 1:                # THE LAST BREAK SHOULD
            #         return                     # BE REMOVED CUS IT'S
            #     scroll(statusUploaderName)     # FOR VIEWING VIEWED STATUS
            #     wait.until(EC.invisibility_of_element((By.XPATH, tempStatusThumbnail)))
            #     bot.find_element(By.XPATH, scrolled_viewed_person_xpath).click()
            #     break

        unviewed_status: int = len(bot.find_elements(By.XPATH, '//div[contains(@class, "mjomr7am")]')) + 1
        total_status: int = len(bot.find_elements(By.XPATH, barsXpath))
        block_line: str = "-"*38
        loop_range: list = range(1, unviewed_status+1)
        viewed_status: int = total_status - unviewed_status
        statusTypeMsg += f"{statusUploaderName}\nUnviewed Statues is/are {unviewed_status} out of {total_status}.\n"
        statusType_xpaths = [img_status_xpath, video_status_xpath, text_status_xpath, audio_status_xpath, oldMessage_status_xpath]
        for status_idx in loop_range:

            img_txt_pause()

            if status_idx == 1: tprint(statusTypeMsg[:-1])

            with ThreadPoolExecutor(5) as pool:
                tasks = [pool.submit(checkStatusType, specific_xpath) for specific_xpath in statusType_xpaths]
                
                for future in as_completed(tasks):
                    if all([future.done(), future.result() is not None]):
                        check_Status = future.result()
                kill = False

            try:
                if check_Status["imgStatusValue"]:
                    try: bot.find_element(By.XPATH, pause_btn_xpath).click()
                    except NoSuchElementException: ...  # ALREADY CLCIKED
                    tprint(f"{status_idx}. Status is an Image.")
                    statusTypeMsg += f"{status_idx}. Status is an Image.\n"
            except KeyError:
                try:
                    if check_Status["videoStatusValue"]:
                        loading_icon: bool = True
                
                        while True:                                
                            with contextlib.suppress(TimeoutException):
                                try:
                                    bot.find_element(By.XPATH, barXpath)  # paused status
                                    style_value = bot.find_element(By.XPATH, barXpath).get_attribute("style")  # Starts @ 100 reduces to 0
                                except NoSuchElementException:
                                    bot.find_element(By.XPATH, barVA_Xpath)  # playing status
                                    style_value = bot.find_element(By.XPATH, barVA_Xpath).get_attribute("style")  # Starts @ 100 reduces to 0
                                finally:
                                    video_progress = style_value.split("(")[1].split(")")[0][1:-1]
                                    with contextlib.suppress(TimeoutException, NoSuchElementException):
                                        wait3secs.until(EC.invisibility_of_element_located(
                                            (By.XPATH, '//button[@class="icon-media-disabled"]')))
                                        loading_icon = False
                                    if all([(0 <= float(video_progress) <= 30), loading_icon, total_status == 1]): # The only Status
                                        bot.find_element(By.XPATH, '//span[@data-icon="x-viewer"]').click()
                                        scroll(statusUploaderName)
                                        bot.find_element(By.XPATH, scrolled_viewed_person_xpath).click()
                                    # while not loading_icon:
                                    if all([(0 <= float(video_progress) <= 30), loading_icon, total_status > 1]): # Not the only Status
                                        _backnforward(); continue
                                    # Continous loopback till loading_icon = False
                                    if all([(30 <= float(video_progress) <= 100), loading_icon]): continue
                                    # try: click_pause()  # THE VIDEO IS DEF. CAHCED/LOADED (_backnforward OR SCROLLING TO STATUS)
                                    # except NoSuchElementException: ...
                                    try: bot.find_element(By.XPATH, pause_btn_xpath).click()
                                    except NoSuchElementException: ...  # ALREADY CLCIKED                                    
                                    tprint(f"{status_idx}. Status is a Video.")
                                    statusTypeMsg += f"{status_idx}. Status is a Video.\n"
                                    loading_icon = False
                                    break
                except KeyError: 
                    try:
                        if check_Status["txtStatusValue"]:
                            try: bot.find_element(By.XPATH, pause_btn_xpath).click()
                            except NoSuchElementException: ...  # ALREADY CLCIKED
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
                    check_Status = None

                    # Click Next Status
                    bot.find_elements(By.XPATH, barsXpath)[viewed_status].click()
                else: # Exit status
                    try:
                        bot.find_element(By.XPATH, '//span[@data-icon="x-viewer"]').click()
                    except NoSuchElementException:
                        sleep(3)
                        with contextlib.suppress(NoSuchElementException):
                            bot.find_element(By.XPATH, f'//span[@title="{statusUploaderName}"]//span')
                    tprint(block_line); sleep(1)
                    bot.find_element(By.XPATH, '//div[@title="Status"]').send_keys(Keys.ESCAPE)

        # Send to Self
        wa_bot.send_message(NUMBER, f"{statusTypeMsg}\n{statusUploaderName} at {gmtTime(timezone)}.", \
            reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job")]))
        statusTypeMsg: str = ""

                
if __name__ == "__main__":
    # try:
    if answer in ["Y", "YES"]: getNotified()
    elif answer in ["N", "NO"]: autoViewStatus()
    # except Exception as e:
    #     tprint(f"Main Exception\n{e}")
    #     wa_bot.send_message(NUMBER, f"ERROR OCCURED 🤦‍♀️:\n{e}", reply_markup=Inline_list("Show list", \
    #         list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job 🤞")]))
        