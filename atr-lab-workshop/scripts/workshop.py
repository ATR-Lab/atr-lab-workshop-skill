#!/usr/bin/env python3
"""workshop.py - the front door of the atr-lab-workshop skill.

Turns a workshop brief (workshop.json) into the full academic-workshop package: outline, schedule, slides
(.pptx and .pdf) with bullet speaker notes, participant code, Google Forms (as an Apps Script) and promotion
(flyers and a hallway TV slide). Slides and promotion are built by the atr-lab-design skill, which must be
installed; this script only needs the Python standard library.

  python3 scripts/workshop.py doctor                       # find the design skill, its Python, LibreOffice
  python3 scripts/workshop.py init ~/work/ros2-workshop    # new folder with a blank workshop.json
  python3 scripts/workshop.py check -w ~/work/ros2-workshop [--json]   # what to ask the presenter
  python3 scripts/workshop.py set when.date 2027-02-13 -w ...          # dotted edit; JSON values parse
  python3 scripts/workshop.py schedule -w ...              # schedule.md/.csv, workshop.ics, pacing checks
  python3 scripts/workshop.py outline -w ... [--force]     # outline.md draft from the brief
  python3 scripts/workshop.py code -w ... [--force]        # code/ scaffold: README, preflight, activities
  python3 scripts/workshop.py deck skeleton -w ... [--force]   # slides/deck.json shaped by the schedule
  python3 scripts/workshop.py deck notes -w ...            # slides/speaker-notes.md and the notes check
  python3 scripts/workshop.py forms init -w ... [--force]  # forms/*.form.json from the brief
  python3 scripts/workshop.py forms build -w ...           # forms/create-forms.gs, preview, IMPORT.md
  python3 scripts/workshop.py build -w ... [--draft] [--only schedule,notes,forms,design,tv,readme]
  python3 scripts/workshop.py official-logos -w ...        # swap in the official Kent State wordmark
  python3 scripts/workshop.py status -w ... [--json]       # deliverables and what is still needed
  python3 scripts/workshop.py bundle -w ...                # <slug>-workshop-package.zip for hand-off

Exit status: 0 done; 1 usage or brief error; 2 refused (questions still open; pass --draft for a draft);
3 a build or check failed.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import zipfile  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wslib import brief as B  # noqa: E402
from wslib import code as C  # noqa: E402
from wslib import deck as D  # noqa: E402
from wslib import design as G  # noqa: E402
from wslib import forms as F  # noqa: E402
from wslib import outline as O  # noqa: E402
from wslib import schedule as S  # noqa: E402
from wslib import status as T  # noqa: E402
from wslib.common import (SKILL_ROOT, WorkshopError, find_brief, find_design_python, find_design_skill,  # noqa: E402
                          read_json, refuse_inside_skill, sha256_of, which, write_json, write_text)

STATE = ".workshop-state.json"
STAGES = ("schedule", "notes", "forms", "design", "tv", "readme")


def load(args) -> tuple:
    path = find_brief(getattr(args, "workshop", None))
    return path, B.load(path), path.parent


def save(path: Path, brief: dict) -> None:
    write_json(path, brief)


# --------------------------------------------------------------------------- commands

def cmd_doctor(args) -> int:
    ok = True
    print(f"atr-lab-workshop skill: {SKILL_ROOT}")
    print(f"python (this script):   {sys.executable} {sys.version.split()[0]}")
    design = find_design_skill(required=False)
    if design:
        version = ""
        manifest = design.parent / ".claude-plugin/plugin.json"
        if manifest.is_file():
            version = " v" + read_json(manifest).get("version", "?")
        print(f"atr-lab-design skill:   {design}{version}")
        python = find_design_python(design, required=False)
        print(f"design python:          {python or 'MISSING: create its venv (see its SKILL.md §7)'}")
        ok &= bool(python)
        if python:
            from wslib.common import run
            proc = run([python, str(design / "scripts/atr_design.py"), "doctor"], quiet=True)
            tail = [ln for ln in proc.stdout.splitlines() if ln.startswith("[")]
            print("design doctor:          " + ("; ".join(tail) or "see output above"))
            ok &= proc.returncode == 0
    else:
        print("atr-lab-design skill:   MISSING (install it: https://github.com/ATR-Lab/atr-lab-design-skill)")
        ok = False
    for tool, why in (("soffice", "renders and PDF export"), ("pdftoppm", "page renders and QR checks"),
                      ("node", "optional: tests the Apps Script offline")):
        print(f"{tool:<23} {which(tool) or 'missing'}  ({why})")
        if tool != "node":
            ok &= bool(which(tool))
    print("\nready" if ok else "\nnot ready: fix the lines marked MISSING or missing")
    return 0 if ok else 1


def cmd_init(args) -> int:
    folder = Path(args.folder).expanduser().resolve()
    refuse_inside_skill(folder)
    path = folder / "workshop.json"
    if path.exists() and not args.force:
        raise WorkshopError(f"{path} exists (use --force to replace it)")
    folder.mkdir(parents=True, exist_ok=True)
    if args.example:
        source = SKILL_ROOT / "examples" / args.example
        if not (source / "workshop.json").is_file():
            names = ", ".join(sorted(p.name for p in (SKILL_ROOT / "examples").iterdir() if p.is_dir()))
            raise WorkshopError(f"no example {args.example!r} (examples: {names})")
        shutil.copytree(source, folder, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    else:
        write_json(path, B.new_brief())
    print(f"wrote {path}")
    print("next: fill it from the presenter's request, then: workshop.py check -w " + str(folder))
    return 0


def cmd_check(args) -> int:
    path, brief, _ = load(args)
    issues = B.check(brief)
    if args.json:
        print(json.dumps({"ready": B.ready_to_build(issues), "issues": [i.as_dict() for i in issues]}, indent=2))
        return 0 if B.ready_to_build(issues) else 2
    if not issues:
        print("brief complete: nothing left to ask")
        return 0
    for severity, heading in (("error", "Fix"), ("required", "Ask before building"),
                              ("recommended", "Ask, or assume and record it in assumptions")):
        group = [i for i in issues if i.severity == severity]
        if group:
            print(f"\n{heading}:")
            for issue in group:
                print(f"  - {issue.question}  [{issue.path}]" + (f"  (used for: {issue.why})" if issue.why else ""))
    print()
    return 0 if B.ready_to_build(issues) else 2


def cmd_set(args) -> int:
    path, brief, _ = load(args)
    value = B.set_value(brief, args.key, args.value)
    save(path, brief)
    print(f"{args.key} = {json.dumps(value, ensure_ascii=False)}")
    if args.key.startswith("registration."):
        print("next: workshop.py build (rebuilds the flyers, the TV slide and the deck's QR codes)")
    return 0


def cmd_schedule(args) -> int:
    _, brief, root = load(args)
    for path in S.write_outputs(brief, root):
        print(f"wrote {path}")
    checks = S.pacing(brief, S.timeline(brief))
    for severity, message in checks:
        print(f"  {severity}: {message}")
    return 3 if any(s == "error" for s, _ in checks) else 0


def cmd_outline(args) -> int:
    _, brief, root = load(args)
    target = root / "outline.md"
    if target.exists() and not args.force:
        raise WorkshopError(f"{target} exists: edit it, or --force to regenerate (edits are lost)")
    write_text(target, O.render(brief))
    print(f"wrote {target}")
    return 0


def cmd_code(args) -> int:
    path, brief, root = load(args)
    written = C.scaffold(brief, root / "code", force=args.force)
    save(path, brief)
    for item in written:
        print(f"wrote {item}")
    print("next: write each activity's starter/ and solution/, and tune code/preflight.json "
          "(references/code-materials.md)")
    return 0


def cmd_deck(args) -> int:
    _, brief, root = load(args)
    if args.action == "skeleton":
        path = D.write_skeleton(brief, root / "slides", args.force)
        count = len(read_json(path)["slides"])
        print(f"wrote {path} ({count} slides). Replace every [bracket] (references/slides-and-notes.md).")
        return 0
    return stage_notes(brief, root)


def cmd_forms(args) -> int:
    _, brief, root = load(args)
    folder = root / "forms"
    if args.action == "init":
        for item in F.init_specs(brief, folder, force=args.force):
            print(f"wrote {item}")
        return 0
    for item in F.build(folder):
        print(f"wrote {item}")
    return 0


# --------------------------------------------------------------------------- build stages

def stage_notes(brief: dict, root: Path) -> int:
    spec = root / "slides/deck.json"
    if not spec.exists():
        raise WorkshopError(f"{spec} missing: run workshop.py deck skeleton first")
    problems = D.write_notes(spec, G.project_facts(brief), root / "slides/speaker-notes.md",
                             brief.get("title") or "Workshop")
    print(f"wrote {root / 'slides/speaker-notes.md'}")
    for problem in problems:
        print(f"  notes: {problem}")
    return 3 if problems else 0


def stage_forms(brief: dict, root: Path) -> int:
    folder = root / "forms"
    if not list(folder.glob("*.form.json")):
        F.init_specs(brief, folder)
    for item in F.build(folder):
        print(f"wrote {item}")
    return 0


def stage_design(brief: dict, root: Path, draft: bool, changed_only: bool) -> int:
    deck_spec = root / "slides/deck.json"
    if not deck_spec.exists():
        raise WorkshopError(f"{deck_spec} missing: run workshop.py deck skeleton first")
    project = G.write_project(brief, root, deck_spec)
    print(f"wrote {project}")
    design = G.Design()
    flags = ["--changed-only"] if changed_only else []
    code = design.project(["build", *flags, *(["--draft"] if draft else [])], project)
    if code not in (0,):
        print(f"design build exited {code}: read the lines above (overflow, placeholders or lint)")
        if code in (1, 2):
            return 3
    fixed = D.unmask(root / "deliverables" / f"{G.names(brief)['deck']}.pptx")
    if fixed:
        print(f"code slides: real brackets restored on {fixed} slide(s)")
    code_export = design.project(["export", *flags], project)
    return 3 if (code or code_export) else 0


def stage_tv(brief: dict, root: Path, draft: bool, state: dict) -> int:
    if not (brief.get("promotion") or {}).get("tv_slide", True):
        return 0
    out = root / "deliverables" / f"{G.names(brief)['tv']}.jpg"
    digest = G.tv_inputs(brief)
    if state.get("tv") == digest and out.exists():
        print(f"tv slide unchanged: {out}")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    qa_dir = root / "design/work/tv"
    qa_dir.mkdir(parents=True, exist_ok=True)
    code = G.Design().tv_slide(brief, out, draft)
    zones = out.with_name(out.stem + "-zones" + out.suffix)
    for extra in (zones, out.with_name(out.stem + "-zones.png")):
        if extra.exists():
            extra.replace(qa_dir / extra.name)
    if code == 0:
        state["tv"] = digest
    return 3 if code else 0


def cmd_build(args) -> int:
    path, brief, root = load(args)
    refuse_inside_skill(root)
    issues = B.check(brief)
    if any(i.severity == "error" for i in issues):
        cmd_check(args)
        return 1
    if not B.ready_to_build(issues) and not args.draft:
        print("questions are still open (workshop.py check); ask them, or pass --draft for a draft with "
              "placeholders")
        return 2
    only = set(args.only.split(",")) if args.only else set(STAGES)
    unknown = only - set(STAGES)
    if unknown:
        raise WorkshopError(f"--only: unknown stage(s) {', '.join(sorted(unknown))}; use {', '.join(STAGES)}")
    state_path = root / STATE
    state = read_json(state_path) if state_path.exists() else {}
    results = {}
    if "schedule" in only:
        results["schedule"] = cmd_schedule(args)
    if "notes" in only:
        results["notes"] = stage_notes(brief, root)
    if "forms" in only:
        results["forms"] = stage_forms(brief, root)
    if "design" in only:
        results["design"] = stage_design(brief, root, args.draft, args.changed_only)
    if "tv" in only:
        results["tv"] = stage_tv(brief, root, args.draft, state)
    write_json(state_path, state)
    if "readme" in only:
        write_text(root / "README.md", T.render_readme(brief, root))
        results["readme"] = 0
        print(f"wrote {root / 'README.md'}")
    print("\nbuild: " + ", ".join(f"{k} {'ok' if v == 0 else 'FAILED'}" for k, v in results.items()))
    return 3 if any(results.values()) else 0


def cmd_official(args) -> int:
    _, brief, root = load(args)
    project = root / "design/project.json"
    if not project.exists():
        raise WorkshopError("design/project.json missing: run workshop.py build first")
    design = G.Design()
    code = design.project(["replace-asset", "ksu-wordmark-white", "official:ksu-stacked-white-png"], project)
    if code == 0:
        D.unmask(root / "deliverables" / f"{G.names(brief)['deck']}.pptx")
        code = design.project(["export", "--changed-only"], project)
        state_path = root / STATE
        state = read_json(state_path) if state_path.exists() else {}
        state.pop("tv", None)
        code |= stage_tv(brief, root, False, state)
        write_json(state_path, state)
        write_text(root / "README.md", T.render_readme(brief, root))
    return 3 if code else 0


def cmd_status(args) -> int:
    _, brief, root = load(args)
    info = T.collect(brief, root)
    if args.json:
        print(json.dumps({"files": [{"path": p, "what": w, "exists": e} for p, w, e in info["files"]],
                          "still_needed": info["needed"]}, indent=2))
        return 0
    for rel, what, exists in info["files"]:
        print(f"  {'ok ' if exists else '-- '} {rel:<58} {what}")
    print("\nStill needed:")
    for item in info["needed"]:
        print(f"  - {item}")
    write_text(root / "README.md", T.render_readme(brief, root))
    return 0


def cmd_bundle(args) -> int:
    _, brief, root = load(args)
    slug = B.derived(brief)["slug"]
    out = root / f"{slug}-workshop-package.zip"
    skip_parts = {"design", ".atr-cache", "__pycache__", ".git"}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root)
            if path == out or not path.is_file() or skip_parts & set(rel.parts) or path.name in (STATE, ".DS_Store"):
                continue
            if rel.suffix == ".zip":
                continue
            zf.write(path, f"{slug}/{rel.as_posix()}")
    print(f"wrote {out}")
    return 0


# --------------------------------------------------------------------------- CLI

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[1], formatter_class=argparse.RawTextHelpFormatter,
                                epilog="Exit status: 0 done, 1 usage or brief error, 2 refused, 3 a check failed.")
    sub = p.add_subparsers(dest="command", required=True)

    def add(name, fn, help_text):
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("-w", "--workshop", help="workshop folder or workshop.json (default: nearest)")
        sp.set_defaults(fn=fn)
        return sp

    sp = sub.add_parser("doctor", help="check the design skill, its Python and the render tools")
    sp.set_defaults(fn=cmd_doctor)
    sp = sub.add_parser("init", help="create a workshop folder with a blank workshop.json")
    sp.add_argument("folder")
    sp.add_argument("--example", help="start from examples/<name> (e.g. intro-ros2)")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(fn=cmd_init)
    add("check", cmd_check, "list what to ask the presenter").add_argument("--json", action="store_true")
    sp = add("set", cmd_set, "set a dotted key in workshop.json")
    sp.add_argument("key")
    sp.add_argument("value")
    add("schedule", cmd_schedule, "write schedule.md/.csv and workshop.ics")
    add("outline", cmd_outline, "write the outline.md draft").add_argument("--force", action="store_true")
    add("code", cmd_code, "scaffold code/").add_argument("--force", action="store_true")
    sp = add("deck", cmd_deck, "deck skeleton or speaker notes")
    sp.add_argument("action", choices=["skeleton", "notes"])
    sp.add_argument("--force", action="store_true")
    sp = add("forms", cmd_forms, "form specs and the Apps Script")
    sp.add_argument("action", choices=["init", "build"])
    sp.add_argument("--force", action="store_true")
    sp = add("build", cmd_build, "build everything (or --only some stages)")
    sp.add_argument("--draft", action="store_true", help="allow [placeholders] and open questions")
    sp.add_argument("--only", help=f"comma list of stages: {', '.join(STAGES)}")
    sp.add_argument("--changed-only", action="store_true", help="design: rebuild only what changed")
    add("official-logos", cmd_official, "swap in the official Kent State wordmark and re-export")
    add("status", cmd_status, "deliverables and what is still needed").add_argument("--json", action="store_true")
    add("bundle", cmd_bundle, "zip the package for hand-off")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.fn(args)
    except WorkshopError as exc:
        print(f"workshop.py: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
