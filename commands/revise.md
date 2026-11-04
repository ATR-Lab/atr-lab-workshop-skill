---
description: Change an existing ATR Lab workshop (room, date, schedule, slides, sizes) and rebuild only what it reaches
argument-hint: <what to change>
disable-model-invocation: true
---

Revise an existing workshop package with the atr-lab-workshop skill.

Change: $ARGUMENTS

1. Read `${CLAUDE_PLUGIN_ROOT}/atr-lab-workshop/SKILL.md` §5 (follow-up changes).
2. Find the workshop folder (the nearest `workshop.json`, or ask). Make the change in `workshop.json` (with
   `python3 "${CLAUDE_PLUGIN_ROOT}/atr-lab-workshop/scripts/workshop.py" set <path> <value> -w <folder>`) or in
   `slides/deck.json`, `code/`, `forms/*.form.json` or `outline.md`; never in generated files under `design/` or
   `deliverables/`.
3. Rebuild: `workshop.py schedule` after schedule changes, `workshop.py forms build` after form changes, then
   `workshop.py build --changed-only`. Re-run the code tests after code changes.
4. Look at the re-rendered pages, and report exactly which deliverables changed and what is still needed.
