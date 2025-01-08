from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from python_whatsapp_bot import Whatsapp, Inline_list, List_item
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from art import tprint, set_default, text2art
from selenium.webdriver.common.by import By
from time import sleep, perf_counter
import contextlib, pyautogui, pytz
from typing import Optional, Dict
from selenium import webdriver
from datetime import datetime
from vars import *


set_default("fancy99")
tprint("WhatsApp Status Viewer", 'rectangles')
tprint('\nDo you want to get notified about status or view them automatically?\n\
Enter "Y" to get notified or "N" to view them automatically: ')

gmtTime: str = lambda tz: datetime.now(
    pytz.timezone(tz)).strftime("%I:%M:%S %p")

checkStatus = lambda : bot.find_element(By.XPATH, pps_xpath)  # Status Circle around profile picture

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
                tprint(f"\n{status_uploader_name} has a status.\n{gmtTime(timezone)}")
                wa_bot.send_message(NUMBER, f"{status_uploader_name} has a status.\n{gmtTime(timezone)}", \
                    reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("GGs 🤞")]))
            else:
                start = reminderFn(time_diff, start)  # Reset time

def open_WhatsApp()-> None:

    wait_until_whatsapp_login_instructions_disappear = lambda: wait3secs.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="_3AjBo"]')))  # WhatsApp list login instructions

    bot.get("https://web.whatsapp.com/")


    try:
        print(text2art("\nLogging in..."), "💿")
        login_count: int = 1
        while True:
            try:
                bot.find_element(By.XPATH, '//div[@id="pane-side"]')
                break
            except NoSuchElementException:  # Log in page (Scan QRCode)
                with contextlib.suppress(TimeoutException):
                    wait_until_whatsapp_login_instructions_disappear()

                    if login_count == 1:
                        print(text2art("Please scan the QRCODE to log in"), "🔑")
                        login_count += 1

                    wait_until_whatsapp_login_instructions_disappear()

                    wait3secs.until(EC.visibility_of_element_located(
                        (By.XPATH, '//div[@class="_1dEQH _26aja"]'))) # WhatsApp: Text
                    wait3secs.until(EC.invisibility_of_element(
                        (By.XPATH, '//div[@class="x1c3i2sq x14ug900 xk82a7y x1sy10c2"]')))  # Loading your chats
                    wait3secs.until(EC.invisibility_of_element(
                        (By.XPATH, '//div[@class="_3HbCE"]'))) # Loading [%]
                    break
        print(text2art("Logged in successfully."), "✌")
        tprint(f'Logged in at {gmtTime(timezone)}\n')
    except TimeoutException:
        wa_bot.send_message(NUMBER, 'Took too long to login.', reply_markup=Inline_list("Show list", \
            list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job 🤞")]))
        bot.quit()

def scroll(contact_name) -> None:

    bot.find_element(By.XPATH, status_list_page_xpath).click()  # Enter Status Screen
    status_container_xpath: str = '//*[@class="g0rxnol2 ggj6brxn m0h2a7mj lb5m6g5c lzi2pvmc ag5g9lrv jhwejjuw ny7g4cd4"]'

    vertical_ordinate: int = 0
    while True:
        with contextlib.suppress(NoSuchElementException):
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
                viewed_circle_xpath: str = f'//span[@title="{contact_name}"]//ancestor::div[@class="lhggkp7q ln8gz9je rx9719la"]\
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
            elif 'l3hfgdr1 qk2y3tb3 myeiuhv9")]' in xpath:
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
    status_uploader_name: str = status_uploader_name, 
) -> Optional[Dict[str, str]]:
    
    def _backnforward():
        # Go backward and forward to get 'blob' in url
        bot.find_elements(By.XPATH, bars_xpath)[viewed_status-1].click(); sleep(1)
        bot.find_elements(By.XPATH, bars_xpath)[viewed_status].click(); sleep(1)

    def click_pause():
        while True:
            try:
                wait.until(EC.invisibility_of_element_located(
                    (By.XPATH, loading_icon_in_status_xpath)))
                bot.find_element(By.XPATH, pause_btn_xpath).click()
                sleep(3)
                break
            except TimeoutException: ...
            except NoSuchElementException: return  # ALREADY PAUSED

    def img_or_txt_pause():
        """This function pauses when image or text status is detected"""
        try:
            WebDriverWait(bot, 1).until(EC.invisibility_of_element_located(
                (By.XPATH, loading_icon_in_status_xpath)))
            bot.find_element(By.XPATH, pause_btn_xpath).click()
        except Exception: return
        # except (TimeoutException, NoSuchElementException): return
        ##  Add StaleElement to the above(Fix this)
    
    global kill
    kill = False

    open_WhatsApp()

    search_field = bot.find_element(By.XPATH, search_field_xpath)
    search_field.send_keys(status_uploader_name)

    counter = 0
    total_status: int  = 1
    while True:
        counter += 1
        while True:
            try:
                wait.until(EC.invisibility_of_element_located(  # SEARCH BAR LOADING SVG ICON
                    (By.XPATH, search_bar_loading_xpath)))
                bot.find_element(By.XPATH, pps_xpath)  # Status Circle around profile picture
                sleep(5)
                bot.find_element(By.XPATH, pp_xpath).click()  # Click Profile Picture to view Status
                break
            # NO GREEN CIRCLE AROUND PROFILE PICTURE (NO STATUS YET) OR STILL LOADING SEARCHED WORD
            except (TimeoutException, NoSuchElementException): continue 
            ######     DEBUGGING PURPOSE     ######
            # except TimeoutException: continue  # STARTING FROM THE
            # except NoSuchElementException:     # TIMEOUTEXECPTION TO
            #     if counter > 1:                # THE LAST BREAK SHOULD
            #         return                     # BE REMOVED CUS IT'S
            #     scroll(status_uploader_name)     # FOR VIEWING VIEWED STATUS
            #     wait.until(EC.invisibility_of_element((By.XPATH, temp_status_thumbnail)))
            #     bot.find_element(By.XPATH, scrolled_viewed_person_xpath).click()
            #     break

        unviewed_status: int = len(bot.find_elements(By.XPATH, unviewed_status_xpath)) + 1
        total_status: int = len(bot.find_elements(By.XPATH, bars_xpath))
        block_line: str = "-"*38
        loop_range: list = range(1, unviewed_status+1)
        viewed_status: int = total_status - unviewed_status
        statusTypeMsg += f"{status_uploader_name}\nUnviewed Statues " + "is" if unviewed_status == 1 else "are" + f" {unviewed_status} out of {total_status}.\n"
        statusType_xpaths = [img_status_xpath, video_status_xpath, text_status_xpath, audio_status_xpath, oldMessage_status_xpath]
        for status_idx in loop_range:

            img_or_txt_pause()

            if status_idx == 1: tprint(statusTypeMsg[:-1])

            with ThreadPoolExecutor(5) as pool:
                tasks = [pool.submit(checkStatusType, specific_xpath) for specific_xpath in statusType_xpaths]
                
                for future in as_completed(tasks):
                    if all([future.done(), future.result() is not None]):
                        check_Status = future.result()
                kill = False # Reset kill to False

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
                                    bot.find_element(By.XPATH, paused_video_bar_xpath)  # paused status
                                    style_value = bot.find_element(By.XPATH, paused_video_bar_xpath).get_attribute("style")  # Starts @ 100 reduces to 0
                                except NoSuchElementException:
                                    bot.find_element(By.XPATH, playing_video_bar_xpath)  # playing status
                                    style_value = bot.find_element(By.XPATH, playing_video_bar_xpath).get_attribute("style")  # Starts @ 100 reduces to 0
                                finally:
                                    video_progress = style_value.split("(")[1].split(")")[0][1:-1]
                                    with contextlib.suppress(TimeoutException, NoSuchElementException):
                                        wait3secs.until(EC.invisibility_of_element_located(
                                            (By.XPATH, loading_icon_in_status_xpath)))
                                        loading_icon = False
                                    if all([(0 <= float(video_progress) <= 30), loading_icon, total_status == 1]): # The only Status
                                        bot.find_element(By.XPATH, status_exit_xpath).click()
                                        scroll(status_uploader_name)
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
                    bot.find_elements(By.XPATH, bars_xpath)[viewed_status].click()
                else: # Status view completed, Exit status
                    try:
                        bot.find_element(By.XPATH, status_exit_xpath).click()
                    except NoSuchElementException:
                        sleep(3)
                        with contextlib.suppress(NoSuchElementException): 
                            # Check if it has truely exited by confirming if the page is on 'contact_name' search page
                            # BUT WHAT IF IT HAS NOT? WHY SKIP DO THIS IN THE FIRST PLACE # TODO FIX THIS
                            bot.find_element(By.XPATH, f'//span[@title="{status_uploader_name}"]//span')
                            bot.find_element(By.XPATH, '//div[@title="Status"]').send_keys(Keys.ESCAPE) # TODO: Confirm what this does
                    tprint(block_line); sleep(1)

        # Send to Self
        wa_bot.send_message(NUMBER, f"{statusTypeMsg}\n{status_uploader_name} at {gmtTime(timezone)}.", \
            reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job")]))
        statusTypeMsg: str = ""

                
if __name__ == "__main__":

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

    if answer in ["Y", "YES"]: getNotified()
    elif answer in ["N", "NO"]: autoViewStatus()
