#!/usr/bin/env python3
"""Workshop preflight: checks that this computer is ready for the hands-on parts.

Run it from the workshop folder:  python3 preflight.py      (Windows: py preflight.py)
It reads preflight.json next to it, prints one line per check and ends with READY or NOT READY.
It changes nothing on your computer. Standard library only, Python 3.8 or newer.
"""
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLOR = sys.stdout.isatty() and os.name != "nt"
MARKS = {"ok": ("\033[32mPASS\033[0m" if COLOR else "PASS"),
         "fail": ("\033[31mFAIL\033[0m" if COLOR else "FAIL"),
         "warn": ("\033[33mWARN\033[0m" if COLOR else "WARN"),
         "todo": ("\033[36mYOU \033[0m" if COLOR else "YOU ")}


def version_tuple(text):
    numbers = re.findall(r"\d+", text or "")
    return tuple(int(n) for n in numbers[:3]) or (0,)


def at_least(found, wanted):
    return not wanted or version_tuple(found) >= version_tuple(wanted)


def report(status, label, detail="", fix=""):
    print(f"  {MARKS[status]}  {label}" + (f"  ({detail})" if detail else ""))
    if fix and status in ("fail", "warn"):
        print(f"        fix: {fix}")
    return status


def check_python(rule):
    found = platform.python_version()
    wanted = rule if isinstance(rule, str) else rule.get("min", "")
    wanted = wanted.lstrip(">= ")
    ok = at_least(found, wanted)
    return report("ok" if ok else "fail", f"Python {wanted or ''}+".replace(" +", "+"), f"found {found}",
                  "install a newer Python from https://www.python.org/downloads/")


def check_command(rule):
    name = rule["name"]
    exe = shutil.which(rule.get("exe", name))
    if not exe:
        return report("fail", name, "not found on PATH", rule.get("fix", f"install {name}"))
    if not rule.get("version_cmd"):
        return report("ok", name, exe)
    try:
        out = subprocess.run(rule["version_cmd"], capture_output=True, text=True, timeout=30)
        text = (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr).strip() else ""
    except (OSError, subprocess.TimeoutExpired) as exc:
        return report("warn", name, f"found, but '{' '.join(rule['version_cmd'])}' failed: {exc}", rule.get("fix", ""))
    ok = at_least(text, rule.get("min"))
    return report("ok" if ok else "fail", f"{name} {rule.get('min', '')}".strip(), text or exe,
                  rule.get("fix", f"update {name}"))


def check_package(rule):
    name = rule["name"]
    module = rule.get("import", name.replace("-", "_"))
    try:
        from importlib import metadata
        found = metadata.version(rule.get("dist", name))
    except Exception:
        found = None
    if found is None:
        try:
            __import__(module)
            found = "installed"
        except Exception:
            return report("fail", f"Python package {name}", "not installed",
                          rule.get("fix", f"{sys.executable} -m pip install {name}"))
    ok = found == "installed" or at_least(found, rule.get("min"))
    return report("ok" if ok else "fail", f"Python package {name} {rule.get('min', '')}".strip(), found,
                  rule.get("fix", f"{sys.executable} -m pip install --upgrade {name}"))


def check_path(rule):
    path = Path(os.path.expanduser(rule["path"]))
    path = path if path.is_absolute() else HERE / path
    return report("ok" if path.exists() else "fail", rule.get("label", f"file {rule['path']}"), str(path),
                  rule.get("fix", ""))


def check_env(rule):
    value = os.environ.get(rule["name"])
    return report("ok" if value else "fail", f"environment variable {rule['name']}", "set" if value else "not set",
                  rule.get("fix", f"set {rule['name']}"))


def check_url(rule):
    try:
        with urllib.request.urlopen(rule["url"], timeout=rule.get("timeout", 8)) as resp:
            return report("ok", rule.get("label", rule["url"]), f"HTTP {resp.status}")
    except Exception as exc:
        return report("warn", rule.get("label", rule["url"]), f"unreachable: {exc}",
                      rule.get("fix", "check the Wi-Fi, or ask a helper"))


def check_port(rule):
    with socket.socket() as sock:
        sock.settimeout(1)
        busy = sock.connect_ex(("127.0.0.1", int(rule["port"]))) == 0
    return report("warn" if busy else "ok", f"port {rule['port']} free", "in use" if busy else "",
                  rule.get("fix", "close the program using it"))


def check_disk(rule):
    free_gb = shutil.disk_usage(str(HERE)).free / 1e9
    ok = free_gb >= float(rule["min_gb"])
    return report("ok" if ok else "fail", f"{rule['min_gb']} GB free disk", f"{free_gb:.1f} GB free",
                  "free up disk space")


def main():
    config_path = HERE / "preflight.json"
    if not config_path.is_file():
        print(f"preflight.json not found next to {Path(__file__).name}")
        return 2
    config = json.loads(config_path.read_text(encoding="utf-8"))
    print(f"\n{config.get('title', 'Workshop preflight')}")
    print(f"  {platform.system()} {platform.release()} · {platform.machine()} · Python {platform.python_version()}\n")
    results = []
    if config.get("os"):
        allowed = [o.lower() for o in config["os"]]
        current = {"Darwin": "macos", "Windows": "windows", "Linux": "linux"}.get(platform.system(),
                                                                              platform.system().lower())
        results.append(report("ok" if current in allowed else "warn", f"operating system ({', '.join(config['os'])})",
                              current, "ask a helper; some steps differ on your system"))
    if config.get("python"):
        results.append(check_python(config["python"]))
    for key, fn in (("commands", check_command), ("python_packages", check_package), ("paths", check_path),
                    ("env", check_env), ("urls", check_url), ("ports", check_port)):
        for rule in config.get(key) or []:
            results.append(fn(rule))
    if config.get("disk"):
        results.append(check_disk(config["disk"]))
    for item in config.get("manual") or []:
        results.append(report("todo", item, "check this yourself"))
    failed = results.count("fail")
    print()
    if failed:
        print(f"NOT READY: {failed} check(s) failed. Follow the fix lines above, then run this again.")
        print(f"Still stuck? Email {config.get('contact', 'the organizers')} before the workshop.")
        return 1
    print("READY" + (" (with warnings: read them above)" if "warn" in results else "") + ". See you there!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
