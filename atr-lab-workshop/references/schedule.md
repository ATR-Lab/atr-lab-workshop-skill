# The schedule

**Read this when** you write `schedule` in the brief or the pacing check complains. `workshop.py schedule` turns
the blocks into `schedule.md` (the run-of-show with AP-style clock times), `schedule.csv` and `workshop.ics` (one
calendar event for confirmations and reminders), and prints the pacing checks.

## 1. Blocks

Each block is `{"kind", "title", "minutes", "module"?, "notes"?}`, in order; clock times are computed from
`when.start`. Kinds and what the deck skeleton makes of them:

| Kind | Use | Slides in the skeleton |
|---|---|---|
| `welcome` | opening, introductions, goals | title, logistics, agenda, objectives |
| `setup` | everyone runs the preflight; hardware hand-out | "Check your setup" |
| `talk` | concept teaching, tied to a module | a section divider (first block of a module), one slide per key point |
| `demo` | the presenter runs something live | "Demo: ..." with what to watch for |
| `hands-on` | participants build | the task (steps) and a checkpoint slide |
| `discussion` | pairs or groups discuss prompts | "Discuss: ..." |
| `qa` | questions | "What questions do you have?" |
| `break`, `lunch` | rest | a statement slide with the return time and what is next |
| `wrap-up` | what they can do now, next steps | "What you can do now" |
| `feedback` | the feedback form | the feedback QR slide (always added before "Thank you") |
| `buffer` | slack for overruns | none |

## 2. Pacing rules (checked)

| Rule | Severity |
|---|---|
| Blocks add up to more than the event | error |
| Blocks add up to less than the event | warning (add a buffer or end earlier) |
| More than 90 minutes without a break or lunch | warning |
| A talk longer than 30 minutes | warning (split it with a demo or a question) |
| Four hours or more without a meal break | warning |
| No Q&A or discussion | warning |
| The last two blocks are not a wrap-up or feedback | warning |
| Hands-on work with no setup block in the first three | warning |
| A break shorter than 10 or longer than 20 minutes | info |
| Practice (hands-on, demo, discussion) under 40% of teaching time in a hands-on workshop | info |
| No buffer in an event of two hours or more | info |

Fix every warning, or say in the hand-off why it stands (a sponsor's fixed talk, for example).

## 3. Recipes

Start from the closest one and adjust. Minutes in brackets.

**90 minutes, one topic.** welcome [5] · talk [15] · demo [10] · hands-on [35] · qa [10] · wrap-up [10] ·
feedback [5]

**Half day, three hours, two modules.** welcome [10] · setup [15] · talk [15] · demo [10] · hands-on [30] ·
break [15] · talk [15] · hands-on [35] · qa [15] · wrap-up [15] · feedback [5]

**Four hours with lunch, three modules** (the path-planning example). welcome [10] · setup [15] · talk [20] ·
demo [10] · hands-on [25] · break [10] · talk [15] · hands-on [35] · lunch [35] · talk [10] · hands-on [30] ·
qa [10] · wrap-up [10] · feedback [5]

**Full day, 9 a.m.-4 p.m., four modules.** welcome [10] · setup [15] · module 1 [60] · break [15] · module 2
[75] · buffer [5] · lunch [60] · module 3 [75] · break [15] · module 4 [45] · buffer [10] · qa [15] · wrap-up
[15] · feedback [5]. A 75-minute module: talk [15] · demo [10] · hands-on [50, the last 5 for the checkpoint]; a
60-minute one: talk [15] · demo [5] · hands-on [40].

**Two days.** Day 1 as the full day ending with a recap instead of feedback; day 2 opens with a 15-minute recap
and a setup check, ends with a project showcase (`discussion`, 45) before Q&A, wrap-up and feedback. Make one
brief per day (two folders) so each day gets its own schedule and deck, and share the forms.

**Virtual, two and a half hours.** welcome [10] · talk [15] · demo [10] · hands-on [30] · break [10] · talk
[15] · hands-on [25] · break [5] · qa [15] · wrap-up [10] · feedback [5]

## 4. Times in Kent State style

The scripts print times in AP style: "10 a.m.", "1:30 p.m.", "noon", ranges "9-11 a.m." and "10 a.m.-2 p.m.",
with the zone ("EST", "EDT") on the flyer and the TV slide. Write your own copy the same way; never "10:00 AM".
