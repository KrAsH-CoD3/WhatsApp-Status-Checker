"""
Monkey-patches for camouchat_whatsapp WapiWrapper to fix:
1. status_get - uses correct wpp.status.get() method  
2. status_send_read - uses correct collection.sendReadStatus(msgObj, mediaKeyTimestamp)
3. BrowserForge.get_screen_size - returns custom screen dimensions from .env

This module applies patches automatically when imported.
"""

import os
from typing import Any


from dotenv import load_dotenv
load_dotenv()


async def patched_status_get(self, contact_id: str) -> Any:
    """
    Patched status_get using the correct WhatsApp Web API.
    """
    
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
    """
    Patched status_send_read using the correct WPP API.
    
    Verified working:
    Uses wpp.status.sendReadStatus (the official WA-JS API) to mark status as read.
    This properly triggers the seen stanza and reports the view to the WhatsApp servers.
    """
    
    js_code = f"""
        (async () => {{
            try {{
                if (!wpp || !wpp.status) {{
                    throw new Error('wpp.status not available');
                }}
                
                // Get the status collection for this participant
                const collection = await wpp.status.get('{participant_jid}');
                if (!collection || !collection.msgs) {{
                    throw new Error('No status collection found');
                }}
                
                // Get the message object
                const msgs = collection.msgs._models || [];
                if (msgs.length === 0) {{
                    throw new Error('No messages in collection');
                }}
                
                // Find the specific message by ID or serialized ID if provided, otherwise use first
                let msgObj = msgs[0];
                if ('{msg_id}') {{
                    const found = msgs.find(m => m.id?.id === '{msg_id}' || m.id?._serialized === '{msg_id}');
                    if (found) msgObj = found;
                }}
                
                if (!msgObj || !msgObj.id || !msgObj.id._serialized) {{
                    throw new Error('Status message object not found');
                }}
                
                // Force local in-memory update FIRST so the model is marked as viewed when sending the read receipt
                msgObj.isViewed = true;
                msgObj.isPlayed = true;
                if (typeof msgObj.set === 'function') {{
                    msgObj.set('isViewed', true);
                    msgObj.set('isPlayed', true);
                }}
                
                // Use the correct timestamp: mediaKeyTimestamp for media statuses, message t (timestamp) for text statuses!
                // Passing undefined or missing timestamp is rejected by the server and won't show on the uploader's view list.
                const timestamp = msgObj.mediaKeyTimestamp || msgObj.t;
                let methodUsed = 'collection.sendReadStatus';
                
                try {{
                    // Primary: Direct internal collection method with accurate timestamp
                    await Promise.race([
                        collection.sendReadStatus(msgObj, timestamp),
                        new Promise((resolve) => setTimeout(resolve, 4000))
                    ]);
                }} catch (err) {{
                    // Fallback: Official sendReadStatus API wrapper
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
    """
    Patched WapiSession.start to automatically inject real-time WhatsApp status listeners
    whenever the bridge starts or restarts.
    
    CRITICAL: 
    Camoufox/Playwright strictly isolates execution contexts. page.expose_function()
    and postMessage() are intercepted or fail due to the heavy anti-bot sandbox.
    
    However, Playwright natively intercepts all console logs via CDP. We use
    console.log("[StatusCheckerEvent]: " + jid) as a 100% reliable cross-context bridge.
    """
    global original_wapi_session_start
    res = await original_wapi_session_start(self, *args, **kwargs)

    # Inject real-time status change listeners via stealth bridge (Main World)
    try:
        js_code = """
            (async () => {
                if (!wpp || !wpp.whatsapp) {
                    console.warn('[StatusChecker] wpp.whatsapp not available for listener injection');
                    return 'no_wpp';
                }
                
                // Handler: extract JID and log it to the console bridge
                const handleNewStatus = (model) => {
                    try {
                        const jid = model.id?._serialized 
                            || model.id?.participant?._serialized 
                            || model.from?._serialized;
                        
                        if (jid) {
                            // This is intercepted by Playwright's page.on("console") in app.py
                            console.log('[StatusCheckerEvent]: ' + jid);
                        }
                    } catch (e) {
                        console.warn('[StatusChecker] handleNewStatus error:', e.message);
                    }
                };
                
                let bound = 0;
                
                // 1. StatusV3Store
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
                
                // 2. MsgStore
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
            print(f"🔌 Real-time listeners: {result}")
        elif hasattr(self, 'page') and self.page:
            print("⚠️ Bridge not available, cannot inject Main World listeners")
    except Exception as e:
        print(f"Failed to inject real-time listeners: {e}")
        
    return res


original_get_screen_size = None

def patched_get_screen_size() -> tuple[int, int]:
    """
    Return custom screen dimensions from env vars SCREEN_WIDTH / SCREEN_HEIGHT.
    Falls back to original OS detection, then to 720x720 default.
    """
    env_w = os.getenv("SCREEN_WIDTH")
    env_h = os.getenv("SCREEN_HEIGHT")
    if env_w and env_h:
        try:
            w, h = int(env_w.strip()), int(env_h.strip())
            if w > 0 and h > 0:
                return w, h
        except ValueError:
            pass
    # Fallback to original OS-level detection
    if original_get_screen_size:
        try:
            return original_get_screen_size()
        except Exception:
            pass
    return 720, 720


# Apply patches automatically when imported
def _apply_patches():
    """Apply all monkey-patches to WapiWrapper, BrowserForge, and camoufox"""
    global original_get_screen_size
    try:
        from camouchat_whatsapp.api.wa_js.wajs_wrapper import WapiWrapper
        
        if not hasattr(WapiWrapper.status_get, '_patched'):
            WapiWrapper.status_get = patched_status_get
            patched_status_get._patched = True
        
        if not hasattr(WapiWrapper.status_send_read, '_patched'):
            WapiWrapper.status_send_read = patched_status_send_read
            patched_status_send_read._patched = True
            
        # Patch BrowserForge screen size detection
        from camouchat_browser.browserforge import BrowserForge
        
        if not hasattr(BrowserForge.get_screen_size, '_patched'):
            original_get_screen_size = BrowserForge.get_screen_size
            BrowserForge.get_screen_size = staticmethod(patched_get_screen_size)
            patched_get_screen_size._patched = True

        # Patch BrowserForge.__gen_fg__ to avoid long regeneration loops and warnings
        if not hasattr(BrowserForge.__gen_fg__, '_patched'):
            def patched_gen_fg(self, avoid=None) -> Any:
                from browserforge.fingerprints import FingerprintGenerator
                gen = FingerprintGenerator(browser='firefox', os=('linux', 'macos', 'windows'))
                return gen.generate()
                
            BrowserForge.__gen_fg__ = patched_gen_fg
            patched_gen_fg._patched = True

        # Patch BrowserForge get_fg to force matching fingerprint properties
        if not hasattr(BrowserForge.get_fg, '_patched'):
            original_get_fg = BrowserForge.get_fg
            
            def patched_get_fg(self, profile) -> Any:
                fg = original_get_fg(self, profile)
                env_w = os.getenv("SCREEN_WIDTH")
                env_h = os.getenv("SCREEN_HEIGHT")
                if env_w and env_h:
                    try:
                        w, h = int(env_w.strip()), int(env_h.strip())
                        if w > 0 and h > 0:
                            if hasattr(fg, "screen") and fg.screen:
                                fg.screen.width = w
                                fg.screen.height = h
                                fg.screen.availWidth = w
                                fg.screen.availHeight = h
                                fg.screen.innerWidth = w
                                fg.screen.innerHeight = h
                                fg.screen.outerWidth = w
                                fg.screen.outerHeight = h
                                fg.screen.clientWidth = w
                                fg.screen.clientHeight = h
                    except ValueError:
                        pass
                return fg
                
            BrowserForge.get_fg = patched_get_fg
            patched_get_fg._patched = True

        # Patch camoufox AsyncNewBrowser to force matching browser viewport/window size
        import camoufox.async_api
        if not hasattr(camoufox.async_api.AsyncNewBrowser, '_patched'):
            original_AsyncNewBrowser = camoufox.async_api.AsyncNewBrowser
            
            async def patched_AsyncNewBrowser(playwright, *args, **kwargs):
                env_w = os.getenv("SCREEN_WIDTH")
                env_h = os.getenv("SCREEN_HEIGHT")
                if env_w and env_h:
                    try:
                        w, h = int(env_w.strip()), int(env_h.strip())
                        if w > 0 and h > 0:
                            # Inject viewport into options passed to persistent context
                            kwargs["viewport"] = {"width": w, "height": h}
                    except ValueError:
                        pass
                return await original_AsyncNewBrowser(playwright, *args, **kwargs)
                
            camoufox.async_api.AsyncNewBrowser = patched_AsyncNewBrowser
            patched_AsyncNewBrowser._patched = True
            
        # Patch WapiSession.start to automatically inject real-time listeners
        from camouchat_whatsapp import WapiSession
        global original_wapi_session_start
        if not hasattr(WapiSession.start, '_patched'):
            original_wapi_session_start = WapiSession.start
            WapiSession.start = patched_wapi_session_start
            patched_wapi_session_start._patched = True
            
        return True
    except Exception as e:
        print(f"Failed to apply patches: {e}")
        return False

# Auto-apply on import
_apply_patches()
