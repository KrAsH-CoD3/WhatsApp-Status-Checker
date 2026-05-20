from datetime import datetime
from typing import Optional
import asyncio
import time
import os

from camouchat_browser import BrowserConfig, CamoufoxBrowser, ProfileManager
from camouchat_core import Platform, LoggerFactory
from camouchat_whatsapp import (
    Login,
    WapiSession,
    InteractionController,
    MediaController,
)

from .whatsapp_operations import WhatsAppOperations
from .patches import apply_all_patches

# Apply all unified framework patches dynamically on startup
apply_all_patches()

from ..config import (
    NUMBER,
    CALLMEBOT_APIKEY,
    STATUS_UPLOADER_NAME,
    TIMEZONE,
    HEADLESS,
    AUTO_VIEW,
    REMINDER_TIME,
)
from ..utils import get_time, calculate_next_reminder_time, initialize_timezone
from art import tprint

logger = LoggerFactory.get_logger(name="status_checker", platform="WHATSAPP")


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
        self.notified_status_ids = set()
        self.reminder_time = 1
        self._last_notification_time = 0.0

    async def initialize(self):
        """Initialize Camoufox and Wapi Bridge"""
        
        
        # 1. Setup Profile & Browser
        pm = ProfileManager()
        self.profile = pm.create_profile(
            platform=Platform.WHATSAPP,
            profile_id="status_checker"
        )

        # Headless mode is more stable for background monitoring
        is_headless = (HEADLESS or "true").lower() == "true"
        
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
        # logger.info("Initializing Wapi Session...")
        self.wapi = WapiSession(page=self.page)
        
        
        try:
            # logger.info("Starting Wapi bridge (injecting wa-js)...")
            await asyncio.wait_for(self.wapi.start(), timeout=60)
            # logger.info("Wapi bridge started.")
        except asyncio.TimeoutError:
            await asyncio.wait_for(self.wapi.start(), timeout=60)
            # logger.info("Wapi bridge started.")
        except asyncio.TimeoutError:
            logger.warning("Wapi start timed out. This often happens if the page reloaded. Retrying once...")
            await asyncio.sleep(2)
            await self.wapi.start()
        except Exception as e:
            logger.error(f"Wapi start error: {e}. Proceeding with caution.")

        # logger.info("Waiting for WhatsApp Web to be ready...")
        # Max wait 60s for readiness
        for _ in range(30):
            if await self.wapi.bridge.conn_is_main_ready():
                # logger.info("WhatsApp Web is fully ready.")
                break
            await asyncio.sleep(2)
        else:
            logger.warning("WhatsApp Web readiness check timed out. Some features may not work.")
        
        self.interaction = InteractionController(page=self.page, wapi=self.wapi)
        self.media = MediaController(page=self.page, wapi=self.wapi, profile=self.profile)
        self.ops = WhatsAppOperations(wapi=self.wapi, media_controller=self.media)

        # 3.5 Warm up the session
        logger.info("Warming up session (waiting for data sync)...")
        await asyncio.sleep(15)
        
        try:
            # Force a click on the status tab to wake up the store
            logger.info("Waking up status store...")
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
        
        logger.info(f"Resolving JID for {self.status_uploader_name}...")
        self.uploader_jid = await self._get_jid_by_name(self.status_uploader_name)
        
        if self.uploader_jid:
            logger.info(f"Target resolved: {self.uploader_jid}")
        else:
            logger.warning(f"Could not resolve JID for {self.status_uploader_name}. Ensure you have an active chat with them.")

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
            logger.error(f"Resolution error: {e}")
        return None

    def get_user_choice(self) -> tuple[bool, Optional[int]]:
        """Determine running mode from environment or default"""
        auto_view_str = AUTO_VIEW
        auto_view = (auto_view_str or "true").lower() == "true"
        try:
            reminder_time = int(REMINDER_TIME) if REMINDER_TIME else 1
        except ValueError:
            reminder_time = 1
        
        if reminder_time not in [1, 2, 3, 4]:
            reminder_time = 1
            
        reminder_intervals = {
            1: "30 Minutes",
            2: "1 Hour",
            3: "3 Hours",
            4: "6 Hours"
        }
        
        if auto_view:
            logger.info("Mode resolved from environment: Auto-View Mode")
        else:
            logger.info(f"Mode resolved from environment: Notification Mode (Reminder Interval: {reminder_intervals.get(reminder_time)})")
            
        return auto_view, reminder_time

    async def check_status(self, prefix_logs: Optional[list[str]] = None) -> list:
        if not self.ops or not self.uploader_jid:
            return []
        return await self.ops.get_unviewed_statuses(self.uploader_jid, name=self.status_uploader_name, prefix_logs=prefix_logs)

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
            logger.error(f"Notification error: {e}")

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

        self._last_realtime_action = now
        prefix = [f"Status update detected from {self.status_uploader_name}..."]
        await self._process_statuses(prefix_logs=prefix)

    # ── Unified status processing (used by both real-time and health loop) ─

    async def _process_statuses(self, prefix_logs: Optional[list[str]] = None):
        """Fetch unviewed statuses and act on them based on active mode"""
        if getattr(self, '_processing_lock', False):
            return
        self._processing_lock = True
        try:
            if not self.uploader_jid:
                self.uploader_jid = await self._get_jid_by_name(self.status_uploader_name)

            unviewed = await self.check_status(prefix_logs=prefix_logs)
            if not unviewed:
                return

            # In notification mode, calculate if we should alert the user
            if self.active_mode == "notification":
                has_new_status = False
                for status in unviewed:
                    sid = status.get('id_id') or status.get('id_serialized') or status.get('id', {}).get('_serialized')
                    if sid and sid not in self.notified_status_ids:
                        has_new_status = True
                        self.notified_status_ids.add(sid)
                
                should_notify = has_new_status
                if not should_notify and unviewed:
                    now_perf = time.perf_counter()
                    last_time = getattr(self, '_last_notification_time', 0.0)
                    if last_time == 0.0:
                        should_notify = True
                    else:
                        new_time = calculate_next_reminder_time(now_perf - last_time, last_time, self.reminder_time)
                        if new_time != last_time:
                            should_notify = True
                
                if not should_notify:
                    return
                
                self._last_notification_time = time.perf_counter()

            unviewed_len = len(unviewed)
            timestamp = datetime.now().strftime("%H:%M:%S")

            if self.active_mode == "autoview":
                if unviewed_len == 1:
                    logger.info("Watching 1 status...")
                else:
                    logger.info(f"Watching {unviewed_len} statuses...")
                await self.ops.view_all_unviewed_statuses(self.uploader_jid, unviewed=unviewed, name=self.status_uploader_name)
                
                if unviewed_len == 1:
                    logger.info(f"Viewed 1 status update from *{self.status_uploader_name}* at {timestamp}")
                else:
                    logger.info(f"Viewed {unviewed_len} status updates from *{self.status_uploader_name}* at {timestamp}")
            elif self.active_mode == "notification":
                is_reminder = not has_new_status
                reminder_suffix = " (Reminder)" if is_reminder else ""
                
                if unviewed_len == 1:
                    msg = f"🔔 *{self.status_uploader_name}* has 1 new status update{reminder_suffix}!\n📅 {timestamp}"
                else:
                    msg = f"🔔 *{self.status_uploader_name}* has {unviewed_len} new status updates{reminder_suffix}!\n📅 {timestamp}"
                
                await self.send_notification(msg)
                logger.info(msg)

        except Exception as e:
            logger.error(f"Status processing error: {e}")
        finally:
            self._processing_lock = False

    # ── Health monitoring loop ────────────────────────────────────────

    async def is_online(self) -> bool:
        """Verify the page is connected and WhatsApp Web is loaded"""
        try:
            if not self.page:
                return False
            url = self.page.url
            if "web.whatsapp.com" not in url:
                return False
            online = await self.page.evaluate("navigator.onLine")
            return bool(online)
        except Exception:
            return False

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
            logger.warning("Listeners lost (page reload detected). Re-injecting...")
            await self.wapi.start()
            await asyncio.sleep(3)
            return await self.wapi.bridge._evaluate_stealth("return typeof window.__statusStoreAddHandler === 'function'")
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False

    async def _health_loop(self):
        """
        Keepalive loop that serves three purposes:
        1. Keeps the asyncio event loop alive so real-time callbacks can fire
        2. Periodically verifies JS listeners are still bound (self-healing)
        3. Falls back to polling ONLY when real-time hasn't fired recently
        """
        logger.info(f"Monitoring {self.status_uploader_name} (real-time active, health check every {self._health_interval // 60}m)...")

        # Initial catch-up for statuses posted while offline
        try:
            if await self.is_online():
                await self._process_statuses()
        except Exception as e:
            logger.error(f"Initial catch-up failed: {e}")

        while True:
            try:
                await asyncio.sleep(self._health_interval)

                if not await self.is_online():
                    logger.warning("Internet connection offline or browser disconnected. Waiting to reconnect...")
                    continue

                # 1. Verify listeners are alive
                listeners_ok = await self._verify_listeners()

                # 2. If real-time fired recently, listeners are working — skip polling
                seconds_since_last = time.time() - self._last_realtime_action
                if self._last_realtime_action > 0 and seconds_since_last < self._health_interval:
                    continue

                # 3. Real-time hasn't fired in a while — either no new statuses, 
                #    or listeners died silently. Poll once as reconciliation.
                if not listeners_ok:
                    logger.warning("Real-time listeners unresponsive. Polling as fallback...")
                
                await self._process_statuses()

            except Exception as e:
                logger.error(f"Health loop error: {e}")
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
        tprint("WhatsApp Status Checker", "rectangles")
        print("Active Modes:")
        print("• Auto-View Mode      - Automatically 'watch' their stories (Configure: AUTO_VIEW=True)")
        print("• Notification Mode   - Get alerted when they post          (Configure: AUTO_VIEW=False)\n")
        try:
            await self.initialize()
            auto_view, reminder_time = self.get_user_choice()
            
            if auto_view:
                await self.auto_view_status()
            else:
                await self.monitor_notifications(reminder_time)
        except KeyboardInterrupt:
            logger.info("Stopped by user.")
        finally:
            if self.browser and self.profile:
                logger.info("Cleaning up browser context...")
                try:
                    await self.browser.close_browser_by_profile(self.profile.profile_id)
                    logger.info("Browser cleanup completed.")
                except Exception as e:
                    logger.error(f"Error during browser cleanup: {e}")

    def run(self):
        """Synchronous wrapper for entry points"""
        asyncio.run(self.run_async())
