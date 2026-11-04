# QA gate and hand-off

**Read this when** you are about to hand the package over, or the presenter asks what is left.

## 1. The gate

Pass every line or say plainly why it does not pass.

**Brief**
- [ ] `workshop.py check` exits 0 (or this is a declared draft).
- [ ] `assumptions` lists every default you chose; `open_questions` everything unsettled.

**Schedule**
- [ ] `workshop.py schedule` reports no errors; warnings fixed or explained.
- [ ] The deck's break slides and agenda times match `schedule.md`.

**Outline**
- [ ] Every module section is written out (purpose, content, demo and fallback, activity, done-when, stretch,
      common problems, check for understanding); logistics, roles, risks and the timeline are filled.
- [ ] No brackets except facts the presenter must confirm.

**Slides and notes**
- [ ] `workshop.py build` built the deck without `--draft`; the design skill's lint shows 0 errors.
- [ ] You looked at the contact sheet and the pages it flags (`deliverables/qa-report.md` lists the paths):
      no overflow, collisions, empty agenda plates or timeline stations, unreadable code.
- [ ] Unique titles; alt text on every picture; code at 14 pt or more.
- [ ] `slides/speaker-notes.md`: bullets for every slide, `deck notes` reported nothing.

**Code**
- [ ] Every solution's tests pass; every starter fails only where the task is. You ran them.
- [ ] `python3 preflight.py` runs and says READY on this machine (or you say what it cannot check here).
- [ ] The README's prerequisites match the brief and the flyer.

**Forms**
- [ ] `workshop.py forms build` validated; you read `forms-preview.md`.
- [ ] The mock run passed when Node.js is available.
- [ ] Questions are only what the workshop needs (references/google-forms.md §4).

**Promotion**
- [ ] Every flyer and the TV slide rendered; you looked at each PNG and the JPEG.
- [ ] QR codes decoded to the expected link (qa-report.md, banner output).
- [ ] The official Kent State wordmark is in place, or its swap is the first item in "Still needed from you".

## 2. The report

Use this shape; keep it short and factual.

```markdown
## <Workshop title>: workshop package

<date, time, place> · folder: <path>

### Deliverables
| Deliverable | File |
|---|---|
| Outline | outline.md |
| Schedule | schedule.md (also .csv, workshop.ics) |
| Slides | deliverables/atr-deck-....pptx and .pdf (N slides) |
| Speaker notes | slides/speaker-notes.md (and in the .pptx) |
| Code | code/ (N activities; README; preflight.py) |
| Google Forms | forms/create-forms.gs (how-to: forms/IMPORT.md; preview: forms/forms-preview.md) |
| Flyers | deliverables/atr-flyer-...-letter.pdf (+ tabloid) |
| TV slide | deliverables/atr-tv-....jpg |

### What I checked
- Source: lint 0 errors on the deck and flyers; budgets; speaker-notes check; schedule pacing.
- Exported files: tagged PDFs with embedded fonts; QR codes decoded to <link> in each PDF and the TV slide.
- Code: <N> tests pass on the solutions; starters fail as intended; preflight READY.
- Looked at: every slide, flyer and the TV slide.

### Assumptions
- ...

### Still needed from you
- [ ] Create the forms (forms/IMPORT.md) and send me the links from the log; I rebuild the QR codes.
- [ ] ... (from `workshop.py status`)
```

Never describe a draft as final, a mock run as a real form, or a decoded QR code as a phone scan.
