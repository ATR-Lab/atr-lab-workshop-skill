# The intake interview

**Read this when** you start a workshop, the user's request leaves facts out, or you need the wording of a
question. The intake turns a request into a complete `workshop.json` with as few questions as possible.

## Contents

1. [The order of work](#1-the-order-of-work)
2. [What must be settled](#2-what-must-be-settled)
3. [The question bank](#3-the-question-bank)
4. [Defaults you may assume](#4-defaults-you-may-assume)
5. [Asking well](#5-asking-well)
6. [Worked examples](#6-worked-examples)
7. [Conflicts, gaps and honesty](#7-conflicts-gaps-and-honesty)

---

## 1. The order of work

1. `python3 scripts/workshop.py init <folder>` (a blank brief), or `--example path-planning` to study a finished
   one.
2. **Extract.** Read the request sentence by sentence and fill every field it answers (references/brief-schema.md).
   Typical phrasings and where they go:

   | The user says | Field |
   |---|---|
   | "a workshop on ROS 2 navigation" | `title` (working title), `topics` |
   | "Saturday Feb. 13, 10 to 2" | `when.date` 2027-02-13, `when.start` 10:00, `when.end` 14:00 |
   | "in MSB 228" | `where.building` Mathematical Sciences Building, `where.room` Room 228 |
   | "on Zoom" | `format` virtual, `where.online_url` (or "sent after registration") |
   | "for grad students who know Python" | `audience.who`, `audience.level`, `prerequisites.skills` |
   | "they need a laptop with Docker" | `prerequisites.hardware`, `prerequisites.software` |
   | "we have 6 TurtleBots" | `prerequisites.provided`, and probably `audience.capacity` (pairs or groups) |
   | "pizza at noon" | a `lunch` block, `audience.cost` "Free, lunch provided" |
   | "can you make it fun for high schoolers" | `audience.who`, `audience.level`, `requests` (tone) |
   | "use my repo github.com/..." | `materials.repo_url` |
   | "I'm presenting with Sam" | `presenters` (ask for Sam's full name and role) |
   | anything else | `requests`, verbatim |

3. **Check.** `workshop.py check -w <folder> --json`. Each issue has a `path`, a `severity` and a ready-made
   `question`.
4. **Ask** (§5), then write the answers into the brief (`workshop.py set <path> <value>` or edit the file).
5. **Record** `assumptions` (every default you chose) and `open_questions` (anything the presenter will settle
   later, such as the room).
6. `check` again. Exit 0 means the brief is complete; exit 2 means something required is still missing.

## 2. What must be settled

The presenter must be able to give, and you must not build without, these facts (the `required` group):

| Fact | Field | Why it matters |
|---|---|---|
| Title or main topic | `title`, `topics` | everything |
| Format | `format` | venue lines, links, schedule |
| Date, start, end, time zone | `when.*` | schedule, flyer, forms, calendar |
| Building and room (in person or hybrid) | `where.building`, `where.room` | flyer, forms, TV slide |
| Audience and level | `audience.who`, `audience.level` | depth, pace, promotion |
| Skills participants need | `prerequisites.skills` (`["none"]` is an answer) | flyer, registration grid, outline |
| Hardware participants need | `prerequisites.hardware` (`["none"]` is an answer) | flyer, setup guide, preflight |
| Presenter and contact email | `presenters[0]`, `contact.email` | title slide, flyer, forms |

Strongly recommended (ask unless the request answers them or a default fits):

| Fact | Field |
|---|---|
| Seats | `audience.capacity` |
| Software and accounts to install beforehand | `prerequisites.software`, `prerequisites.accounts` |
| Registration deadline | `registration.deadline` |
| Cost and food | `audience.cost`, a `lunch` block |
| Programming languages and tools for the hands-on parts | `materials.languages`, `materials.stack` |
| Learning objectives | `objectives` (draft them; confirm at the checkpoint) |
| Wi-Fi network | `where.wifi` |
| Online link for virtual or hybrid | `where.online_url` |
| Anything else to include or avoid | `requests` |

## 3. The question bank

Use these wordings, shortened to what is still missing. Group them by theme in one message.

**The basics**
- "What's the working title, and the two or three main topics you want to cover?"
- "When is it: date, start and end time? (I'll assume Eastern time.)"
- "Where: building and room? Or online, and should the link go out after registration?"

**The people**
- "Who is it for, and at what level: beginner, intermediate, advanced or mixed?"
- "Roughly how many seats?"
- "Who's presenting (full name and role, as it should appear on the slides), and which email should questions
  go to? A kent.edu address is best on public pieces."
- "Will helpers or TAs be in the room? (For hands-on work, one per eight to ten people works well.)"

**What participants need**
- "What should they already know before they come?"
- "What do they need to bring: a laptop (any OS?), boards, cables, a phone?"
- "What must be installed beforehand, and which accounts do they need?"
- "What will you provide on the day: robots, kits, cloud credits, food?"

**The shape of the day**
- "How hands-on should it be: mostly talks with demos, or mostly building?"
- "Any fixed points: a lunch time, a guest speaker, a hard stop?"
- "Do you have slides, code or a repository I should build on?"

**Registration and promotion**
- "Is there a registration deadline? Should the form close when seats run out?"
- "Anything extra the registration form must ask (student ID, T-shirt size, team name)?"
- "Flyer sizes: Letter for bulletin boards (default), Tabloid or 17 × 22 for posters?"
- "Should it run on the hallway TVs? Animated or still?"

**Always**
- "Anything else you want the workshop to include or avoid?"

## 4. Defaults you may assume

Assume these without asking, and list each one in `assumptions`:

| Item | Default |
|---|---|
| Time zone | America/New_York |
| Campus | Kent State University, Kent Campus |
| Format | in person when a room is given, virtual when a meeting link is given |
| Breaks | 10 minutes at least every 90 minutes; 30-45 minutes for a meal in events of four hours or more |
| Setup check | 10-15 minutes near the start of any hands-on workshop |
| Q&A | 10-15 minutes before the wrap-up |
| Feedback | 5 minutes at the end, with a QR slide |
| Forms | registration and feedback |
| Flyer | Letter only, plus the hallway TV slide |
| Motion and Teo | off unless asked for |
| Code license | MIT (confirm with the presenter before publishing a repository) |
| Wi-Fi | eduroam for Kent State people, KSU-Guest for visitors (confirm) |
| Learning objectives | three to five, drafted from the topics (confirmed at the checkpoint) |

Never default: dates, rooms, people, the registration link, cost or food, capacity, prerequisites.

## 5. Asking well

- **One round.** Put every required question and every recommended one you cannot default into a single
  message. A second round only when an answer opens a new question (a hybrid event needs a link plan).
- **Claude Code:** the AskUserQuestion tool takes up to four questions per call with two to four options each and
  a free-text "Other". Use it for choices (format, level, flyer sizes, forms, how hands-on); put your proposal
  first with "(Recommended)". Free-text facts (title, room, names) go in the same round as plain questions.
- **Codex and chat:** a numbered list, grouped by theme, with your proposed answer in parentheses where you have
  one: "3. Seats? (I'll plan for 24.)"
- **Show your reading.** Start with one line on what you understood ("A four-hour hands-on ROS 2 workshop for
  graduate students on Feb. 13 in MSB 228"), so the presenter can correct it.
- **Don't interrogate.** About ten questions in all is the ceiling. Anything that can wait for the checkpoint
  (objectives, module titles, flyer wording) waits.
- **Answers go straight into the brief**, then `check` again.

## 6. Worked examples

**A detailed request.** "I'm running a 3-hour intro to ROS 2 for undergrads in MSB 228 on March 6 from 1 to 4.
They should know Python. Bring laptops with Docker. 20 seats, pizza at the start."
Extracted: title, topics, date, times, building, room, audience, level (beginner, from "intro"), skills,
hardware, software, capacity, food. Ask only: presenter name, role and email; registration deadline; Wi-Fi;
"anything else?". Assume: Eastern time, a 15-minute pizza-and-setup block at 1 p.m., one 10-minute break, Q&A,
feedback, Letter flyer and TV slide.

**A thin request.** "Can you make me a workshop on reinforcement learning?"
Ask, in one round: date and time; place or online; audience and level; what they should know and bring; who
presents and the contact email; seats; how hands-on; "anything else?". Propose: "a three-hour hands-on session,
Python with Gymnasium, laptops required".

**A piece only.** "Make the slides for my sensor-fusion workshop next Friday."
It is still a workshop: build the brief (the slides need the schedule and the facts), ask for what is missing,
and offer the rest of the package in one line rather than building it unasked.

## 7. Conflicts, gaps and honesty

- When an answer contradicts the design skill's verified facts (a wrong building name, Room 236, `@atr_kent`,
  "College of Arts and Sciences"), explain the conflict and use the verified value (design skill §5).
- A fact the presenter has not settled stays a visible `[placeholder]` in the brief and in `open_questions`. The
  final build refuses placeholders on slides and flyers; a `--draft` build shows them.
- Never fill a gap with something plausible: a guessed room, a made-up helper, an invented sponsor or a sample
  registration link presented as real.
