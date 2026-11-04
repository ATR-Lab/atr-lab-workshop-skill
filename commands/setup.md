---
description: Check that the ATR Lab workshop plugin and the atr-lab-design plugin it depends on are ready
disable-model-invocation: true
---

Set up the atr-lab-workshop plugin on this machine.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/atr-lab-workshop/scripts/workshop.py" doctor`. The workshop scripts need
   only Python 3.9 or newer; everything else comes from the atr-lab-design skill.
2. If the design skill is missing, tell the user to install it: `/plugin marketplace add ATR-Lab/atr-lab-design-skill`,
   `/plugin install atr-lab-design@atr-lab`, then `/atr-lab-design:setup`, and to restart Claude Code. Do not
   install plugins or system software yourself.
3. If the design skill is found but its Python is missing, point to `/atr-lab-design:setup`.
4. Node.js is optional (it lets the skill test the Google Forms script offline); mention it only if missing.
5. Report what is ready, what is missing with its fix, and the commands: `/atr-lab-workshop:workshop`,
   `:forms-ready`, `:revise`, `:status`.
