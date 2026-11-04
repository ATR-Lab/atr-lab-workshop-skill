# Workshop outline: Robot path planning in Python

> Example outline for the atr-lab-workshop skill. The date and room are sample values.

## 1. At a glance

| | |
|---|---|
| When | Saturday, Feb. 13, 2027, 10 a.m.-2 p.m. EST |
| Where | Mathematical Sciences Building, Room 228, Kent State University |
| Format | in-person |
| Audience | Undergraduate and graduate students (beginner) |
| Seats | 24 |
| Cost | Free, lunch provided |
| Presenters | ATR Lab workshop team |
| Contact | atrlab.kent@gmail.com |

## 2. Description

Turn a map into a graph, find a path with A* and drive a simulated robot along it, all in plain Python.

**Listing abstract (about 100 words, for the department calendar and the registration form):**

How does a robot get from here to there without hitting anything? In this four-hour hands-on workshop, undergraduate and graduate students build the answer in plain Python: turn a floor plan into an occupancy grid, find the shortest route with the A* search algorithm and drive a simulated robot along it with a pure-pursuit controller. Each part ends with code you run and test yourself. You need basic Python (functions, lists and loops) and a laptop with Python 3.10 or newer; no robotics background is expected. Lunch is provided. Hosted by the Advanced Telerobotics Research Lab, Department of Computer Science, Kent State University.

## 3. Learning objectives

By the end of the workshop, participants can:

- Represent a map as an occupancy grid and a graph
- Implement A* and explain how its heuristic works
- Smooth a path into waypoints a robot can follow
- Drive a simulated robot along a path and debug it

## 4. Prerequisites

**Skills**

- Python basics: functions, lists and loops
- Running a script from a terminal

**Hardware**

- Laptop with macOS, Windows or Linux and its charger

**Software (installed before arrival)**

- Python 3.10 or newer
- Git
- VS Code or another editor

**Accounts**

- None

**Provided on the day**

- Printed map sheets
- Lunch

**Pre-work**

- Clone the workshop repository and run python3 preflight.py

## 5. Modules

### 5.1 Maps as graphs (10:25-11:20 a.m., 55 min)

**Purpose.** An occupancy grid turns a floor plan into cells a planner can search.

**Objectives.**

- Represent a map as an occupancy grid and a graph

**Content.**

- Maps are grids of free and wall cells
- Neighbors make the grid a graph

**Demo.** Run `grid.py` on the warehouse map; show that row 0 is the top line and that the start has two free neighbors. Fallback: the printed output in the module README.

**Hands-on activity: Load a map and find neighbors** (25 min)

1. Load the map file
2. Mark start and goal
3. Write neighbors()
4. Run the tests

- Done when: test_grid.py passes and the map prints
- Stretch goal: Allow diagonal moves with the right cost
- Code: `code/01-maps-as-graphs`
- Common problems and fixes: (row, col) swapped for (x, y); forgetting the bounds check; diagonal steps through wall corners.
- Check for understanding: Ask: how many neighbors does a corridor cell have, and a dead end?

### 5.2 A* search (11:30 a.m.-12:20 p.m., 50 min)

**Purpose.** A* finds the shortest path by expanding the most promising cell first.

**Objectives.**

- Implement A* and explain how its heuristic works

**Content.**

- Blind search explores everything
- Heuristics aim the search at the goal
- Admissible heuristics keep A* optimal

**Demo.** Run `astar.py` with the three heuristics side by side: same 32-step path, 100, 60 and 64 cells expanded. Fallback: the numbers on the slide.

**Hands-on activity: Write A* and compare heuristics** (35 min)

1. Fill in the open set
2. Pop the lowest f-score
3. Reconstruct the path
4. Try two heuristics

- Done when: test_astar.py passes and the path is drawn
- Stretch goal: Count expanded cells for each heuristic
- Code: `code/02-a-star-search`
- Common problems and fixes: Pushing a cell twice without the closed set (still correct, just slower); comparing tuples with None; reconstructing the path backwards.
- Check for understanding: Ask: why does the zero heuristic still find the shortest path, and what does it cost?

### 5.3 From path to motion (12:55-1:35 p.m., 40 min)

**Purpose.** A robot follows waypoints: simplify the path, then steer toward a point ahead.

**Objectives.**

- Smooth a path into waypoints a robot can follow
- Drive a simulated robot along a path and debug it

**Content.**

- Grid paths zigzag: keep the corners
- Pure pursuit aims at a point ahead

**Demo.** Run `follow.py` and show the trajectory; then halve the look-ahead and show the wobble. Fallback: a screen recording.

**Hands-on activity: Drive the robot to the goal** (30 min)

1. Simplify the path
2. Pick a look-ahead point
3. Compute the steering
4. Run the simulation

- Done when: The robot reaches the goal without hitting a wall
- Stretch goal: Tune the look-ahead distance and compare
- Code: `code/03-from-path-to-motion`
- Common problems and fixes: Mixing (row, col) cells with (x, y) points; angle errors not wrapped into [-pi, pi), so the robot spins; a look-ahead too large cuts corners into walls.
- Check for understanding: Ask: what happens to the trajectory when the turn limit is halved?

## 6. Schedule

The run-of-show with clock times is in [schedule.md](schedule.md).

| Time | Block | Kind |
|---|---|---|
| 10 a.m. | Welcome and goals | Welcome |
| 10:10 a.m. | Setup check | Setup |
| 10:25 a.m. | Maps as graphs | Talk |
| 10:45 a.m. | A grid in code | Demo |
| 10:55 a.m. | Load a map and find neighbors | Hands-on |
| 11:20 a.m. | Break | Break |
| 11:30 a.m. | A* search | Talk |
| 11:45 a.m. | Write A* | Hands-on |
| 12:20 p.m. | Lunch | Lunch |
| 12:55 p.m. | From path to motion | Talk |
| 1:05 p.m. | Drive the robot | Hands-on |
| 1:35 p.m. | Questions | Q&A |
| 1:45 p.m. | Wrap-up and next steps | Wrap-up |
| 1:55 p.m. | Feedback form | Feedback |

## 7. Materials

- Slides: `deliverables/` (.pptx and .pdf) with speaker notes in `slides/speaker-notes.md`
- Code: `code/` (participant README, preflight check, starter and solution per activity)
- Forms: `forms/` (registration and feedback, created with `create-forms.gs`)
- Promotion: flyers and the hallway TV slide in `deliverables/`
- Printed handouts: one warehouse map per pair, for sketching paths by hand

## 8. Roles, room and logistics

- Helpers: three, one per eight participants, who have run every solution beforehand
- Room setup: tables in pairs, a power strip per table, projector with HDMI and USB-C adapters, a microphone
- Wi-Fi: eduroam or KSU-Guest
- Parking: confirm Saturday parking with the department before the flyer goes out
- Accessibility: step-free entrance and elevator; large-print map sheets on request; requests through the registration form
- Food: lunch at 12:20 p.m.; dietary needs come from the registration form

## 9. Risks and fallbacks

| Risk | Fallback |
|---|---|
| Installs fail on some laptops | Preflight a week ahead; pair people; a browser-based Python (for example a Codespace) as a last resort |
| Wi-Fi is slow | Packages on a USB stick or local mirror; repository cloned in advance |
| Live demo fails | Recorded demo video in the deck |
| Running late | Cut the stretch goals, never the breaks |

## 10. Assessment and feedback

- During: checkpoints at the end of each activity
- After: the feedback form (QR code on the last slide), results reviewed within a week

## 11. Promotion and communication timeline

| Date | When | What |
|---|---|---|
| Jan. 16, 2027 | 28 days before | Flyers printed and posted; TV slide submitted to the building's slideshow; registration open |
| Jan. 23, 2027 | 21 days before | Social post and department newsletter item (atr-lab-design skill: social card and copy) |
| Feb. 6, 2027 | 7 days before | Reminder to registrants with the setup guide and the preflight check |
| Feb. 10, 2027 | 3 days before | Registration closes or the form closes at capacity; confirm room, AV and catering |
| Feb. 11, 2027 | 2 days before | Last reminder: time, room, what to bring; helpers run the preflight on a spare laptop |
| Feb. 13, 2027 | Day of | Workshop; feedback form on the last slide |
| Feb. 15, 2027 | 2 days after | Thank-you email with the slides, the code repository and the feedback link |

## 12. Still to confirm

- Assumption: Lunch is provided (from the presenter's note: free, lunch provided)
