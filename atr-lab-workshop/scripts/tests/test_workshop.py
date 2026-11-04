"""Offline tests for the workshop scripts (no design skill, LibreOffice or network needed).

Run from the skill folder:  python3 -m pytest -q -p no:cacheprovider scripts/tests
"""
import copy
import datetime as dt
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from wslib import brief as B  # noqa: E402
from wslib import code as C  # noqa: E402
from wslib import deck as D  # noqa: E402
from wslib import design as G  # noqa: E402
from wslib import forms as F  # noqa: E402
from wslib import schedule as S  # noqa: E402
from wslib import status as T  # noqa: E402
from wslib.common import ap_date, ap_time_range, duration_words, slugify  # noqa: E402

EXAMPLE = SKILL / "examples/path-planning"


@pytest.fixture()
def example():
    return B.load(EXAMPLE / "workshop.json")


@pytest.fixture()
def folder(tmp_path):
    target = tmp_path / "ws"
    shutil.copytree(EXAMPLE, target)
    return target


def test_ap_dates_and_times():
    assert ap_date(dt.date(2027, 2, 13)) == "Saturday, Feb. 13, 2027"
    assert ap_date(dt.date(2027, 9, 3), weekday=False) == "Sept. 3, 2027"
    assert ap_date(dt.date(2027, 6, 1), weekday=False) == "June 1, 2027"
    assert ap_time_range(dt.time(10), dt.time(14)) == "10 a.m.-2 p.m."
    assert ap_time_range(dt.time(9), dt.time(11)) == "9-11 a.m."
    assert ap_time_range(dt.time(9), dt.time(12)) == "9 a.m.-noon"
    assert ap_time_range(dt.time(13, 30), dt.time(15)) == "1:30-3 p.m."


def test_duration_words_and_slugs():
    assert duration_words(240) == "four-hour"
    assert duration_words(90) == "90-minute"
    assert duration_words(150) == "two-and-a-half-hour"
    assert slugify("A* search") == "a-star-search"


def test_blank_brief_asks_every_required_question():
    issues = B.check(B.new_brief())
    required = {i.path for i in issues if i.severity == "required"}
    for path in ("title", "topics", "when.date", "when.start", "when.end", "where.building", "where.room",
                 "audience.who", "audience.level", "prerequisites.skills", "prerequisites.hardware",
                 "presenters.0.name", "presenters.0.email"):
        assert path in required
    assert not B.ready_to_build(issues)


def test_example_brief_is_complete(example):
    assert B.ready_to_build(B.check(example))


def test_check_catches_wrong_building_and_times(example):
    bad = copy.deepcopy(example)
    bad["where"]["building"] = "Mathematics and Computer Science Building"
    bad["when"]["end"] = "09:00"
    paths = {i.path for i in B.check(bad) if i.severity == "error"}
    assert {"where.building", "when.end"} <= paths


def test_placeholders_are_required_questions(example):
    draft = copy.deepcopy(example)
    draft["where"]["room"] = "[Room ###]"
    assert any(i.path == "where.room" and i.severity == "required" for i in B.check(draft))


def test_set_value_parses_json_and_paths(example):
    B.set_value(example, "audience.capacity", "30")
    B.set_value(example, "presenters.1.name", "Second Presenter")
    assert example["audience"]["capacity"] == 30
    assert example["presenters"][1]["name"] == "Second Presenter"


def test_schedule_times_and_clean_pacing(example):
    slots = S.timeline(example)
    assert slots[0].clock == "10:00" and slots[-1].end == dt.time(14)
    assert not [n for n in S.pacing(example, slots) if n[0] in ("error", "warning")]


def test_pacing_flags_overrun_and_missing_breaks(example):
    long = copy.deepcopy(example)
    long["schedule"] = [{"kind": "talk", "title": "Everything", "minutes": 250}]
    severities = {sev for sev, _ in S.pacing(long, S.timeline(long))}
    assert "error" in severities and "warning" in severities


def test_schedule_outputs(example, tmp_path):
    written = S.write_outputs(example, tmp_path)
    assert {p.name for p in written} == {"schedule.md", "schedule.csv", "workshop.ics"}
    ics = (tmp_path / "workshop.ics").read_text()
    assert "DTSTART:20270213T150000Z" in ics and "DTEND:20270213T190000Z" in ics


def test_default_forms_validate_and_build(example, tmp_path):
    F.init_specs(example, tmp_path)
    for path in tmp_path.glob("*.form.json"):
        assert F.validate(json.loads(path.read_text()), path.name) == []
    F.build(tmp_path)
    script = (tmp_path / "create-forms.gs").read_text()
    assert "function createAllForms()" in script and "/*__FORMS__*/" not in script
    registration = json.loads((tmp_path / "registration.form.json").read_text())
    assert registration["capacity"] == 24
    titles = [i["title"] for s in registration["sections"] for i in s["items"]]
    assert "Dietary needs for the meal (optional)" in titles


def test_form_validation_rejects_bad_items():
    spec = {"key": "x", "title": "X", "sections": [{"title": "s", "items": [
        {"type": "multiple_choice", "title": "One choice", "choices": ["only"]},
        {"type": "scale", "title": "Scale", "low": 2, "high": 20},
        {"type": "slider", "title": "Unknown"}]}]}
    assert len(F.validate(spec, "x")) == 3


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js not installed")
def test_apps_script_runs_in_the_mock(example, tmp_path):
    F.init_specs(example, tmp_path)
    F.build(tmp_path)
    out = subprocess.run(["node", str(SCRIPTS / "tests/mock_apps_script.js"), str(tmp_path / "create-forms.gs")],
                         capture_output=True, text=True, check=True)
    result = json.loads(out.stdout)
    assert [r["key"] for r in result["results"]] == ["registration", "feedback"]
    assert all(f["published"] and f["accepting"] for f in result["forms"])


def test_skeleton_follows_the_schedule(example, tmp_path):
    spec = D.skeleton(example, tmp_path)
    layouts = [s["layout"] for s in spec["slides"]]
    assert layouts[0] == "ATR - Title" and layouts[-1] == "ATR - Thank You"
    assert layouts.count("ATR - Section Divider") == 3
    statements = [s["statement"] for s in spec["slides"] if s["layout"] == "ATR - Statement"]
    assert "Break: back at 11:30 a.m." in statements and "Lunch: back at 12:55 p.m." in statements
    agenda = next(s for s in spec["slides"] if s["layout"] == "ATR - Agenda")
    assert [agenda[f"item{i}"] for i in range(1, 6)][0] == "Setup check"
    titles = [s.get("title") for s in spec["slides"] if s.get("title")]
    assert len(titles) == len(set(titles))
    assert all(len(t) <= 38 for t in titles if "{{" not in t)


def test_example_deck_notes_are_complete(example):
    spec = json.loads((EXAMPLE / "slides/deck.json").read_text())
    rows = D.speaker_notes(spec, G.project_facts(example))
    assert len(rows) == len(spec["slides"])
    assert D.check_notes(rows) == []


def test_notes_check_flags_missing_and_unbulleted():
    rows = [(1, "A", ["• only one"]), (2, "B", ["no bullet", "• fine"])]
    problems = D.check_notes(rows)
    assert any("at least two" in p for p in problems) and any("not a bullet" in p for p in problems)


def test_code_brackets_are_masked_and_restored(tmp_path):
    spec = {"slides": [D.code_slide("Code", "grid[row][col]\nnames = ['a', 'b']")]}
    built = D.build_copy(spec)
    text = built["slides"][0]["textboxes"][0]["text"]
    assert "[" not in text and "code" not in built["slides"][0]["textboxes"][0]
    pptx = tmp_path / "deck.pptx"
    with zipfile.ZipFile(pptx, "w") as zf:
        zf.writestr("ppt/slides/slide1.xml", f"<a:t>{text}</a:t>")
        zf.writestr("ppt/presentation.xml", "<p/>")
    assert D.unmask(pptx) == 1
    with zipfile.ZipFile(pptx) as zf:
        assert zf.read("ppt/slides/slide1.xml").decode() == "<a:t>grid[row][col]\nnames = ['a', 'b']</a:t>"


def test_design_project_has_deck_flyers_and_assets(example, folder):
    (folder / "slides").mkdir(exist_ok=True)
    project = json.loads(G.write_project(example, folder, folder / "slides/deck.json").read_text())
    assert set(project["artifacts"]) == {"deck", "flyer-letter", "flyer-tabloid"}
    assert project["facts"]["event_date"] == "Saturday, Feb. 13, 2027"
    assert project["facts"]["registration_url"] == G.PLACEHOLDER_URL
    assert (folder / "design/deck.build.json").is_file()
    assert Path(project["assets"]["code-panel"]["path"]).is_file()


def test_code_scaffold_keeps_existing_files(example, folder):
    keep = folder / "code/02-a-star-search/solution/astar.py"
    before = keep.read_text()
    C.scaffold(example, folder / "code")
    assert keep.read_text() == before
    assert (folder / "code/README.md").is_file() and (folder / "code/preflight.py").is_file()


def test_example_solutions_pass_their_tests(folder):
    for activity in sorted((folder / "code").glob("[0-9][0-9]-*")):
        run = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q"], cwd=activity / "solution",
                             capture_output=True, text=True)
        assert run.returncode == 0, f"{activity.name}: {run.stderr}"


def test_example_starters_fail_on_the_task(folder):
    for activity in sorted((folder / "code").glob("[0-9][0-9]-*")):
        run = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q"], cwd=activity / "starter",
                             capture_output=True, text=True)
        assert run.returncode != 0 and "NotImplementedError" in run.stderr


def test_status_ignores_code_and_markdown_links(example, folder):
    info = T.collect(example, folder)
    assert not any(n.startswith("Slides:") for n in info["needed"])
    assert any("Create the Google Forms" in n for n in info["needed"])
