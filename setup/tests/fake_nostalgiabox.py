#!/usr/bin/env python3
"""Stand-in for the nostalgiabox program: --check lists channels; otherwise it 'plays'."""
import os, sys, time
import yaml

args = sys.argv[1:]
cfg_path = args[args.index("--config") + 1]
cfg = yaml.safe_load(open(cfg_path))
if "--check" in args:
    for c in cfg["channels"]:
        print(f"CH {c['number']:>2}  {c['name']}  ok")
    print("config OK")
    sys.exit(0)
mark = os.environ.get("NB_FAKE_MARK")
if mark:
    with open(mark, "a") as f:
        f.write(cfg_path + "\n")
keys = os.environ.get("NB_FAKE_KEYS")
if keys and os.isatty(0):
    import select, tty
    tty.setcbreak(0)
    while True:
        if select.select([0], [], [], 0.5)[0]:
            data = os.read(0, 64)
            with open(keys, "a") as f:
                f.write(repr(data.decode()) + "\n")
else:
    while True:
        time.sleep(1)
