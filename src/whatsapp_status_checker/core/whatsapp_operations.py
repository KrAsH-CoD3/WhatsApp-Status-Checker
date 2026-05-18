"""
WhatsApp-specific operations and status detection logic using CamouChat
"""

import asyncio
import time
import random
import contextlib
from typing import Optional, Dict, List, Any
from camouchat_whatsapp import WapiSession, MediaController

class WhatsAppOperations:
    """Handles WhatsApp operations and status detection using camouchat-whatsapp"""
    
    def __init__(self, wapi: WapiSession, media_controller: Optional[MediaController] = None):
        self.wapi = wapi
        self.media_controller = media_controller
    
    async def get_status_info(self, uploader_jid: str) -> Dict[str, int]:
        """Get information about statuses (total, unviewed, viewed) with retry logic"""
        for attempt in range(3):
            try:
                # Ensure bridge is ready
                if not await self.wapi.bridge.conn_is_main_ready():
                    await asyncio.sleep(2)
                    continue

                statuses = await asyncio.wait_for(
                    self.wapi.bridge.status_get(uploader_jid),
                    timeout=35.0
                )
                
                if not statuses:
                    return {'total_status': 0, 'unviewed_status': 0, 'viewed_status': 0}
                    
                total_status = len(statuses)
                unviewed_status = len([s for s in statuses if isinstance(s, dict) and not s.get('isViewed')])
                viewed_status = total_status - unviewed_status
                
                return {
                    'total_status': total_status,
                    'unviewed_status': unviewed_status,
                    'viewed_status': viewed_status
                }
            except (asyncio.TimeoutError, Exception) as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    break
                await asyncio.sleep(2)
        
        return {'total_status': 0, 'unviewed_status': 0, 'viewed_status': 0}

    async def get_unviewed_statuses(self, uploader_jid: str) -> List[dict]:
        """Get list of unviewed status objects with retry logic, fallback, and page refresh"""
        for attempt in range(3):
            try:
                # Ensure bridge is ready
                if not await self.wapi.bridge.conn_is_main_ready():
                    print(f"Bridge not ready, waiting... (attempt {attempt + 1})")
                    await asyncio.sleep(5)
                    continue

                print(f"Fetching statuses for {uploader_jid}...")
                statuses = await asyncio.wait_for(
                    self.wapi.bridge.status_get(uploader_jid),
                    timeout=45.0
                )
                
                if statuses is not None:
                    unviewed = [s for s in statuses if isinstance(s, dict) and not s.get('isViewed')]
                    print(f"Successfully fetched {len(unviewed)} unviewed statuses.")
                    return unviewed
                    
            except Exception as e:
                err_msg = str(e).lower()
                print(f"Attempt {attempt + 1} failed: {e}")
                
                if "timeout" in err_msg or "bridge" in err_msg:
                    print("Bridge issue detected. Trying global fallback...")
                    try:
                        # Fallback: Fetch ALL statuses and filter manually
                        all_statuses = await asyncio.wait_for(
                            self.wapi.bridge.status_get("status@broadcast"),
                            timeout=45.0
                        )
                        if all_statuses:
                            unviewed = [
                                s for s in all_statuses 
                                if isinstance(s, dict) and 
                                (s.get('id', {}).get('remote') == uploader_jid or s.get('from') == uploader_jid) and
                                not s.get('isViewed')
                            ]
                            if unviewed:
                                print(f"Fallback successful: found {len(unviewed)} statuses in global list.")
                                return unviewed
                            else:
                                print("Fallback succeeded but no statuses found for this contact.")
                    except Exception as fallback_e:
                        print(f"Fallback fetch failed: {fallback_e}")
                
                if attempt == 1: # On second failure, try refreshing the bridge
                    print("Refreshing Wapi bridge...")
                    try:
                        await self.wapi.start()
                        await asyncio.sleep(5)
                    except:
                        pass
                
            await asyncio.sleep(3)
            
        print("Failed to fetch statuses after all attempts. Bridge might be stuck.")
        return []

    async def view_status(self, status_id: str, participant_jid: str = "") -> bool:
        """Mark a specific status as viewed"""
        try:
            # patched_status_send_read needs participant_jid and optionally msg_id
            await self.wapi.bridge.status_send_read(participant_jid, status_id)
            return True
        except Exception as e:
            print(f"Failed to view status {status_id}: {e}")
            return False

    async def view_all_unviewed_statuses(self, uploader_jid: str, unviewed: Optional[List[dict]] = None, humanize_delay: bool = True) -> int:
        """View all unviewed statuses for a contact and return count viewed.
        
        If unviewed list is provided, uses it directly (avoids double fetch).
        Otherwise fetches fresh.
        """
        if unviewed is None:
            unviewed = await self.get_unviewed_statuses(uploader_jid)
        
        count = 0
        
        for status in unviewed:
            sid = status.get('id_id') or status.get('id_serialized')
            participant = status.get('id_participant') or uploader_jid
            if sid:
                success = await self.view_status(sid, participant)
                if success:
                    count += 1
                if humanize_delay:
                    await asyncio.sleep(random.uniform(2.0, 5.0))
        
        return count

    async def check_status_type(self, status_obj: dict) -> Dict[str, bool]:
        """Check what type of status is currently displayed"""
        # WA-JS status objects usually identify type natively
        msg_type = status_obj.get('type', '')
        mimetype = status_obj.get('mimetype', '')
        
        return {
            "videoStatusValue": msg_type == 'video' or 'video' in mimetype,
            "imgStatusValue": msg_type == 'image' or 'image' in mimetype,
            "txtStatusValue": msg_type == 'chat' or msg_type == 'ciphertext' or 'text' in mimetype,
            "audioStatusValue": msg_type == 'audio' or msg_type == 'ptt' or 'audio' in mimetype,
            "old_messageValue": False
        }

    async def download_status_media(self, status_msg: Any) -> Optional[str]:
        """Download media from a status if available"""
        if not self.media_controller:
            print("MediaController not provided")
            return None
        
        try:
            path = await self.media_controller.save_media(message=status_msg)
            return path
        except Exception as e:
            print(f"Failed to download status media: {e}")
            return None
