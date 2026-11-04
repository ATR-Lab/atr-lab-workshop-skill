# Promotion: flyers and the hallway TV slide

**Read this when** you build or change the flyers or the TV slide, or plan when promotion goes out. Both come
from the atr-lab-design skill; its references/print-and-merch.md §5 (event flyers) and references/web-and-
digital.md §9-§10 (QR codes, signage) are the full rules.

## 1. How they are built

`workshop.py build` writes `design/project.json` (the design skill's project manifest) from the brief: facts
(date, time, venue, audience, agenda, workflow, registration link, contact), the deck and one artifact per flyer
size. The design skill builds each flyer on its event-flyer template by field name, generates the registration
QR code at its printed size, exports a tagged PDF, decodes the QR code back from the PDF and lints everything.
The TV slide is made with `banner.py --preset signage-16x9` and its QR code is decoded from the image.

| Output | Template or preset | Size |
|---|---|---|
| `atr-flyer-<topic>-<date>-letter` | `event-flyer` | 8.5 × 11 in: bulletin boards, handouts |
| `atr-flyer-<topic>-<date>-tabloid` | `event-flyer-tabloid` | 11 × 17 in: posters |
| `atr-flyer-<topic>-<date>-17x22` | `event-flyer-17x22` | 17 × 22 in: large posters, easels |
| `atr-tv-<topic>-<date>.jpg` | `signage-16x9` | 1920 × 1080: the Mathematical Sciences Building TVs, lab monitors |

Each flyer comes as `.pdf` (print and share), `.pptx` (edit) and `.png` (preview).

## 2. Flyer copy

Set it in `promotion` (references/brief-schema.md has the budgets); the defaults come from the brief.

- **Eyebrow:** event type and series, all caps: "HANDS-ON WORKSHOP · ROBOTICS IN PYTHON".
- **Title:** what they will learn, two lines: "Robot path planning\nin Python".
- **Subtitle:** the summary sentence: what they do and who it is for.
- **WHEN / WHERE / WHO:** formatted from the brief; WHO is three short lines (who, level, cost and seats).
- **What you will do:** three activities, one line each.
- **Workflow:** three steps, a verb and a detail ("Search / Shortest path with A*").
- **Requirements:** what to bring and install, one or two lines.
- **Registration panel:** "Sign up by Feb. 10" (or the duration), the QR code, the printed short link and the
  contact.
- **Tools row:** optional icons with plain product names; use official product icons from the vendor's brand kit,
  unmodified, or the design skill's icons as stand-ins (say so).

Read the render: the design skill measures every field with the brand fonts and warns about overflow. Cut words
until there are no warnings.

## 3. The TV slide

About 20 words, read in a glance from across a hallway: eyebrow, title (the `short_title` or `tv_title`), the date
and time line, the place line and a QR code with "Scan to register" and the printed link. The Kent State wordmark
sits bottom-right. If banner.py refuses ("does not fit at the legibility floor"), shorten the title or the
eyebrow, never the type. `promotion.motion` adds a 12-second looping MP4 (the JPEG is its still frame);
`teo_cameo` only when asked for.

Submitting it: the building's TV slideshow has an owner (ask the department office); give them the JPEG (and the
MP4 if their player takes video) with the run dates.

## 4. QR codes

- Flyers and slides encode `registration.url` exactly; no tracking parameters, no other URL.
- The TV slide prints the address it encodes, so it uses the forms.gle short link (`registration.printed_url`,
  Google's own link to the same form) when there is one, to stay readable from across a hallway;
  `promotion.tv_qr_url` overrides it.
- Until the forms exist the link is `https://example.org/register`, a placeholder: the hand-off says so and
  nothing is printed or posted.
- The printed text on the flyer is `registration.printed_url` (in the panel when it is 20 characters or fewer,
  otherwise on the contact line) or, without one, the cleaned URL.
- The QA report shows the decoded value from each PDF and the TV image. A person still scans a printed proof with
  an iPhone and an Android phone.

## 5. The Kent State wordmark

The templates carry a working copy. Before anything is shared, printed or posted: `workshop.py official-logos`
fetches the official file from kent.edu (checksum-verified), swaps it into the deck and flyers, re-exports and
remakes the TV slide. A failed download is a network problem: retry, or ask the presenter to download the
Stacked artwork zip (design skill `official_assets.py --archive`).

## 6. Approvals and printing

- Printing goes to a Kent State contracted printer; give them the PDF and ask for a proof.
- Posting on campus follows building and university posting rules; the TV slideshow has its own contact.
- Social posts, newsletter items and department calendar entries: hand the brief's facts to the atr-lab-design
  skill (social cards, captions, copy). Outline §11 has the timeline (about four weeks out).
