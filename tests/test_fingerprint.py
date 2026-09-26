"""
Guard for the fingerprint generator patch.

Runs in a fresh interpreter against the real browserforge/camouchat code, because
tests/conftest.py mocks every camouchat module.
"""

import pathlib
import subprocess
import sys


_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"


_SMOKE = """
import os, sys
os.environ["SCREEN_WIDTH"] = "1920"
os.environ["SCREEN_HEIGHT"] = "1080"
sys.path.insert(0, "__SRC__")

from whatsapp_status_checker.core.patches import apply_all_patches
assert apply_all_patches() is True

from browserforge.fingerprints import FingerprintGenerator
from browserforge.headers import Browser
from camouchat_browser.browserforge import BrowserForge

assert BrowserForge.get_screen_size() == (1920, 1080), BrowserForge.get_screen_size()
TARGET = (1920, 1080)

def deviation(fg):
    w, h = fg.screen.width, fg.screen.height
    return max(abs(w - TARGET[0]) / TARGET[0], abs(h - TARGET[1]) / TARGET[1])

control = FingerprintGenerator(
    browser=[Browser(name='firefox', min_version=120)],
    os=('macos', 'windows'),
    device='desktop',
)

N = 12
control_mean = sum(deviation(control.generate()) for _ in range(N)) / N
patched_mean = sum(deviation(BrowserForge.__gen_fg__(None)) for _ in range(N)) / N

print("control_mean=%.3f patched_mean=%.3f" % (control_mean, patched_mean))
assert patched_mean < control_mean * 0.6, (
    "patched generator is no closer to the configured display than an "
    "unconstrained one (control %.3f vs patched %.3f)" % (control_mean, patched_mean)
)
"""


def test_fingerprint_screen_size_tracks_the_configured_display():
    """The generated fingerprint's screen size must be pulled toward the display
    the browser will actually report.

    patched_gen_fg() used to return gen.generate() directly, dropping the
    upstream tolerance loop, so the spoofed display could sit ~100% away from
    the host's — a strong headless/automation signal.

    The assertion is statistical rather than single-shot on purpose: the
    generator only produces any given resolution a fraction of the time, and
    like upstream it gives up after 10 attempts, so one sample proves nothing.
    An unconstrained generator is used as the control — before the fix the two
    were the same code and scored identically.
    """
    code = _SMOKE.replace("__SRC__", str(_SRC))
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "patched_mean" in proc.stdout
