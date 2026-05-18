"""
Modern WhatsApp Status Checker - Powered by CamouChat & wa-js
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Optional

from camouchat_browser import BrowserConfig, CamoufoxBrowser, ProfileManager
from camouchat_core import Platform
from camouchat_whatsapp import (
    Login,
    WapiSession,
    InteractionController,
    MediaController,
)

from .whatsapp_operations import WhatsAppOperations
from .patch_status_get import _apply_patches as apply_status_get_patch

from ..config import NUMBER, CALLMEBOT_APIKEY, STATUS_UPLOADER_NAME, TIMEZONE
from ..utils import get_time, calculate_next_reminder_time, initialize_timezone
from art import tprint, text2art


class RateLimiter:
    """Rate limiter to prevent spam"""
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.last_call: float = 0
    
    async def wait(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_call = time.time()


class WhatsAppStatusChecker:
    """Main application controller using CamouChat Bridge"""
    
    def __init__(self, 
        phone_number: Optional[str] = None,
        api_key: Optional[str] = None,
        status_uploader_name: Optional[str] = None,
        timezone: Optional[str] = None
    ):
        self.phone_number = phone_number or NUMBER
        self.api_key = api_key or CALLMEBOT_APIKEY
        self.status_uploader_name = status_uploader_name or STATUS_UPLOADER_NAME
        self.timezone = timezone or TIMEZONE
        
        self.profile = None
        self.browser = None
        self.page = None
        self.wapi: Optional[WapiSession] = None
        self.interaction: Optional[InteractionController] = None
        self.uploader_jid: Optional[str] = None
        self.notification_jid: Optional[str] = None
        self.rate_limiter = RateLimiter(min_interval=10.0)
        self.ops: Optional[WhatsAppOperations] = None

    async def initialize(self):
        """Initialize Camoufox and Wapi Bridge"""
        tprint("Initializing...", "small")
        
        # 1. Setup Profile & Browser
        pm = ProfileManager()
        self.profile = pm.create_profile(
            platform=Platform.WHATSAPP,
            profile_id="status_checker_testingprofile"
        )

        # Headless mode is more stable for background monitoring
        is_headless = os.getenv("HEADLESS", "true").lower() == "true"
        
        config = BrowserConfig.from_dict({
            "platform": Platform.WHATSAPP,
            "headless": is_headless,
        })

        self.browser = CamoufoxBrowser(config=config, profile=self.profile)
        self.page = await self.browser.get_page()

        # 2. Login Flow
        login = Login(page=self.page, profile=self.profile)
        # Use method=0 for QR scan (default in camouchat-whatsapp is 1/Code)
        await login.login(method=0)

        # 3. Start Wapi Session
        print("Initializing Wapi Session...")
        self.wapi = WapiSession(page=self.page)
        
        # Apply monkey-patch for status_get to fix bridge timeout
        apply_status_get_patch()
        
        try:
            print("Starting Wapi bridge (injecting wa-js)...")
            await asyncio.wait_for(self.wapi.start(), timeout=60)
            print("✅ Wapi bridge started.")
        except asyncio.TimeoutError:
            print("⚠️ Wapi start timed out. This often happens if the page reloaded. Retrying once...")
            await asyncio.sleep(2)
            await self.wapi.start()
        except Exception as e:
            print(f"⚠️ Wapi start error: {e}. Proceeding with caution.")

        print("Waiting for WhatsApp Web to be ready...")
        # Max wait 60s for readiness
        for _ in range(30):
            if await self.wapi.bridge.conn_is_main_ready():
                print("✅ WhatsApp Web is fully ready.")
                break
            await asyncio.sleep(2)
        else:
            print("⚠️ WhatsApp Web readiness check timed out. Some features may not work.")
        
        self.interaction = InteractionController(page=self.page, wapi=self.wapi)
        self.media = MediaController(page=self.page, wapi=self.wapi, profile=self.profile)
        self.ops = WhatsAppOperations(wapi=self.wapi, media_controller=self.media)

        # 3.5 Warm up the session
        print("Warming up session (waiting for data sync)...")
        await asyncio.sleep(15)
        
        try:
            # Force a click on the status tab to wake up the store
            print("Waking up status store...")
            await self.interaction.click_status_tab()
            await asyncio.sleep(5)
            # Click back to chats
            await self.interaction.click_chats_tab()
        except:
            pass

        # 4. Resolve JIDs
        if self.phone_number:
            clean_number = "".join(filter(str.isdigit, self.phone_number))
            self.notification_jid = f"{clean_number}@c.us"
        
        print(f"Resolving JID for {self.status_uploader_name}...")
        self.uploader_jid = await self._get_jid_by_name(self.status_uploader_name)
        
        if self.uploader_jid:
            print(f"✅ Target resolved: {self.uploader_jid}")
        else:
            print(f"⚠️ Could not resolve JID for {self.status_uploader_name}. Ensure you have an active chat with them.")

    async def _get_jid_by_name(self, name: str) -> Optional[str]:
        """Resolve name to JID using Chat and Contact stores, prioritizing @c.us"""
        try:
            potential_jids = []
            
            # 1. Check Chat Store
            chats = await self.wapi.chat_manager.get_chat_list(only_users=True)
            for chat in chats:
                if chat.name == name or chat.id_serialized.split('@')[0] == name:
                    potential_jids.append(chat.id_serialized)
            
            # 2. Check Contact Store
            contacts = await self.wapi.bridge.contact_list(count=500)
            for contact in contacts:
                if contact.get('name') == name or contact.get('pushname') == name:
                    jid = contact.get('id_serialized')
                    if jid:
                        potential_jids.append(jid)
            
            if not potential_jids:
                return None
            
            # Prioritize @c.us JIDs as they are more reliable for Status API
            c_us_jids = [j for j in potential_jids if j.endswith('@c.us')]
            if c_us_jids:
                return c_us_jids[0]
            
            # Fallback to whatever we found (e.g. @lid)
            return potential_jids[0]
            
        except Exception as e:
            print(f"Resolution error: {e}")
        return None

    def get_user_choice(self) -> tuple[str, Optional[int]]:
        """Rich terminal UI for mode selection"""
        tprint("Status Checker", "rectangles")
        print("\n[Y] Notification Mode - Get alerted when they post.")
        print("[N] Auto-View Mode - Automatically 'watch' their stories.")
        
        answer = "N" # Defaulting for now or input if interactive
        # answer = input("Choice: ").upper()
        
        reminder_time = 1 # 30 mins
        return answer, reminder_time

    async def check_status(self) -> list:
        if not self.ops or not self.uploader_jid:
            return []
        return await self.ops.get_unviewed_statuses(self.uploader_jid)

    async def send_notification(self, message: str):
        """Send notification via CallMeBot or Direct WhatsApp"""
        # 1. Attempt Direct WhatsApp Notification if possible
        if self.interaction and self.notification_jid:
            try:
                await self.rate_limiter.wait()
                await self.interaction.send_api_text(
                    chat_id=self.notification_jid,
                    text=message
                )
                return
            except Exception:
                pass
        
        # 2. Fallback to CallMeBot (Original behavior)
        try:
            from callmebot import send_message
            send_message(message, self.phone_number, self.api_key)
        except Exception as e:
            print(f"Notification error: {e}")

    async def monitor_notifications(self, reminder_time_idx: int):
        """Notification Mode loop"""
        interval_map = {1: 30, 2: 60, 3: 180, 4: 360}
        minutes = interval_map.get(reminder_time_idx, 30)
        
        print(f"Monitoring {self.status_uploader_name} (Notifications every {minutes}m)...")
        while True:
            try:
                unviewed = await self.check_status()
                if unviewed:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg = f"🔔 *{self.status_uploader_name}* has {len(unviewed)} new status update(s)!\n📅 {timestamp}"
                    # await self.send_notification(msg)
                    print(msg)
                
                await asyncio.sleep(minutes * 60)
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(60)

    async def auto_view_status(self):
        """Auto-View Mode loop"""
        print(f"Monitoring {self.status_uploader_name} (Auto-View)...")
        while True:
            try:
                if not self.uploader_jid:
                    self.uploader_jid = await self._get_jid_by_name(self.status_uploader_name)

                unviewed = await self.check_status()
                if unviewed:
                    print(f"Found {len(unviewed)} new status(es). Watching...")
                    await self.ops.view_all_unviewed_statuses(self.uploader_jid, unviewed=unviewed)
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg = f"✅ Viewed {len(unviewed)} new status update(s) from *{self.status_uploader_name}*\n📅 {timestamp}"
                    # await self.send_notification(msg)
                    print(msg)

                await asyncio.sleep(60)
            except Exception as e:
                print(f"Auto-view error: {e}")
                await asyncio.sleep(60)

    async def run_async(self):
        """Async entry point"""
        try:
            await self.initialize()
            answer, reminder_time = self.get_user_choice()
            
            if answer in ["Y", "YES"]:
                await self.monitor_notifications(reminder_time)
            else:
                await self.auto_view_status()
        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            if self.browser:
                # Cleanup if needed
                pass

    def run(self):
        """Synchronous wrapper for entry points"""
        asyncio.run(self.run_async())
