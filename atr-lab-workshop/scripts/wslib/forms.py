"""Google Forms: default registration and feedback specs from the brief, validation, a preview and the Apps Script.

Google Forms has no file import. The importable file is an Apps Script (create-forms.gs) that builds each form
from its .form.json spec when the presenter runs it at script.google.com.
"""
from __future__ import annotations

import json
from pathlib import Path

from .brief import derived
from .common import SKILL_ROOT, WorkshopError, read_json, write_json, write_text

ITEM_TYPES = {"short_text", "email", "number", "paragraph", "multiple_choice", "checkboxes", "dropdown", "scale",
              "grid", "checkbox_grid", "date", "time", "section_header"}
CHOICE_TYPES = {"multiple_choice", "checkboxes", "dropdown"}
GRID_TYPES = {"grid", "checkbox_grid"}
EXPERIENCE = ["None yet", "Some", "Comfortable", "Very comfortable"]
AGREEMENT = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]
ROLES = ["Undergraduate student", "Graduate student", "Faculty", "Staff", "Industry or community", "K-12 educator"]
OSES = ["macOS", "Windows", "Linux", "ChromeOS", "I don't have a laptop"]


def _plain(text: str) -> str:
    return " ".join(str(text).split())


def registration_spec(brief: dict) -> dict:
    facts = derived(brief)
    pre = brief.get("prerequisites") or {}
    skills = [s for s in pre.get("skills") or [] if s.strip().lower() != "none"]
    hardware = [h for h in pre.get("hardware") or [] if h.strip().lower() != "none"]
    software = pre.get("software") or []
    has_meal = any(b.get("kind") == "lunch" for b in brief.get("schedule") or [])
    deadline = (brief.get("registration") or {}).get("deadline")
    where = facts["venue"].replace("\n", ", ").replace("  ·  ", ", ")

    about = [
        {"type": "short_text", "title": "Full name", "required": True},
        {"type": "email", "title": "Email address", "required": True,
         "help": "We send the setup guide and any changes here."},
        {"type": "multiple_choice", "title": "Which best describes you?", "choices": ROLES, "other": True,
         "required": True},
        {"type": "short_text", "title": "Department, program or organization", "required": False},
    ]
    background = []
    if skills:
        background.append({"type": "grid", "title": "How comfortable are you with each of these?",
                           "help": "This helps us pair people and pace the hands-on parts. There are no wrong "
                                   "answers.", "rows": skills, "columns": EXPERIENCE, "required": True})
    background.append({"type": "paragraph", "title": "What do you hope to learn or build?", "required": False})

    setup = []
    if hardware or software:
        setup.append({"type": "multiple_choice", "title": "Which operating system will your laptop run?",
                      "choices": OSES, "other": True, "required": True})
        needs = hardware + [f"Installed: {s}" for s in software]
        setup.append({"type": "checkboxes", "title": "Check what you will have ready on the day",
                      "help": "We email setup steps after you register. Leave a box empty if you need help.",
                      "choices": needs, "required": False})
        setup.append({"type": "paragraph", "title": "Anything about your setup we should know?",
                      "required": False})

    logistics = [
        {"type": "paragraph", "title": "Do you need any accommodations to take part fully?",
         "help": "Optional. Only the organizers see this, and we follow up privately.", "required": False},
        {"type": "multiple_choice", "title": "Photos may be taken for the lab's news and social media. Your "
                                             "preference:",
         "choices": ["Photos of me are fine", "Please do not photograph me"], "required": True},
    ]
    if has_meal:
        logistics.insert(1, {"type": "short_text", "title": "Dietary needs for the meal (optional)",
                             "required": False})
    for extra in (brief.get("registration") or {}).get("extra_questions") or []:
        logistics.append(extra)

    sections = [{"title": "About you", "items": about},
                {"title": "Your background", "items": background}]
    if setup:
        sections.append({"title": "Your setup", "items": setup,
                         "description": "What participants need: " + "; ".join(hardware + software)})
    sections.append({"title": "Logistics", "items": logistics})

    description = (f"{_plain(brief.get('summary') or '')}\n\n"
                   f"When: {facts['date_long']}, {facts['time_range']}\n"
                   f"Where: {where}\n"
                   f"Hosted by the Advanced Telerobotics Research Lab, Department of Computer Science, Kent State "
                   f"University.")
    if deadline:
        description += f"\nRegister by: {deadline}"
    capacity = (brief.get("audience") or {}).get("capacity")
    if capacity:
        description += f"\nSeats: {capacity}, first come, first served."
    description += f"\nQuestions: {facts['contact']}"
    return {
        "key": "registration",
        "title": f"Register: {brief.get('title') or '[Workshop title]'}",
        "description": description.strip(),
        "confirmation": f"You're registered for {brief.get('title')} on {facts['date_long']}. We'll email setup "
                        f"steps before the workshop. Questions: {facts['contact']}",
        "closed_message": f"Registration is full or closed. Questions: {facts['contact']}",
        "collect_email": False,
        "progress_bar": True,
        "responses_sheet": True,
        "capacity": capacity or None,
        "sections": sections,
    }


def feedback_spec(brief: dict) -> dict:
    facts = derived(brief)
    objectives = [_plain(o) for o in brief.get("objectives") or []]
    items = [
        {"type": "scale", "title": "Overall, how useful was this workshop?", "low": 1, "high": 5,
         "low_label": "Not useful", "high_label": "Very useful", "required": True},
    ]
    if objectives:
        items.append({"type": "grid", "title": "After today, I can...", "rows": objectives[:8],
                      "columns": AGREEMENT, "required": True})
    items += [
        {"type": "multiple_choice", "title": "The pace was", "choices": ["Too slow", "About right", "Too fast"],
         "required": True},
    ]
    if any(b.get("kind") == "hands-on" for b in brief.get("schedule") or []):
        items.append({"type": "scale", "title": "How helpful were the hands-on activities?", "low": 1, "high": 5,
                      "low_label": "Not helpful", "high_label": "Very helpful", "required": True})
        items.append({"type": "multiple_choice", "title": "Did your setup work during the hands-on parts?",
                      "choices": ["Yes, the whole time", "After some help", "No"], "required": False})
    items += [
        {"type": "paragraph", "title": "What was most useful?", "required": False},
        {"type": "paragraph", "title": "What should we change next time?", "required": False},
        {"type": "paragraph", "title": "Which topics would you like a future workshop on?", "required": False},
        {"type": "email", "title": "Email, if you'd like to hear about future workshops (optional)",
         "required": False},
    ]
    return {
        "key": "feedback",
        "title": f"Feedback: {brief.get('title') or '[Workshop title]'}",
        "description": f"Thank you for coming to {brief.get('title')} on {facts['date_short']}. This takes about "
                       "two minutes and is anonymous unless you add your email.",
        "confirmation": "Thank you. Your answers shape the next workshop.",
        "collect_email": False,
        "progress_bar": False,
        "responses_sheet": True,
        "sections": [{"title": "Your feedback", "items": items}],
    }


DEFAULT_BUILDERS = {"registration": registration_spec, "feedback": feedback_spec}


def init_specs(brief: dict, folder: Path, force: bool = False) -> list:
    written = []
    for key in (brief.get("registration") or {}).get("forms") or ["registration", "feedback"]:
        path = folder / f"{key}.form.json"
        if path.exists() and not force:
            print(f"kept {path} (exists; --force to regenerate)")
            continue
        builder = DEFAULT_BUILDERS.get(key)
        if not builder:
            raise WorkshopError(f"no default for form {key!r}: write {path} by hand (references/google-forms.md)")
        write_json(path, builder(brief))
        written.append(path)
    return written


def validate(spec: dict, where: str) -> list:
    errors = []
    for field in ("key", "title", "sections"):
        if not spec.get(field):
            errors.append(f"{where}: needs {field!r}")
    for s, section in enumerate(spec.get("sections") or []):
        for i, item in enumerate(section.get("items") or []):
            loc = f"{where} › sections[{s}].items[{i}] ({item.get('title', '?')!r})"
            kind = item.get("type")
            if kind not in ITEM_TYPES:
                errors.append(f"{loc}: type {kind!r} is not one of {', '.join(sorted(ITEM_TYPES))}")
                continue
            if not str(item.get("title", "")).strip():
                errors.append(f"{loc}: needs a title")
            if kind in CHOICE_TYPES and len(item.get("choices") or []) < 2:
                errors.append(f"{loc}: needs at least two choices")
            if kind in GRID_TYPES and (not item.get("rows") or len(item.get("columns") or []) < 2):
                errors.append(f"{loc}: needs rows and at least two columns")
            if kind == "scale":
                low, high = int(item.get("low", 1)), int(item.get("high", 5))
                if low not in (0, 1) or not 3 <= high <= 10 or high <= low:
                    errors.append(f"{loc}: Google Forms scales run from 0 or 1 up to 3-10")
            for choice_list in ("choices", "rows", "columns"):
                values = item.get(choice_list) or []
                if len(set(values)) != len(values):
                    errors.append(f"{loc}: duplicate {choice_list} (Google Forms rejects them)")
    return errors


def preview(specs: list) -> str:
    lines = ["# Google Forms preview", "",
             "What each form will ask. Review it with the presenter before running `create-forms.gs`.", ""]
    for spec in specs:
        lines += [f"## {spec['title']}", "", spec.get("description", "").replace("\n", "  \n"), ""]
        extras = []
        if spec.get("capacity"):
            extras.append(f"closes itself after {spec['capacity']} responses")
        if spec.get("responses_sheet"):
            extras.append("saves responses to a new Google Sheet")
        if extras:
            lines += ["*Settings: " + "; ".join(extras) + ".*", ""]
        number = 0
        for section in spec["sections"]:
            lines += [f"### {section['title']}", ""]
            if section.get("description"):
                lines += [f"_{section['description']}_", ""]
            for item in section.get("items") or []:
                number += 1
                req = " *(required)*" if item.get("required") else ""
                lines.append(f"{number}. **{item['title']}**{req}: {item['type'].replace('_', ' ')}")
                if item.get("help"):
                    lines.append(f"   - _{item['help']}_")
                for choice in item.get("choices") or []:
                    lines.append(f"   - ( ) {choice}")
                if item.get("other"):
                    lines.append("   - ( ) Other: ____")
                if item.get("rows"):
                    lines.append(f"   - rows: {'; '.join(item['rows'])}")
                    lines.append(f"   - columns: {' | '.join(item['columns'])}")
                if item["type"] == "scale":
                    lines.append(f"   - {item.get('low', 1)} ({item.get('low_label', '')}) to {item.get('high', 5)} "
                                 f"({item.get('high_label', '')})")
            lines.append("")
        lines += [f"> Confirmation message: {spec.get('confirmation', '')}", ""]
    return "\n".join(lines)


def build(folder: Path) -> list:
    """Validate every *.form.json in the folder and write create-forms.gs and forms-preview.md."""
    paths = sorted(folder.glob("*.form.json"))
    if not paths:
        raise WorkshopError(f"{folder}: no *.form.json specs (run: workshop.py forms init)")
    paths.sort(key=lambda p: (p.name != "registration.form.json", p.name))
    specs, errors = [], []
    for path in paths:
        spec = read_json(path)
        errors += validate(spec, path.name)
        specs.append(spec)
    keys = [s.get("key") for s in specs]
    if len(set(keys)) != len(keys):
        errors.append("two form specs share a key")
    if errors:
        raise WorkshopError("form specs have problems:\n  " + "\n  ".join(errors))
    template = (SKILL_ROOT / "assets/templates/create-forms.gs.tmpl").read_text(encoding="utf-8")
    payload = json.dumps(specs, indent=2, ensure_ascii=False)
    script = (template.replace("/*__FORMS__*/", payload)
              .replace("__TITLE__", "Workshop forms: " + ", ".join(s["title"] for s in specs))
              .replace("__SOURCES__", ", ".join(p.name for p in paths)))
    write_text(folder / "create-forms.gs", script)
    write_text(folder / "forms-preview.md", preview(specs))
    howto = (SKILL_ROOT / "assets/templates/IMPORT-FORMS.md").read_text(encoding="utf-8")
    write_text(folder / "IMPORT.md", howto)
    return [folder / "create-forms.gs", folder / "forms-preview.md", folder / "IMPORT.md"]
