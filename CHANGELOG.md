# Changelog

## 1.0.0 (Nov. 4, 2026)

First release of the ATR Lab workshop skill.

- **Intake:** `workshop.py init` and `check` turn a request into `workshop.json` and list what is still missing as
  ready-to-ask questions (required, recommended, contradictions with the design skill's verified facts, leftover
  placeholders). The interview guide covers location, date and time, topics, prerequisites, hardware and any
  other requests, in one round.
- **Schedule:** clock times in Kent State style from typed blocks, pacing checks, `schedule.md`, `schedule.csv`
  and a calendar file.
- **Outline:** a full draft from the brief, with modules, logistics, risks and the promotion timeline.
- **Slides and notes:** a deck skeleton shaped by the schedule for the design skill's presentation template,
  code slides with editable Source Code Pro (brackets kept intact through the design skill's placeholder check),
  bullet speaker notes on every slide with a checker and `speaker-notes.md`.
- **Code:** a participant folder with a README, a standard-library `preflight.py` driven by `preflight.json`, and
  starter, solution and tests per activity.
- **Google Forms:** registration and feedback specs from the brief, validated, compiled into an Apps Script that
  creates, publishes and links the forms (closing registration at capacity), with a preview and import guide; an
  offline FormApp mock for testing.
- **Promotion:** event flyers (Letter, Tabloid, 17 × 22 in) and a hallway TV slide through the design skill, QR
  codes verified from the exported files, the official Kent State wordmark swap, and changed-only rebuilds when
  the real form links arrive.
- **Example:** a four-hour "Robot path planning in Python" workshop with tested code.
- **Plugin:** `/atr-lab-workshop:workshop`, `:forms-ready`, `:revise`, `:status`, `:setup`.
