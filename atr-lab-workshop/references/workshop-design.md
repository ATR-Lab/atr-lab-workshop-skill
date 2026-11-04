# Designing the workshop

**Read this when** you turn topics into objectives, modules and activities (phase 2), or a presenter asks how to
structure the day.

## 1. Start from the end (backward design)

1. **Objectives first.** Write three to five things participants will be able to *do* by the end. Each has a
   verb, a task and, when it helps, a condition: "Drive a simulated robot along a path and debug it".
2. **Evidence second.** For each objective, the activity checkpoint that shows it happened ("test_astar.py
   passes and the path is drawn").
3. **Content last.** Only the concepts the activities need. Everything else goes in the README's "going further".

Verbs that can be observed in a workshop, by level:

| Level | Verbs |
|---|---|
| Remember and understand | identify, describe, explain, compare |
| Apply | implement, run, configure, use, modify |
| Analyze | debug, measure, trace, diagnose |
| Evaluate and create | tune, choose, design, extend, build |

Avoid "understand", "learn about" and "be familiar with": nobody can check them.

## 2. Modules

A module is one objective (sometimes two) taught as a loop; the schedule repeats the loop:

| Step | Block kind | Typical share | What happens |
|---|---|---|---|
| Concept | `talk` | 10-20 min | the idea, one worked example, one question to the room |
| Show | `demo` | 5-10 min | the presenter runs it live, with a recorded fallback |
| Do | `hands-on` | 20-40 min | participants build it from `starter/`, helpers circulate |
| Check | end of the hands-on block | 3-5 min | the done-when result; two people share what they saw |

Three modules fill a half day; five a full day. The agenda slide shows at most five rows (setup and wrap-up count
when there is room).

Name modules by what participants build, not by the chapter of a textbook ("From path to motion", not
"Kinematics").

## 3. Activities

Every hands-on block needs, in the brief's `activity`:

- **Title**: what they do ("Write A* and compare heuristics").
- **Steps**: three to five, each one line, imperative. Five steps get a timeline slide; fewer get a numbered list.
- **Checkpoint**: what they see when it works. Make it observable: a passing test, a printed result, a robot
  that reaches the goal.
- **Stretch goal**: for fast finishers, so the room can wait together for the slowest pair without boredom.
- **Minutes**: the block length, with about 20% slack.

Pair programming by default for beginners: one laptop, two people, swap at each step. Mixed-level rooms: seat
experienced and new participants together and say so on the logistics slide.

## 4. Calibrating to the level

| Level | Talks | Starter code | Help |
|---|---|---|---|
| Beginner | short, one idea each, analogies | most of the program written; they fill one function | one helper per eight; the solution shown at the checkpoint |
| Intermediate | concepts and trade-offs | the skeleton and tests; they write the core | one per ten; hints in the README |
| Advanced | design choices, the literature | a problem statement and tests; they design | one per 12; discussion blocks |
| Mixed | as beginner, with stretch goals as the advanced track | as beginner, with an "extension" folder | pair across levels |

## 5. Inclusive and accessible teaching

- Say everything that is on the slide; describe figures and demos aloud.
- Captions on any video; a microphone in rooms over 30 people.
- Code at 16 pt or larger on slides (the code slide does this) and in the editor during demos (zoom in).
- No color-only meaning in slides or code output (design skill accessibility rules).
- The registration form asks about accommodations privately; follow up before the day.
- Breaks on time, every time; announce the return time.
- Offer a non-laptop path when the hardware ask is heavy: pairs, loaner laptops, or a browser environment.

## 6. Hardware workshops

When participants use robots, boards or sensors:

- Count the kits and set `audience.capacity` to kits × people per kit.
- Put the kits in `prerequisites.provided` and their setup (charging, flashing, network) in the outline's
  logistics section.
- Add a `setup` block long enough to hand out, connect and test the hardware (20-30 minutes), and a
  `buffer` before the last activity.
- Plan a simulation fallback for every hardware activity (a dead battery should not end someone's workshop).
- Safety: moving robots get a marked area and a stop procedure on a slide; K-12 events follow the design skill's
  supervision rules.

## 7. Virtual and hybrid

- Shorter blocks (talks of 15 minutes at most), a break every 60 minutes.
- Breakout rooms for hands-on work, one helper each; a shared document for questions.
- The setup check happens before the day: make the preflight part of registration ("run it and tell us the
  result").
- Hybrid: a room microphone for questions, a helper watching the chat, the online link in the confirmation email,
  not on the flyer.
