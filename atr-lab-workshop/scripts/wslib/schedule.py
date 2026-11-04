"""Run-of-show: clock times for each block, pacing checks, and schedule.md / schedule.csv / workshop.ics."""
from __future__ import annotations

import csv
import datetime as _dt
import io
import uuid
from dataclasses import dataclass
from pathlib import Path

from .brief import derived
from .common import (WorkshopError, add_minutes, ap_clock, ap_time_range, minutes_between, parse_date, parse_time,
                     to_utc, write_text)

ACTIVE_KINDS = {"talk", "demo", "hands-on", "discussion", "qa", "setup", "welcome", "wrap-up", "feedback"}
REST_KINDS = {"break", "lunch"}
PRACTICE_KINDS = {"hands-on", "demo", "discussion"}
KIND_LABELS = {"setup": "Setup", "welcome": "Welcome", "talk": "Talk", "demo": "Demo", "hands-on": "Hands-on",
               "discussion": "Discussion", "qa": "Q&A", "break": "Break", "lunch": "Lunch", "wrap-up": "Wrap-up",
               "feedback": "Feedback", "buffer": "Buffer"}

MAX_WITHOUT_BREAK = 90
MAX_TALK = 30
MEAL_THRESHOLD = 240


@dataclass
class Slot:
    index: int
    start: _dt.time
    end: _dt.time
    block: dict

    @property
    def minutes(self) -> int:
        return int(self.block["minutes"])

    @property
    def kind(self) -> str:
        return self.block["kind"]

    @property
    def clock(self) -> str:
        return f"{self.start:%H:%M}"


def timeline(brief: dict) -> list:
    when = brief["when"]
    if not when.get("start"):
        raise WorkshopError("when.start is empty: set the start time first")
    blocks = brief.get("schedule") or []
    if not blocks:
        raise WorkshopError("schedule is empty: add blocks (references/schedule.md has the recipes)")
    at = parse_time(when["start"])
    slots = []
    for index, block in enumerate(blocks):
        end = add_minutes(at, int(block["minutes"]))
        slots.append(Slot(index, at, end, block))
        at = end
    return slots


def pacing(brief: dict, slots: list) -> list:
    """(severity, message) pairs: 'error' blocks a final build, 'warning' needs a reason, 'info' is advice."""
    notes = []
    when = brief["when"]
    total = sum(s.minutes for s in slots)
    if when.get("end"):
        planned = minutes_between(parse_time(when["start"]), parse_time(when["end"]))
        if total > planned:
            notes.append(("error", f"the blocks add up to {total} min, {total - planned} min past the {planned}-min "
                                   "event: cut or shorten blocks"))
        elif total < planned:
            notes.append(("warning", f"{planned - total} min unscheduled at the end: add a buffer block or end "
                                     "earlier"))
    run = 0
    for slot in slots:
        if slot.kind in REST_KINDS:
            run = 0
            continue
        run += slot.minutes
        if run > MAX_WITHOUT_BREAK:
            notes.append(("warning", f"{run} min without a break by {ap_clock(slot.end)} ({slot.block['title']}): "
                                     f"put a 10-15 min break at least every {MAX_WITHOUT_BREAK} min"))
            run = 0
        if slot.kind == "talk" and slot.minutes > MAX_TALK:
            notes.append(("warning", f"talk '{slot.block['title']}' runs {slot.minutes} min: split it with a "
                                     f"demo, question or activity (attention drops after about 20 min)"))
        if slot.kind == "break" and not 10 <= slot.minutes <= 20:
            notes.append(("info", f"break at {ap_clock(slot.start)} is {slot.minutes} min; 10-15 is typical"))
    if total >= MEAL_THRESHOLD and not any(s.kind == "lunch" for s in slots):
        notes.append(("warning", f"a {total}-min workshop has no meal break: add lunch (30-60 min) or say why"))
    if not any(s.kind in ("qa", "discussion") for s in slots):
        notes.append(("warning", "no Q&A or discussion block: add one (10-15 min) before the wrap-up"))
    if not any(s.kind in ("wrap-up", "feedback") for s in slots[-2:]):
        notes.append(("warning", "the workshop does not end with a wrap-up or feedback block"))
    hands_on = sum(s.minutes for s in slots if s.kind == "hands-on")
    if any(s.kind == "hands-on" for s in slots) and not any(s.kind == "setup" for s in slots[:3]):
        notes.append(("warning", "hands-on workshop without an early setup check: add a 10-15 min 'setup' block "
                                 "near the start so environment problems surface before the first activity"))
    teaching = sum(s.minutes for s in slots if s.kind not in REST_KINDS | {"buffer"})
    if teaching and hands_on:
        share = round(100 * sum(s.minutes for s in slots if s.kind in PRACTICE_KINDS) / teaching)
        if share < 40:
            notes.append(("info", f"practice (hands-on, demo, discussion) is {share}% of teaching time; hands-on "
                                  "workshops usually aim for 50% or more"))
    if not any(s.kind == "buffer" for s in slots) and total >= 120:
        notes.append(("info", "no buffer: a 5-10 min buffer before lunch or the wrap-up absorbs overruns"))
    return notes


def totals(slots: list) -> dict:
    out: dict = {}
    for slot in slots:
        out[slot.kind] = out.get(slot.kind, 0) + slot.minutes
    return out


def write_outputs(brief: dict, root: Path) -> list:
    slots = timeline(brief)
    facts = derived(brief)
    modules = {m["id"]: m for m in brief.get("modules") or []}
    lines = [f"# Schedule: {brief.get('title') or '[title]'}", "",
             f"{facts['date_long']}, {facts['time_range']}  ·  {facts['venue_short']}", "",
             "| Time | Min | Block | Kind | Module | What happens |", "|---|---:|---|---|---|---|"]
    for slot in slots:
        block = slot.block
        module = modules.get(block.get("module"), {}).get("title", "") if block.get("module") else ""
        lines.append(f"| {ap_time_range(slot.start, slot.end)} | {slot.minutes} | {block['title']} | "
                     f"{KIND_LABELS.get(slot.kind, slot.kind)} | {module} | {block.get('notes', '')} |")
    lines += ["", "**Time by kind:** " + ", ".join(f"{KIND_LABELS.get(k, k)} {v} min"
                                                  for k, v in totals(slots).items()), ""]
    checks = pacing(brief, slots)
    if checks:
        lines += ["## Pacing checks", ""] + [f"- **{sev}**: {msg}" for sev, msg in checks] + [""]
    lines += ["## Presenter cues", "",
              "- Start the room timer at each block; the clock times above are the hard stops.",
              "- If a hands-on block overruns, cut the stretch goal, not the break.",
              "- Announce the return time before every break and put it on the break slide.", ""]
    write_text(root / "schedule.md", "\n".join(lines))

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["start", "end", "minutes", "title", "kind", "module", "notes"])
    for slot in slots:
        writer.writerow([f"{slot.start:%H:%M}", f"{slot.end:%H:%M}", slot.minutes, slot.block["title"], slot.kind,
                         slot.block.get("module", ""), slot.block.get("notes", "")])
    write_text(root / "schedule.csv", buffer.getvalue())

    written = [root / "schedule.md", root / "schedule.csv"]
    ics = calendar(brief, slots, facts)
    if ics:
        write_text(root / "workshop.ics", ics)
        written.append(root / "workshop.ics")
    return written


def _ics_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def calendar(brief: dict, slots: list, facts: dict) -> str:
    """One VEVENT for the whole workshop in UTC, for confirmation emails and the presenter's calendar."""
    when = brief["when"]
    if not (when.get("date") and when.get("timezone")):
        return ""
    try:
        day = parse_date(when["date"])
        begin = to_utc(day, slots[0].start, when["timezone"])
        finish = to_utc(day, slots[-1].end, when["timezone"])
    except Exception:
        return ""
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid = uuid.uuid5(uuid.NAMESPACE_URL, f"atr-workshop:{facts['slug']}")
    description = brief.get("summary") or ""
    if brief.get("registration", {}).get("url"):
        description += f"\nRegistration: {brief['registration']['url']}"
    location = facts["venue"].replace("\n", ", ")
    body = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ATR Lab//atr-lab-workshop//EN", "CALSCALE:GREGORIAN",
            "BEGIN:VEVENT", f"UID:{uid}@atr.cs.kent.edu", f"DTSTAMP:{stamp}",
            f"DTSTART:{begin:%Y%m%dT%H%M%SZ}", f"DTEND:{finish:%Y%m%dT%H%M%SZ}",
            f"SUMMARY:{_ics_escape(brief.get('title') or 'Workshop')}",
            f"LOCATION:{_ics_escape(location)}", f"DESCRIPTION:{_ics_escape(description.strip())}",
            "END:VEVENT", "END:VCALENDAR", ""]
    return "\r\n".join(body)
