# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.


### Sample Output
'''
================================================
       🐾  PawPal+ — Today's Schedule
================================================
  Owner : Jordan
  Pets  : Mochi, Luna
  Budget: 90 min available
------------------------------------------------
  1. [Mochi] Morning walk             30 min   priority 5/5
  2. [Mochi] Breakfast                10 min   priority 5/5
  3. [Mochi] Lunch                    10 min   priority 5/5
  4. [Luna] Wet food serving          5 min   priority 5/5
  5. [Mochi] Heartworm pill            5 min   priority 4/5
  6. [Mochi] Fetch in yard            20 min   priority 3/5
------------------------------------------------
  Total scheduled : 80 min
  Tasks skipped   : 3 (over budget or not due)
================================================

Scheduled 6 task(s) totalling 80 minute(s):

  1. [WALK] Morning walk — 30 min, priority 5/5
  2. [FEEDING] Breakfast — 10 min, priority 5/5
  3. [FEEDING] Lunch — 10 min, priority 5/5
  4. [FEEDING] Wet food serving — 5 min, priority 5/5
  5. [MEDICATION] Heartworm pill — 5 min, priority 4/5
  6. [ENRICHMENT] Fetch in yard — 20 min, priority 3/5

================================================
       ⚠️  Conflict Check
================================================
⚠️ Conflict at 08:00 (different pets): Heartworm pill, Morning walk, Wet food serving

================================================
       🔎  Filter + Sort Demo
================================================
All tasks (in insertion order):
  - [Mochi] Fetch in yard (20 min, incomplete, due_today=True, time=17:30)
  - [Mochi] Heartworm pill (5 min, incomplete, due_today=True, time=08:00)
  - [Mochi] Morning walk (30 min, incomplete, due_today=True, time=08:00)
  - [Mochi] Breakfast (10 min, incomplete, due_today=True, time=08:30)
  - [Mochi] Lunch (10 min, incomplete, due_today=True, time=12:00)
  - [Luna] Laser pointer (10 min, completed, due_today=True, time=18:00)
  - [Luna] Wet food serving (5 min, incomplete, due_today=True, time=08:00)
  - [Luna] Brush coat (15 min, incomplete, due_today=True, time=19:00)
  - [Luna] Vet follow-up (10 min, incomplete, due_today=False, time=08:00)

Filtered: Mochi + incomplete
  - Fetch in yard (20 min)
  - Heartworm pill (5 min)
  - Morning walk (30 min)
  - Breakfast (10 min)
  - Lunch (10 min)

Sorted (by duration asc): Mochi + incomplete
  - Heartworm pill (5 min)
  - Breakfast (10 min)
  - Lunch (10 min)
  - Fetch in yard (20 min)
  - Morning walk (30 min)

Filtered: due today only
  - Fetch in yard (priority 3)
  - Heartworm pill (priority 4)
  - Morning walk (priority 5)
  - Breakfast (priority 5)
  - Lunch (priority 5)
  - Laser pointer (priority 3)
  - Wet food serving (priority 5)
  - Brush coat (priority 2)

Sorted (by priority desc): due today only
  - Morning walk (priority 5)
  - Breakfast (priority 5)
  - Lunch (priority 5)
  - Wet food serving (priority 5)
  - Heartworm pill (priority 4)
  - Fetch in yard (priority 3)
  - Laser pointer (priority 3)
  - Brush coat (priority 2)
================================================
'''