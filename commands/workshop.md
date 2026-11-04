---
description: Plan and build a complete ATR Lab workshop (outline, schedule, slides, notes, code, forms, flyers, TV slide)
argument-hint: <topic, date and time, place, audience, what participants need, anything else>
disable-model-invocation: true
---

Plan and build a workshop with the atr-lab-workshop skill.

Request: $ARGUMENTS

## Before you start

1. Read `${CLAUDE_PLUGIN_ROOT}/atr-lab-workshop/SKILL.md` and follow its workflow (§2) phase by phase.
2. Run `python3 "${CLAUDE_PLUGIN_ROOT}/atr-lab-workshop/scripts/workshop.py" doctor`. It must find the
   atr-lab-design skill and its Python; if it does not, tell the user to install the design plugin
   (`/plugin install atr-lab-design@atr-lab`, then `/atr-lab-design:setup`) and stop.
3. Write the workshop folder under the current working directory (or the folder the user names), never inside
   `${CLAUDE_PLUGIN_ROOT}`; plugin updates replace that folder.

## Do

Start with the intake (SKILL.md §3, references/intake.md): `workshop.py init`, extract every fact from the request
into `workshop.json`, run `workshop.py check --json` and ask everything still missing in one round with the
AskUserQuestion tool, including "anything else you want the workshop to include or avoid?". Then design the
workshop, check the plan with the presenter, write and test the code, write the slides and notes, make the forms,
run `workshop.py build`, look at every render and hand off with the report in references/qa-and-handoff.md.
If the request is empty, ask what the workshop is about and when it is before anything else.
