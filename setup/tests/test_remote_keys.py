#!/usr/bin/env python3
"""Feeds every on-screen remote button into NostalgiaBox's REAL keyboard-input code (inside a
pseudo-terminal, exactly how the controller does it) and checks each becomes the right action.

Needs the nostalgiabox package importable (run it inside NostalgiaBox's virtual environment);
it skips itself otherwise.
"""
import os
import pty
import sys
import time
import tty

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT + "/app")
try:
    from nostalgiabox.input.stdin_backend import StdinBackend
    from nostalgiabox.actions import Action
except ImportError:
    print("skipped: nostalgiabox is not importable here")
    sys.exit(0)
import nbcommon as nb

EXPECT = {
    "channel_up": (Action.CHANNEL_UP, None), "channel_down": (Action.CHANNEL_DOWN, None),
    "volume_up": (Action.VOLUME_UP, None), "volume_down": (Action.VOLUME_DOWN, None),
    "mute": (Action.MUTE, None), "enter": (Action.ENTER, None), "info": (Action.INFO, None),
    "last": (Action.LAST_CHANNEL, None), "power": (Action.POWER, None),
    **{f"digit_{d}": (Action.DIGIT, d) for d in range(10)},
}
assert set(EXPECT) == set(nb.REMOTE_KEYS), "button lists differ"

master, slave = pty.openpty()
tty.setcbreak(slave)
os.dup2(slave, 0)
sys.stdin = os.fdopen(0, "r", closefd=False)
from queue import Queue
q = Queue()
be = StdinBackend()
be.start(q)
time.sleep(0.5)
ok = True
for key, (action, value) in EXPECT.items():
    nb.type_keys(master, nb.REMOTE_KEYS[key])
    try:
        ev = q.get(timeout=2)
        good = ev.action == action and ev.value == value
    except Exception:
        ev, good = None, False
    ok &= good
    print(("  ok   " if good else "  FAIL ") + f"{key:13s} -> {ev}")
be.stop()
print("\nPASS" if ok else "\nFAIL")
sys.exit(0 if ok else 1)
