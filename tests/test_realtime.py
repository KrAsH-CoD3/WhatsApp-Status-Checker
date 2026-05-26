"""
Tests for the real-time event-driven callback and integrations in WhatsAppStatusChecker.
"""

from unittest.mock import patch
import asyncio
import time

import pytest


# ═══════════════════════════════════════════════════════════════════════
# 1. REAL-TIME EVENT CALLBACK
# ═══════════════════════════════════════════════════════════════════════


class TestRealtimeEventCallback:
    """Tests for _handle_realtime_status_event"""

    @pytest.mark.asyncio
    async def test_ignores_event_when_no_uploader_jid(self, checker, mock_ops):
        """Should silently return if uploader_jid hasn't been resolved yet"""
        checker.uploader_jid = None
        checker.active_mode = "autoview"

        await checker._handle_realtime_status_event("9999999999@c.us")

        mock_ops.get_unviewed_statuses.assert_not_called()

    @pytest.mark.asyncio
    async def test_ignores_event_from_wrong_contact(self, checker, mock_ops):
        """Should not process events from contacts we're not monitoring"""
        checker.uploader_jid = "1234567890@c.us"
        checker.active_mode = "autoview"

        await checker._handle_realtime_status_event("9999999999@c.us")

        mock_ops.get_unviewed_statuses.assert_not_called()
        assert checker._last_realtime_action == 0  # unchanged

    @pytest.mark.asyncio
    async def test_matches_target_contact_c_us(self, checker, mock_ops):
        """Should trigger processing when target @c.us JID matches"""
        checker.uploader_jid = "1234567890@c.us"
        checker.active_mode = "autoview"
        mock_ops.get_unviewed_statuses.return_value = [{"id_id": "abc"}]

        await checker._handle_realtime_status_event("1234567890@c.us")

        assert checker._last_realtime_action > 0
        mock_ops.get_unviewed_statuses.assert_called_once()

    @pytest.mark.asyncio
    async def test_matches_cross_jid_types(self, checker, mock_ops):
        """Should match even when uploader is @c.us but event arrives as @lid"""
        checker.uploader_jid = "1234567890@c.us"
        checker.active_mode = "notification"
        mock_ops.get_unviewed_statuses.return_value = []

        await checker._handle_realtime_status_event("1234567890@lid")

        # Match is phone-number prefix, not full JID
        assert checker._last_realtime_action > 0

    @pytest.mark.asyncio
    async def test_stamps_last_realtime_action(self, checker, mock_ops):
        """Should update _last_realtime_action timestamp on match"""
        checker.uploader_jid = "1234567890@c.us"
        checker.active_mode = "autoview"
        mock_ops.get_unviewed_statuses.return_value = []

        before = time.time()
        await checker._handle_realtime_status_event("1234567890@c.us")
        after = time.time()

        assert before <= checker._last_realtime_action <= after


# ═══════════════════════════════════════════════════════════════════════
# 2. INTEGRATION — FULL REAL-TIME → PROCESS FLOW
# ═══════════════════════════════════════════════════════════════════════


class TestRealtimeIntegration:
    """End-to-end flow: event arrives → statuses fetched → action taken"""

    @pytest.mark.asyncio
    async def test_realtime_autoview_full_flow(self, checker, mock_ops):
        """
        Simulates: JS fires onStatusNewEvent → Python callback →
        fetch unviewed → view them all
        """
        checker.active_mode = "autoview"
        checker.uploader_jid = "1234567890@c.us"
        mock_ops.get_unviewed_statuses.return_value = [
            {"id_id": "status_1", "isViewed": False},
            {"id_id": "status_2", "isViewed": False},
            {"id_id": "status_3", "isViewed": False},
        ]

        await checker._handle_realtime_status_event("1234567890@c.us")

        # Verify the full chain executed
        assert checker._last_realtime_action > 0
        mock_ops.get_unviewed_statuses.assert_called_once()
        mock_ops.view_all_unviewed_statuses.assert_called_once()

    @pytest.mark.asyncio
    async def test_realtime_notification_full_flow(self, checker, mock_ops):
        """
        Simulates: JS fires onStatusNewEvent → Python callback →
        fetch unviewed → print notification (no viewing)
        """
        checker.active_mode = "notification"
        checker.uploader_jid = "1234567890@c.us"
        mock_ops.get_unviewed_statuses.return_value = [
            {"id_id": "status_1", "isViewed": False},
        ]

        with patch("whatsapp_status_checker.core.app.logger.info") as mock_log_info:
            await checker._handle_realtime_status_event("1234567890@c.us")

            assert checker._last_realtime_action > 0
            mock_ops.view_all_unviewed_statuses.assert_not_called()

            # Find the notification message in the logs
            log_messages = [call_args[0][0] for call_args in mock_log_info.call_args_list]
            notification = next((msg for msg in log_messages if "new status update" in msg), "")
            assert "TestContact" in notification
            assert "1 new status update" in notification

    @pytest.mark.asyncio
    async def test_realtime_deduplicates_health_loop(self, checker, mock_ops, mock_page):
        """
        After real-time fires, the next health loop iteration should
        skip polling because _last_realtime_action is recent.
        """
        checker._health_interval = 0.1
        checker.active_mode = "autoview"
        checker.uploader_jid = "1234567890@c.us"
        mock_page.evaluate.return_value = True

        # First: real-time event fires
        mock_ops.get_unviewed_statuses.return_value = [{"id_id": "s1"}]
        await checker._handle_realtime_status_event("1234567890@c.us")
        assert mock_ops.get_unviewed_statuses.call_count == 1

        # Reset call count and set timestamp into the future so dedup always holds
        mock_ops.get_unviewed_statuses.reset_mock()
        checker._last_realtime_action = time.time() + 10

        # Second: health loop runs — should skip because real-time is recent
        task = asyncio.create_task(checker._health_loop())
        await asyncio.sleep(0.3)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        # Should only have called once during initial catch-up, and skipped periodic polling
        assert mock_ops.get_unviewed_statuses.call_count == 1
