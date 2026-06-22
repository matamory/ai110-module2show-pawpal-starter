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

### Running the app

```bash
streamlit run app.py
```

The app runs in your browser. Add an owner, add pets, add tasks, then click **Generate Schedule** to build today's plan. Use the Filter & Sort section to explore tasks by pet, status, or priority.

### UML diagrams

| File | Description |
|---|---|
| `diagrams/uml_draft.mmd` | Initial design created before implementation |
| `diagrams/uml_final.mmd` | Updated diagram reflecting the final build — includes new attributes (`times_skipped`, `must_follow`, `time_budget`), all Scheduler methods, and private helpers |

Render either file with the [Mermaid Live Editor](https://mermaid.live) or any Mermaid-compatible Markdown viewer.

---

## 🖥️ Sample Output

```
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
  4. [Luna] Wet food serving           5 min   priority 5/5
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
⚠️ Conflict at 08:00 (different pets): Morning walk, Wet food serving
⚠️ Conflict at 08:00 (same pet): Morning walk, Heartworm pill
⚠️ Conflict at 08:00 (different pets): Wet food serving, Heartworm pill
```

---

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python3 -m pytest tests/tests_pawpal.py -v

# Note: the file is named tests_pawpal.py (with an 's'), which does not match
# pytest's default test_*.py discovery — point to the file directly.
```

**Confidence Level: ★★★★★ (5/5)**
All core scheduling, filtering, sorting, conflict detection, data model behaviors, and edge cases are covered by 62 passing tests.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.1.0, pluggy-1.6.0
collected 62 items

tests/tests_pawpal.py::test_mark_complete_changes_status PASSED          [  1%]
tests/tests_pawpal.py::test_mark_incomplete_resets_status PASSED         [  3%]
tests/tests_pawpal.py::test_add_task_increases_pet_task_count PASSED     [  4%]
tests/tests_pawpal.py::test_add_task_stamps_pet_id_on_task PASSED        [  6%]
tests/tests_pawpal.py::test_filter_tasks_by_pet_and_status PASSED        [  8%]
tests/tests_pawpal.py::test_filter_tasks_due_today_only PASSED           [  9%]
tests/tests_pawpal.py::test_sort_tasks_by_duration_ascending PASSED      [ 11%]
tests/tests_pawpal.py::test_sort_tasks_rejects_invalid_key PASSED        [ 12%]
tests/tests_pawpal.py::test_sort_tasks_chronological_order_by_scheduled_time PASSED [ 14%]
tests/tests_pawpal.py::test_sort_tasks_chronological_puts_unscheduled_last PASSED [ 16%]
tests/tests_pawpal.py::test_detect_time_conflicts_flags_duplicate_times PASSED [ 17%]
tests/tests_pawpal.py::test_detect_time_conflicts_ignores_completed_or_not_due_tasks PASSED [ 19%]
tests/tests_pawpal.py::test_generate_plan_returns_empty_when_no_tasks_exist PASSED [ 20%]
tests/tests_pawpal.py::test_generate_plan_returns_empty_when_all_tasks_filtered_out PASSED [ 22%]
tests/tests_pawpal.py::test_fit_to_time_budget_exact_fit_and_just_over PASSED [ 24%]
tests/tests_pawpal.py::test_sort_tasks_same_priority_keeps_input_order PASSED [ 25%]
tests/tests_pawpal.py::test_owner_add_task_raises_for_unknown_pet_id PASSED [ 27%]
tests/tests_pawpal.py::test_detect_time_conflicts_reports_same_vs_different_pet_scope PASSED [ 29%]
tests/tests_pawpal.py::test_detect_time_conflicts_ignores_tasks_without_scheduled_time PASSED [ 30%]
tests/tests_pawpal.py::test_detect_time_conflicts_catches_true_window_overlap PASSED [ 32%]
tests/tests_pawpal.py::test_detect_time_conflicts_no_false_positive_for_adjacent_tasks PASSED [ 33%]
tests/tests_pawpal.py::test_resolve_conflicts_bumps_overlapping_task_forward PASSED [ 35%]
tests/tests_pawpal.py::test_resolve_conflicts_leaves_non_overlapping_tasks_unchanged PASSED [ 37%]
tests/tests_pawpal.py::test_resolve_conflicts_places_unscheduled_tasks_last PASSED [ 38%]
tests/tests_pawpal.py::test_record_skipped_increments_tasks_not_in_plan PASSED [ 40%]
tests/tests_pawpal.py::test_record_skipped_does_not_increment_completed_tasks PASSED [ 41%]
tests/tests_pawpal.py::test_record_skipped_does_not_increment_not_due_tasks PASSED [ 43%]
tests/tests_pawpal.py::test_record_skipped_accumulates_across_multiple_calls PASSED [ 45%]
tests/tests_pawpal.py::test_must_follow_enforces_dependency_order_in_plan PASSED [ 46%]
tests/tests_pawpal.py::test_must_follow_pointing_outside_plan_is_silently_ignored PASSED [ 48%]
tests/tests_pawpal.py::test_times_skipped_raises_effective_priority_above_higher_base PASSED [ 50%]
tests/tests_pawpal.py::test_prefer_time_morning_boosts_morning_task_over_same_priority_afternoon PASSED [ 51%]
tests/tests_pawpal.py::test_avoid_category_lowers_task_score_below_same_priority_task PASSED [ 53%]
tests/tests_pawpal.py::test_fairness_mode_includes_task_from_each_pet PASSED [ 54%]
tests/tests_pawpal.py::test_pet_time_budget_caps_tasks_for_that_pet PASSED [ 56%]
tests/tests_pawpal.py::test_pet_remove_task_by_id PASSED                 [ 58%]
tests/tests_pawpal.py::test_pet_remove_task_unknown_id_does_nothing PASSED [ 59%]
tests/tests_pawpal.py::test_pet_edit_task_updates_fields PASSED          [ 61%]
tests/tests_pawpal.py::test_pet_edit_task_unknown_id_does_nothing PASSED [ 62%]
tests/tests_pawpal.py::test_filter_tasks_raises_for_invalid_status PASSED [ 64%]
tests/tests_pawpal.py::test_format_conflict_warnings_returns_clean_message_when_no_conflicts PASSED [ 66%]
tests/tests_pawpal.py::test_sort_tasks_by_title_alphabetical PASSED      [ 67%]
tests/tests_pawpal.py::test_fit_to_time_budget_returns_empty_for_zero_budget PASSED [ 69%]
tests/tests_pawpal.py::test_fit_to_time_budget_returns_empty_when_all_tasks_exceed_budget PASSED [ 70%]
tests/tests_pawpal.py::test_owner_add_task_raises_when_no_pet_id_on_task_or_argument PASSED [ 72%]
tests/tests_pawpal.py::test_owner_remove_task_unknown_id_does_nothing PASSED [ 74%]
tests/tests_pawpal.py::test_owner_edit_task_unknown_id_does_nothing PASSED [ 75%]
tests/tests_pawpal.py::test_owner_remove_pet_reduces_pet_count PASSED    [ 77%]
tests/tests_pawpal.py::test_owner_remove_pet_unknown_id_does_nothing PASSED [ 79%]
tests/tests_pawpal.py::test_owner_get_pet_returns_correct_pet PASSED     [ 80%]
tests/tests_pawpal.py::test_owner_get_pet_returns_none_for_unknown_id PASSED [ 82%]
tests/tests_pawpal.py::test_owner_add_task_with_explicit_pet_id PASSED   [ 83%]
tests/tests_pawpal.py::test_owner_remove_task_removes_from_correct_pet PASSED [ 85%]
tests/tests_pawpal.py::test_owner_edit_task_updates_across_pets PASSED   [ 87%]
tests/tests_pawpal.py::test_task_update_details_changes_all_fields PASSED [ 88%]
tests/tests_pawpal.py::test_task_update_details_partial_update_leaves_others_unchanged PASSED [ 90%]
tests/tests_pawpal.py::test_add_medical_condition_appends_to_list PASSED [ 91%]
tests/tests_pawpal.py::test_add_allergy_appends_to_list PASSED           [ 93%]
tests/tests_pawpal.py::test_generate_plan_duration_strategy_picks_shortest_first PASSED [ 95%]
tests/tests_pawpal.py::test_generate_plan_priority_strategy_picks_highest_priority_first PASSED [ 96%]
tests/tests_pawpal.py::test_generate_plan_activity_boost_promotes_walk_for_high_activity_pet PASSED [ 98%]
tests/tests_pawpal.py::test_filter_by_health_returns_tasks_unchanged PASSED [100%]

============================== 62 passed in 0.18s ==============================
```

---

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---|---|---|
| Task sorting | `Scheduler.sort_tasks()` | Sorts by `"priority"`, `"duration"`, or `"title"`; accepts a `key_func` for custom ordering (e.g., chronological by `scheduled_time`) |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.filter_due_tasks()` | Filter by `pet_id`, completion status (`"completed"` / `"incomplete"`), or `due_today_only`; combinable in one call |
| Conflict handling | `Scheduler.detect_time_conflicts()`, `Scheduler.resolve_conflicts()` | Overlap-aware pairwise scan catches windows that overlap, not just exact same-start-time; `resolve_conflicts()` auto-bumps lower-priority tasks forward |
| Recurring tasks | `Task.times_skipped`, `Scheduler.record_skipped()` | No calendar recurrence; each day a task is skipped its `times_skipped` counter increments, raising its effective priority until it gets scheduled |
| Budget optimization | `Scheduler.fit_to_time_budget()` | 0/1 knapsack — finds the combination of tasks that maximises total effective priority within the time budget, unlike a greedy approach |
| Activity boost | `Scheduler.generate_plan()` (`ACTIVITY_BOOST`) | Walk tasks for high-activity pets receive a +2 score bonus, ensuring energetic dogs get exercise even when competing with other high-priority tasks |
| Owner preferences | `Scheduler._preference_bonus()` | `prefer_time` (`"morning"` / `"afternoon"` / `"evening"`) adds +1 to tasks in that window; `avoid_category` subtracts 1 from unwanted task categories |
| Fairness across pets | `Scheduler._fair_select()` (`fairness=True`) | Round-robin guarantees each pet gets its top task before filling the remaining budget with the best leftover tasks |
| Per-pet time budget | `Pet.time_budget`, `Scheduler._apply_pet_budgets()` | Each pet can cap its own daily time; prevents one pet from consuming the full owner budget before others are considered |
| Task ordering constraints | `Task.must_follow`, `Scheduler._enforce_ordering()` | Topological sort ensures a task always appears after its dependency in the output plan (e.g., walk before breakfast) |

---

## 📸 Demo Walkthrough

1. **Owner Setup** — Enter the owner name and daily time budget (minutes). Optionally set a preferred time of day (`morning` / `afternoon` / `evening`) or a category to avoid; these shift task scores during planning.
2. **Add pets** — Fill in the pet form (name, species, age, activity level) and click **Add pet**. The pet table updates immediately. Repeat for each pet.
3. **Add tasks** — Select a pet from the dropdown, fill in title, category, duration (minutes), and priority (1–5 slider). Optionally add a scheduled time (`HH:MM`) to enable conflict detection. Check **Due today** to include the task in today's plan.
4. **Generate schedule** — Choose a strategy (`priority`, `duration`, or `balanced`) and optionally enable **Fairness mode** to guarantee each pet at least one task. Click **Generate Schedule**. Three metrics appear at the top: tasks scheduled, total time used, and tasks skipped.
5. **Review the plan** — The schedule table shows each task in score order with pet name, category, duration, and priority. Below it, the conflict checker runs automatically — each overlap appears as a `st.warning`, or a `st.success` if the schedule is clean.
6. **Filter & Sort** — Use the dropdowns to filter by pet, completion status (`completed` / `incomplete`), or due-today flag, then pick a sort key (`priority`, `duration`, `title`) and direction. Results render with status-aware callouts: green for completed tasks, yellow for tasks that have been skipped at least once, blue for not-due tasks.
