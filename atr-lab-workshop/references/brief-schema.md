# workshop.json reference

**Read this when** you fill or edit the brief. Every deliverable is built from this file; change it and rebuild
instead of editing outputs. `workshop.py init` writes a blank one; `examples/path-planning/workshop.json` is a
complete one.

Edit it directly, or with `workshop.py set <dotted.path> <value>` (values parse as JSON when they can:
`set audience.capacity 24`, `set promotion.flyer_sizes '["letter","tabloid"]'`).

## Top level

| Field | Type | Used for | Notes |
|---|---|---|---|
| `schema` | `"atr-workshop/1"` | | required |
| `slug` | string | file names | default: from `short_title` or `title` and the date |
| `title` | string | everything | sentence case |
| `short_title` | string | TV slide, file names | three to five words |
| `subtitle` | string | title slide | one line, about 50 characters |
| `summary` | string | flyer subtitle, forms, outline | one sentence, at most 115 characters on the flyer |
| `topics` | list | outline, intake | the presenter's own words |
| `format` | `in-person`, `virtual`, `hybrid` | venue lines | |
| `requests` | list | outline, your plan | anything else the presenter asked for, verbatim |
| `assumptions` | list | hand-off list | every default you chose |
| `open_questions` | list | hand-off list | what the presenter will settle later |

## `when`

| Field | Example | Notes |
|---|---|---|
| `date` | `2027-02-13` | ISO date; printed "Saturday, Feb. 13, 2027" |
| `start`, `end` | `10:00`, `14:00` | 24-hour; printed "10 a.m.-2 p.m. EST" |
| `timezone` | `America/New_York` | IANA name; the abbreviation follows daylight saving |
| `check_in` | `9:45 a.m.` | optional second line on the flyer |

## `where`

`building`, `room`, `campus` (default "Kent State University, Kent Campus"), `address`, `online_url`,
`parking`, `wifi`, `notes`. Use the verified building name, "Mathematical Sciences Building", never "Mathematics
and Computer Science Building".

## `audience`

`who` (string), `level` (`beginner`, `intermediate`, `advanced`, `mixed`), `capacity` (number: the registration
form closes itself there), `cost` ("Free, lunch provided").

## `presenters`

A list of `{"name", "role", "email"}`. The first one is on the title slide and the thank-you slide; the first two
appear on the title slide's presenter line. Roles follow Kent State style: "Ph.D. student", "associate professor
of computer science".

## `prerequisites`

Lists: `skills`, `hardware`, `software`, `accounts`, `provided`, `pre_work`. `["none"]` is an explicit "nothing
needed". These feed the flyer's requirements line, the registration form's background grid and setup checklist,
the participant README and the generated `code/preflight.json`.

## `objectives`

Three to five measurable outcomes: a verb, a task, a condition ("Implement A* and explain how its heuristic
works"). They appear on the objectives and wrap-up slides, in the outline and as rows in the feedback form.

## `modules`

A list of teaching units, at most five on the agenda slide.

| Field | Notes |
|---|---|
| `id` | short key that schedule blocks point to (`m1`) |
| `title`, `agenda_title` | `agenda_title` at most 24 characters (the agenda plate) |
| `verb` | one word for the flyer's workflow step ("Model", "Search", "Drive") |
| `summary` | one or two lines, at most 80 characters (the section divider) |
| `objectives` | which course objectives it serves |
| `key_points` | each one becomes a concept slide title: 38 characters at most |
| `activity` | `{"title", "minutes", "steps": [...], "checkpoint", "stretch"}`; five steps make a timeline slide |
| `code_dir` | `code/NN-name`, set by `workshop.py code` |

## `schedule`

An ordered list of blocks `{"kind", "title", "minutes", "module"?, "notes"?}`. Kinds: `setup`, `welcome`,
`talk`, `demo`, `hands-on`, `discussion`, `qa`, `break`, `lunch`, `wrap-up`, `feedback`, `buffer`. The minutes
must add up to the event's length (references/schedule.md).

## `materials`

`repo_url`, `languages`, `stack`, `license`.

## `registration`

| Field | Notes |
|---|---|
| `url` | the registration form's respondent link (from the Apps Script log); the flyer and TV QR codes encode it exactly |
| `printed_url` | the short link printed as text, without `https://` (`forms.gle/...` from the Apps Script log); 20 characters or fewer go in the flyer's registration panel, longer ones on its contact line; the TV slide encodes and prints it |
| `feedback_url` | the feedback form's link, for the last slide's QR code |
| `deadline` | "Wednesday, Feb. 10" |
| `forms` | which forms to generate: `["registration", "feedback"]` |
| `extra_questions` | form items (references/google-forms.md) appended to the registration form |

## `promotion`

| Field | Default | Notes |
|---|---|---|
| `eyebrow` | "HANDS-ON WORKSHOP · ATR LAB" | flyer eyebrow, caps, at most 61 characters |
| `flyer_title` | `title` | two lines at most; `\n` sets the break |
| `audience` | built from `audience` | flyer WHO block, three lines at most |
| `requirements` | built from `prerequisites` | flyer fine print, at most 108 characters |
| `agenda` | the first three module titles | flyer "What you will do", three lines of 45 characters |
| `workflow` | module verbs and titles | three `[title, detail]` steps, 29 characters each |
| `registration_head` | "Four-hour workshop" | flyer panel line, 19 characters ("Sign up by Feb. 10") |
| `tools` | none | `[{"label", "image", "alt"}]` icons for the tools row; `image` is a path in the design skill (`assets/icons/png/code-navy.png`) or absolute |
| `flyer_sizes` | `["letter"]` | `letter`, `tabloid`, `17x22` |
| `tv_slide` | `true` | the hallway TV slide |
| `tv_title`, `tv_eyebrow`, `tv_subtitle`, `tv_qr_label` | from `short_title` | keep the slide to about 20 words |
| `motion` | `""` | `lattice-drift`, `grid-scan` or `chevron-flow`: animated TV slide and deck |
| `teo_cameo` | `false` | Teo the mascot pops up on the TV slide; only on request |

## `contact`

`email` (overrides the first presenter's), `phone` (label a department line as the department's).
