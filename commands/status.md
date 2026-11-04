---
description: Show an ATR Lab workshop's deliverables and everything still needed before it can be shared
argument-hint: [workshop folder]
disable-model-invocation: true
---

Report the state of a workshop package.

Folder: $ARGUMENTS

Run `python3 "${CLAUDE_PLUGIN_ROOT}/atr-lab-workshop/scripts/workshop.py" status -w <folder>` (the nearest
`workshop.json` when no folder is given). Summarize which deliverables exist and the "Still needed" list, grouped
into what the presenter must do (create the forms, approvals, phone scans) and what you can do next (placeholders,
the official logo swap, warnings). Offer to do the next step; do not start it unasked.
