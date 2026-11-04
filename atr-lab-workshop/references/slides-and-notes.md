# Slides and speaker notes

**Read this when** you write `slides/deck.json` (phase 5) or fix a deck warning. The deck is a spec for the
design skill's `new_deck.py` on its presentation template (22 layouts); `workshop.py build` builds it through
the design skill's `project.py`, exports a tagged PDF, decodes the QR codes and renders every page.

## 1. Start from the skeleton

`workshop.py deck skeleton -w <folder>` writes `slides/deck.json` shaped by the schedule:

1. Title (`ATR - Title`): date eyebrow, title, subtitle, presenters
2. Before we start: Wi-Fi, break times, how to get help, materials link
3. Agenda (`ATR - Agenda`): setup, modules, wrap-up with start times, and a WHEN / WHERE panel
4. By the end, you can: the objectives
5. Check your setup: the preflight command
6. Per module: a section divider, a slide per key point, a demo slide, the hands-on task and a checkpoint
7. A statement slide for every break and lunch with the return time and what comes next
8. Questions, What you can do now, Tell us how it went (feedback QR), Thank you

Facts come from the brief as `{{facts.NAME}}` (date, time, venue, presenter, links), so a change to the brief
reaches the deck on the next build. Content you must write is in `[brackets]`; the final build refuses them.
Compare with the finished `examples/path-planning/slides/deck.json`.

## 2. Writing slides

- **One message per slide.** The title says it ("Heuristics aim the search at the goal"), the body supports it.
- **Titles:** 38 characters at most (longer ones drop to 28 pt and warn). Every slide title must be unique (the
  linter checks): "Checkpoint: A* search", not "Checkpoint" three times.
- **Bodies:** up to seven one-line bullets of about 46 characters on `ATR - Title + Content`; a nested list is a
  sub-bullet. Under a third full gets a hint to use a visual layout; a text-only slide is fine for a hands-on
  task.
- **Pick the layout by job** (`python3 <design>/scripts/new_deck.py --list-layouts presentation` prints every
  field and budget):

  | Job | Layout |
  |---|---|
  | A concept with a figure or screenshot | `ATR - Content + Image` (figure plus caption "FIG. 01 // ...") |
  | Before and after, two approaches | `ATR - Two Content` |
  | Three options or parts | `ATR - Three Icon Columns` (design skill icons) |
  | Exactly five steps | `ATR - Timeline` |
  | One number that matters | `ATR - Key Numbers` or `ATR - Chart + Takeaway` |
  | A table (parameters, commands) | `ATR - Table` (six rows) |
  | A demo video | `ATR - Video` (its "what to watch for" placeholder is `fields.notes`; slide notes go in `speaker_notes`) |
  | A pause, a key takeaway, a break | `ATR - Statement` |
  | Anything custom | `ATR - Blank Branded` with `textboxes` and `images` |

- **Figures and screenshots:** `"figure": "path/to/file.png", "figure_alt": "..."` (alt text is required).
  Real screenshots and plots are best; AI images only as captioned concept illustrations, never as lab photos or
  results (design skill rules).
- **QR codes on slides:** `"figure": {"qr": {"url": "{{facts.feedback_url}}", "size_in": 1.6}}` on
  `ATR - Content + Image`, with the printed link in the caption (`{{facts.feedback_url|printed}}`).
- **Fix warnings by cutting words or choosing another layout,** never by shrinking type.

## 3. Code slides

The template has no code layout. Use the code slide pattern (what `wslib/deck.py` `code_slide()` makes):
`ATR - Title + Content` with `"body": ""` (deletes the body), the mist panel as a decorative picture and the
code as a Source Code Pro text box with `"code": true`:

```json
{"layout": "ATR - Title + Content", "section": 3, "title": "The A* loop", "body": "",
 "images": [{"path": "{{assets.code-panel}}", "alt": "", "decorative": true,
             "box": {"x": 0.5, "y": 1.42, "w": 9.0, "h": 3.2}, "fit": "contain"}],
 "textboxes": [{"text": "while open_set:\n    ...", "box": {"x": 0.68, "y": 1.56, "w": 8.64, "h": 2.95},
                "size": 16, "font": "Source Code Pro", "color": "1B2533", "code": true}],
 "notes": ["• Walk through one iteration.", "• Ask what the heap returns first."]}
```

- At most 11 lines of 64 characters at 16 pt (`deck notes` checks it); 14 pt is the floor. Show the part that matters, with `...`
  for the rest; the full file is in `code/`.
- Brackets in code (`grid[row]`, `["a", "b"]`) are fine: the design skill would refuse them as placeholders, so
  the build masks them in code text boxes and puts the real characters back in the `.pptx` before export. Brackets
  anywhere else are still placeholders.
- The code is editable and copyable in PowerPoint and in the PDF.

## 4. Speaker notes

Every slide has notes: a list of 2-6 strings (8 at most), each starting with `• `, each under about 200
characters. `workshop.py deck notes` checks this and writes `slides/speaker-notes.md`, one section per slide in
deck order; the same bullets are in the `.pptx` notes (Presenter View).

Write notes the presenter can glance at:

- **Say:** the one sentence that carries the slide.
- **Do:** what to show, run or point at.
- **Ask:** a question for the room, with what a good answer includes.
- **Time:** on section, demo, hands-on and break slides ("Time: 25 min, until 11:20 a.m.").
- **If it goes wrong:** the fallback (a recorded demo, the solution folder).

Bad: "Talk about A*." Good: "• Write f = g + h on the board and leave it there." Notes may not contain
`[brackets]` in a final build either.

## 5. Moving backgrounds and the mascot

Only on request: `promotion.motion` ("lattice-drift", "grid-scan", "chevron-flow") also animates the deck's
bookend slides (the PDF shows still frames); Teo appears only when asked for (K-12, outreach). Present the
`.pptx` when animated; share the PDF.

## 6. Delivering the deck

- The `.pptx` (for presenting and editing) and the tagged PDF (for sharing) in `deliverables/`.
- Fonts: the brand fonts are embedded in the PDF; for editing on another machine, install them from the design
  skill's `assets/fonts/` (Google Slides has them built in).
- LibreOffice renders the QA pages; PowerPoint may break a line one word differently. Ask the presenter to page
  through the `.pptx` once in PowerPoint or Keynote.
