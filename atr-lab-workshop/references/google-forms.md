# Google Forms

**Read this when** you make the registration or feedback form (phase 6), the presenter asks for extra
questions, or the links come back from the Apps Script.

## 1. How the import works

Google Forms has no file import (its own "Import questions" copies from another form). The file the presenter
imports is `forms/create-forms.gs`, a Google Apps Script:

1. `workshop.py forms init` writes `registration.form.json` and `feedback.form.json` from the brief.
2. You adjust them (§3), then `workshop.py forms build` validates every spec and writes `create-forms.gs` (the
   specs embedded as data, plus a small builder), `forms-preview.md` (every question, for review) and `IMPORT.md`
   (step-by-step for the presenter).
3. The presenter pastes the script into script.google.com, runs `createAllForms` once and approves the
   permissions. The forms are created in their Drive, published, linked to new response sheets and, when a
   capacity is set, given a trigger that closes registration when it fills.
4. The execution log prints one JSON line per form: `edit_url`, `respond_url`, `short_url` (forms.gle).
5. They paste those back; you run `workshop.py set registration.url <respond_url>`,
   `set registration.printed_url <short_url without https://>` and `set registration.feedback_url <respond_url>`,
   then `workshop.py build`. The flyers, the TV slide and the feedback slide now point at the real forms.

Never create the forms yourself through a connector, an API or a browser unless the user asks you to, and never
on an account other than theirs.

Test the script offline when Node.js is installed: `node scripts/tests/mock_apps_script.js forms/create-forms.gs`
runs it against a mock of FormApp and prints what it would build (it catches unknown item types, empty or
duplicate choices and bad scale bounds).

## 2. The default forms

**Registration** (sections: About you, Your background, Your setup, Logistics): full name, email (validated),
role, department; a comfort grid with one row per prerequisite skill; what they hope to learn; laptop OS and a
checklist of the hardware and software to have ready; accommodations (private follow-up), dietary needs when the
schedule has a meal, a photo preference; then `registration.extra_questions`. The description carries the date,
time, place, host line, deadline, seats and contact; the confirmation repeats the date. Closes at
`audience.capacity`.

**Feedback** (one section): overall usefulness (1-5), "After today, I can..." grid with the objectives as rows,
pace, hands-on usefulness and whether the setup worked (when there was hands-on work), what was most useful,
what to change, future topics, an optional email.

## 3. The spec format

```json
{
  "key": "registration",
  "title": "Register: Robot path planning in Python",
  "description": "...",
  "confirmation": "You're registered ...",
  "closed_message": "Registration is full or closed ...",
  "collect_email": false,
  "limit_one_response": false,
  "progress_bar": true,
  "responses_sheet": true,
  "capacity": 24,
  "sections": [{"title": "About you", "description": "...", "items": [ ... ]}]
}
```

Item types (`type`), each with `title`, optional `help` and `required`:

| Type | Extra fields | Google Forms item |
|---|---|---|
| `short_text` | | Short answer |
| `email` | | Short answer with email validation |
| `number` | | Short answer with number validation |
| `paragraph` | | Paragraph |
| `multiple_choice` | `choices`, `other` | Multiple choice |
| `checkboxes` | `choices`, `other` | Checkboxes |
| `dropdown` | `choices` | Dropdown |
| `scale` | `low` (0 or 1), `high` (3-10), `low_label`, `high_label` | Linear scale |
| `grid` | `rows`, `columns` | Multiple-choice grid |
| `checkbox_grid` | `rows`, `columns` | Checkbox grid |
| `date`, `time` | | Date, Time |
| `section_header` | | Title and description |

Each section after the first becomes a new page. `limit_one_response` requires respondents to sign in to Google;
leave it off for events open to people without Google accounts.

## 4. Privacy and fairness

- Ask only what the workshop needs. No student ID numbers, birth dates or demographic questions unless the
  presenter needs them for a stated reason (a sponsor report) and says so on the form.
- Accommodations stay optional and private ("Only the organizers see this").
- The photo preference is not a photo release; Kent State's release forms apply to anyone featured
  (design skill imagery rules).
- **K-12 participants:** the form is filled in by a parent or guardian; add the participant's grade (not their
  age or birth date), an emergency contact and the guardian's consent question supplied by the program, and follow
  the design skill's K-12 rules. Never ask minors for photos or social handles.
- Responses live in the presenter's Google account; share the sheet only with the organizers.

## 5. Changing a form later

Small changes: edit the form in Google Forms directly. Rebuilding with the script creates new forms with new
links, so after a rebuild the presenter must send you the new links and you rebuild the promotion.
