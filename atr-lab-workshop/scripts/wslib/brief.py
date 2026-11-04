"""The workshop brief (workshop.json): skeleton, dotted edits, the intake check and derived facts."""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .common import (SCHEMA, WorkshopError, ap_date, ap_time_range, duration_words, minutes_between,
                     parse_date, parse_time, slugify, tz_abbrev)

FORMATS = ("in-person", "virtual", "hybrid")
LEVELS = ("beginner", "intermediate", "advanced", "mixed")
BLOCK_KINDS = ("setup", "welcome", "talk", "demo", "hands-on", "discussion", "qa", "break", "lunch",
               "wrap-up", "feedback", "buffer")

SKELETON = {
    "schema": SCHEMA,
    "slug": "",
    "title": "",
    "short_title": "",
    "summary": "",
    "topics": [],
    "format": "",
    "when": {"date": "", "start": "", "end": "", "timezone": "America/New_York", "check_in": ""},
    "where": {"building": "", "room": "", "campus": "Kent State University, Kent Campus", "address": "",
              "online_url": "", "parking": "", "wifi": "", "notes": ""},
    "audience": {"who": "", "level": "", "capacity": None, "cost": ""},
    "presenters": [{"name": "", "role": "", "email": ""}],
    "prerequisites": {"skills": [], "hardware": [], "software": [], "accounts": [], "provided": [],
                      "pre_work": []},
    "objectives": [],
    "modules": [],
    "schedule": [],
    "materials": {"repo_url": "", "languages": [], "stack": [], "license": "MIT"},
    "registration": {"url": "", "printed_url": "", "deadline": "", "feedback_url": "", "forms": ["registration",
                     "feedback"], "extra_questions": []},
    "promotion": {"eyebrow": "", "flyer_title": "", "flyer_sizes": ["letter"], "tv_slide": True, "motion": "",
                  "teo_cameo": False, "agenda": [], "workflow": [], "tools": [], "registration_head": ""},
    "contact": {"email": "", "phone": ""},
    "requests": [],
    "assumptions": [],
    "open_questions": [],
}

PLACEHOLDER = re.compile(r"\[[^\]\n]{1,80}\]")
EXAMPLE_URL = re.compile(r"https?://(www\.)?example\.(org|com|net)\b")


# --------------------------------------------------------------------------- load, save, edit

def new_brief() -> dict:
    return copy.deepcopy(SKELETON)


def load(path: Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise WorkshopError(f"{path}: schema is {data.get('schema')!r}, expected {SCHEMA!r}")
    merged = new_brief()
    _merge(merged, data)
    return merged


def _merge(base: dict, extra: dict) -> None:
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value


def get(brief: dict, dotted: str) -> Any:
    node: Any = brief
    for part in dotted.split("."):
        if isinstance(node, list):
            node = node[int(part)]
        elif isinstance(node, dict):
            node = node.get(part)
        else:
            return None
    return node


def set_value(brief: dict, dotted: str, raw: str) -> Any:
    """Set a dotted key ('when.date', 'presenters.0.email'); the value is JSON when it parses, else a string."""
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = raw
    parts = dotted.split(".")
    node: Any = brief
    for part in parts[:-1]:
        if isinstance(node, list):
            index = int(part)
            while len(node) <= index:
                node.append({})
            node = node[index]
        else:
            node = node.setdefault(part, {})
    last = parts[-1]
    if isinstance(node, list):
        index = int(last)
        while len(node) <= index:
            node.append(None)
        node[index] = value
    else:
        node[last] = value
    return value


# --------------------------------------------------------------------------- the intake check

@dataclass
class Issue:
    path: str
    severity: str        # "required" (ask before building), "recommended" (ask or assume and say so), "error"
    question: str
    why: str = ""

    def as_dict(self) -> dict:
        return {"path": self.path, "severity": self.severity, "question": self.question, "why": self.why}


def _blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def check(brief: dict) -> list:
    """Everything the workshop still needs, phrased as the question to ask the presenter."""
    issues: list = []

    def need(path: str, question: str, why: str = "", severity: str = "required") -> None:
        if _blank(get(brief, path)):
            issues.append(Issue(path, severity, question, why))

    need("title", "What is the workshop called (a working title is fine)?", "slides, flyer, forms, TV slide")
    need("topics", "Which main topics should the workshop cover?", "drives the outline and modules")
    need("format", "Is it in person, virtual or hybrid?", "venue, links and schedule")
    need("when.date", "What date is the workshop (YYYY-MM-DD)?", "every deliverable")
    need("when.start", "What time does it start?", "schedule, flyer, forms")
    need("when.end", "What time does it end?", "schedule length")
    need("when.timezone", "Which time zone (default America/New_York for Kent)?", "flyer, calendar file")
    fmt = brief.get("format")
    if fmt in ("in-person", "hybrid", ""):
        need("where.building", "Which building is it in?", "flyer and forms; building names are checked")
        need("where.room", "Which room?", "flyer and forms")
    if fmt in ("virtual", "hybrid"):
        need("where.online_url", "What is the meeting link (or say it will be emailed after registration)?",
             "forms and reminders", severity="recommended")
    need("audience.who", "Who is it for (for example undergraduates, graduate students, faculty, K-12 teachers)?",
         "tone, level and promotion")
    need("audience.level", "What level: beginner, intermediate, advanced or mixed?", "depth and pacing")
    need("prerequisites.skills", "What should participants already know (skills or courses)? Say 'none' if "
         "nothing.", "flyer requirements and the registration form")
    need("prerequisites.hardware", "What hardware do participants need (laptop and OS, robots, boards, cables)? "
         "Say 'none' if nothing.", "flyer, setup guide, preflight check")
    need("presenters.0.name", "Who is presenting (name and role)?", "title slide, flyer contact")
    need("presenters.0.email", "Which email should questions go to (a kent.edu address is preferred)?",
         "flyer contact, forms")
    need("audience.capacity", "How many seats are there?", "registration form cap", severity="recommended")
    need("prerequisites.software", "Which software or accounts must be installed before they arrive?",
         "setup guide, preflight", severity="recommended")
    need("registration.deadline", "Is there a registration deadline?", "flyer and form", severity="recommended")
    need("audience.cost", "Is it free? Is food provided?", "flyer and forms", severity="recommended")
    need("materials.languages", "Which programming languages and tools will the hands-on parts use?",
         "code materials", severity="recommended")
    need("objectives", "What should participants be able to do by the end? (Draft three to five and confirm "
         "them with the presenter if not given.)", "outline, slides, feedback form", severity="recommended")
    if fmt in ("in-person", "hybrid"):
        need("where.wifi", "Which Wi-Fi network should participants use (for example eduroam or KSU-Guest)?",
             "welcome slide", severity="recommended")

    for path, what in unresolved(brief):
        issues.append(Issue(path, "required", f"Confirm {what} at {path}", "a [placeholder] blocks a final build"))
    issues += _consistency(brief)
    return issues


def _consistency(brief: dict) -> list:
    out = []
    when = brief.get("when") or {}
    try:
        start = parse_time(when["start"]) if when.get("start") else None
        end = parse_time(when["end"]) if when.get("end") else None
        if when.get("date"):
            parse_date(when["date"])
        if start and end and minutes_between(start, end) <= 0:
            out.append(Issue("when.end", "error", "The end time is not after the start time: which is right?"))
    except WorkshopError as exc:
        out.append(Issue("when", "error", f"Fix the date or time: {exc}"))
    if brief.get("format") and brief["format"] not in FORMATS:
        out.append(Issue("format", "error", f"format must be one of {', '.join(FORMATS)}"))
    level = (brief.get("audience") or {}).get("level")
    if level and level not in LEVELS:
        out.append(Issue("audience.level", "error", f"level must be one of {', '.join(LEVELS)}"))
    building = (brief.get("where") or {}).get("building", "")
    if re.search(r"mathematics and computer science", building, re.I):
        out.append(Issue("where.building", "error", "The building is the Mathematical Sciences Building (MSB), "
                         "not 'Mathematics and Computer Science Building'."))
    room = (brief.get("where") or {}).get("room", "")
    if re.search(r"\b236\b", room) and re.search(r"math", building, re.I):
        out.append(Issue("where.room", "error", "Room 236 is not the lab's room: confirm the workshop room."))
    for i, block in enumerate(brief.get("schedule") or []):
        if block.get("kind") not in BLOCK_KINDS:
            out.append(Issue(f"schedule.{i}.kind", "error",
                             f"block {block.get('title')!r}: kind must be one of {', '.join(BLOCK_KINDS)}"))
        if not isinstance(block.get("minutes"), int) or block["minutes"] <= 0:
            out.append(Issue(f"schedule.{i}.minutes", "error", f"block {block.get('title')!r}: minutes must be a "
                             "positive whole number"))
    module_ids = {m.get("id") for m in brief.get("modules") or []}
    for i, block in enumerate(brief.get("schedule") or []):
        if block.get("module") and block["module"] not in module_ids:
            out.append(Issue(f"schedule.{i}.module", "error", f"block {block.get('title')!r} names module "
                             f"{block['module']!r}, which is not in modules"))
    for m in brief.get("modules") or []:
        for point in m.get("key_points") or []:
            if len(point) > 38:
                out.append(Issue(f"modules.{m.get('id')}.key_points", "recommended",
                                 f"Key point {point!r} becomes a slide title: cut it to 38 characters "
                                 f"(it is {len(point)})"))
    url = (brief.get("registration") or {}).get("url", "")
    if url and not re.match(r"https://", url):
        out.append(Issue("registration.url", "error", "The registration link must start with https://"))
    printed = (brief.get("registration") or {}).get("printed_url", "")
    if printed.startswith("http"):
        out.append(Issue("registration.printed_url", "error", "printed_url is printed as text: leave out "
                         "https:// (forms.gle/AbC123)"))
    return out


def ready_to_build(issues: list) -> bool:
    return not any(i.severity in ("required", "error") for i in issues)


def unresolved(brief: dict) -> list:
    """[placeholders] and example.org links still inside the brief, with their paths."""
    found = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else key)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}.{index}")
        elif isinstance(node, str):
            for match in PLACEHOLDER.findall(node):
                found.append((path, match))
            if EXAMPLE_URL.search(node):
                found.append((path, "example.org placeholder link"))

    walk({k: v for k, v in brief.items() if k not in ("assumptions", "open_questions")}, "")
    return found


# --------------------------------------------------------------------------- derived facts

def derived(brief: dict) -> dict:
    """Facts computed from the brief in Kent State style, for slides, flyers, forms and the TV slide."""
    when = brief["when"]
    where = brief["where"]
    day = parse_date(when["date"]) if when.get("date") else None
    start = parse_time(when["start"]) if when.get("start") else None
    end = parse_time(when["end"]) if when.get("end") else None
    zone = tz_abbrev(day, start, when.get("timezone") or "") if day and start else ""
    minutes = minutes_between(start, end) if start and end else 0
    presenters = [p for p in brief.get("presenters") or [] if p.get("name")]
    contact_email = (brief.get("contact") or {}).get("email") or (presenters[0].get("email") if presenters else "")
    venue_lines = []
    if brief.get("format") == "virtual":
        venue_lines = ["Online", "Link sent after registration" if not where.get("online_url") else
                       where["online_url"]]
    else:
        venue_lines = [where.get("building") or "[Building]",
                       "  ·  ".join(x for x in (where.get("room"), _campus_short(where.get("campus"))) if x)]
        if brief.get("format") == "hybrid":
            venue_lines.append("Or join online")
    slug = brief.get("slug") or slugify(f"{brief.get('short_title') or brief.get('title')} {when.get('date', '')}")
    return {
        "slug": slug,
        "date_long": ap_date(day) if day else "[date]",
        "date_short": ap_date(day, weekday=False) if day else "[date]",
        "date_tv": ap_date(day, short_weekday=True, year=False) if day else "[date]",
        "time_range": f"{ap_time_range(start, end)} {zone}".strip() if start and end else "[time]",
        "time_range_no_zone": ap_time_range(start, end) if start and end else "[time]",
        "minutes": minutes,
        "duration": f"{duration_words(minutes).capitalize()} workshop" if minutes else "",
        "venue": "\n".join(venue_lines),
        "venue_short": ", ".join(x for x in (where.get("room"), where.get("building")) if x) or
                       ("Online" if brief.get("format") == "virtual" else "[venue]"),
        "presenter_line": ", ".join(f"{p['name']}, {p['role']}" if p.get("role") else p["name"]
                                    for p in presenters[:2]) or "[Presenter Name]",
        "contact": contact_email or "[contact email]",
        "zone": zone,
    }


def _campus_short(campus: Optional[str]) -> str:
    if not campus:
        return ""
    return "Kent State University" if re.match(r"kent state", campus, re.I) else campus
