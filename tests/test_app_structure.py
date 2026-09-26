"""
Structural guards for app.py.

tests/conftest.py replaces every camouchat module with a MagicMock, so the suite
cannot see how app.py is wired; these read the source instead.
"""

import ast
import pathlib


_ROOT = pathlib.Path(__file__).resolve().parents[1]
_APP = _ROOT / "src" / "whatsapp_status_checker" / "core" / "app.py"


def test_no_duplicate_except_clauses():
    """Python matches the first `except` that fits, so a repeated clause makes
    every clause after it unreachable.

    initialize() listed `except asyncio.TimeoutError` twice; the branch that
    logged and retried could never run, and the first clause retried with the
    same budget and let a second timeout escape initialize() entirely.
    """
    tree = ast.parse(_APP.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        kinds = [ast.unparse(h.type) if h.type else "<bare>" for h in node.handlers]
        duplicates = {k for k in kinds if kinds.count(k) > 1}
        assert not duplicates, (
            f"try at line {node.lineno} has unreachable handlers "
            f"{sorted(duplicates)}: {kinds}"
        )


def test_no_bare_except_in_app():
    """A bare `except:` swallows everything, CancelledError included, so it can
    break Ctrl+C.

    initialize() wrapped the status-store warm-up in one, which hid the fact
    that both methods it called raised AttributeError.
    """
    tree = ast.parse(_APP.read_text())
    bare = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler) and node.type is None
    ]
    assert not bare, f"bare except clauses at lines {bare}"
