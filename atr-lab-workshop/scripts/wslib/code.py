"""The participant code folder: README, preflight check and one starter/solution pair per hands-on module."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from .brief import derived
from .common import SKILL_ROOT, slugify, write_json, write_text

KNOWN_COMMANDS = {
    "git": {"name": "git", "version_cmd": ["git", "--version"], "min": "2.30",
            "fix": "install Git from https://git-scm.com/downloads"},
    "python": None,
    "docker": {"name": "docker", "version_cmd": ["docker", "--version"], "fix": "install Docker Desktop"},
    "vs code": {"name": "VS Code", "exe": "code", "fix": "install VS Code and run 'Shell Command: Install code "
                                                       "command in PATH'"},
    "node": {"name": "node", "version_cmd": ["node", "--version"], "min": "20", "fix": "install Node.js LTS"},
    "ros 2": {"name": "ros2", "version_cmd": ["ros2", "--help"], "fix": "install ROS 2 or use the workshop container; "
                                                                      "remember to source the setup file"},
    "arduino": {"name": "arduino-cli", "version_cmd": ["arduino-cli", "version"], "fix": "install Arduino CLI"},
    "conda": {"name": "conda", "version_cmd": ["conda", "--version"], "fix": "install Miniconda"},
    "uv": {"name": "uv", "version_cmd": ["uv", "--version"], "fix": "install uv: https://docs.astral.sh/uv/"},
    "matlab": {"name": "matlab", "fix": "install MATLAB with your Kent State license"},
    "unity": {"name": "Unity Hub", "exe": "unityhub", "fix": "install Unity Hub"},
    "gcc": {"name": "gcc", "version_cmd": ["gcc", "--version"], "fix": "install a C compiler"},
    "cmake": {"name": "cmake", "version_cmd": ["cmake", "--version"], "fix": "install CMake"},
}


def preflight_config(brief: dict) -> dict:
    pre = brief.get("prerequisites") or {}
    langs = [x.lower() for x in (brief.get("materials") or {}).get("languages") or []]
    config = {"title": f"Preflight: {brief.get('title') or 'workshop'}", "contact": derived(brief)["contact"],
              "commands": [], "python_packages": [], "urls": [], "manual": [], "disk": {"min_gb": 5}}
    if "python" in langs:
        config["python"] = ">=3.10"
    seen = set()
    for item in ["git"] + list(pre.get("software") or []):
        key = None if " or " in item.lower() else next(
            (k for k in KNOWN_COMMANDS if re.search(rf"\b{re.escape(k)}\b", item.lower())), None)
        if key and KNOWN_COMMANDS[key] and key not in seen:
            config["commands"].append(dict(KNOWN_COMMANDS[key]))
            seen.add(key)
        elif not key:
            config["manual"].append(f"Installed and opens: {item}")
    for item in list(pre.get("hardware") or []) + list(pre.get("accounts") or []):
        if item.strip().lower() != "none":
            config["manual"].append(f"Ready: {item}")
    if brief.get("materials", {}).get("repo_url"):
        config["urls"].append({"url": brief["materials"]["repo_url"], "label": "workshop materials reachable"})
    return config


def scaffold(brief: dict, code_dir: Path, force: bool = False) -> list:
    """Create code/ without overwriting anything the agent or presenter already wrote."""
    written = []

    def put(path: Path, text: str) -> None:
        if path.exists() and not force:
            return
        write_text(path, text)
        written.append(path)

    facts = derived(brief)
    modules = [m for m in brief.get("modules") or [] if m.get("activity") or m.get("hands_on", True)]
    rows = []
    for number, module in enumerate(modules, start=1):
        folder = module.get("code_dir") or f"code/{number:02d}-{slugify(module.get('title', 'module'))}"
        module["code_dir"] = folder
        rel = Path(folder).relative_to("code") if folder.startswith("code/") else Path(folder)
        base = code_dir / rel
        activity = module.get("activity") or {}
        steps = "\n".join(f"{i}. {s}" for i, s in enumerate(activity.get("steps") or ["[Step]"], start=1))
        put(base / "README.md",
            f"# {number:02d}. {module.get('title', '')}\n\n"
            f"{module.get('summary', '')}\n\n"
            f"## Your task\n\n{steps}\n\n"
            f"**Done when:** {activity.get('checkpoint') or '[what you see when it works]'}\n\n"
            + (f"**Finished early?** {activity['stretch']}\n\n" if activity.get("stretch") else "")
            + "Work in `starter/`. `solution/` has a finished version: try for ten minutes before you look.\n")
        put(base / "starter" / ".gitkeep", "")
        put(base / "solution" / ".gitkeep", "")
        rows.append(f"| {number:02d} | [{module.get('title', '')}]({rel.as_posix()}/README.md) | "
                    f"{activity.get('minutes') or ''} |")

    template = (SKILL_ROOT / "assets/templates/code-README.md").read_text(encoding="utf-8")
    pre = brief.get("prerequisites") or {}

    def bullets(items: list, empty: str) -> str:
        items = [i for i in items or [] if i.strip().lower() != "none"]
        return "\n".join(f"- {i}" for i in items) if items else f"- {empty}"

    readme = (template
              .replace("{{title}}", brief.get("title") or "[Workshop title]")
              .replace("{{when}}", f"{facts['date_long']}, {facts['time_range']}")
              .replace("{{where}}", facts["venue"].replace("\n", ", "))
              .replace("{{skills}}", bullets(pre.get("skills"), "No experience needed"))
              .replace("{{hardware}}", bullets(pre.get("hardware"), "Nothing to bring"))
              .replace("{{software}}", bullets(pre.get("software"), "Nothing to install"))
              .replace("{{accounts}}", bullets(pre.get("accounts"), "No accounts needed"))
              .replace("{{provided}}", bullets(pre.get("provided"), "Nothing extra"))
              .replace("{{pre_work}}", bullets(pre.get("pre_work"), "None"))
              .replace("{{modules}}", "\n".join(rows) or "| | | |")
              .replace("{{contact}}", facts["contact"]))
    put(code_dir / "README.md", readme)
    if not (code_dir / "preflight.json").exists() or force:
        write_json(code_dir / "preflight.json", preflight_config(brief))
        written.append(code_dir / "preflight.json")
    target = code_dir / "preflight.py"
    if not target.exists() or force:
        shutil.copyfile(SKILL_ROOT / "assets/templates/preflight.py", target)
        target.chmod(0o755)
        written.append(target)
    put(code_dir / ".gitignore", "__pycache__/\n*.pyc\n.venv/\n.env\n.DS_Store\nbuild/\n*.egg-info/\n")
    return written
