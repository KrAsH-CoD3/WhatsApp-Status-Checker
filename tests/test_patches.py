"""
Smoke test for the monkey-patch layer.

This one deliberately runs in a **fresh interpreter**: tests/conftest.py replaces
every camouchat module with a MagicMock, which makes patch registration
invisible (a MagicMock answers hasattr() for any name). That blind spot hid a
real regression — a bad registration guard raised AttributeError, aborted the
rest of _apply_stealth_patches(), and silently left the real-time listeners and
fingerprint overrides unbound while apply_all_patches() merely returned False,
which app.py ignores.
"""

import pathlib
import subprocess
import sys


_SRC = pathlib.Path(__file__).resolve().parents[1] / "src"

_SMOKE = """
import sys
sys.path.insert(0, {src!r})

from whatsapp_status_checker.core.patches import apply_all_patches
from camouchat_whatsapp.api.wa_js.wajs_wrapper import WapiWrapper
from camouchat_whatsapp import WapiSession, Login
from camouchat_browser.browserforge import BrowserForge

assert apply_all_patches() is True, "apply_all_patches() reported failure"

assert hasattr(WapiWrapper.status_get, "_patched")
assert hasattr(WapiWrapper.status_send_read, "_patched")
assert hasattr(WapiWrapper, "status_get_all"), "status_get_all was never bound"
assert hasattr(WapiSession.start, "_patched"), "real-time listeners not injected"
assert hasattr(BrowserForge.get_screen_size, "_patched")
assert hasattr(BrowserForge.get_fg, "_patched")
assert Login._Login__qr_login.__name__ == "patched_qr_login"

# A second call must stay a no-op rather than double-wrap anything.
assert apply_all_patches() is True
print("ok")
""".format(src=str(_SRC))


def test_patch_layer_binds_against_the_real_sdk():
    proc = subprocess.run(
        [sys.executable, "-c", _SMOKE],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "ok" in proc.stdout
