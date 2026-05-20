"""
Tests for checking status modes entry points in WhatsAppStatusChecker.
"""

import asyncio

import pytest


# ═══════════════════════════════════════════════════════════════════════
# 1. MODE ENTRY POINTS
# ═══════════════════════════════════════════════════════════════════════


class TestModeEntryPoints:
    """Tests for monitor_notifications and auto_view_status"""

    @pytest.mark.asyncio
    async def test_autoview_mode_sets_mode(self, checker):
        """auto_view_status should set active_mode to 'autoview'"""
        checker._health_interval = 0.05

        task = asyncio.create_task(checker.auto_view_status())
        await asyncio.sleep(0.1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert checker.active_mode == "autoview"

    @pytest.mark.asyncio
    async def test_notification_mode_sets_mode(self, checker):
        """monitor_notifications should set active_mode to 'notification'"""
        checker._health_interval = 0.05

        task = asyncio.create_task(checker.monitor_notifications(1))
        await asyncio.sleep(0.1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert checker.active_mode == "notification"
