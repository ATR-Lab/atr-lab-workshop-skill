"""Hand-off to the atr-lab-design skill: the design project (deck + flyers), its builds and the hallway TV slide."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .brief import derived
from .common import (WorkshopError, find_design_python, find_design_skill, read_json, run, sha256_of,
                     write_json)
from .schedule import timeline

FLYER_TEMPLATES = {"letter": ("event-flyer", "8.5 x 11 in", "document"),
                   "tabloid": ("event-flyer-tabloid", "11 x 17 in", "document"),
                   "17x22": ("event-flyer-17x22", "17 x 22 in", "poster")}
PLACEHOLDER_URL = "https://example.org/register"
PLACEHOLDER_FEEDBACK = "https://example.org/feedback"
PANEL_URL_BUDGET = 20   # the smallest registration_url budget across the flyer sizes (Tabloid)


def names(brief: dict) -> dict:
    """Deliverable base names in the design skill's atr-[piece]-[topic]-[yyyy-mm-dd] pattern."""
    facts = derived(brief)
    slug = facts["slug"]
    date = brief["when"].get("date") or ""
    topic = slug[:-len(date)].strip("-") if date and slug.endswith(date) else slug
    stem = f"{topic}-{date}".strip("-")
    return {"deck": f"atr-deck-{stem}", "flyer": f"atr-flyer-{stem}", "tv": f"atr-tv-{stem}"}


def project_facts(brief: dict) -> dict:
    """Facts for design/project.json; deck.json and flyer.json reach them as {{facts.NAME}}."""
    facts = derived(brief)
    promo = brief.get("promotion") or {}
    pre = brief.get("prerequisites") or {}
    reg = brief.get("registration") or {}
    title = brief.get("title") or "[Workshop title]"
    modules = brief.get("modules") or []
    skills = [s for s in pre.get("skills") or [] if s.strip().lower() != "none"]
    level = brief.get("audience", {}).get("level") or ""
    audience_lines = [brief.get("audience", {}).get("who") or "[Who it is for]"]
    audience_lines.append(promo.get("experience") or (f"{level.capitalize()} level" if level and level != "mixed"
                                                       else "All levels") +
                          ("" if skills else ", no experience needed"))
    cost = brief.get("audience", {}).get("cost")
    capacity = brief.get("audience", {}).get("capacity")
    extra = "  ·  ".join(x for x in (cost, f"{capacity} seats" if capacity else "") if x)
    if extra:
        audience_lines.append(extra)
    needs = [h for h in pre.get("hardware") or [] if h.strip().lower() != "none"] + (pre.get("software") or [])
    requirements = promo.get("requirements") or ("Bring: " + "; ".join(needs) + "." if needs else
                                                 "Everything you need is provided.")
    breaks = []
    try:
        for slot in timeline(brief):
            if slot.kind in ("break", "lunch"):
                breaks.append(f"{slot.start:%H:%M} {'lunch' if slot.kind == 'lunch' else 'break'}")
    except WorkshopError:
        pass
    return {
        "event_title": promo.get("flyer_title") or title,
        "event_title_plain": title,
        "subtitle": brief.get("subtitle") or "Hands-on workshop",
        "eyebrow": promo.get("eyebrow") or "HANDS-ON WORKSHOP  ·  ATR LAB",
        "summary": brief.get("summary") or "[One sentence on what people learn or do.]",
        "event_date": facts["date_long"],
        "event_date_short": facts["date_short"],
        "event_date_tv": facts["date_tv"],
        "event_time": brief["when"].get("check_in") and f"{facts['time_range']}\nCheck-in {brief['when']['check_in']}"
                      or facts["time_range"],
        "time_range": facts["time_range"],
        "event_duration": promo.get("registration_head") or facts["duration"] or "Register now",
        "venue": facts["venue"],
        "venue_short": facts["venue_short"],
        "audience": promo.get("audience") or "\n".join(audience_lines),
        "agenda": promo.get("agenda") or [m.get("title", "") for m in modules[:3]] or ["[What you will do]"],
        "requirements": requirements,
        "workflow": promo.get("workflow") or [[m.get("verb") or f"Part {i + 1}", m.get("title", "")]
                                              for i, m in enumerate(modules[:3])],
        "registration_url": reg.get("url") or PLACEHOLDER_URL,
        "printed_url": reg.get("printed_url") or "",
        "feedback_url": reg.get("feedback_url") or PLACEHOLDER_FEEDBACK,
        "contact": "Questions: " + facts["contact"],
        "presenter_line": facts["presenter_line"],
        "presenter_name": (brief.get("presenters") or [{}])[0].get("name") or "[Presenter Name]",
        "presenter_email": facts["contact"],
        "wifi": brief.get("where", {}).get("wifi") or "",
        "repo_url": brief.get("materials", {}).get("repo_url") or "",
        "breaks": ", ".join(breaks),
    }


def flyer_spec(brief: dict) -> dict:
    promo = brief.get("promotion") or {}
    slide = {
        "layout": "Workshop flyer",
        "eyebrow": "{{facts.eyebrow}}",
        "event_title": "{{facts.event_title}}",
        "event_subtitle": "{{facts.summary}}",
        "event_date": "{{facts.event_date}}",
        "event_time": "{{facts.event_time}}",
        "venue": "{{facts.venue}}",
        "audience": "{{facts.audience}}",
        "agenda": "{{facts.agenda}}",
        "requirements": "{{facts.requirements}}",
        "workflow": "{{facts.workflow}}",
        "registration_head": "{{facts.event_duration}}",
        "registration_qr": {"qr": {"url": "{{facts.registration_url}}"}},
        "contact": "{{facts.contact}}",
        "notes": "Workshop flyer built by atr-lab-workshop from workshop.json. The QR code and the printed address "
                 "point to the registration form. The Kent State wordmark must be the official file before print.",
    }
    printed = (brief.get("registration") or {}).get("printed_url") or ""
    if printed and len(printed) <= PANEL_URL_BUDGET:
        slide["registration_url"] = "{{facts.printed_url}}"
    elif printed:
        slide["registration_url"] = ""
        slide["contact"] = "{{facts.printed_url}}\n{{facts.presenter_email}}"
    tools = promo.get("tools") or []
    if tools:
        slide["tools"] = [{"label": t["label"], "image": f"{{{{assets.tool-{i}}}}}",
                           "alt": t.get("alt") or f"{t['label']} icon"} for i, t in enumerate(tools[:4])]
        if promo.get("tools_label"):
            slide["tools_label"] = promo["tools_label"]
    else:
        slide["tools_label"] = ""
    return {"template": "event-flyer", "title": "{{facts.event_title_plain}}",
            "author": "Advanced Telerobotics Research Lab", "slides": [slide]}


def write_project(brief: dict, root: Path, deck_spec: Path) -> Path:
    """design/project.json, design/flyer.json and a link to slides/deck.json, ready for project.py."""
    design_dir = root / "design"
    project_path = design_dir / "project.json"
    old = read_json(project_path) if project_path.exists() else {}
    base = names(brief)
    promo = brief.get("promotion") or {}
    assets = dict(old.get("assets") or {})
    assets.setdefault("ksu-wordmark-white", {
        "path": "skill:assets/logos/ksu/ksu-wordmark-white.png",
        "match": "skill:assets/logos/ksu/ksu-wordmark-white.png", "scope": "all",
        "alt": "Kent State University wordmark.",
        "note": "Working copy from the templates. Swap it before sharing: workshop.py official-logos."})
    from .deck import ensure_panel
    assets["code-panel"] = {"path": str(ensure_panel(root / "slides")),
                            "note": "Mist panel behind code on code slides ({{assets.code-panel}} in deck.json)."}
    for i, tool in enumerate(promo.get("tools") or []):
        assets[f"tool-{i}"] = {"path": tool["image"] if tool["image"].startswith(("skill:", "/"))
                               else f"skill:{tool['image']}", "note": tool.get("note", "")}
    from .deck import build_copy
    write_json(design_dir / "deck.build.json", build_copy(read_json(deck_spec)))
    artifacts = {"deck": {"spec": "deck.build.json", "output": base["deck"],
                          "size": "10 x 5.625 in", "formats": ["pptx", "pdf"], "lint_medium": "slide"}}
    for size in promo.get("flyer_sizes") or ["letter"]:
        if size not in FLYER_TEMPLATES:
            raise WorkshopError(f"promotion.flyer_sizes: {size!r} is not one of {', '.join(FLYER_TEMPLATES)}")
        template, label, medium = FLYER_TEMPLATES[size]
        artifacts[f"flyer-{size}"] = {"spec": "flyer.json", "template": template,
                                      "output": f"{base['flyer']}-{size}", "size": label,
                                      "formats": ["pptx", "pdf", "png"], "lint_medium": medium}
    project = {
        "_comment": "Generated by atr-lab-workshop from ../workshop.json and ../slides/deck.json on every "
                    "workshop.py build: edit those, not this file or deck.build.json. Asset swaps made with "
                    "project.py replace-asset are kept.",
        "schema": "atr-project/1",
        "name": derived(brief)["slug"],
        "title": brief.get("title") or "Workshop",
        "dirs": {"work": "work", "out": "../deliverables", "cache": ".atr-cache"},
        "facts": project_facts(brief),
        "assets": assets,
        "artifacts": artifacts,
    }
    write_json(project_path, project)
    write_json(design_dir / "flyer.json", flyer_spec(brief))
    return project_path


class Design:
    """The located design skill and a Python that runs its scripts."""

    def __init__(self) -> None:
        self.root = find_design_skill()
        self.python = find_design_python(self.root)

    def script(self, name: str) -> str:
        return str(self.root / "scripts" / name)

    def project(self, args: list, project: Path) -> int:
        return run([self.python, self.script("project.py"), *args, "-p", str(project)]).returncode

    def tv_slide(self, brief: dict, out: Path, draft: bool) -> int:
        facts = project_facts(brief)
        promo = brief.get("promotion") or {}
        cmd = [self.python, self.script("banner.py"), "--preset", "signage-16x9",
               "--eyebrow", promo.get("tv_eyebrow") or "HANDS-ON WORKSHOP",
               "--title", promo.get("tv_title") or brief.get("short_title") or brief.get("title") or "[Title]",
               "--details", f"{facts['event_date_tv']}  ·  {facts['time_range']}",
               "--details", facts["venue_short"],
               "--qr", tv_qr_url(brief), "--qr-label", promo.get("tv_qr_label") or "Scan to register",
               "-o", str(out), "--safe-zones"]
        if promo.get("tv_subtitle"):
            cmd[cmd.index("--details"):cmd.index("--details")] = ["--subtitle", promo["tv_subtitle"]]
        if promo.get("motion"):
            cmd += ["--motion", promo["motion"]]
        if promo.get("teo_cameo"):
            cmd += ["--teo-cameo"]
        if draft:
            cmd += ["--allow-placeholders"]
        return run(cmd).returncode

    def qr_verify(self, pdf_or_image: Path, url: str) -> int:
        return run([self.python, self.script("qr_code.py"), "verify", str(pdf_or_image), "--url", url]).returncode

    def fetch_official(self, asset_id: str) -> Optional[str]:
        proc = run([self.python, self.script("official_assets.py"), "fetch", asset_id], quiet=True)
        if proc.returncode:
            return None
        lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
        paths = [ln for ln in lines if re.search(r"\.(png|eps)$", ln)]
        return paths[-1] if paths else (lines[-1] if lines else None)


def tv_qr_url(brief: dict) -> str:
    """The TV slide prints the address it encodes, so it uses the short link when there is one (readable from
    across a hallway); promotion.tv_qr_url overrides it."""
    promo = brief.get("promotion") or {}
    printed = (brief.get("registration") or {}).get("printed_url") or ""
    if promo.get("tv_qr_url"):
        return promo["tv_qr_url"]
    if printed:
        return printed if printed.startswith("https://") else "https://" + printed
    return project_facts(brief)["registration_url"]


def tv_inputs(brief: dict) -> str:
    facts = dict(project_facts(brief), tv_qr=tv_qr_url(brief))
    keys = ("event_date_tv", "time_range", "venue_short", "registration_url", "tv_qr")
    return sha256_of([{k: facts[k] for k in keys}, brief.get("promotion"), brief.get("title"),
                      brief.get("short_title")])
