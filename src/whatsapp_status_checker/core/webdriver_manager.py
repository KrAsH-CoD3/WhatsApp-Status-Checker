"""
WebDriver management for Chrome browser automation
"""

from ..vars import bot_profile_name, bot_profile_user_data_dir
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import contextlib
import platform
import signal
import atexit
import psutil
import sys


class BotManager:
    """Manages Chrome WebDriver lifecycle with proper cleanup"""
    
    def __init__(self) -> None:
        self.driver = None
        self.service = None
        self.options = None
        self.chrome_process = None
    
    def get_child_procs(self, parent_pid):
        """Get all child processes of a given parent process."""
        try:
            parent = psutil.Process(parent_pid)
            return parent.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return []
    
    def start_chrome(self, driver_path: str) -> WebDriver:
        """Start Chrome browser with configured options"""
        self.service = Service(executable_path=driver_path)
        self.options = Options()
        
        # Configure Chrome options
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
        """Clean up Chrome processes and resources"""
        try:
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
        """Handle system signals for graceful shutdown"""
        self.cleanup()
        # Without exiting, the program will continue to run
        # Which will move execution to the KeyboardInterrupt block
        sys.exit(1)
