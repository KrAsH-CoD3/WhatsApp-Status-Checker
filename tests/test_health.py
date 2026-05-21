"""
Tests for health monitoring, listener verification, and smart fallback polling logic.
"""

from unittest.mock import AsyncMock, patch
import asyncio
import time

import pytest


# ═══════════════════════════════════════════════════════════════════════
# 1. HEALTH MONITORING — LISTENER VERIFICATION
# ═══════════════════════════════════════════════════════════════════════


class TestVerifyListeners:
    """Tests for _verify_listeners"""

    @pytest.mark.asyncio
    async def test_returns_true_when_listeners_alive(self, checker, mock_page, mock_wapi):
        """Should return True if handler exists in Main World"""
        mock_wapi.bridge = AsyncMock()
        mock_wapi.bridge._evaluate_stealth.return_value = True

        result = await checker._verify_listeners()

        assert result is True
        mock_wapi.bridge._evaluate_stealth.assert_called_once_with(
            "return typeof window.__statusStoreAddHandler === 'function'"
        )

    @pytest.mark.asyncio
    async def test_reinjects_when_listeners_lost(self, checker, mock_page, mock_wapi):
        """Should call wapi.start() to re-inject when listeners are gone"""
        mock_wapi.bridge = AsyncMock()
        # First call: listeners dead. Second call after re-injection: alive
        mock_wapi.bridge._evaluate_stealth.side_effect = [False, True]

        result = await checker._verify_listeners()

        assert result is True
        mock_wapi.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_false_when_reinject_fails(self, checker, mock_page, mock_wapi):
        """Should return False if re-injection also fails"""
        mock_wapi.bridge = AsyncMock()
        mock_wapi.bridge._evaluate_stealth.side_effect = [False, False]

        result = await checker._verify_listeners()

        assert result is False
        mock_wapi.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self, checker, mock_page, mock_wapi):
        """Should return False and not crash if evaluate throws"""
        mock_wapi.bridge = AsyncMock()
        mock_wapi.bridge._evaluate_stealth.side_effect = Exception("bridge crashed")

        result = await checker._verify_listeners()

        assert result is False


# ═══════════════════════════════════════════════════════════════════════
# 2. HEALTH LOOP — SMART FALLBACK LOGIC
# ═══════════════════════════════════════════════════════════════════════


class TestHealthLoop:
    """Tests for _health_loop decision logic"""

    @pytest.mark.asyncio
    async def test_skips_poll_when_realtime_recently_fired(self, checker, mock_ops, mock_page):
        """
        If real-time handled an event within the health interval,
        the health loop should skip polling entirely.
        """
        checker._health_interval = 0.1  # 100ms for fast test
        # Set timestamp slightly into the future so seconds_since_last is always
        # negative (always "recent") regardless of asyncio.sleep drift
        checker._last_realtime_action = time.time() + 10
        mock_page.evaluate.return_value = True  # listeners alive

        # Run one iteration then cancel
        loop_task = asyncio.create_task(checker._health_loop())
        await asyncio.sleep(0.3)  # let it run one cycle
        loop_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await loop_task

        # Should only have called once during initial catch-up, and skipped periodic polling (real-time was recent)
        assert mock_ops.get_unviewed_statuses.call_count == 1

    @pytest.mark.asyncio
    async def test_polls_when_realtime_stale(self, checker, mock_ops, mock_page):
        """
        If real-time hasn't fired recently (stale), health loop should
        fall back to polling.
        """
        checker._health_interval = 0.1
        checker._last_realtime_action = 0  # never fired
        checker.active_mode = "autoview"
        mock_page.evaluate.return_value = True
        mock_ops.get_unviewed_statuses.return_value = []

        loop_task = asyncio.create_task(checker._health_loop())
        await asyncio.sleep(0.3)
        loop_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await loop_task

        # Should have polled as fallback
        mock_ops.get_unviewed_statuses.assert_called()

    @pytest.mark.asyncio
    async def test_polls_when_listeners_dead_and_stale(self, checker, mock_ops, mock_page, mock_wapi):
        """
        When listeners are dead AND real-time is stale, should warn
        and poll as fallback.
        """
        checker._health_interval = 0.1
        checker._last_realtime_action = 0
        checker.active_mode = "autoview"
        mock_wapi.bridge = AsyncMock()
        mock_wapi.bridge._evaluate_stealth.return_value = False  # listeners dead, reinject also fails
        mock_ops.get_unviewed_statuses.return_value = []

        # Patch asyncio.sleep to resolve instantly — otherwise the 3s wait
        # inside _verify_listeners blocks the loop from reaching _process_statuses
        real_sleep = asyncio.sleep
        iterations = 0

        async def fast_sleep(duration):
            nonlocal iterations
            iterations += 1
            if iterations > 5:
                raise asyncio.CancelledError()
            await real_sleep(0.01)

        with patch("whatsapp_status_checker.core.app.logger.warning") as mock_log_warn:
            with patch("asyncio.sleep", side_effect=fast_sleep):
                loop_task = asyncio.create_task(checker._health_loop())
                await real_sleep(0.3)
                loop_task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await loop_task

            # _verify_listeners prints "Listeners lost" when it detects dead listeners
            warn_messages = [call_args[0][0].lower() for call_args in mock_log_warn.call_args_list]
            assert any("listeners lost" in msg or "unresponsive" in msg for msg in warn_messages)
        mock_ops.get_unviewed_statuses.assert_called()
