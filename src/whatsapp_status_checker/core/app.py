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
        self.active_mode = None
        self._last_realtime_action: float = 0  # Timestamp of last real-time event handled
        self._health_interval = int(os.getenv("HEALTH_CHECK_MINUTES", "15")) * 60

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
        
        # Route browser console messages to our terminal and intercept custom bridge events
        self.page.on("console", self._handle_browser_console)
        
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

    # ── Real-time event path ───────────────────────────────────────────

    def _handle_browser_console(self, msg):
        """Intercepts specific console logs from the Main World as a bridge for real-time events."""
        text = msg.text
            
        if text.startswith("[StatusCheckerEvent]:"):
            try:
                jid = text.split(":", 1)[1].strip()
                # Run the async callback without blocking the Playwright event loop
                asyncio.create_task(self._handle_realtime_status_event(jid))
            except Exception as e:
                pass

    async def _handle_realtime_status_event(self, jid: str):
        """Python callback fired by JS when WhatsApp's native WebSocket pushes a status update"""
        # Debounce: WhatsApp fires multiple events (add, change) across multiple stores 
        # for a single status. We only need to process once every few seconds.
        now = time.time()
        if hasattr(self, '_last_realtime_trigger') and now - self._last_realtime_trigger < 5:
            return
        self._last_realtime_trigger = now

        if not self.uploader_jid:
            return
        
        # Compare phone-number prefix to support both @c.us and @lid JIDs
        incoming_prefix = jid.split('@')[0]
        expected_prefix = self.uploader_jid.split('@')[0]
        
        if incoming_prefix != expected_prefix:
            return

        print(f"✨ Status update detected from {self.status_uploader_name}...")
        self._last_realtime_action = now
        await self._process_statuses()

    # ── Unified status processing (used by both real-time and health loop) ─

    async def _process_statuses(self):
        """Fetch unviewed statuses and act on them based on active mode"""
        if getattr(self, '_processing_lock', False):
            return
        self._processing_lock = True
        try:
            if not self.uploader_jid:
                self.uploader_jid = await self._get_jid_by_name(self.status_uploader_name)

            unviewed = await self.check_status()
            if not unviewed:
                return

            timestamp = datetime.now().strftime("%H:%M:%S")

            if self.active_mode == "autoview":
                print(f"Watching {len(unviewed)} status(es)...")
                await self.ops.view_all_unviewed_statuses(self.uploader_jid, unviewed=unviewed)
                print(f"✅ Viewed {len(unviewed)} status update(s) from *{self.status_uploader_name}*\n📅 {timestamp}")
            elif self.active_mode == "notification":
                msg = f"🔔 *{self.status_uploader_name}* has {len(unviewed)} new status update(s)!\n📅 {timestamp}"
                # await self.send_notification(msg)
                print(msg)

        except Exception as e:
            print(f"Status processing error: {e}")
        finally:
            self._processing_lock = False

    # ── Health monitoring loop ────────────────────────────────────────

    async def _verify_listeners(self) -> bool:
        """Check if real-time JS listeners are still bound; re-inject if page reloaded"""
        try:
            if not hasattr(self.wapi, 'bridge') or not self.wapi.bridge:
                return False
                
            # Check for the Main World handler injected in patch_status_get.py
            alive = await self.wapi.bridge._evaluate_stealth("return typeof window.__statusStoreAddHandler === 'function'")
            if alive:
                return True

            # Listeners lost (page reload). Re-inject via wapi.start() which triggers our patch.
            print("⚠️ Listeners lost (page reload detected). Re-injecting...")
            await self.wapi.start()
            await asyncio.sleep(3)
            return await self.wapi.bridge._evaluate_stealth("return typeof window.__statusStoreAddHandler === 'function'")
        except Exception as e:
            print(f"Health check error: {e}")
            return False

    async def _health_loop(self):
        """
        Keepalive loop that serves three purposes:
        1. Keeps the asyncio event loop alive so real-time callbacks can fire
        2. Periodically verifies JS listeners are still bound (self-healing)
        3. Falls back to polling ONLY when real-time hasn't fired recently
        """
        print(f"Monitoring {self.status_uploader_name} (real-time active, health check every {self._health_interval // 60}m)...")

        # Initial catch-up for statuses posted while offline
        try:
            await self._process_statuses()
        except Exception as e:
            print(f"Initial catch-up failed: {e}")

        while True:
            try:
                await asyncio.sleep(self._health_interval)

                # 1. Verify listeners are alive
                listeners_ok = await self._verify_listeners()

                # 2. If real-time fired recently, listeners are working — skip polling
                seconds_since_last = time.time() - self._last_realtime_action
                if self._last_realtime_action > 0 and seconds_since_last < self._health_interval:
                    continue

                # 3. Real-time hasn't fired in a while — either no new statuses, 
                #    or listeners died silently. Poll once as reconciliation.
                if not listeners_ok:
                    print("⚠️ Real-time listeners unresponsive. Polling as fallback...")
                
                await self._process_statuses()

            except Exception as e:
                print(f"Health loop error: {e}")
                await asyncio.sleep(60)

    # ── Mode entry points ─────────────────────────────────────────────

    async def monitor_notifications(self, reminder_time_idx: int):
        """Notification Mode — real-time alerts, health-monitored"""
        self.active_mode = "notification"
        await self._health_loop()

    async def auto_view_status(self):
        """Auto-View Mode — real-time viewing, health-monitored"""
        self.active_mode = "autoview"
        await self._health_loop()

    # ── Lifecycle ─────────────────────────────────────────────────────

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
