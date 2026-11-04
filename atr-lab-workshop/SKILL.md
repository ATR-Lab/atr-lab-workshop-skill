---
name: atr-lab-workshop
description: "Plan and build a complete academic workshop for the Advanced Telerobotics Research (ATR) Lab at Kent State University, on any topic a researcher wants to teach: interview the presenter for the location, date and time, topics, audience, required skills and hardware and any special requests, then deliver a detailed outline, a run-of-show schedule (breaks, Q&A, talks, demos, hands-on), branded slides in PowerPoint and PDF with bullet speaker notes on every slide, tested hands-on code with a setup check, Google Forms (registration and feedback) as an importable Apps Script, and promotion (printed flyers and a hallway TV slide). Uses the atr-lab-design skill for all slides and promotional material. Use it whenever someone asks to plan, prepare, run or promote a workshop, tutorial, hands-on session, bootcamp, short course, training, hackathon session or seminar series, even if they only ask for one piece of it (slides, a schedule, a sign-up form, a flyer) for an event that is a workshop."
---

# ATR Lab academic workshop builder

Turns a researcher's request ("I want to run a workshop on X") into a complete, branded, checked workshop
package. The work has two halves: **find out everything the workshop needs from the presenter** (the intake),
then **build every asset from one brief** with the scripts, so a later change (a new room, a real registration
link) reaches every file.

All slides and promotion are made by the **atr-lab-design** skill (`../atr-lab-design/`, or wherever it is
installed; `workshop.py doctor` finds it). Its brand card, facts policy and QA gate apply to everything here.
Read its `SKILL.md` §1 (brand card) and §5 (facts policy) once per session before you write any copy.

Run every command from this skill's folder (the one that holds this file). `python3` here needs only the standard
library; the scripts call the design skill's own Python for slides and promotion.

## Contents

1. [What you deliver](#1-what-you-deliver)
2. [Workflow](#2-workflow)
3. [The intake interview](#3-the-intake-interview)
4. [Building each deliverable](#4-building-each-deliverable)
5. [Follow-up changes](#5-follow-up-changes)
6. [The QA gate and the hand-off report](#6-the-qa-gate-and-the-hand-off-report)
7. [Rules that are easy to break](#7-rules-that-are-easy-to-break)
8. [File map](#8-file-map)
9. [Environment](#9-environment)

---

## 1. What you deliver

Everything lives in one workshop folder outside this skill (default: a new folder named after the workshop in the
user's current directory, or the folder they name). `workshop.json` is the source of truth.

| # | Deliverable | File(s) | Made by |
|---|---|---|---|
| 1 | Detailed outline of the workshop's material | `outline.md` | `workshop.py outline`, then you write it out in full |
| 2 | Schedule outline: talks, demos, hands-on, breaks, lunch, Q&A, clock times | `schedule.md`, `schedule.csv`, `workshop.ics` | `workshop.py schedule` |
| 3 | Presentation slides, PowerPoint and PDF | `deliverables/atr-deck-<topic>-<date>.pptx` and `.pdf` | `slides/deck.json` → design skill |
| 4 | Speaker notes in bullet form for every slide | in the `.pptx` notes and `slides/speaker-notes.md` | `workshop.py deck notes` (checked) |
| 5 | Code used in the workshop | `code/` (README, `preflight.py` + `preflight.json`, starter and solution per activity, tests) | `workshop.py code`, then you write and test the code |
| 6 | Google Form file to import | `forms/create-forms.gs` (+ `*.form.json`, `forms-preview.md`, `IMPORT.md`) | `workshop.py forms init` / `forms build` |
| 7 | Paper flyers | `deliverables/atr-flyer-<topic>-<date>-letter.pdf` (+ `tabloid`, `17x22`; `.pptx` and `.png`) | design skill event-flyer templates |
| 8 | Hallway TV promo slide | `deliverables/atr-tv-<topic>-<date>.jpg` (+ `.mp4` when animated) | design skill `banner.py --preset signage-16x9` |
| - | Index and "still needed from you" | `README.md`, `deliverables/qa-report.md` | `workshop.py status` / `build` |

**About the Google Form.** Google Forms cannot import a file. The importable file is an Apps Script the presenter
pastes into script.google.com and runs once; it creates the forms in their Drive and prints the links
(`forms/IMPORT.md` walks them through it). Say this plainly when you deliver it.

## 2. Workflow

Follow the phases in order. Each ends with a check; do not skip ahead past a failed one.

| Phase | Do | Check before moving on |
|---|---|---|
| 0. Set up | `python3 scripts/workshop.py doctor` | prints `ready` (design skill, its Python, LibreOffice, poppler) |
| 1. Intake | `workshop.py init <folder>`; put every fact from the request into `workshop.json`; `workshop.py check -w <folder>`; ask what is missing (§3); record answers, assumptions and open questions | `check` exits 0, or the user asked for a draft |
| 2. Design the workshop | Write `objectives`, `modules` and `schedule` in the brief (references/workshop-design.md, references/schedule.md); `workshop.py schedule`; `workshop.py outline`, then write `outline.md` out in full | no pacing errors; warnings fixed or explained |
| 3. Checkpoint with the presenter | Show the objectives, the module list and the schedule table (a short summary, not the files) and ask for changes, unless the user said to build everything without stopping | approval, or changes applied |
| 4. Code | `workshop.py code`; write each activity's `solution/` first, then derive `starter/`; write the tests; tune `code/preflight.json` (references/code-materials.md) | every solution's tests pass; every starter's tests fail only where the task is; `preflight.py` runs |
| 5. Slides and notes | `workshop.py deck skeleton`; replace every `[bracket]` in `slides/deck.json` with real content and notes (references/slides-and-notes.md) | `workshop.py deck notes` reports no problems |
| 6. Forms | `workshop.py forms init`; adjust the specs to the brief; `workshop.py forms build` (references/google-forms.md) | the build validates; read `forms-preview.md` |
| 7. Build and promotion | `workshop.py build -w <folder>` (deck, flyers, TV slide, PDFs, QR checks, README) (references/promotion.md) | build ok; you looked at every render (§6) |
| 8. Hand off | `workshop.py status`; the report in §6 | nothing hidden: every gap is in "Still needed from you" |

`workshop.py build --draft` builds with `[placeholders]` and open questions, for a user who wants to see a draft
first. A draft is labeled as one in your report and is never printed or posted.

## 3. The intake interview

The intake decides the quality of everything else. Full question bank, defaults and examples:
references/intake.md. Brief fields: references/brief-schema.md.

1. **Extract first.** Read the user's request and put every stated fact into `workshop.json` before asking
   anything. Never ask for something they already said.
2. **Run the check.** `workshop.py check -w <folder> --json` lists what is missing as ready-to-ask questions, in
   three groups: `error` (contradictions to fix), `required` (cannot build without it) and `recommended` (ask, or
   choose a sensible default and record it in `assumptions`).
3. **Ask once, grouped, specific.** One round of questions covering every `required` item and the `recommended`
   items you cannot default. In Claude Code, use the AskUserQuestion tool (up to four questions per call, options
   where the answer is a choice: format, level, flyer sizes, forms); elsewhere, a short numbered list. Offer your
   proposal as the first option ("10 a.m.-2 p.m. with lunch (recommended)"). A second round only for answers that
   raise new questions. The presenter should never have to answer more than about ten questions in all.
4. **The facts the user asked to be able to give** must each be settled, by the user or as a recorded
   assumption: **location** (building and room, or the online link plan), **date, start, end and time zone**,
   **main topics**, **what participants must bring or know** (skills, hardware, software, accounts) and **any
   other details or requests** (catering, recording, accessibility, co-presenters, sponsors, a theme, an
   existing repo or slides to reuse). Ask explicitly, every time: "Anything else you want the workshop to
   include or avoid?" and put the answers in `requests`.
5. **Draft what the presenter would expect you to draft**, and confirm it in the checkpoint (phase 3) instead of
   asking up front: learning objectives, modules, the schedule, activities, the flyer wording.
6. **Facts you may not invent** (design skill §5): people, titles, rooms, results, sponsors, quotes, the
   registration link. Unknown means a visible `[placeholder]` and a line in "Still needed from you". Contradictions
   with the design skill's verified facts (a wrong building name, Room 236, `@atr_kent`) are explained and
   corrected, not used. `check` catches the common ones.
7. **Record what you assumed** in `assumptions` (they appear in the hand-off list) and anything still open in
   `open_questions`.

If the user says "just make something" or gives very little, ask the minimum required set in one round anyway
(title or topic, date and time, place, audience and level, prerequisites); everything else you may default.

## 4. Building each deliverable

Each reference has the full rules; the short version:

- **Outline** (`outline.md`): the generated draft is a skeleton. Write every module out: purpose, objectives,
  content with the examples used, the live demo and its fallback, the activity with steps, the done-when check,
  the stretch goal, common problems and a check for understanding. Fill logistics, roles, risks and the
  promotion timeline. Keep brackets only for facts the presenter must confirm.
- **Schedule**: blocks of kind `setup`, `welcome`, `talk`, `demo`, `hands-on`, `discussion`, `qa`, `break`,
  `lunch`, `wrap-up`, `feedback`, `buffer`; minutes add up to the event exactly. The pacing check enforces a
  break at least every 90 minutes, talks of 30 minutes or less, a meal break for four hours or more, a Q&A and a
  closing wrap-up, and an early setup check before hands-on work (references/schedule.md has recipes for 90 min
  to two days).
- **Slides**: the skeleton follows the schedule (title, logistics, agenda with clock times, objectives, setup
  check, a section per module with concept, demo, code and hands-on slides, break and lunch slides with return
  times, Q&A, wrap-up, a feedback QR slide, thank you). Every slide carries 2-6 speaker-note bullets that start
  with `• ` and say what to say, do and ask, with timing cues. Code goes on code slides (editable Source Code Pro
  on a mist panel). Layout budgets come from the design skill: one message per slide, titles of 38 characters or
  fewer.
- **Code**: a participant-ready folder: README (before you come, activities), `preflight.py` (a standard-library
  setup check driven by `preflight.json`), and per activity `starter/` (what they edit), `solution/` (finished)
  and tests that pass on the solution. Run them. Never ship code you have not run; if something cannot run here
  (robot hardware, a GPU, a licensed tool), say exactly what was and was not tested.
- **Forms**: a registration form (contact, background grid built from the prerequisites, setup readiness,
  accommodations, photo preference, dietary needs when there is a meal, the presenter's extra questions; closes
  itself at capacity) and a feedback form (usefulness, objectives met, pace, hands-on, open comments).
- **Flyers and TV slide**: built from the brief on the design skill's event-flyer templates (Letter by default;
  Tabloid and 17 × 22 in on request) and its 16:9 signage preset, each with a QR code to the registration form,
  verified from the exported file. Promotion wording lives in `promotion` in the brief.

## 5. Follow-up changes

Change the brief or `slides/deck.json`, then rebuild; never hand-edit generated files.

| Request | Do |
|---|---|
| The forms exist now (links from the Apps Script log) | `workshop.py set registration.url <respond_url>`, `set registration.printed_url forms.gle/...`, `set registration.feedback_url <url>`, then `workshop.py build` |
| New room, date or time | `workshop.py set where.room "Room 204"` (or `when.date`, `when.start`...), then `build`; the schedule, deck, flyers, TV slide, forms and calendar file all follow |
| Official Kent State logo before sharing | `workshop.py official-logos` (downloads from kent.edu and re-exports) |
| Add a size (Tabloid, 17 × 22) | add it to `promotion.flyer_sizes`, `build` |
| Animated TV slide or deck | `promotion.motion: "lattice-drift"` (Teo only on request: `promotion.teo_cameo`), `build` |
| More time for a module | edit `schedule`, `workshop.py schedule`, adjust the deck, `build` |
| A social post, a newsletter blurb, a certificate | hand off to the atr-lab-design skill with the brief's facts |
| Everything in one zip | `workshop.py bundle` |

Report which files changed after every follow-up.

## 6. The QA gate and the hand-off report

Before you hand anything over (references/qa-and-handoff.md has the full checklist):

1. `workshop.py build` ends with every stage `ok` (or you say which failed and why).
2. You opened and looked at the deck contact sheet, every flyer PNG and the TV slide JPEG (paths in
   `deliverables/qa-report.md`): no overflow, collisions, empty plates or text on the band.
3. `slides/speaker-notes.md` has bullets for every slide; `deck notes` reported nothing.
4. Every activity's solution tests pass and you ran `preflight.py`.
5. `forms build` validated; the Apps Script ran in the offline mock when Node is available
   (`node scripts/tests/mock_apps_script.js forms/create-forms.gs`).
6. The design skill's QA gate (its §4) holds for the deck and flyers.

Then report, in this order: the deliverables (table with paths), what you checked and how (keep source checks,
checks of the exported PDFs and what a person must still look at apart, as the design skill does), the
assumptions you made, and **Still needed from you**: `workshop.py status` prints the list (forms to create and
links to return, the official logo swap, placeholders, approvals for printing and the TV slideshow, phone scans
of printed QR codes).

## 7. Rules that are easy to break

1. Never put a placeholder link on anything printed or posted. Until the forms exist the QR codes point at
   `example.org`; say so, and rebuild once the real links arrive.
2. Never invent a presenter, helper, room, sponsor, result or quote. Brackets and the hand-off list instead.
3. Never write the workshop folder inside this skill or the design skill.
4. Never edit `design/project.json` or `design/deck.build.json` by hand: they are regenerated on every build.
5. Never shrink type or crowd a slide to make content fit: cut words or add a slide (design skill rule).
6. Kent State style in all copy: no Oxford comma, "Feb. 13", "10 a.m.-2 p.m.", "Ph.D.", "the lab" after the
   full name on first reference. The scripts format dates and times; you keep your own copy consistent.
7. Minors (K-12 workshops): no names or photos without releases; the registration form asks a parent or guardian;
   follow the design skill's K-12 rules (its references/pr-events-outreach.md).
8. Ask before anything outward-facing: the skill never sends email, creates the forms itself, posts or prints.

## 8. File map

```
SKILL.md                      this file
references/
  intake.md                   the interview: required facts, question bank, defaults, worked examples
  brief-schema.md             every workshop.json field
  workshop-design.md          objectives, modules, activities, levels, inclusive teaching
  schedule.md                 block kinds, pacing rules, recipes from 90 minutes to two days
  slides-and-notes.md         deck recipe, layouts, code slides, speaker-note format
  code-materials.md           participant repo layout, starter/solution/tests, preflight.json, hardware workshops
  google-forms.md             form specs, item types, privacy, importing with Apps Script
  promotion.md                flyers, TV slide, QR codes, timeline, approvals
  qa-and-handoff.md           the gate and the report template
assets/templates/             create-forms.gs.tmpl, IMPORT-FORMS.md, preflight.py, code-README.md
examples/path-planning/       a finished example: brief, outline, deck.json and tested code
scripts/
  workshop.py                 the front door (doctor, init, check, set, schedule, outline, code, deck, forms,
                              build, official-logos, status, bundle)
  wslib/                      brief, schedule, outline, deck, forms, code, design, status (standard library)
  tests/                      offline tests (pytest) and the Apps Script mock (Node)
```

## 9. Environment

- **This skill:** Python 3.9 or newer, standard library only. Node.js is optional (the Apps Script mock test).
- **The design skill** must be installed and set up (its `atr_design.py doctor` passes); `workshop.py doctor`
  finds it next to this skill, in `~/.claude/skills`, `~/.codex/skills`, the Claude Code plugin cache or
  `$ATR_DESIGN_SKILL`, and finds its Python in its `.venv`, the plugin's data folder or `$ATR_DESIGN_PYTHON`.
- **Rendering and PDF export** need LibreOffice and poppler (the design skill's requirement). Without them the
  `.pptx` files still build; say that nothing was rendered.
- **Official Kent State artwork** is downloaded from kent.edu on `official-logos`; a failed download is a
  network problem, not a reason to ship the working copy.
- **Codex and other agents:** the workflow is the same. Where there is no question tool, ask the intake questions
  as one numbered list and wait for the answers.
