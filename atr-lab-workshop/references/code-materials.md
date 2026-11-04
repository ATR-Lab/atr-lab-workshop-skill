# Code and hands-on materials

**Read this when** you write the workshop's code (phase 4), a presenter supplies a repository, or the hands-on
parts use hardware or a non-Python stack.

## 1. The layout

`workshop.py code -w <folder>` scaffolds `code/` without overwriting anything already there:

```
code/
├── README.md            for participants: before you come, check your setup, the activities
├── preflight.py         setup check (standard library, Python 3.8+), driven by preflight.json
├── preflight.json       what to check: Python, commands, packages, files, URLs, ports, disk, manual items
├── .gitignore
├── maps/, data/ ...     shared inputs (your choice of name)
└── NN-activity-name/    one folder per hands-on module (module.code_dir in the brief)
    ├── README.md        the task, the steps, "done when", the stretch goal
    ├── starter/         what participants edit: runs, but the task is a stub
    └── solution/        the finished version, with the same tests
```

Each activity folder is self-contained: copy shared helpers in (as the example copies `grid.py` into later
activities) so someone who skipped an activity can still start the next one.

## 2. Writing the code

1. **Solution first.** Write it, run it, write its tests (`unittest` from the standard library unless the stack
   already brings `pytest`), and run them until they pass.
2. **Then the starter.** Copy the solution and replace only the parts the activity asks for with a stub that
   raises `NotImplementedError("<function>: your turn")`, keeping the docstring and a `# TODO step N:` comment that
   matches the step on the slide. The starter's tests must fail only on the stubbed parts.
3. **Run both.** Solutions pass; starters fail where expected and nowhere else. Paste the result counts in your
   hand-off ("01: 5 passed on the solution, 3 of 5 fail on the starter as intended").
4. **Keep the slide and the code in step:** function names, step numbers and the done-when check are the same on
   the slide, in the activity README and in the code.
5. **Dependencies:** as few as the topic allows, pinned (`requirements.txt` with versions, or a lock file).
   Anything heavy (ROS 2, CUDA, a simulator) goes in a container or a prepared image, with the plain install as
   the fallback.
6. **Clean code:** clear names, small functions, comments that explain why. No secrets, tokens or personal data
   in the code or the data.

## 3. preflight.json

`workshop.py code` writes a first version from the prerequisites; tune it to the real stack. Each section is
optional:

```json
{
  "title": "Preflight: Robot path planning in Python",
  "contact": "atrlab.kent@gmail.com",
  "os": ["macOS", "Windows", "Linux"],
  "python": ">=3.10",
  "commands": [{"name": "git", "version_cmd": ["git", "--version"], "min": "2.30",
                "fix": "install Git from https://git-scm.com/downloads"},
               {"name": "VS Code", "exe": "code", "fix": "install VS Code"}],
  "python_packages": [{"name": "numpy", "min": "1.26", "fix": "python3 -m pip install numpy"}],
  "paths": [{"path": "maps/warehouse.txt", "label": "workshop map present"}],
  "env": [{"name": "ROS_DISTRO", "fix": "source /opt/ros/jazzy/setup.bash"}],
  "urls": [{"url": "https://pypi.org", "label": "package index reachable"}],
  "ports": [{"port": 8888}],
  "disk": {"min_gb": 5},
  "manual": ["Laptop charger packed"]
}
```

`python3 preflight.py` prints PASS, FAIL (with the fix), WARN or YOU (a manual item) per check, and READY or NOT
READY; exit 1 when anything fails. It changes nothing on the computer. Run it yourself before you hand off, and
put it in the reminder email a week before the workshop.

Software named with alternatives ("VS Code or another editor") becomes a manual item, not a failing command.

## 4. Other stacks

- **C/C++, Arduino, embedded:** keep `preflight.py` (it checks `arduino-cli`, `gcc`, `cmake` and paths), or write
  an equivalent shell script if participants will not have Python. Provide a board-specific `README` section on
  drivers (CH340 and CP210x on Windows and macOS).
- **ROS 2:** prefer a container image or a prepared VM; `env` checks `ROS_DISTRO`; give the source command.
- **Notebooks:** commit them with outputs cleared; provide a `requirements.txt` and a Colab link only when the
  presenter wants a browser option.
- **MATLAB, Unity, licensed tools:** check the license path in the README (Kent State software portal) and make
  the install a pre-work item.

## 5. Hardware

- Write the code against a simulation first so it is testable here; mark hardware-only steps clearly.
- A `hardware.md` in `code/` lists each kit's parts, wiring and a smoke test per kit, for the helpers.
- Never claim hardware code was tested when only the simulation ran; say exactly what ran.

## 6. Publishing

- The repository lives where the presenter decides (the lab's GitHub organization, ATR-Lab, needs its owners'
  approval). Never create or push a repository without being asked.
- License: MIT by default for teaching code (confirm with the presenter); third-party data and assets keep their
  own licenses, listed in the README.
- Put the repository link in `materials.repo_url` so the slides, the README and the preflight URL check pick it up.
