"""
Shared test fixtures for WhatsApp Status Checker tests.

All external dependencies (CamouChat, Playwright, WhatsApp) are fully mocked.
These tests exercise application logic only — no browser or network required.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Mock all heavy external imports before any app code is loaded ──────

@pytest.fixture(autouse=True)
def _mock_external_imports(monkeypatch):
    """
    Patch all CamouChat / Playwright imports so tests never touch real browsers.
    autouse=True means every test gets this automatically.
    """
    # Create mock modules
    mock_browser = MagicMock()
    mock_core = MagicMock()
    mock_whatsapp = MagicMock()
    mock_art = MagicMock()
    mock_callmebot = MagicMock()
    mock_dotenv = MagicMock()

    modules = {
        "camouchat_browser": mock_browser,
        "camouchat_core": mock_core,
        "camouchat_whatsapp": mock_whatsapp,
        "camouchat_whatsapp.api": MagicMock(),
        "camouchat_whatsapp.api.wa_js": MagicMock(),
        "camouchat_whatsapp.api.wa_js.wajs_wrapper": MagicMock(),
        "art": mock_art,
        "callmebot": mock_callmebot,
        "dotenv": mock_dotenv,
    }
    for mod_name, mod in modules.items():
        monkeypatch.setitem(__import__("sys").modules, mod_name, mod)


@pytest.fixture
def mock_page():
    """A mock Playwright page with expose_function and evaluate"""
    page = AsyncMock()
    page.expose_function = AsyncMock()
    page.evaluate = AsyncMock(return_value=True)
    page.url = "https://web.whatsapp.com"
    return page


@pytest.fixture
def mock_wapi():
    """A mock WapiSession with bridge and start"""
    wapi = AsyncMock()
    wapi.bridge = AsyncMock()
    wapi.bridge.conn_is_main_ready = AsyncMock(return_value=True)
    wapi.bridge.status_get = AsyncMock(return_value=[])
    wapi.start = AsyncMock()
    wapi.chat_manager = AsyncMock()
    wapi.chat_manager.get_chat_list = AsyncMock(return_value=[])
    return wapi


@pytest.fixture
def mock_ops():
    """A mock WhatsAppOperations"""
    ops = AsyncMock()
    ops.get_unviewed_statuses = AsyncMock(return_value=[])
    ops.view_all_unviewed_statuses = AsyncMock(return_value=0)
    return ops


@pytest.fixture
def checker(mock_page, mock_wapi, mock_ops):
    """
    A WhatsAppStatusChecker instance with all external deps pre-wired.
    Ready to test application logic without any real browser.
    """
    # Avoid import-time side effects from patches
    with patch("whatsapp_status_checker.core.patches.apply_all_patches", return_value=True):
        from whatsapp_status_checker.core.app import WhatsAppStatusChecker

    instance = WhatsAppStatusChecker.__new__(WhatsAppStatusChecker)

    # Wire up state as if initialize() had already run
    instance.phone_number = "1234567890"
    instance.api_key = "test_key"
    instance.status_uploader_name = "TestContact"
    instance.profile = MagicMock()
    instance.browser = MagicMock()
    instance.page = mock_page
    instance.wapi = mock_wapi
    instance.interaction = AsyncMock()
    instance.uploader_jid = "1234567890@c.us"
    instance.notification_jid = "1234567890@c.us"
    instance.rate_limiter = MagicMock()
    instance.rate_limiter.wait = AsyncMock()
    instance.ops = mock_ops
    instance.active_mode = None
    instance._last_realtime_action = 0
    instance._health_interval = 5  # 5 seconds for fast tests
    instance.notified_status_ids = set()
    instance.reminder_time = 1
    instance._last_notification_time = 0.0

    return instance
