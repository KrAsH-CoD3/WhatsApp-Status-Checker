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

    @pytest.mark.asyncio
    async def test_notification_mode_stores_reminder_interval(self, checker):
        """The parsed REMINDER_TIME must reach the instance, not be discarded.

        _process_statuses gates the reminder cadence on self.reminder_time, so if
        this is dropped the interval stays pinned to the __init__ default of 1
        (30 min) no matter what REMINDER_TIME says.
        """
        checker._health_interval = 0.05
        checker.reminder_time = 1  # the __init__ default

        task = asyncio.create_task(checker.monitor_notifications(4))
        await asyncio.sleep(0.1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert checker.reminder_time == 4

    @pytest.mark.asyncio
    @pytest.mark.parametrize("interval", [1, 2, 3, 4])
    async def test_notification_mode_stores_each_interval(self, checker, interval):
        """Each valid REMINDER_TIME value must survive the hand-off"""
        checker._health_interval = 0.05

        task = asyncio.create_task(checker.monitor_notifications(interval))
        await asyncio.sleep(0.1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert checker.reminder_time == interval
