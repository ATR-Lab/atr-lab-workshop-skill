"""outline.md: the detailed workshop outline, prefilled from the brief for the agent to write out in full."""
from __future__ import annotations

import datetime as _dt

from .brief import derived
from .common import ap_clock, ap_date, ap_time_range, parse_date
from .schedule import KIND_LABELS, timeline


def _list(items: list, empty: str = "[to confirm]") -> list:
    items = [i for i in items or [] if str(i).strip()]
    return [f"- {i}" for i in items] if items else [f"- {empty}"]


def promotion_timeline(brief: dict) -> list:
    date = brief["when"].get("date")
    if not date:
        return ["- [Set the date to get the promotion timeline]"]
    day = parse_date(date)
    rows = [(-28, "Flyers printed and posted; TV slide submitted to the building's slideshow; registration open"),
            (-21, "Social post and department newsletter item (atr-lab-design skill: social card and copy)"),
            (-7, "Reminder to registrants with the setup guide and the preflight check"),
            (-3, "Registration closes or the form closes at capacity; confirm room, AV and catering"),
            (-2, "Last reminder: time, room, what to bring; helpers run the preflight on a spare laptop"),
            (0, "Workshop; feedback form on the last slide"),
            (2, "Thank-you email with the slides, the code repository and the feedback link")]
    out = []
    for offset, text in rows:
        when = day + _dt.timedelta(days=offset)
        label = "Day of" if offset == 0 else (f"{-offset} days before" if offset < 0 else f"{offset} days after")
        out.append(f"| {ap_date(when, weekday=False)} | {label} | {text} |")
    return ["| Date | When | What |", "|---|---|---|"] + out


def render(brief: dict) -> str:
    facts = derived(brief)
    pre = brief.get("prerequisites") or {}
    aud = brief.get("audience") or {}
    lines = [f"# Workshop outline: {brief.get('title') or '[title]'}", "",
             "> Draft generated from workshop.json. Write every section out in full; keep square-bracket placeholders "
             "only for facts the presenter still has to confirm.", "",
             "## 1. At a glance", "",
             "| | |", "|---|---|",
             f"| When | {facts['date_long']}, {facts['time_range']} |",
             f"| Where | {facts['venue'].replace(chr(10), ', ').replace('  ·  ', ', ')} |",
             f"| Format | {brief.get('format') or '[format]'} |",
             f"| Audience | {aud.get('who') or '[audience]'} ({aud.get('level') or '[level]'}) |",
             f"| Seats | {aud.get('capacity') or '[capacity]'} |",
             f"| Cost | {aud.get('cost') or '[cost]'} |",
             f"| Presenters | {facts['presenter_line']} |",
             f"| Contact | {facts['contact']} |", "",
             "## 2. Description", "",
             brief.get("summary") or "[One-sentence summary]", "",
             "**Listing abstract (about 100 words, for the department calendar and the registration form):**", "",
             "[Who it is for, what they will do, what they leave with, what to bring.]", "",
             "## 3. Learning objectives", "",
             "By the end of the workshop, participants can:", ""]
    lines += _list(brief.get("objectives"), "[Measurable objective: verb + task + condition]")
    lines += ["", "## 4. Prerequisites", "",
              "**Skills**", ""] + _list(pre.get("skills"), "None") + \
             ["", "**Hardware**", ""] + _list(pre.get("hardware"), "None") + \
             ["", "**Software (installed before arrival)**", ""] + _list(pre.get("software"), "None") + \
             ["", "**Accounts**", ""] + _list(pre.get("accounts"), "None") + \
             ["", "**Provided on the day**", ""] + _list(pre.get("provided"), "Nothing extra") + \
             ["", "**Pre-work**", ""] + _list(pre.get("pre_work"), "None") + ["", "## 5. Modules", ""]
    slots = []
    try:
        slots = timeline(brief)
    except Exception:
        pass
    for number, module in enumerate(brief.get("modules") or [], start=1):
        mine = [s for s in slots if s.block.get("module") == module.get("id")]
        minutes = sum(s.minutes for s in mine)
        span = f"{ap_time_range(mine[0].start, mine[-1].end)}, {minutes} min" if mine else "[time]"
        activity = module.get("activity") or {}
        lines += [f"### 5.{number} {module.get('title', '[Module title]')} ({span})", "",
                  f"**Purpose.** {module.get('summary') or '[Why this module, in two sentences]'}", "",
                  "**Objectives.**", ""] + _list(module.get("objectives"), "[Which course objectives it serves]") + \
                 ["", "**Content.**", ""] + _list(module.get("key_points"), "[Key point, with the example used]") + \
                 ["", "**Demo.** [What the presenter shows live, and the recorded fallback]", "",
                  f"**Hands-on activity: {activity.get('title') or '[title]'}** "
                  f"({activity.get('minutes') or '[minutes]'} min)", ""]
        lines += [f"{i}. {s}" for i, s in enumerate(activity.get("steps") or ["[Step]"], start=1)]
        lines += ["", f"- Done when: {activity.get('checkpoint') or '[observable result]'}",
                  f"- Stretch goal: {activity.get('stretch') or '[for fast finishers]'}",
                  f"- Code: `{module.get('code_dir') or '[code folder]'}`",
                  "- Common problems and fixes: [what helpers should expect]",
                  "- Check for understanding: [question or task that shows they got it]", ""]
    lines += ["## 6. Schedule", "", "The run-of-show with clock times is in [schedule.md](schedule.md).", "",
              "| Time | Block | Kind |", "|---|---|---|"]
    lines += [f"| {ap_clock(s.start)} | {s.block['title']} | {KIND_LABELS.get(s.kind, s.kind)} |" for s in slots]
    lines += ["", "## 7. Materials", "",
              "- Slides: `deliverables/` (.pptx and .pdf) with speaker notes in `slides/speaker-notes.md`",
              "- Code: `code/` (participant README, preflight check, starter and solution per activity)",
              "- Forms: `forms/` (registration and feedback, created with `create-forms.gs`)",
              "- Promotion: flyers and the hallway TV slide in `deliverables/`",
              "- Printed handouts: [if any]", "",
              "## 8. Roles, room and logistics", "",
              "- Helpers: [names; one per 8-10 participants for hands-on work]",
              "- Room setup: [tables, power strips, projector and adapters, microphone]",
              f"- Wi-Fi: {brief.get('where', {}).get('wifi') or '[network]'}",
              f"- Parking: {brief.get('where', {}).get('parking') or '[parking]'}",
              "- Accessibility: [step-free access, captions for any video, the request contact]",
              "- Food: [if any; dietary needs come from the registration form]", "",
              "## 9. Risks and fallbacks", "",
              "| Risk | Fallback |", "|---|---|",
              "| Installs fail on some laptops | Preflight a week ahead; pair people; [container or cloud image] |",
              "| Wi-Fi is slow | Packages on a USB stick or local mirror; repository cloned in advance |",
              "| Live demo fails | Recorded demo video in the deck |",
              "| Running late | Cut the stretch goals, never the breaks |", "",
              "## 10. Assessment and feedback", "",
              "- During: checkpoints at the end of each activity",
              "- After: the feedback form (QR code on the last slide), results reviewed within a week", "",
              "## 11. Promotion and communication timeline", ""]
    lines += promotion_timeline(brief)
    lines += ["", "## 12. Still to confirm", ""]
    lines += _list(brief.get("open_questions") + [f"Assumption: {a}" for a in brief.get("assumptions") or []],
                   "Nothing open")
    lines.append("")
    return "\n".join(lines)
