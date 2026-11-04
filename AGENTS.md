# atr-lab-workshop-skill

The ATR Lab workshop skill: a Claude Code / Codex skill (and Claude Code plugin) that interviews a presenter and
builds a complete academic workshop package (outline, schedule, slides with speaker notes, code, Google Forms as an
Apps Script, flyers, hallway TV slide). Slides and promotion are delegated to the atr-lab-design skill
(https://github.com/ATR-Lab/atr-lab-design-skill), which must be installed.

## Layout

- `atr-lab-workshop/`: the skill. `SKILL.md` is the entry point; `references/` the detailed guides;
  `scripts/workshop.py` the CLI with `scripts/wslib/` behind it; `assets/templates/` the files it copies or fills;
  `examples/path-planning/` the finished reference workshop.
- `.claude-plugin/`, `commands/`: the Claude Code plugin and its slash commands.
- `.claude/skills/atr-lab-workshop`: committed symlink so sessions in this repo load the skill.
- `.github/images/`: README images, generated from the example build (README "For maintainers").

## Rules

- Scripts are Python 3.9+ standard library only. Anything needing packages (python-pptx, Pillow) runs through the
  design skill's own Python, located by `wslib/common.py`.
- Never write into the skill or the design skill at run time; workshop folders live wherever the user works.
- Facts policy comes from the design skill: no invented people, rooms, results or links; placeholders stay visible.
- Keep `SKILL.md`, the references, the README and the slash commands consistent when behavior changes; bump
  `.claude-plugin/plugin.json` and add a `CHANGELOG.md` entry for releases.

## Checks

From `atr-lab-workshop/`:

```bash
python3 -m pytest -q -p no:cacheprovider scripts/tests      # or: uvx pytest -q -p no:cacheprovider scripts/tests
python3 scripts/workshop.py doctor
python3 scripts/workshop.py init /tmp/ex --example path-planning && python3 scripts/workshop.py code -w /tmp/ex \
  && python3 scripts/workshop.py build -w /tmp/ex             # full build; look at design/work/qa/ renders
```

Remove `__pycache__` and `.DS_Store` before committing.
