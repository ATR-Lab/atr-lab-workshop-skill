"""Shared helpers: paths, JSON files, the atr-lab-design skill, subprocesses and Kent State (AP) date style."""
from __future__ import annotations

import datetime as _dt
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

SKILL_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT_AS_INVOKED = Path(os.path.abspath(__file__)).parents[2]
SCHEMA = "atr-workshop/1"
BRIEF_NAME = "workshop.json"


class WorkshopError(Exception):
    """A problem the user or agent has to fix; printed without a traceback."""


# --------------------------------------------------------------------------- files

def read_json(path: Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise WorkshopError(f"{path}: not found")
    except json.JSONDecodeError as exc:
        raise WorkshopError(f"{path}: not valid JSON ({exc})")


def write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_of(items: Iterable[Any]) -> str:
    digest = hashlib.sha256()
    for item in items:
        if isinstance(item, Path):
            digest.update(item.read_bytes() if item.is_file() else str(item).encode())
        else:
            digest.update(json.dumps(item, sort_keys=True, ensure_ascii=False).encode())
        digest.update(b"\0")
    return digest.hexdigest()


def find_brief(given: Optional[str]) -> Path:
    """The workshop.json named on the command line, else the nearest one in this folder or above."""
    if given:
        path = Path(given).expanduser()
        if path.is_dir():
            path = path / BRIEF_NAME
        if not path.is_file():
            raise WorkshopError(f"{path}: no workshop brief here (run: workshop.py init <folder>)")
        return path.resolve()
    here = Path.cwd()
    for folder in (here, *here.parents):
        if (folder / BRIEF_NAME).is_file():
            return (folder / BRIEF_NAME).resolve()
    raise WorkshopError("no workshop.json in this folder or above: pass -w <folder or file>, or run "
                        "workshop.py init <folder>")


def refuse_inside_skill(path: Path) -> None:
    try:
        Path(path).resolve().relative_to(SKILL_ROOT)
    except ValueError:
        return
    raise WorkshopError(f"{path}: inside the skill folder. Workshop files go in the user's own folder.")


# --------------------------------------------------------------------------- the design skill

def _plugin_caches() -> list:
    home = Path.home()
    found = sorted(glob.glob(str(home / ".claude/plugins/cache/*/atr-lab-design/*/atr-lab-design")),
                   key=lambda p: os.path.getmtime(p), reverse=True)
    return [Path(p) for p in found]


def design_skill_candidates() -> list:
    home = Path.home()
    out = []
    if os.environ.get("ATR_DESIGN_SKILL"):
        out.append(Path(os.environ["ATR_DESIGN_SKILL"]).expanduser())
    out.append(SKILL_ROOT_AS_INVOKED.parent / "atr-lab-design")
    out.append(SKILL_ROOT.parent / "atr-lab-design")
    for folder in (Path.cwd(), *Path.cwd().parents):
        out.append(folder / ".claude/skills/atr-lab-design")
    out += [home / ".claude/skills/atr-lab-design", home / ".codex/skills/atr-lab-design",
            home / ".agents/skills/atr-lab-design", home / ".local/share/atr-lab-design-skill/atr-lab-design"]
    if os.environ.get("CLAUDE_PLUGIN_ROOT"):
        out.append(Path(os.environ["CLAUDE_PLUGIN_ROOT"]).parent / "atr-lab-design")
    out += _plugin_caches()
    if os.environ.get("LOCALAPPDATA"):
        out.append(Path(os.environ["LOCALAPPDATA"]) / "atr-lab-design-skill/atr-lab-design")
    return out


def find_design_skill(required: bool = True) -> Optional[Path]:
    for cand in design_skill_candidates():
        if (cand / "SKILL.md").is_file() and (cand / "scripts/new_deck.py").is_file():
            return cand.resolve()
    if required:
        raise WorkshopError(
            "the atr-lab-design skill was not found. Install it (https://github.com/ATR-Lab/atr-lab-design-skill) "
            "or point ATR_DESIGN_SKILL at its atr-lab-design/ folder.")
    return None


def _has_pptx(python: str) -> bool:
    try:
        return subprocess.run([python, "-c", "import pptx, lxml, PIL"], capture_output=True,
                              timeout=60).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def find_design_python(design: Path, required: bool = True) -> Optional[str]:
    """A Python with the design skill's requirements: $ATR_DESIGN_PYTHON, its .venv, the plugin's venv, this one."""
    home = Path.home()
    cands = []
    if os.environ.get("ATR_DESIGN_PYTHON"):
        cands.append(os.environ["ATR_DESIGN_PYTHON"])
    for venv in (design / ".venv", home / ".claude/plugins/data/atr-lab-design-atr-lab/venv",
                 *[Path(p) for p in glob.glob(str(home / ".claude/plugins/data/atr-lab-design*/venv"))]):
        for rel in ("bin/python", "Scripts/python.exe"):
            if (venv / rel).is_file():
                cands.append(str(venv / rel))
    cands.append(sys.executable)
    for python in cands:
        if _has_pptx(python):
            return python
    if required:
        raise WorkshopError(
            f"no Python with the design skill's packages. Create one: python3 -m venv {design}/.venv && "
            f"{design}/.venv/bin/pip install -r {design}/scripts/requirements.txt (or run /atr-lab-design:setup)")
    return None


def run(cmd: list, cwd: Optional[Path] = None, quiet: bool = False) -> subprocess.CompletedProcess:
    """Run a command, echo it, stream its output unless quiet, and return the result (never raises on exit codes)."""
    shown = " ".join(str(c) if " " not in str(c) else repr(str(c)) for c in cmd)
    print(f"$ {shown}", flush=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run([str(c) for c in cmd], cwd=str(cwd) if cwd else None, env=env,
                          capture_output=True, text=True)
    if not quiet or proc.returncode:
        if proc.stdout.strip():
            print(proc.stdout.rstrip())
        if proc.stderr.strip():
            print(proc.stderr.rstrip(), file=sys.stderr)
    return proc


def which(name: str) -> Optional[str]:
    return shutil.which(name)


# --------------------------------------------------------------------------- Kent State / AP style

AP_MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
AP_DAYS_SHORT = ["Mon.", "Tues.", "Wed.", "Thurs.", "Fri.", "Sat.", "Sun."]
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
                9: "nine", 10: "10"}


def parse_date(value: str) -> _dt.date:
    try:
        return _dt.date.fromisoformat(str(value).strip())
    except ValueError:
        raise WorkshopError(f"date {value!r}: use YYYY-MM-DD")


def parse_time(value: str) -> _dt.time:
    match = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*", str(value))
    if not match or int(match.group(1)) > 23 or int(match.group(2)) > 59:
        raise WorkshopError(f"time {value!r}: use 24-hour HH:MM")
    return _dt.time(int(match.group(1)), int(match.group(2)))


def ap_date(day: _dt.date, weekday: bool = True, year: bool = True, short_weekday: bool = False) -> str:
    """'Saturday, Feb. 13, 2027' (Kent State follows AP: Aug., Sept., March-July spelled out)."""
    text = f"{AP_MONTHS[day.month - 1]} {day.day}"
    if year:
        text += f", {day.year}"
    if weekday:
        name = AP_DAYS_SHORT[day.weekday()] if short_weekday else day.strftime("%A")
        text = f"{name}, {text}"
    return text


def ap_clock(t: _dt.time, meridiem: bool = True) -> str:
    """'10 a.m.', '1:30 p.m.', 'noon', 'midnight' (AP)."""
    if t.hour == 12 and t.minute == 0:
        return "noon"
    if t.hour == 0 and t.minute == 0:
        return "midnight"
    hour = t.hour % 12 or 12
    text = f"{hour}" if t.minute == 0 else f"{hour}:{t.minute:02d}"
    if meridiem:
        text += " a.m." if t.hour < 12 else " p.m."
    return text


def ap_time_range(start: _dt.time, end: _dt.time) -> str:
    """'10 a.m.-2 p.m.', '9-11 a.m.', '9 a.m.-noon'."""
    same_half = (start.hour < 12) == (end.hour < 12)
    if same_half and ap_clock(start) not in ("noon", "midnight") and ap_clock(end) not in ("noon", "midnight"):
        return f"{ap_clock(start, meridiem=False)}-{ap_clock(end)}"
    return f"{ap_clock(start)}-{ap_clock(end)}"


def tz_abbrev(day: _dt.date, at: _dt.time, tz_name: str) -> str:
    try:
        from zoneinfo import ZoneInfo
        return _dt.datetime.combine(day, at, ZoneInfo(tz_name)).tzname() or ""
    except Exception:  # unknown zone or no tz database: leave the zone off rather than guess
        return ""


def to_utc(day: _dt.date, at: _dt.time, tz_name: str) -> _dt.datetime:
    from zoneinfo import ZoneInfo
    return _dt.datetime.combine(day, at, ZoneInfo(tz_name)).astimezone(_dt.timezone.utc)


def minutes_between(start: _dt.time, end: _dt.time) -> int:
    return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)


def add_minutes(t: _dt.time, minutes: int) -> _dt.time:
    total = t.hour * 60 + t.minute + minutes
    return _dt.time((total // 60) % 24, total % 60)


def duration_words(minutes: int) -> str:
    """'Four-hour workshop' style compound adjective: 'four-hour', '90-minute', 'three-and-a-half-hour'."""
    if minutes % 60 == 0 and minutes // 60 in NUMBER_WORDS:
        return f"{NUMBER_WORDS[minutes // 60]}-hour"
    if minutes % 60 == 30 and minutes // 60 in NUMBER_WORDS and minutes >= 150:
        return f"{NUMBER_WORDS[minutes // 60]}-and-a-half-hour"
    return f"{minutes}-minute"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(text).lower().replace("*", " star")).strip("-")
    return re.sub(r"-{2,}", "-", slug)[:48].strip("-") or "workshop"
