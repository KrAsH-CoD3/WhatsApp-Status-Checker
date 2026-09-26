"""
SDK-contract guard for app.py.

tests/conftest.py replaces every camouchat module with a MagicMock, which
answers hasattr() for any name — so the suite cannot tell whether the methods
app.py calls actually exist. This runs in a fresh interpreter against the real
SDK instead.
"""

import ast
import pathlib
import subprocess
import sys


_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
_APP = _SRC / "whatsapp_status_checker" / "core" / "app.py"


_SMOKE = """
import ast, pathlib, sys
sys.path.insert(0, "__SRC__")
from camouchat_whatsapp import InteractionController

tree = ast.parse(pathlib.Path("__APP__").read_text())
called = {
    n.func.attr
    for n in ast.walk(tree)
    if isinstance(n, ast.Call)
    and isinstance(n.func, ast.Attribute)
    and isinstance(n.func.value, ast.Attribute)
    and n.func.value.attr == "interaction"
}
missing = sorted(m for m in called if not hasattr(InteractionController, m))
assert not missing, "app.py calls non-existent InteractionController methods: %s" % missing
print("ok: " + ", ".join(sorted(called)))
"""


def test_app_only_calls_existing_interaction_methods():
    """Every `self.interaction.<method>()` call in app.py must exist on the real
    SDK class.

    initialize() called interaction.click_status_tab()/click_chats_tab();
    neither exists on InteractionController or its protocol, so both raised
    AttributeError into a bare `except: pass` and the warm-up step was a silent
    no-op. WebSelectorConfig exposes no status-tab or chats-tab selector, so
    there is no SDK-supported replacement.
    """
    code = _SMOKE.replace("__SRC__", str(_SRC)).replace("__APP__", str(_APP))
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert proc.stdout.startswith("ok")
