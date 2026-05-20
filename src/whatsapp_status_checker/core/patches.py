"""
Centralized Monkey-Patches for WhatsApp Status Checker and CamouChat Framework.

This module houses all monkey-patches for WapiWrapper, WapiSession, BrowserForge,
camoufox, LoggerFactory, and Login classes. Call apply_all_patches() to bind all hooks.
"""

import os
import time
import asyncio
import logging
from typing import Any
from camouchat_core import LoggerFactory
from dotenv import load_dotenv
from ..config import SCREEN_WIDTH as _RAW_SCREEN_WIDTH, SCREEN_HEIGHT as _RAW_SCREEN_HEIGHT


try:
    if _RAW_SCREEN_WIDTH:
        _clean_width = _RAW_SCREEN_WIDTH.split('#')[0].strip()
        SCREEN_WIDTH = int(_clean_width) if _clean_width else None
    else:
        SCREEN_WIDTH = None
except ValueError:
    SCREEN_WIDTH = None

try:
    if _RAW_SCREEN_HEIGHT:
        _clean_height = _RAW_SCREEN_HEIGHT.split('#')[0].strip()
        SCREEN_HEIGHT = int(_clean_height) if _clean_height else None
    else:
        SCREEN_HEIGHT = None
except ValueError:
    SCREEN_HEIGHT = None

load_dotenv()

# We retrieve a direct system logger for the patches module itself
logger = LoggerFactory.get_logger(name="status_checker.patches", platform="WHATSAPP")


# =========================================================================
# 1. Logging Patches (Sleek CLI colorization & noise filtering)
# =========================================================================

class ConsoleNoiseFilter(logging.Filter):
    """Filter out excessive framework integration noise from the console."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        suppress_keywords = [
            "WapiSession initialized",
            "WapiSession starting",
            "Injecting WPP engine",
            "window.WPP annihilated",
            "Stealth DOM Bridge active",
            "MessageApiManager",
            "WapiSession is ready",
            "Wapi bridge started",
            "Resolving JID",
            "Target resolved:"
        ]
        for kw in suppress_keywords:
            if kw in msg:
                return False
        return True


class FriendlyFormatter(logging.Formatter):
    """Sleek, user-friendly formatter for CLI display."""
    
    def __init__(self, use_color: bool = True):
        super().__init__()
        self.use_color = use_color
        self.COLORS = {
            "DEBUG": "\033[36m",      # Cyan
            "INFO": "\033[32m",       # Green
            "WARNING": "\033[33m",    # Yellow
            "ERROR": "\033[31m",      # Red
            "CRITICAL": "\033[41m\033[37m", # White on Red
            "RESET": "\033[0m"
        }

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        msg = record.getMessage()
        
        # Translate framework logs to be extremely user-friendly
        if "Skiping, profile exists" in msg:
            msg = "Using existing browser profile: status_checker"
        elif "No locale provided" in msg:
            msg = "Headless browser initialized (locale: en-US)"
        elif "No proxy provided" in msg:
            msg = "Connecting directly to network (no proxy)"
        elif "Waiting for QR scan" in msg:
            msg = "Please scan the QR code to log in..."
        elif "WhatsApp login session stored" in msg:
            msg = "Session loaded successfully!"
        elif "Initializing Wapi Session" in msg:
            msg = "Initializing secure connection to WhatsApp..."
        elif "Real-time listeners:" in msg:
            msg = "Real-time status listeners bound."
        elif "Waiting for WhatsApp Web" in msg:
            msg = "Waiting for WhatsApp Web connection..."
        elif "WhatsApp Web is fully ready" in msg:
            msg = "WhatsApp connection established."
        elif "Warming up session" in msg:
            msg = "Syncing in-memory status database..."
        elif "Waking up status store" in msg:
            msg = "Ready to receive status updates."
        elif "Bridge timeout (30s)" in msg or "Main World did not respond" in msg:
            msg = "Browser connection temporarily unresponsive. Retrying sync..."
        
        if "Mode resolved from environment: Auto-View Mode" in msg:
            if self.use_color:
                msg = "Mode resolved from environment: \033[1;36m⚡ Auto-View Mode\033[22;32m"
            else:
                msg = "Mode resolved from environment: [Auto-View Mode]"
        elif "Mode resolved from environment: Notification Mode" in msg:
            if self.use_color:
                msg = msg.replace("Notification Mode", "\033[1;33m🔔 Notification Mode\033[22;32m")
            else:
                msg = msg.replace("Notification Mode", "[Notification Mode]")
        
        # Customize message prefix/icon based on level
        if level == "INFO":
            prefix = "• "
        elif level == "WARNING":
            prefix = "• [WARN] "
        elif level == "ERROR":
            prefix = "• [ERROR] "
        elif level == "CRITICAL":
            prefix = "• [FATAL] "
        else:
            prefix = ""
            
        color_start = self.COLORS.get(level, "") if self.use_color else ""
        color_end = self.COLORS.get("RESET", "") if self.use_color else ""
        
        return f"{color_start}{prefix}{msg}{color_end}"


def _apply_logging_patches():
    """Apply the custom logging formats and filters to LoggerFactory."""
    _orig_setup = LoggerFactory._setup_root_handlers

    @classmethod
    def _patched_setup(cls, log_file=None):
        _orig_setup(log_file)
        if "console" in cls._handlers:
            console_handler = cls._handlers["console"]
            console_handler.setFormatter(FriendlyFormatter())
            console_handler.addFilter(ConsoleNoiseFilter())

    LoggerFactory._setup_root_handlers = _patched_setup

    # Immediately apply to already initialized console handlers
    if hasattr(LoggerFactory, "_handlers") and "console" in LoggerFactory._handlers:
        console_handler = LoggerFactory._handlers["console"]
        console_handler.setFormatter(FriendlyFormatter())
        console_handler.addFilter(ConsoleNoiseFilter())


# =========================================================================
# 2. Login QR Code Patches (Terminal-based headless QR scanner)
# =========================================================================

async def patched_qr_login(self, wait_time: int) -> bool:
    """Custom QR login handler that renders QR code in the terminal using qrcode library."""
    self.log.info("Logging into WhatsApp...")
    
    last_ref = None
    printed_height = 0
    start_time = time.time()
    
    while time.time() - start_time < (wait_time / 1000.0):
        # 1. Check if chat list is visible (login successful)
        chats = self.ui_config.chat_list()
        if await chats.count() > 0 and await chats.first.is_visible():
            if last_ref is not None and printed_height > 0:
                import sys
                # Move cursor up and clear all text below it to erase the QR code block precisely
                sys.stdout.write(f"\033[{printed_height}A\033[J")
                sys.stdout.flush()
            self.log.info("WhatsApp login session restored successfully.")
            return True
            
        # 2. Check if QR code is visible
        qr_canvas = self.ui_config.qr_canvas()
        if await qr_canvas.count() > 0:
            qr_el = qr_canvas.locator("xpath=./ancestor-or-self::*[@data-ref]").first
            ref = await qr_el.get_attribute("data-ref")
            if ref and ref != last_ref:
                if last_ref is not None and printed_height > 0:
                    import sys
                    # Erase the previously printed QR code block before rendering the new one precisely
                    sys.stdout.write(f"\033[{printed_height}A\033[J")
                    sys.stdout.flush()
                last_ref = ref
                self.log.info("Scan this QR code in your WhatsApp app to log in:")
                try:
                    import qrcode
                    import math
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        border=2
                    )
                    qr.add_data(ref)
                    qr.make(fit=True)
                    qr.print_ascii()
                    
                    # Store printed height: math.ceil(matrix_size / 2.0) + 2 for print_ascii + 1 for message
                    printed_height = math.ceil(len(qr.modules) / 2.0) + 3
                except ImportError:
                    self.log.warning("qrcode library not installed. Install it using 'pip install qrcode'.")
                    self.log.info(f"Raw QR Ref: {ref}")
                    printed_height = 2  # Standard 2 lines fallback
                    
        await asyncio.sleep(2)
        
    raise Exception("QR login timeout.")


def _apply_qr_patches():
    """Apply the custom QR login patch to camouchat_whatsapp.Login."""
    from camouchat_whatsapp import Login
    Login._Login__qr_login = patched_qr_login


# =========================================================================
# 3. WhatsApp Stealth API and Window Sizing Patches
# =========================================================================

async def patched_status_get(self, contact_id: str) -> Any:
    """Patched status_get using the correct WhatsApp Web API."""
    js_code = f"""
        (async () => {{
            try {{
                if (!wpp || !wpp.status || typeof wpp.status.get !== 'function') {{
                    return [];
                }}
                
                const statusObj = await Promise.race([
                    wpp.status.get('{contact_id}'),
                    new Promise((_, reject) => setTimeout(() => reject(new Error('get timeout')), 15000))
                ]);
                
                if (!statusObj || !statusObj.msgs) {{
                    return [];
                }}
                
                const msgs = statusObj.msgs._models || [];
                
                return msgs.map(m => ({{
                    id_serialized: m.id?._serialized || 'unknown',
                    id_id: m.id?.id || 'unknown',
                    id_participant: m.id?.participant?._serialized || '',
                    id_remote: m.id?.remote?._serialized || 'status@broadcast',
                    isViewed: m.isViewed === true || m.isPlayed === true,
                    author: m.author?._serialized || m.from?._serialized || '',
                    t: m.t || Date.now(),
                    mediaType: m.type || 'unknown',
                    mimeType: m.mimetype || (m.mediaKey ? 'media' : 'text')
                }}));
            }} catch (e) {{
                return [];
            }}
        }})()
    """
    data = await self._evaluate_stealth(js_code)
    return data or []


async def patched_status_send_read(self, participant_jid: str, msg_id: str = "") -> Any:
    """Patched status_send_read using correct WPP APIs."""
    js_code = f"""
        (async () => {{
            try {{
                if (!wpp || !wpp.status) {{
                    throw new Error('wpp.status not available');
                }}
                
                const collection = await wpp.status.get('{participant_jid}');
                if (!collection || !collection.msgs) {{
                    throw new Error('No status collection found');
                }}
                
                const msgs = collection.msgs._models || [];
                if (msgs.length === 0) {{
                    throw new Error('No messages in collection');
                }}
                
                let msgObj = msgs[0];
                if ('{msg_id}') {{
                    const found = msgs.find(m => m.id?.id === '{msg_id}' || m.id?._serialized === '{msg_id}');
                    if (found) msgObj = found;
                }}
                
                if (!msgObj || !msgObj.id || !msgObj.id._serialized) {{
                    throw new Error('Status message object not found');
                }}
                
                msgObj.isViewed = true;
                msgObj.isPlayed = true;
                if (typeof msgObj.set === 'function') {{
                    msgObj.set('isViewed', true);
                    msgObj.set('isPlayed', true);
                }}
                
                const timestamp = msgObj.mediaKeyTimestamp || msgObj.t;
                let methodUsed = 'collection.sendReadStatus';
                
                try {{
                    await Promise.race([
                        collection.sendReadStatus(msgObj, timestamp),
                        new Promise((resolve) => setTimeout(resolve, 4000))
                    ]);
                }} catch (err) {{
                    if (typeof wpp.status.sendReadStatus === 'function') {{
                        try {{
                            await Promise.race([
                                wpp.status.sendReadStatus('{participant_jid}', msgObj.id._serialized),
                                new Promise((resolve) => setTimeout(resolve, 4000))
                            ]);
                            methodUsed = 'wpp.status.sendReadStatus';
                        }} catch (e) {{
                            methodUsed = 'failed';
                        }}
                    }} else {{
                        methodUsed = 'failed';
                    }}
                }}
                
                return {{ 
                    success: true, 
                    method: methodUsed, 
                    ack: msgObj.ack,
                    msg_id: msgObj.id?._serialized,
                    msg_participant: msgObj.id?.participant?._serialized || msgObj.author?._serialized,
                    passed_jid: '{participant_jid}'
                }};
            }} catch (e) {{
                return {{ success: false, error: e.message }};
            }}
        }})()
    """
    result = await self._evaluate_stealth(js_code)
    if isinstance(result, dict) and not result.get('success'):
        raise Exception(f"[status_send_read] {result.get('error', 'Unknown error')}")
    return result


original_wapi_session_start = None

async def patched_wapi_session_start(self, *args, **kwargs) -> Any:
    """Patched WapiSession.start to inject real-time WhatsApp listeners."""
    global original_wapi_session_start
    res = await original_wapi_session_start(self, *args, **kwargs)

    try:
        js_code = """
            (async () => {
                if (!wpp || !wpp.whatsapp) {
                    console.warn('[StatusChecker] wpp.whatsapp not available for listener injection');
                    return 'no_wpp';
                }
                
                const handleNewStatus = (model) => {
                    try {
                        const jid = model.id?._serialized 
                            || model.id?.participant?._serialized 
                            || model.from?._serialized;
                        
                        if (jid) {
                            console.log('[StatusCheckerEvent]: ' + jid);
                        }
                    } catch (e) {
                        console.warn('[StatusChecker] handleNewStatus error:', e.message);
                    }
                };
                
                let bound = 0;
                
                if (wpp.whatsapp.StatusV3Store) {
                    if (window.__statusStoreAddHandler) {
                        wpp.whatsapp.StatusV3Store.off('add', window.__statusStoreAddHandler);
                    }
                    if (window.__statusStoreChangeHandler) {
                        wpp.whatsapp.StatusV3Store.off('change', window.__statusStoreChangeHandler);
                    }
                    
                    window.__statusStoreAddHandler = handleNewStatus;
                    window.__statusStoreChangeHandler = handleNewStatus;
                    
                    wpp.whatsapp.StatusV3Store.on('add', window.__statusStoreAddHandler);
                    wpp.whatsapp.StatusV3Store.on('change', window.__statusStoreChangeHandler);
                    bound++;
                }
                
                if (wpp.whatsapp.MsgStore) {
                    if (window.__statusMsgStoreHandler) {
                        wpp.whatsapp.MsgStore.off('add', window.__statusMsgStoreHandler);
                    }
                    
                    window.__statusMsgStoreHandler = (msg) => {
                        try {
                            const remote = msg.id?.remote?._serialized || msg.id?.remote;
                            if (remote === 'status@broadcast') {
                                const author = msg.author?._serialized || msg.from?._serialized;
                                if (author) {
                                    console.log('[StatusCheckerEvent]: ' + author);
                                }
                            }
                        } catch (e) {}
                    };
                    
                    wpp.whatsapp.MsgStore.on('add', window.__statusMsgStoreHandler);
                    bound++;
                }
                
                console.log('[StatusChecker] Real-time listeners injected: ' + bound + ' store(s) bound');
                return 'listeners_bound_' + bound;
            })()
        """
        if hasattr(self, 'bridge') and self.bridge:
            result = await self.bridge._evaluate_stealth(js_code)
            logger.info(f"Real-time listeners: {result}")
        elif hasattr(self, 'page') and self.page:
            logger.warning("Bridge not available, cannot inject Main World listeners")
    except Exception as e:
        logger.error(f"Failed to inject real-time listeners: {e}")
        
    return res


original_get_screen_size = None

def patched_get_screen_size() -> tuple[int, int]:
    """Return custom screen dimensions from env vars SCREEN_WIDTH / SCREEN_HEIGHT."""
    if SCREEN_WIDTH and SCREEN_HEIGHT:
        if SCREEN_WIDTH > 0 and SCREEN_HEIGHT > 0:
            return SCREEN_WIDTH, SCREEN_HEIGHT
    if original_get_screen_size:
        try:
            return original_get_screen_size()
        except Exception:
            pass
    return 800, 800


def _apply_stealth_patches():
    """Apply all monkey-patches to WapiWrapper, BrowserForge, and camoufox."""
    global original_get_screen_size, original_wapi_session_start
    from camouchat_whatsapp.api.wa_js.wajs_wrapper import WapiWrapper
    
    if not hasattr(WapiWrapper.status_get, '_patched'):
        WapiWrapper.status_get = patched_status_get
        patched_status_get._patched = True
    
    if not hasattr(WapiWrapper.status_send_read, '_patched'):
        WapiWrapper.status_send_read = patched_status_send_read
        patched_status_send_read._patched = True
        
    from camouchat_browser.browserforge import BrowserForge
    
    if not hasattr(BrowserForge.get_screen_size, '_patched'):
        original_get_screen_size = BrowserForge.get_screen_size
        BrowserForge.get_screen_size = staticmethod(patched_get_screen_size)
        patched_get_screen_size._patched = True

    if not hasattr(BrowserForge.__gen_fg__, '_patched'):
        def patched_gen_fg(self, avoid=None) -> Any:
            from browserforge.fingerprints import FingerprintGenerator
            from browserforge.headers import Browser
            gen = FingerprintGenerator(
                browser=[Browser(name='firefox', min_version=120)],
                os=('macos', 'windows'),
                device='desktop'
            )
            return gen.generate()
            
        BrowserForge.__gen_fg__ = patched_gen_fg
        patched_gen_fg._patched = True

    if not hasattr(BrowserForge.get_fg, '_patched'):
        original_get_fg = BrowserForge.get_fg
        
        def patched_get_fg(self, profile) -> Any:
            fg = original_get_fg(self, profile)
            if SCREEN_WIDTH and SCREEN_HEIGHT:
                w, h = SCREEN_WIDTH, SCREEN_HEIGHT
                if w > 0 and h > 0:
                    if hasattr(fg, "screen") and fg.screen:
                        # Realistic proportions for a desktop browser
                        # Inner width/height must be smaller than outer to pass anti-bot checks
                        chrome_width = 16  # 8px left and right border
                        chrome_height = 88  # title bar + address bar + bookmarks bar
                        
                        fg.screen.width = w
                        fg.screen.height = h
                        fg.screen.availWidth = w
                        fg.screen.availHeight = h - 40  # typical taskbar height
                        fg.screen.outerWidth = w
                        fg.screen.outerHeight = h
                        fg.screen.innerWidth = w - chrome_width
                        fg.screen.innerHeight = h - chrome_height
                        fg.screen.clientWidth = w - chrome_width
                        fg.screen.clientHeight = h - chrome_height
            return fg
            
        BrowserForge.get_fg = patched_get_fg
        patched_get_fg._patched = True


    from camouchat_whatsapp import WapiSession
    if not hasattr(WapiSession.start, '_patched'):
        original_wapi_session_start = WapiSession.start
        WapiSession.start = patched_wapi_session_start
        patched_wapi_session_start._patched = True


# =========================================================================
# 4. Entry Point to Apply All Patches
# =========================================================================

def apply_all_patches() -> bool:
    """Apply all monkey-patches dynamically across the application ecosystem."""
    try:
        _apply_logging_patches()
        _apply_qr_patches()
        _apply_stealth_patches()
        return True
    except Exception as e:
        logger.error(f"Failed to bind monkey patches: {e}")
        return False
