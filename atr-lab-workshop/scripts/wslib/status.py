"""What exists, what still has gaps, and the workshop folder's README.md (the hand-off index)."""
from __future__ import annotations

import re
from pathlib import Path

import re as _re

from .brief import check, derived, unresolved
from .common import read_json
from .deck import check_notes, speaker_notes
from .design import names, project_facts
from .schedule import pacing, timeline

LAYOUT = [
    ("workshop.json", "The brief: every fact the deliverables use"),
    ("outline.md", "Detailed outline of the workshop's material"),
    ("schedule.md", "Run-of-show with clock times, breaks, Q&A and pacing checks"),
    ("schedule.csv", "The same schedule for spreadsheets"),
    ("workshop.ics", "Calendar event for confirmations and reminders"),
    ("slides/deck.json", "Slide content (source for the deck)"),
    ("slides/speaker-notes.md", "Speaker notes in bullet form, one section per slide"),
    ("code/README.md", "Participant guide: before you come, activities"),
    ("code/preflight.py", "Setup check participants run before the workshop"),
    ("forms/create-forms.gs", "Google Apps Script that creates the Google Forms"),
    ("forms/forms-preview.md", "Every question on the forms, for review"),
    ("forms/IMPORT.md", "How to create the forms in Google Forms"),
]


# The design skill's placeholder pattern ([2] and [1-3] are citations), minus Markdown links and admonitions.
PLACEHOLDER = _re.compile(r"\[(?![!\d])[^\[\]\n]{1,80}\](?!\()")


def _brackets(path: Path) -> list:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    text = _re.sub(r"```.*?```|`[^`\n]*`", "", text, flags=_re.S)
    return sorted(set(PLACEHOLDER.findall(text)))


def _slide_strings(node, in_code=False):
    if isinstance(node, dict):
        code = in_code or bool(node.get("code")) or node.get("font") == "Source Code Pro"
        for key, value in node.items():
            if key not in ("notes", "speaker_notes"):
                yield from _slide_strings(value, code)
    elif isinstance(node, list):
        for value in node:
            yield from _slide_strings(value, in_code)
    elif isinstance(node, str) and not in_code:
        yield node


def collect(brief: dict, root: Path) -> dict:
    base = names(brief)
    deliverables = root / "deliverables"
    files = []
    for rel, what in LAYOUT:
        files.append((rel, what, (root / rel).exists()))
    for suffix, what in ((".pptx", "Presentation slides (PowerPoint)"), (".pdf", "Presentation slides (PDF)")):
        rel = f"deliverables/{base['deck']}{suffix}"
        files.append((rel, what, (root / rel).exists()))
    for size in (brief.get("promotion") or {}).get("flyer_sizes") or ["letter"]:
        for suffix in (".pdf", ".pptx"):
            rel = f"deliverables/{base['flyer']}-{size}{suffix}"
            files.append((rel, f"Flyer, {size} ({suffix[1:].upper()})", (root / rel).exists()))
    if (brief.get("promotion") or {}).get("tv_slide", True):
        rel = f"deliverables/{base['tv']}.jpg"
        files.append((rel, "Hallway TV promo slide (1920 x 1080)", (root / rel).exists()))
        if (brief.get("promotion") or {}).get("motion"):
            rel = f"deliverables/{base['tv']}.mp4"
            files.append((rel, "Hallway TV promo slide, animated (MP4)", (root / rel).exists()))
    files.append(("deliverables/qa-report.md", "Design QA report from the atr-lab-design skill",
                  (deliverables / "qa-report.md").exists()))

    needed = []
    for issue in check(brief):
        if issue.severity in ("required", "error"):
            needed.append(f"Answer: {issue.question} (`{issue.path}`)")
    for path, what in unresolved(brief):
        needed.append(f"Fill `{path}` in workshop.json: {what}")
    reg = brief.get("registration") or {}
    if not reg.get("url"):
        needed.append("Create the Google Forms (forms/IMPORT.md), then give the agent the registration and "
                      "feedback links: the flyers, the TV slide and the feedback slide use a placeholder "
                      "link (example.org) until then. Do not print or post them before.")
    elif not reg.get("feedback_url") and "feedback" in (reg.get("forms") or []):
        needed.append("Give the agent the feedback form link (forms/IMPORT.md): the last slide's QR code is a "
                      "placeholder.")
    try:
        for severity, message in pacing(brief, timeline(brief)):
            if severity in ("error", "warning"):
                needed.append(f"Schedule {severity}: {message}")
    except Exception as exc:
        needed.append(f"Schedule: {exc}")
    deck_json = root / "slides/deck.json"
    if deck_json.exists():
        spec = read_json(deck_json)
        brackets = set()
        for slide in spec.get("slides") or []:
            for text in _slide_strings(slide):
                brackets.update(PLACEHOLDER.findall(text))
            for note in slide.get("notes") or []:
                brackets.update(PLACEHOLDER.findall(str(note)))
        if brackets:
            needed.append(f"Slides: {len(brackets)} [placeholder]s left in slides/deck.json, for example "
                          + ", ".join(sorted(brackets)[:3]))
        for problem in check_notes(speaker_notes(spec, project_facts(brief))):
            needed.append(f"Speaker notes: {problem}")
    for rel in ("outline.md", "code/README.md"):
        left = _brackets(root / rel)
        if left:
            needed.append(f"{rel}: {len(left)} [placeholder]s left, for example " + ", ".join(left[:3]))
    code = root / "code"
    for module_dir in sorted(code.glob("[0-9][0-9]-*")) if code.is_dir() else []:
        for part in ("starter", "solution"):
            folder = module_dir / part
            if folder.is_dir() and not [p for p in folder.iterdir() if p.name != ".gitkeep"]:
                needed.append(f"Code: {module_dir.name}/{part}/ is empty")
    report = deliverables / "qa-report.md"
    if report.exists():
        text = report.read_text(encoding="utf-8", errors="replace")
        if re.search(r"working[- ]copy", text, re.I):
            needed.append("Swap in the official Kent State wordmark before anything is shared "
                          "(workshop.py official-logos; needs internet access to kent.edu).")
    needed += [
        "Look at every slide and flyer page yourself (renders are listed in deliverables/qa-report.md).",
        "Scan each QR code with a phone from a printed proof and from the TV.",
        "Approvals: printing through a Kent State contracted printer; the TV slide through the building's "
        "slideshow contact; anything with Kent State marks follows the brand rules.",
    ]
    needed += [f"Confirm assumption: {a}" for a in brief.get("assumptions") or []]
    needed += [f"Open question: {q}" for q in brief.get("open_questions") or []]
    return {"files": files, "needed": needed}


def render_readme(brief: dict, root: Path) -> str:
    facts = derived(brief)
    info = collect(brief, root)
    lines = [f"# {brief.get('title') or 'Workshop'}", "",
             f"{facts['date_long']}, {facts['time_range']} · {facts['venue'].replace(chr(10), ', ')}", "",
             "Workshop package built with the atr-lab-workshop skill on the atr-lab-design brand system. "
             "`workshop.json` holds the facts; rebuild after any change with `workshop.py build`.", "",
             "## Deliverables", "", "| File | What it is | Ready |", "|---|---|---|"]
    for rel, what, exists in info["files"]:
        lines.append(f"| [{rel}]({rel}) | {what} | {'yes' if exists else 'not yet'} |")
    lines += ["", "## Still needed from you", ""] + [f"- [ ] {n}" for n in info["needed"]] + [""]
    return "\n".join(lines)
