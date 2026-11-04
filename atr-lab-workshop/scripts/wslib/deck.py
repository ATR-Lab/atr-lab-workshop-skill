"""The workshop deck: a schedule-shaped skeleton for the design skill's new_deck.py, and the speaker notes."""
from __future__ import annotations

import json
import re
import struct
import zipfile
import zlib
from pathlib import Path

from .brief import derived
from .common import WorkshopError, ap_clock, read_json, write_json, write_text
from .design import project_facts
from .schedule import timeline

BULLET = "• "
CODE_BOX = {"x": 0.5, "y": 1.42, "w": 9.0, "h": 3.2}
CODE_TEXT_BOX = {"x": 0.68, "y": 1.56, "w": 8.64, "h": 2.95}
MIST = (0xF3, 0xF6, 0xFA)
FACT = re.compile(r"\{\{\s*facts\.([A-Za-z0-9_]+)\s*(?:\|\s*([a-z]+))?\s*\}\}")
TITLE_FIELDS = ("title", "statement", "event_title")


TITLE_BUDGET = 38


def fit(prefix: str, text: str) -> str:
    """'Hands-on: X' when it fits the 38-character title budget, else just X."""
    return f"{prefix}{text}" if len(prefix + text) <= TITLE_BUDGET else text


def notes(*lines: str) -> list:
    return [BULLET + line for line in lines]


def _png(path: Path, rgb: tuple, width: int = 1350, height: int = 480) -> None:
    """A flat-color PNG at the code panel's aspect and 150 ppi, written with the standard library."""
    row = b"\x00" + bytes(rgb) * width
    raw = zlib.compress(row * height, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", raw) + chunk(b"IEND", b""))


def ensure_panel(slides_dir: Path) -> Path:
    panel = slides_dir / "code-panel-mist.png"
    if not panel.exists() or panel.stat().st_size < 200:
        _png(panel, MIST)
    return panel


def code_slide(title: str, code: str, section: int = 0, speaker: list = None) -> dict:
    """A titled slide whose body is editable Source Code Pro text on a mist panel (no code layout exists)."""
    slide = {"layout": "ATR - Title + Content", "title": title, "body": "",
             "images": [{"path": "{{assets.code-panel}}", "alt": "", "decorative": True, "box": CODE_BOX,
                         "fit": "contain"}],
             "textboxes": [{"text": code, "box": CODE_TEXT_BOX, "size": 16, "font": "Source Code Pro",
                            "color": "1B2533", "code": True}],
             "notes": speaker or notes("[Walk through the code line by line: what each part does]",
                                       "[Ask: what do you expect this prints?]")}
    if section:
        slide["section"] = section
    return slide


def skeleton(brief: dict, slides_dir: Path) -> dict:
    """One slide (or a few) per schedule block, in order, with the brief's facts and [brackets] for content."""
    slots = timeline(brief)
    facts = derived(brief)
    pfacts = project_facts(brief)
    modules = brief.get("modules") or []
    kinds = [s.kind for s in slots]
    rows = [("module", m) for m in modules[:5]]
    if len(rows) < 5 and "setup" in kinds:
        rows.insert(0, ("setup", {"title": "Setup check"}))
    if len(rows) < 5 and ({"qa", "wrap-up"} & set(kinds)):
        rows.append(("wrap", {"title": "Questions and wrap-up"}))
    module_index = {m["id"]: i + 1 for i, (kind, m) in enumerate(rows) if kind == "module"}
    module_by_id = {m["id"]: m for m in modules}
    ensure_panel(slides_dir)
    first_clock = {}
    for slot in slots:
        mid = slot.block.get("module")
        if mid and mid not in first_clock:
            first_clock[mid] = slot.clock

    out = [{
        "layout": "ATR - Title",
        "eyebrow": "WORKSHOP  ·  {{facts.event_date_short|upper}}",
        "title": "{{facts.event_title_plain}}",
        "subtitle": "{{facts.subtitle}}",
        "presenter": "{{facts.presenter_line}}",
        "notes": notes("Welcome everyone; introduce yourself and the Advanced Telerobotics Research Lab.",
                       "Say in one sentence what they will be able to do by the end.",
                       f"Time: we run {facts['time_range']}; doors close the session at {ap_clock(slots[-1].end)}."),
    }]
    logistics = []
    if pfacts["wifi"]:
        logistics.append("Wi-Fi: {{facts.wifi}}")
    breaks = [s for s in slots if s.kind in ("break", "lunch")]
    if breaks:
        logistics.append("Breaks: " + ", ".join(f"{ap_clock(s.start)}{' (lunch)' if s.kind == 'lunch' else ''}"
                                                for s in breaks))
    logistics.append("Stuck? Raise a hand and a helper comes to you")
    if pfacts["repo_url"]:
        logistics.append("Materials: {{facts.repo_url}}")
    logistics.append("Questions are welcome at any time")
    out.append({"layout": "ATR - Title + Content", "title": "Before we start", "body": logistics,
                "notes": notes("Point out restrooms, exits and where the helpers are.",
                               "Repeat the break times; they are also on the schedule.",
                               "Explain how to ask for help during the hands-on parts.")})
    if modules:
        agenda = {"layout": "ATR - Agenda", "eyebrow": "TODAY", "title": "Agenda",
                  "panel": [["WHEN"], "{{facts.event_date_short}}", "{{facts.time_range}}",
                            ["WHERE"], "{{facts.venue_short}}"],
                  "notes": notes("Walk through the parts; each one ends with something they build or run.",
                                 "The clock times are when each part starts.")}
        for i, (kind, module) in enumerate(rows, start=1):
            agenda[f"item{i}"] = module.get("agenda_title") or module["title"]
            if kind == "module" and module["id"] in first_clock:
                agenda[f"timing{i}"] = first_clock[module["id"]]
            elif kind == "setup":
                agenda[f"timing{i}"] = next(s.clock for s in slots if s.kind == "setup")
            elif kind == "wrap":
                agenda[f"timing{i}"] = next(s.clock for s in slots if s.kind in ("qa", "wrap-up"))
        out.append(agenda)
    if brief.get("objectives"):
        out.append({"layout": "ATR - Title + Content", "title": "By the end, you can",
                    "body": list(brief["objectives"][:6]),
                    "notes": notes("Read the objectives aloud; we come back to them at the wrap-up.",
                                   "Ask who has done any of these before, to calibrate the pace.")})

    seen_modules: set = set()
    for n, slot in enumerate(slots):
        block = slot.block
        kind = slot.kind
        mid = block.get("module")
        module = module_by_id.get(mid, {})
        section = module_index.get(mid, 0)
        nxt = slots[n + 1].block["title"] if n + 1 < len(slots) else ""
        if mid and mid not in seen_modules and kind not in ("break", "lunch"):
            seen_modules.add(mid)
            if section:
                out.append({"layout": "ATR - Section Divider", "section": section,
                            "subtitle": module.get("summary") or f"[What part {section} is about, in one line]",
                            "notes": notes(f"Part {section}: {module.get('title', '')}.",
                                           f"Time: {slot.minutes} min for this block, until {ap_clock(slot.end)}.",
                                           "[Why this part matters for what they will build]")})
        tag = {"section": section} if section else {}
        if kind in ("welcome",):
            continue
        if kind == "setup":
            out.append({"layout": "ATR - Title + Content", "title": "Check your setup",
                        "body": ["Open a terminal in the workshop folder", "Run the preflight check:",
                                 ["python3 preflight.py"], "Green: you are ready",
                                 "Red: raise a hand, a helper will fix it with you"],
                        "notes": notes(f"Time: {slot.minutes} min. Everyone runs the preflight before we start.",
                                       "Helpers walk the room; pair anyone whose setup fails with a neighbor.",
                                       "Do not move on until most of the room is green.")})
        elif kind == "talk":
            points = module.get("key_points") or [f"[Key idea {i} of {block['title']}]" for i in (1, 2)]
            for point in points:
                out.append({"layout": "ATR - Title + Content", **tag, "title": point,
                            "body": ["[Point that explains it]", "[Example or analogy]", "[Why it matters here]"],
                            "notes": notes("[What to say first]", "[The example to show]",
                                           "[Question to ask the room]")})
        elif kind == "demo":
            out.append({"layout": "ATR - Title + Content", **tag, "title": fit("Demo: ", block["title"]),
                        "body": ["What to watch for:", ["[Thing 1]"], ["[Thing 2]"], ["[Thing 3]"]],
                        "notes": notes(f"Time: {slot.minutes} min.", "[The command or steps you run live]",
                                       "Have a recording ready in case the live demo fails.")})
        elif kind == "hands-on":
            activity = module.get("activity") or {}
            steps = activity.get("steps") or [f"[Step {i}]" for i in (1, 2, 3)]
            task = {**tag, "title": fit("Hands-on: ", activity.get("title") or block["title"]),
                    "notes": notes(f"Time: {slot.minutes} min, until {ap_clock(slot.end)}.",
                                   "Read the steps; say where the starter code is.",
                                   "Walk the room; note common problems to address at the checkpoint.")}
            if len(steps) == 5:
                task["layout"] = "ATR - Timeline"
                for i, step in enumerate(steps, start=1):
                    task[f"date{i}"] = f"STEP {i}"
                    task[f"step{i}"] = step
            else:
                task["layout"] = "ATR - Title + Content"
                task["body"] = [f"{i}. {step}" for i, step in enumerate(steps[:6], start=1)]
                task["body"].append(f"Time: {slot.minutes} min, until {ap_clock(slot.end)}")
            out.append({"layout": task.pop("layout"), **task})
            body = [f"Done when: {activity.get('checkpoint') or '[what they see when it works]'}"]
            if activity.get("stretch"):
                body.append(f"Finished early? {activity['stretch']}")
            if module.get("code_dir"):
                body.append(f"Starter code: {module['code_dir']}/starter")
            body.append("Stuck for 5 minutes? Raise a hand")
            label = module.get("agenda_title") or module.get("title") or ""
            check_title = fit("Checkpoint: ", label) if len("Checkpoint: " + label) <= TITLE_BUDGET else \
                f"Checkpoint, part {section or len(seen_modules)}"
            out.append({"layout": "ATR - Title + Content", **tag, "title": check_title, "body": body,
                        "notes": notes("Show what success looks like before they start.",
                                       "At the end, ask two people to share what they saw.",
                                       f"Solutions are in {module.get('code_dir') or 'the solution folder'}.")})
        elif kind in ("break", "lunch"):
            word = "Lunch" if kind == "lunch" else "Break"
            out.append({"layout": "ATR - Statement", "eyebrow": word.upper(),
                        "statement": f"{word}: back at {ap_clock(slot.end)}",
                        "attribution": f"Next: {nxt}" if nxt else "",
                        "notes": notes(f"{slot.minutes} min. Say the return time out loud.",
                                       "Leave this slide up for the whole break.")})
        elif kind == "qa":
            out.append({"layout": "ATR - Statement", "eyebrow": "QUESTIONS",
                        "statement": "What questions do you have?", "attribution": "{{facts.presenter_line}}",
                        "notes": notes(f"Time: {slot.minutes} min.", "Repeat each question for the room.",
                                       "Park anything off-topic and follow up by email.")})
        elif kind == "discussion":
            out.append({"layout": "ATR - Title + Content", **tag, "title": fit("Discuss: ", block["title"]),
                        "body": ["[Prompt 1]", "[Prompt 2]", "Pairs for 5 min, then share"],
                        "notes": notes(f"Time: {slot.minutes} min.", "[What a good answer includes]")})
        elif kind == "wrap-up":
            body = list(brief.get("objectives") or [])[:4] or ["[What they can do now]"]
            out.append({"layout": "ATR - Title + Content", "title": "What you can do now", "body": body,
                        "notes": notes("Go back to the objectives from the start; ask for a show of hands.",
                                       "Point to the materials and what to try next.")})
        elif kind == "feedback":
            pass
    out.append({"layout": "ATR - Content + Image", "title": "Tell us how it went",
                "subhead": "Two minutes, anonymous", "body": ["Scan the code", "Or open the link below"],
                "figure": {"qr": {"url": "{{facts.feedback_url}}", "size_in": 1.6}},
                "figure_alt": "QR code that opens the workshop feedback form.",
                "caption": "FEEDBACK // {{facts.feedback_url|printed}}",
                "notes": notes("Ask everyone to fill in the form before they leave; it takes two minutes.",
                               "Leave this slide up while people pack up.")})
    out.append({"layout": "ATR - Thank You", "title": "Thank you", "presenter": "{{facts.presenter_name}}",
                "email": "{{facts.presenter_email}}", "message": "Questions and collaboration welcome.",
                "notes": notes("Thank the helpers and the hosts.", "Remind them where the materials live.")})
    return {"_comment": "Workshop deck for the atr-lab-design skill's new_deck.py, built through design/project.json. "
                        "{{facts.x}} comes from workshop.json. Replace every [bracket]; every slide keeps 2-6 "
                        "bullet speaker notes starting with '• '. Code slides: see references/slides-and-notes.md.",
            "template": "presentation", "title": "{{facts.event_title_plain}}",
            "author": "Advanced Telerobotics Research Lab", "motion": (brief.get("promotion") or {}).get("motion") or None,
            "slides": out}


def write_skeleton(brief: dict, slides_dir: Path, force: bool) -> Path:
    path = slides_dir / "deck.json"
    if path.exists() and not force:
        raise WorkshopError(f"{path} exists: edit it, or pass --force to start over (your edits are lost)")
    spec = skeleton(brief, slides_dir)
    if not spec.get("motion"):
        spec.pop("motion")
    write_json(path, spec)
    return path


# --------------------------------------------------------------------------- code brackets

# new_deck.py refuses any [text] on a slide as a leftover placeholder, which code (grid[row], ["a", "b"]) is not.
# Code text boxes are built with look-alike brackets, which unmask() turns back into [ and ] in the .pptx.
MASK = {"[": "\u27e6", "]": "\u27e7"}


def build_copy(spec: dict) -> dict:
    """deck.json as new_deck.py should see it: brackets inside code text boxes masked, the "code" flag dropped."""
    out = json.loads(json.dumps(spec))
    for slide in out.get("slides") or []:
        for box in slide.get("textboxes") or []:
            if box.pop("code", False) or box.get("font") == "Source Code Pro":
                box["text"] = "".join(MASK.get(ch, ch) for ch in str(box.get("text", "")))
    return out


def unmask(pptx: Path) -> int:
    """Put the real brackets back into every slide of a built .pptx; returns how many slides changed."""
    if not pptx.is_file():
        return 0
    back = {v: k for k, v in MASK.items()}
    changed = 0
    tmp = pptx.with_suffix(".unmask.tmp")
    with zipfile.ZipFile(pptx) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename.startswith("ppt/slides/slide") and info.filename.endswith(".xml"):
                text = data.decode("utf-8")
                if any(ch in text for ch in back):
                    text = "".join(back.get(ch, ch) for ch in text)
                    data = text.encode("utf-8")
                    changed += 1
            dst.writestr(info, data)
    if changed:
        tmp.replace(pptx)
    else:
        tmp.unlink()
    return changed


# --------------------------------------------------------------------------- speaker notes

def resolve(text: str, facts: dict) -> str:
    def sub(match: re.Match) -> str:
        value = facts.get(match.group(1), "")
        if isinstance(value, list):
            value = "; ".join(v if isinstance(v, str) else " - ".join(v) for v in value)
        value = str(value)
        flt = match.group(2)
        if flt == "upper":
            return value.upper()
        if flt == "lower":
            return value.lower()
        if flt == "capitalize":
            return value[:1].upper() + value[1:]
        if flt == "printed":
            return re.sub(r"^https?://", "", value).rstrip("/")
        return value
    return FACT.sub(sub, text)


def _title(slide: dict, facts: dict, number: int) -> str:
    fields = slide.get("fields") or {}
    for key in TITLE_FIELDS:
        value = slide.get(key, fields.get(key))
        if isinstance(value, str) and value.strip():
            return resolve(value, facts).replace("\n", " ")
    if slide.get("layout") == "ATR - Section Divider":
        return f"Section {slide.get('section', '')}"
    return f"Slide {number} ({slide.get('layout', '?')})"


def speaker_notes(spec: dict, facts: dict) -> list:
    rows = []
    for number, slide in enumerate(spec.get("slides") or [], start=1):
        raw = slide.get("speaker_notes", slide.get("notes"))
        lines = raw if isinstance(raw, list) else [ln for ln in str(raw or "").split("\n") if ln.strip()]
        rows.append((number, _title(slide, facts, number), [resolve(str(ln), facts) for ln in lines]))
    return rows


def check_notes(rows: list) -> list:
    problems = []
    for number, title, lines in rows:
        if len(lines) < 2:
            problems.append(f"slide {number} ({title}): needs at least two speaker-note bullets")
        if len(lines) > 8:
            problems.append(f"slide {number} ({title}): {len(lines)} bullets; keep notes to eight or fewer")
        for line in lines:
            if not line.startswith(("• ", "- ")):
                problems.append(f"slide {number} ({title}): note {line[:40]!r} is not a bullet (start with '• ')")
            if len(line) > 220:
                problems.append(f"slide {number} ({title}): a note bullet runs {len(line)} characters; split it")
    return problems


CODE_MAX_LINES = 11      # 2.95 in of 16 pt Source Code Pro at single spacing
CODE_MAX_CHARS = 64      # 8.64 in at 0.6 em per character


def check_code(spec: dict) -> list:
    """Code text boxes that would wrap or overflow the panel (PowerPoint wraps; nothing measures mono text)."""
    problems = []
    for number, slide in enumerate(spec.get("slides") or [], start=1):
        for box in slide.get("textboxes") or []:
            if not (box.get("code") or box.get("font") == "Source Code Pro"):
                continue
            size = float(box.get("size", 16))
            lines = str(box.get("text", "")).split("\n")
            max_chars = int(CODE_MAX_CHARS * 16 / size)
            max_lines = int(CODE_MAX_LINES * 16 / size)
            if len(lines) > max_lines:
                problems.append(f"slide {number}: code has {len(lines)} lines; {max_lines} fit at {size:g} pt")
            for line in lines:
                if len(line) > max_chars:
                    problems.append(f"slide {number}: code line of {len(line)} characters wraps (at most "
                                    f"{max_chars} at {size:g} pt): {line.strip()[:40]!r}")
    return problems


def write_notes(spec_path: Path, facts: dict, out_path: Path, title: str) -> list:
    spec = read_json(spec_path)
    rows = speaker_notes(spec, facts)
    lines = [f"# Speaker notes: {title}", "",
             "One section per slide, in deck order. The same bullets are in each slide's notes in the .pptx "
             "(PowerPoint: View > Notes; Presenter View shows them while you present).", ""]
    for number, slide_title, bullets in rows:
        lines += [f"## Slide {number}: {slide_title}", ""]
        lines += [("- " + b[2:]) if b.startswith("• ") else b for b in bullets] or ["- (no notes yet)"]
        lines.append("")
    write_text(out_path, "\n".join(lines))
    return check_notes(rows) + check_code(spec)
