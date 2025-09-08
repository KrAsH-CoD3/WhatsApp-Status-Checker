from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException, WebDriverException
import contextlib, pyautogui, pytz, signal, atexit, sys, psutil, platform
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from python_whatsapp_bot import Whatsapp, Inline_list, List_item
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.organize_chromedriver import ensure_chromedriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from art import tprint, set_default, text2art
from urllib3.exceptions import ProtocolError
from selenium.webdriver.common.by import By
from typing import Optional, Dict, List
from time import sleep, perf_counter
from selenium import webdriver
from datetime import datetime
from vars import *
import threading


ensure_chromedriver() # Handle ChromeDriver

set_default("fancy99")
tprint("WhatsApp Status Viewer", 'rectangles')
tprint('\nDo you want to get notified about status or view them automatically?\n\
Enter "Y" to get notified or "N" to view them automatically: ')

gmtTime: str = lambda tz: datetime.now(
    pytz.timezone(tz)).strftime("%I:%M:%S %p")

checkStatus = lambda : bot.find_element(By.XPATH, profile_picture_status_xpath)  # Status Circle around profile picture

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

    wait_until_whatsapp_login_instructions_disappear = lambda: wait3secs.until(EC.visibility_of_element_located((By.XPATH, login_instructions_xpath)))  # WhatsApp login instructions

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
        wa_bot.send_message(
            NUMBER, 
            'Took too long to login.', 
            reply_markup=Inline_list(
                "Show list", 
                list_items=[
                    List_item("Nice one 👌"), 
                    List_item("Thanks ✨"), 
                    List_item("Great Job 🤞")
                ]
            )
        )
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

def waitt(bot: WebDriver, seconds: int):
    return WebDriverWait(bot, seconds)

def _backnforward(bot: WebDriver, viewed_status: int):
    # Go backward and forward to get 'blob' in url
    bot.find_elements(By.XPATH, bars_xpath)[viewed_status-1].click(); 
    sleep(.2)
    bot.find_elements(By.XPATH, bars_xpath)[viewed_status].click()

def _forwardnback(bot: WebDriver, viewed_status: int):
    # Go forward and backward to get 'blob' in url
    bot.find_elements(By.XPATH, bars_xpath)[viewed_status+1].click()
    sleep(.2)
    bot.find_elements(By.XPATH, bars_xpath)[viewed_status].click()

def _close_status(bot: WebDriver):
    bot.find_element(By.XPATH, status_exit_xpath).click()

def handle_status_not_loaded(bot: WebDriver, total_status: int, viewed_status: int):
    unviewed_status: int = total_status - viewed_status

    if total_status == 1: # Only one status
        # _close_status(bot)
        # scroll(status_uploader_name)
        # bot.find_element(By.XPATH, scrolled_viewed_person_xpath).click()
        _close_status(bot)
        sleep(3)
        _click_profile_picture(bot)
    else: # Multiple statuses
        if unviewed_status == 1: # Only one new status uploaded
            _backnforward(bot, viewed_status)
        else:
            _forwardnback(bot, viewed_status)

def _click_profile_picture(bot: WebDriver):
    try:
        bot.find_element(By.XPATH, profile_picture_img_xpath).click()  # Click profile picture to view Status
    except NoSuchElementException: # 
        bot.find_element(By.XPATH, default_profile_picture_xpath).click()  # Click default profile picture to view Status 

def checkStatusType(bot: WebDriver, xpath: str) -> Optional[Dict[str, bool]]:
    while not stop_event.is_set():
        with contextlib.suppress(NoSuchElementException, TimeoutException):
            waitt(bot, .1).until(EC.presence_of_element_located((By.XPATH, xpath)))

            if '//video' in xpath:
                stop_event.set()
                return {"videoStatusValue": True}
            elif 'x5yr21d"]//img' in xpath:
                element: WebElement = bot.find_element(By.XPATH, xpath)
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

def click_pause():
    try:
        waitt(bot, .5).until(EC.invisibility_of_element_located(
            (By.XPATH, loading_icon_in_status_xpath)))
        bot.find_element(By.XPATH, pause_btn_xpath).click()
    except(NoSuchElementException, TimeoutException): 
        return  # ALREADY PAUSED

def autoViewStatus(
    statusTypeMsg: str = "", 
    status_uploader_name: str = status_uploader_name, 
) -> Optional[Dict[str, str]]:
    
    open_WhatsApp()

    search_field: WebElement = bot.find_element(By.XPATH, search_field_xpath)
    search_field.send_keys(status_uploader_name)

    # counter = 0
    total_status: int  = 1
    while True:
        # counter += 1
        # Continous check for status update
        while True:
            try:
                wait60secs.until(EC.visibility_of_element_located(  # Wait for status Circle around profile picture
                    (By.XPATH, profile_picture_status_xpath)))
                bot.find_element(By.XPATH, profile_picture_status_xpath)  # Status Circle around profile picture
                sleep(5)
                _click_profile_picture(bot)
                break
            # NO GREEN CIRCLE AROUND PROFILE PICTURE (NO STATUS YET) OR STILL LOADING SEARCHED WORD
            except (TimeoutException, NoSuchElementException): continue 
            ######     DEBUGGING PURPOSE     ######
            # except TimeoutException: continue  # STARTING FROM THE
            # except NoSuchElementException:     # TIMEOUTEXECPTION TO
            #     if counter > 1:                # THE LAST BREAK SHOULD
            #         return                     # BE REMOVED CUS IT'S
            #     scroll(status_uploader_name)     # FOR VIEWING VIEWED STATUS
            #     wait60secs.until(EC.invisibility_of_element((By.XPATH, temp_status_thumbnail)))
            #     bot.find_element(By.XPATH, scrolled_viewed_person_xpath).click()
            #     break

        bars: List[WebElement] = bot.find_elements(By.XPATH, bars_xpath)
        # +1 because the currently playing status is not included in the unviewed status
        unviewed_status: int = len(bot.find_elements(By.XPATH, unviewed_status_xpath)) + 1
        total_status: int = len(bars)
        block_line: str = "-"*38
        loop_range: list = range(1, unviewed_status+1)
        viewed_status: int = total_status - unviewed_status
        is_more_than_one_status: bool = unviewed_status > 1
        statusTypeMsg += f"{status_uploader_name}\nUnviewed Status update" + ("s" if is_more_than_one_status else "") + f" {unviewed_status} out of {total_status}.\n"
        statusType_xpaths = [img_status_xpath, video_status_xpath, text_status_xpath, audio_status_xpath, oldMessage_status_xpath]
        for status_idx in loop_range:

            if status_idx == 1: 
                tprint(statusTypeMsg[:-1])
            
            tasks = None
            stop_event.clear()
            executor = ThreadPoolExecutor(max_workers=5)
            tasks = [executor.submit(checkStatusType, bot, xpath) for xpath in statusType_xpaths]

            check_status = None
            for future in as_completed(tasks):
                check_status = future.result()
                if check_status is not None:
                    break

            # Stop accepting new tasks, return immediately
            executor.shutdown(wait=False)

            try:
                if check_status["imgStatusValue"]:
                    click_pause()
                    msg: str = f"{status_idx}. Status is an Image."
                    tprint(msg)
                    statusTypeMsg += msg + '\n'
            except KeyError:
                try:
                    if check_status["videoStatusValue"]:
                        loading_icon: bool = True

                        attempts = 0
                
                        while True:
                            with contextlib.suppress(TimeoutException):
                                waitt(bot, .1).until(EC.invisibility_of_element_located(
                                    (By.XPATH, loading_icon_in_status_xpath)))
                                loading_icon = False
                            
                            try:
                                playing_status: WebElement = bot.find_element(By.XPATH, playing_bar_xpath)  # playing status
                                style_value = playing_status.get_attribute("style")  # Starts @ 100 reduces to 0
                            except NoSuchElementException:
                                paused_status: WebElement = bot.find_element(By.XPATH, paused_bar_xpath)  # paused status
                                style_value = paused_status.get_attribute("style")  # Starts @ 100 reduces to 0
                            finally:
                                try:
                                    video_progress = float(style_value.split("(")[1].split(")")[0][1:-1])
                                except (IndexError, ValueError): # Unable to get video progress
                                    continue
                                
                                # Try to detect if the video status is loaded. If not, try to load it.
                                try:
                                    waitt(bot, .5).until(EC.invisibility_of_element_located(
                                        (By.XPATH, loading_icon_in_status_xpath)))
                                    loading_icon = False
                                except(TimeoutException, NoSuchElementException):
                                    if loading_icon and (0 <= video_progress <= 30):
                                        handle_status_not_loaded(bot, total_status, viewed_status)
                                        attempts += 1
                                    if attempts >= 5:
                                        # Send to Self
                                        wa_bot.send_message(
                                            NUMBER, 
                                            f"Unable to load {status_uploader_name}'s video status.\
                                                Use a better internet i guess.", 
                                            reply_markup=Inline_list(
                                                "Show list",
                                                list_items=[
                                                    List_item("Nice one 👌"), 
                                                    List_item("Thanks ✨"), 
                                                    List_item("Great Job")
                                                ]
                                            )
                                        )
                                        sys.exit()   
                                    continue
                                                                
                                try: 
                                    click_pause()
                                except NoSuchElementException: 
                                    ...  # ALREADY PAUSED
                                msg = f"{status_idx}. Status is a Video."                            
                                tprint(msg)
                                statusTypeMsg += msg + '\n'
                                loading_icon = False
                                break
                except KeyError: 
                    try:
                        if check_status["txtStatusValue"]:
                            click_pause()
                            msg: str = f"{status_idx}. Status is a Text."
                            tprint(msg)
                            statusTypeMsg += msg + '\n'
                    except KeyError:
                        try:
                            if check_status["audioStatusValue"]:
                                msg: str = f"{status_idx}. Status is an Audio."
                                tprint(msg)
                                statusTypeMsg += msg + '\n'
                        except KeyError:
                            try: 
                                if check_status["old_messageValue"]:
                                    msg: str = f"{status_idx}. Status is an Old Whatsapp Version."
                                    tprint(msg)
                                    statusTypeMsg += msg + '\n'
                            except KeyError as e: 
                                tprint(f'Failed! -> {e}')
            finally:
                if status_idx != loop_range[-1]:
                    viewed_status += 1
                    check_status = None

                    # Click Next Status
                    bot.find_elements(By.XPATH, bars_xpath)[viewed_status].click()
                else: # Status view completed, Exit status
                    try:
                        bot.find_element(By.XPATH, status_exit_xpath).click()
                    except NoSuchElementException: # Status already exited
                        sleep(3)
                        with contextlib.suppress(NoSuchElementException): 
                            # Check if it has truely exited by confirming if the page is on 'contact_name' search page
                            # BUT WHAT IF IT HAS NOT? WHY SKIP DO THIS IN THE FIRST PLACE # TODO FIX THIS
                            bot.find_element(By.XPATH, f'//span[@title="{status_uploader_name}"]//span')
                            bot.find_element(By.XPATH, '//div[@title="Status"]').send_keys(Keys.ESCAPE) # TODO: Confirm what this does
                    tprint(block_line)
    
        # Send to Self
        wa_bot.send_message(
            NUMBER, 
            f"{statusTypeMsg}\n{status_uploader_name} at {gmtTime(timezone)}.",
            reply_markup=Inline_list(
                "Show list",
                list_items=[
                    List_item("Nice one 👌"), 
                    List_item("Thanks ✨"), 
                    List_item("Great Job")
                ]
            )
        )
        
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
    

    class BotManager:
        def __init__(self, driverpath: str) -> None:
            self.driverpath: str = driverpath
            self.driver = None
            self.service = None
            self.options = None
        
        def get_child_procs(self, parent_pid):
            """Get all child processes of a given parent process."""
            try:
                parent = psutil.Process(parent_pid)
                return parent.children(recursive=True)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return []
        
        def start_chrome(self):
            self.service = Service(executable_path=self.driverpath)
            self.options = Options()
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--no-first-run")
            self.options.add_argument('--disable-dev-shm-usage')
            # self.options.add_argument("--auto-open-devtools-for-tabs")
            self.options.add_argument('--disable-software-rasterizer')
            self.options.add_argument(fr'--profile-directory={bot_profile_name}')
            self.options.add_argument(fr'user-data-dir={bot_profile_user_data_dir}')
            self.options.add_experimental_option('useAutomationExtension', False)
            self.options.add_experimental_option(
                "excludeSwitches", ["enable-automation", 'enable-logging'])
            self.options.add_argument('--disable-blink-features=AutomationControlled')

            self.driver = webdriver.Chrome(service=self.service, options=self.options)

            chromedriver_pid = self.driver.service.process.pid # Get ChromeDriver process
            
            # Find the Chrome browser process spawned by ChromeDriver
            chrome_children = self.get_child_procs(chromedriver_pid)
            for proc in chrome_children:
                if 'chrome' in proc.name().lower():
                    self.chrome_process = proc
                    break
            
            atexit.register(self.cleanup) # Handle atexit cleanup
            signal.signal(signal.SIGINT, self.signal_handler)   # Handle Ctrl+C
            signal.signal(signal.SIGTERM, self.signal_handler)  # Handle termination request
            if platform.system() != 'Windows':  # On Linux or MacOS
                signal.signal(signal.SIGHUP, self.signal_handler) # Terminal closed

            return self.driver
        
        def cleanup(self):
            try:
                # # TAKES TIME TO QUIT AND DOESN'T QUIT DESPITE TAKING TIME
                # if self.driver: # First try to quit gracefully
                #     self.driver.quit() 
                
                # If we have the specific Chrome process, ensure it's terminated
                if self.chrome_process:
                    with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                        # Get all child processes before terminating
                        children = self.chrome_process.children(recursive=True)
                        
                        # Terminate child processes
                        for child in children:
                            try:
                                child.terminate()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                        
                        # Terminate the main Chrome process
                        self.chrome_process.terminate()
                        
                        # Wait for processes to terminate
                        _, alive = psutil.wait_procs([self.chrome_process, *children], timeout=3)
                        
                        # Force kill any remaining processes
                        for p in alive:
                            # Handled this same error here again to avoid continuing execution outside the if block and to the except block 
                            with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                                p.kill()
                        
                        atexit.unregister(self.cleanup) # Unregister atexit cleanup handler since cleanup was successful
            except Exception as e:
                print(f"Error during cleanup: {e}")
            finally:
                self.driver = None
                self.chrome_process = None

        def signal_handler(self, signum, frame):
            self.cleanup()
            # Without exiting, the program will continue to run
            # Which will move execution to the KeyboardInterrupt block
            sys.exit(1)

    bot_manager = BotManager(driverpath)

    try:
        bot: WebDriver = bot_manager.start_chrome()
        wait60secs: WebDriverWait = waitt(bot, 60)
        wait3secs: WebDriverWait = waitt(bot, 3)
        action: ActionChains = ActionChains(bot)
        bot.set_window_size(700, 730)
        bot.set_window_position(676, 0)
        wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)
        pyautogui.FAILSAFE = False
        pyautogui.press('esc')

        # Shared stop signal for all threads
        stop_event = threading.Event()

        if answer in ["Y", "YES"]: getNotified()
        elif answer in ["N", "NO"]: autoViewStatus()
    except KeyboardInterrupt as e:
        print("Keyboard Interrupt")
    except (NoSuchWindowException, WebDriverException, ProtocolError) as e:
        print("Webdriver Chrome Browser Closed!")
    finally:
        print("Program ended!")
