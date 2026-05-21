"""
Tests for unified status processing in WhatsAppStatusChecker.
"""

from unittest.mock import AsyncMock, patch

import pytest


# ═══════════════════════════════════════════════════════════════════════
# 1. UNIFIED STATUS PROCESSING
# ═══════════════════════════════════════════════════════════════════════


class TestProcessStatuses:
    """Tests for _process_statuses"""

    @pytest.mark.asyncio
    async def test_autoview_mode_views_statuses(self, checker, mock_ops):
        """In autoview mode, should fetch and view all unviewed statuses"""
        checker.active_mode = "autoview"
        mock_ops.get_unviewed_statuses.return_value = [
            {"id_id": "s1", "isViewed": False},
            {"id_id": "s2", "isViewed": False},
        ]

        await checker._process_statuses()

        mock_ops.get_unviewed_statuses.assert_called_once_with("1234567890@c.us", name="TestContact", prefix_logs=None)
        mock_ops.view_all_unviewed_statuses.assert_called_once()
        # Verify both statuses were passed
        call_args = mock_ops.view_all_unviewed_statuses.call_args
        assert len(call_args.kwargs.get("unviewed", call_args[1].get("unviewed", []))) == 2

    @pytest.mark.asyncio
    async def test_notification_mode_does_not_view(self, checker, mock_ops):
        """In notification mode, should NOT call view_all_unviewed_statuses"""
        checker.active_mode = "notification"
        mock_ops.get_unviewed_statuses.return_value = [
            {"id_id": "s1", "isViewed": False},
        ]

        await checker._process_statuses()

        mock_ops.get_unviewed_statuses.assert_called_once()
        mock_ops.view_all_unviewed_statuses.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_op_when_no_unviewed(self, checker, mock_ops):
        """Should do nothing when there are no unviewed statuses"""
        checker.active_mode = "autoview"
        mock_ops.get_unviewed_statuses.return_value = []

        await checker._process_statuses()

        mock_ops.view_all_unviewed_statuses.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolves_jid_if_missing(self, checker, mock_ops):
        """Should attempt JID resolution if uploader_jid is None"""
        checker.uploader_jid = None
        checker.active_mode = "autoview"
        mock_ops.get_unviewed_statuses.return_value = []

        with patch.object(checker, "_get_jid_by_name", new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = "5555555555@c.us"
            await checker._process_statuses()

        mock_resolve.assert_called_once_with("TestContact")

    @pytest.mark.asyncio
    async def test_handles_exception_gracefully(self, checker, mock_ops):
        """Should catch and print exceptions without crashing"""
        checker.active_mode = "autoview"
        mock_ops.get_unviewed_statuses.side_effect = Exception("bridge timeout")

        with patch("whatsapp_status_checker.core.app.logger.error") as mock_log_err:
            await checker._process_statuses()  # Should not raise
            mock_log_err.assert_called_once()
            assert "Status processing error" in mock_log_err.call_args[0][0]
