---
description: Put the real Google Forms links on the flyers, TV slide and feedback slide, then rebuild
argument-hint: <the JSON lines from the Apps Script execution log, or the links>
disable-model-invocation: true
---

The presenter ran `forms/create-forms.gs` and has the form links.

Links: $ARGUMENTS

1. Read `${CLAUDE_PLUGIN_ROOT}/atr-lab-workshop/SKILL.md` §5 and references/google-forms.md §1.
2. Find the workshop folder (the nearest `workshop.json`, or ask). From the log lines take, per form, the
   `respond_url` and the `short_url`. Use the links exactly as given; never swap in another URL.
3. Run, from `${CLAUDE_PLUGIN_ROOT}/atr-lab-workshop`:
   `python3 scripts/workshop.py set registration.url <registration respond_url> -w <folder>`,
   `set registration.printed_url <registration short_url without https://>` and
   `set registration.feedback_url <feedback respond_url or short_url>`.
4. `python3 scripts/workshop.py build --changed-only -w <folder>`, then confirm in `deliverables/qa-report.md` and
   the build output that every QR code decodes to the new link.
5. Report which files changed and what is still needed (`workshop.py status`), including a phone scan of a printed
   proof.
