import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Test 1: Task Completion ───────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task("Morning walk", category="walk", duration=30, priority=4)
    assert task.completed is False       # starts incomplete

    task.mark_complete()
    assert task.completed is True        # now completed

def test_mark_incomplete_resets_status():
    task = Task("Breakfast", category="feeding", duration=10, priority=5)
    task.mark_complete()
    assert task.completed is True

    task.mark_incomplete()
    assert task.completed is False       # back to incomplete


# ── Test 2: Task Addition ─────────────────────────────────────────────────────

def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0           # starts with no tasks

    pet.add_task(Task("Walk", category="walk", duration=20, priority=3))
    assert len(pet.tasks) == 1

    pet.add_task(Task("Feeding", category="feeding", duration=10, priority=5))
    assert len(pet.tasks) == 2

def test_add_task_stamps_pet_id_on_task():
    pet = Pet("Luna", species="cat", age=5)
    task = Task("Brush coat", category="grooming", duration=15, priority=2)
    assert task.pet_id is None           # no pet linked yet

    pet.add_task(task)
    assert task.pet_id == pet.pet_id     # stamped with pet's ID after addition


# ── Test 3: Filtering + Sorting Helpers ──────────────────────────────────────

def test_filter_tasks_by_pet_and_status():
    scheduler = Scheduler()

    pet_a = Pet("Mochi", species="dog", age=3)
    pet_b = Pet("Luna", species="cat", age=5)

    task_a1 = Task("Morning walk", category="walk", duration=30, priority=5)
    task_a2 = Task("Breakfast", category="feeding", duration=10, priority=4)
    task_b1 = Task("Brush coat", category="grooming", duration=15, priority=2)

    pet_a.add_task(task_a1)
    pet_a.add_task(task_a2)
    pet_b.add_task(task_b1)

    task_a1.mark_complete()

    tasks = [task_a1, task_a2, task_b1]
    filtered = scheduler.filter_tasks(tasks, pet_id=pet_a.pet_id, status="incomplete")

    assert len(filtered) == 1
    assert filtered[0].title == "Breakfast"


def test_filter_tasks_due_today_only():
    scheduler = Scheduler()

    due_task = Task("Lunch", category="feeding", duration=10, priority=4, due_today=True)
    not_due_task = Task("Nail trim", category="grooming", duration=20, priority=2, due_today=False)

    filtered = scheduler.filter_tasks([due_task, not_due_task], due_today_only=True)

    assert filtered == [due_task]


def test_sort_tasks_by_duration_ascending():
    scheduler = Scheduler()

    t1 = Task("Long walk", category="walk", duration=30, priority=3)
    t2 = Task("Quick feed", category="feeding", duration=5, priority=5)
    t3 = Task("Play", category="enrichment", duration=15, priority=4)

    ordered = scheduler.sort_tasks([t1, t2, t3], key="duration", reverse=False)

    assert [t.title for t in ordered] == ["Quick feed", "Play", "Long walk"]


def test_sort_tasks_rejects_invalid_key():
    scheduler = Scheduler()
    task = Task("Walk", category="walk", duration=20, priority=3)

    with pytest.raises(ValueError):
        scheduler.sort_tasks([task], key="time")


# ── Test 4: Time Ordering + Conflict Detection ──────────────────────────────

def test_sort_tasks_chronological_order_by_scheduled_time():
    scheduler = Scheduler()

    t1 = Task("Dinner", category="feeding", duration=10, priority=3, scheduled_time="18:00")
    t2 = Task("Morning walk", category="walk", duration=30, priority=4, scheduled_time="07:30")
    t3 = Task("Lunch", category="feeding", duration=10, priority=3, scheduled_time="12:00")

    ordered = scheduler.sort_tasks(
        [t1, t2, t3],
        key_func=lambda t: t.scheduled_time or "99:99",
        reverse=False,
    )

    assert [t.title for t in ordered] == ["Morning walk", "Lunch", "Dinner"]


def test_sort_tasks_chronological_puts_unscheduled_last():
    scheduler = Scheduler()

    scheduled = Task("Breakfast", category="feeding", duration=10, priority=4, scheduled_time="08:00")
    unscheduled = Task("Brush", category="grooming", duration=15, priority=2, scheduled_time=None)

    ordered = scheduler.sort_tasks(
        [unscheduled, scheduled],
        key_func=lambda t: t.scheduled_time or "99:99",
        reverse=False,
    )

    assert [t.title for t in ordered] == ["Breakfast", "Brush"]


def test_detect_time_conflicts_flags_duplicate_times():
    scheduler = Scheduler()

    t1 = Task("Morning walk", category="walk", duration=30, priority=5, scheduled_time="08:00")
    t2 = Task("Medication", category="medication", duration=5, priority=5, scheduled_time="08:00")
    t3 = Task("Lunch", category="feeding", duration=10, priority=3, scheduled_time="12:00")

    warnings = scheduler.detect_time_conflicts([t1, t2, t3])

    assert len(warnings) == 1
    assert "Conflict at 08:00" in warnings[0]
    assert "Morning walk" in warnings[0]
    assert "Medication" in warnings[0]


def test_detect_time_conflicts_ignores_completed_or_not_due_tasks():
    scheduler = Scheduler()

    completed_task = Task(
        "Done walk",
        category="walk",
        duration=20,
        priority=4,
        scheduled_time="09:00",
        completed=True,
    )
    not_due_task = Task(
        "Tomorrow grooming",
        category="grooming",
        duration=15,
        priority=2,
        scheduled_time="09:00",
        due_today=False,
    )

    warnings = scheduler.detect_time_conflicts([completed_task, not_due_task])

    assert warnings == []


# ── Test 5: Additional MVP Edge Cases ───────────────────────────────────────

def test_generate_plan_returns_empty_when_no_tasks_exist():
    scheduler = Scheduler()
    owner = Owner("Yesenia", daily_time_budget=60)
    owner.add_pet(Pet("Mochi", species="dog", age=3))

    plan = scheduler.generate_plan(owner)

    assert plan == []
    assert "No tasks were scheduled" in scheduler.explain_plan(plan)


def test_generate_plan_returns_empty_when_all_tasks_filtered_out():
    scheduler = Scheduler()
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Luna", species="cat", age=5)
    owner.add_pet(pet)

    completed_task = Task("Done feed", category="feeding", duration=10, priority=5, completed=True)
    not_due_task = Task("Tomorrow walk", category="walk", duration=20, priority=4, due_today=False)
    pet.add_task(completed_task)
    pet.add_task(not_due_task)

    plan = scheduler.generate_plan(owner)

    assert plan == []


def test_fit_to_time_budget_exact_fit_and_just_over():
    scheduler = Scheduler()

    t1 = Task("Task A", category="walk", duration=30, priority=5)
    t2 = Task("Task B", category="feeding", duration=30, priority=4)
    ordered = [t1, t2]

    exact_fit_plan = scheduler.fit_to_time_budget(ordered, minutes=60)
    just_over_plan = scheduler.fit_to_time_budget(ordered, minutes=59)

    assert [t.title for t in exact_fit_plan] == ["Task A", "Task B"]
    assert [t.title for t in just_over_plan] == ["Task A"]


def test_sort_tasks_same_priority_keeps_input_order():
    scheduler = Scheduler()

    t1 = Task("First", category="walk", duration=20, priority=3)
    t2 = Task("Second", category="feeding", duration=10, priority=3)
    t3 = Task("Third", category="grooming", duration=15, priority=3)

    ordered = scheduler.sort_tasks([t1, t2, t3], key="priority", reverse=True)

    assert [t.title for t in ordered] == ["First", "Second", "Third"]


def test_owner_add_task_raises_for_unknown_pet_id():
    owner = Owner("Yesenia", daily_time_budget=45)
    owner.add_pet(Pet("Mochi", species="dog", age=3))

    orphan_task = Task(
        "Orphan task",
        category="feeding",
        duration=10,
        priority=3,
        pet_id="missing-pet-id",
    )

    with pytest.raises(ValueError):
        owner.add_task(orphan_task)


def test_detect_time_conflicts_reports_same_vs_different_pet_scope():
    scheduler = Scheduler()

    same_pet_1 = Task("Walk", category="walk", duration=20, priority=4, scheduled_time="08:00", pet_id="pet-a")
    same_pet_2 = Task("Feed", category="feeding", duration=10, priority=5, scheduled_time="08:00", pet_id="pet-a")
    diff_pet_1 = Task("Meds", category="medication", duration=5, priority=5, scheduled_time="09:00", pet_id="pet-a")
    diff_pet_2 = Task("Groom", category="grooming", duration=15, priority=2, scheduled_time="09:00", pet_id="pet-b")

    warnings = scheduler.detect_time_conflicts([same_pet_1, same_pet_2, diff_pet_1, diff_pet_2])

    assert any("08:00" in warning and "same pet" in warning for warning in warnings)
    assert any("09:00" in warning and "different pets" in warning for warning in warnings)


def test_detect_time_conflicts_ignores_tasks_without_scheduled_time():
    scheduler = Scheduler()

    no_time_1 = Task("Anytime play", category="enrichment", duration=20, priority=3, scheduled_time=None)
    no_time_2 = Task("Anytime brush", category="grooming", duration=10, priority=2, scheduled_time=None)

    warnings = scheduler.detect_time_conflicts([no_time_1, no_time_2])

    assert warnings == []


# ── Test 11: True Overlap Detection ──────────────────────────────────────────

def test_detect_time_conflicts_catches_true_window_overlap():
    scheduler = Scheduler()
    # t1 runs 08:00–08:30; t2 starts at 08:15 — overlaps before t1 finishes
    t1 = Task("Walk", category="walk", duration=30, priority=5, scheduled_time="08:00")
    t2 = Task("Brush", category="grooming", duration=10, priority=3, scheduled_time="08:15")

    warnings = scheduler.detect_time_conflicts([t1, t2])

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Brush" in warnings[0]


def test_detect_time_conflicts_no_false_positive_for_adjacent_tasks():
    scheduler = Scheduler()
    # t1 ends exactly at 08:30; t2 starts at 08:30 — no overlap
    t1 = Task("Walk", category="walk", duration=30, priority=5, scheduled_time="08:00")
    t2 = Task("Breakfast", category="feeding", duration=10, priority=4, scheduled_time="08:30")

    warnings = scheduler.detect_time_conflicts([t1, t2])

    assert warnings == []


# ── Test 12: resolve_conflicts ────────────────────────────────────────────────

def test_resolve_conflicts_bumps_overlapping_task_forward():
    scheduler = Scheduler()
    # t1 higher priority stays at 08:00 (30 min); t2 should move to 08:30
    t1 = Task("Walk", category="walk", duration=30, priority=5, scheduled_time="08:00")
    t2 = Task("Medication", category="medication", duration=10, priority=4, scheduled_time="08:00")

    scheduler.resolve_conflicts([t1, t2])

    assert t1.scheduled_time == "08:00"
    assert t2.scheduled_time == "08:30"


def test_resolve_conflicts_leaves_non_overlapping_tasks_unchanged():
    scheduler = Scheduler()
    t1 = Task("Walk", category="walk", duration=20, priority=5, scheduled_time="08:00")
    t2 = Task("Lunch", category="feeding", duration=10, priority=4, scheduled_time="12:00")

    scheduler.resolve_conflicts([t1, t2])

    assert t1.scheduled_time == "08:00"
    assert t2.scheduled_time == "12:00"


def test_resolve_conflicts_places_unscheduled_tasks_last():
    scheduler = Scheduler()
    t1 = Task("Walk", category="walk", duration=20, priority=5, scheduled_time="08:00")
    t2 = Task("Anytime play", category="enrichment", duration=15, priority=3, scheduled_time=None)

    result = scheduler.resolve_conflicts([t1, t2])

    assert result[0].title == "Walk"
    assert result[-1].title == "Anytime play"


# ── Test 13: record_skipped ───────────────────────────────────────────────────

def test_record_skipped_increments_tasks_not_in_plan():
    scheduler = Scheduler()
    planned = Task("Walk", category="walk", duration=20, priority=5)
    missed = Task("Medication", category="medication", duration=5, priority=4)

    scheduler.record_skipped([planned], [planned, missed])

    assert planned.times_skipped == 0   # was in plan
    assert missed.times_skipped == 1    # was not in plan


def test_record_skipped_does_not_increment_completed_tasks():
    scheduler = Scheduler()
    done = Task("Done walk", category="walk", duration=20, priority=5, completed=True)

    scheduler.record_skipped([], [done])

    assert done.times_skipped == 0


def test_record_skipped_does_not_increment_not_due_tasks():
    scheduler = Scheduler()
    future = Task("Tomorrow walk", category="walk", duration=20, priority=3, due_today=False)

    scheduler.record_skipped([], [future])

    assert future.times_skipped == 0


def test_record_skipped_accumulates_across_multiple_calls():
    scheduler = Scheduler()
    task = Task("Medication", category="medication", duration=5, priority=4)

    scheduler.record_skipped([], [task])
    scheduler.record_skipped([], [task])

    assert task.times_skipped == 2


# ── Test 14: must_follow / ordering constraints ───────────────────────────────

def test_must_follow_enforces_dependency_order_in_plan():
    scheduler = Scheduler()
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    walk = Task("Walk", category="walk", duration=20, priority=5)
    breakfast = Task("Breakfast", category="feeding", duration=10, priority=4)
    pet.add_task(walk)
    pet.add_task(breakfast)
    breakfast.must_follow = walk.task_id  # breakfast must come after walk

    plan = scheduler.generate_plan(owner)
    titles = [t.title for t in plan]

    assert titles.index("Walk") < titles.index("Breakfast")


def test_must_follow_pointing_outside_plan_is_silently_ignored():
    scheduler = Scheduler()
    owner = Owner("Yesenia", daily_time_budget=30)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    walk = Task("Walk", category="walk", duration=30, priority=5)
    pet.add_task(walk)
    walk.must_follow = "nonexistent-task-id"

    plan = scheduler.generate_plan(owner)

    assert len(plan) == 1
    assert plan[0].title == "Walk"


# ── Test 15: times_skipped escalation ────────────────────────────────────────

def test_times_skipped_raises_effective_priority_above_higher_base():
    scheduler = Scheduler(strategy="priority")
    owner = Owner("Yesenia", daily_time_budget=20)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    # base priority 1 but skipped 5 times → effective score 6
    urgent = Task("Medication", category="medication", duration=20, priority=1, times_skipped=5)
    # base priority 5, never skipped → effective score 5
    normal = Task("Walk", category="walk", duration=20, priority=5)
    pet.add_task(urgent)
    pet.add_task(normal)

    plan = scheduler.generate_plan(owner, pet=pet)

    assert len(plan) == 1
    assert plan[0].title == "Medication"


# ── Test 16: Owner preferences ────────────────────────────────────────────────

def test_prefer_time_morning_boosts_morning_task_over_same_priority_afternoon():
    scheduler = Scheduler(strategy="priority")
    owner = Owner("Yesenia", daily_time_budget=20)
    owner.preferences = {"prefer_time": "morning"}
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    # Both priority 4; morning gets +1 → effective 5 vs 4 → morning wins
    morning = Task("AM walk", category="walk", duration=20, priority=4, scheduled_time="08:00")
    afternoon = Task("PM walk", category="walk", duration=20, priority=4, scheduled_time="14:00")
    pet.add_task(morning)
    pet.add_task(afternoon)

    plan = scheduler.generate_plan(owner)

    assert len(plan) == 1
    assert plan[0].title == "AM walk"


def test_avoid_category_lowers_task_score_below_same_priority_task():
    scheduler = Scheduler(strategy="priority")
    owner = Owner("Yesenia", daily_time_budget=20)
    owner.preferences = {"avoid_category": "grooming"}
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    # Both priority 5; grooming gets -1 → effective 4 vs 5 → medication wins
    grooming = Task("Brush coat", category="grooming", duration=20, priority=5)
    medication = Task("Meds", category="medication", duration=20, priority=5)
    pet.add_task(grooming)
    pet.add_task(medication)

    plan = scheduler.generate_plan(owner)

    assert len(plan) == 1
    assert plan[0].title == "Meds"


# ── Test 17: fairness mode ────────────────────────────────────────────────────

def test_fairness_mode_includes_task_from_each_pet():
    scheduler = Scheduler(fairness=True)
    owner = Owner("Yesenia", daily_time_budget=60)

    pet_a = Pet("Mochi", species="dog", age=3)
    pet_b = Pet("Luna", species="cat", age=5)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    # pet_a has two high-priority tasks; without fairness both slots go to pet_a
    pet_a.add_task(Task("Walk", category="walk", duration=20, priority=5))
    pet_a.add_task(Task("Feed A", category="feeding", duration=20, priority=4))
    pet_b.add_task(Task("Feed B", category="feeding", duration=20, priority=3))

    plan = scheduler.generate_plan(owner)

    pet_ids_in_plan = {t.pet_id for t in plan}
    assert pet_a.pet_id in pet_ids_in_plan
    assert pet_b.pet_id in pet_ids_in_plan


# ── Test 18: per-pet time budget ──────────────────────────────────────────────

def test_pet_time_budget_caps_tasks_for_that_pet():
    scheduler = Scheduler()
    owner = Owner("Yesenia", daily_time_budget=120)

    pet = Pet("Mochi", species="dog", age=3, time_budget=20)
    owner.add_pet(pet)

    pet.add_task(Task("Walk", category="walk", duration=20, priority=5))
    pet.add_task(Task("Feed", category="feeding", duration=20, priority=4))
    pet.add_task(Task("Play", category="enrichment", duration=20, priority=3))

    plan = scheduler.generate_plan(owner)

    pet_total = sum(t.duration for t in plan if t.pet_id == pet.pet_id)
    assert pet_total <= pet.time_budget


# ── Test 19: Pet direct methods ───────────────────────────────────────────────

def test_pet_remove_task_by_id():
    pet = Pet("Mochi", species="dog", age=3)
    task = Task("Walk", category="walk", duration=20, priority=3)
    pet.add_task(task)

    pet.remove_task(task.task_id)

    assert len(pet.tasks) == 0


def test_pet_remove_task_unknown_id_does_nothing():
    pet = Pet("Mochi", species="dog", age=3)
    task = Task("Walk", category="walk", duration=20, priority=3)
    pet.add_task(task)

    pet.remove_task("nonexistent-id")

    assert len(pet.tasks) == 1


def test_pet_edit_task_updates_fields():
    pet = Pet("Mochi", species="dog", age=3)
    task = Task("Walk", category="walk", duration=20, priority=3)
    pet.add_task(task)

    pet.edit_task(task.task_id, title="Long walk", duration=45)

    assert task.title == "Long walk"
    assert task.duration == 45
    assert task.priority == 3  # unchanged


def test_pet_edit_task_unknown_id_does_nothing():
    pet = Pet("Mochi", species="dog", age=3)
    task = Task("Walk", category="walk", duration=20, priority=3)
    pet.add_task(task)

    pet.edit_task("nonexistent-id", title="Should not change")

    assert task.title == "Walk"


# ── Test 20: Error paths and edge cases ──────────────────────────────────────

def test_filter_tasks_raises_for_invalid_status():
    scheduler = Scheduler()
    task = Task("Walk", category="walk", duration=20, priority=3)

    with pytest.raises(ValueError):
        scheduler.filter_tasks([task], status="invalid")


def test_format_conflict_warnings_returns_clean_message_when_no_conflicts():
    scheduler = Scheduler()
    t1 = Task("Walk", category="walk", duration=20, priority=5, scheduled_time="08:00")
    t2 = Task("Lunch", category="feeding", duration=10, priority=4, scheduled_time="12:00")

    result = scheduler.format_conflict_warnings([t1, t2])

    assert result == "No scheduling conflicts detected."


def test_sort_tasks_by_title_alphabetical():
    scheduler = Scheduler()
    t1 = Task("Zumba", category="enrichment", duration=20, priority=3)
    t2 = Task("Breakfast", category="feeding", duration=10, priority=5)
    t3 = Task("Morning walk", category="walk", duration=30, priority=4)

    ordered = scheduler.sort_tasks([t1, t2, t3], key="title")

    assert [t.title for t in ordered] == ["Breakfast", "Morning walk", "Zumba"]


def test_fit_to_time_budget_returns_empty_for_zero_budget():
    scheduler = Scheduler()
    tasks = [Task("Walk", category="walk", duration=10, priority=5)]

    assert scheduler.fit_to_time_budget(tasks, minutes=0) == []


def test_fit_to_time_budget_returns_empty_when_all_tasks_exceed_budget():
    scheduler = Scheduler()
    task = Task("Long walk", category="walk", duration=60, priority=5)

    assert scheduler.fit_to_time_budget([task], minutes=30) == []


def test_owner_add_task_raises_when_no_pet_id_on_task_or_argument():
    owner = Owner("Yesenia", daily_time_budget=60)
    owner.add_pet(Pet("Mochi", species="dog", age=3))
    task = Task("Walk", category="walk", duration=20, priority=3)
    # task.pet_id is None and no pet_id argument passed

    with pytest.raises(ValueError):
        owner.add_task(task)


def test_owner_remove_task_unknown_id_does_nothing():
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", category="walk", duration=20, priority=3))

    owner.remove_task("nonexistent-id")

    assert len(pet.tasks) == 1


def test_owner_edit_task_unknown_id_does_nothing():
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)
    task = Task("Walk", category="walk", duration=20, priority=3)
    pet.add_task(task)

    owner.edit_task("nonexistent-id", title="Should not change")

    assert task.title == "Walk"


# ── Test 6: Owner Pet Management ─────────────────────────────────────────────

def test_owner_remove_pet_reduces_pet_count():
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)
    assert len(owner.pets) == 1

    owner.remove_pet(pet.pet_id)
    assert len(owner.pets) == 0


def test_owner_remove_pet_unknown_id_does_nothing():
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    owner.remove_pet("nonexistent-id")
    assert len(owner.pets) == 1


def test_owner_get_pet_returns_correct_pet():
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    result = owner.get_pet(pet.pet_id)
    assert result is pet


def test_owner_get_pet_returns_none_for_unknown_id():
    owner = Owner("Yesenia", daily_time_budget=60)

    result = owner.get_pet("nonexistent-id")
    assert result is None


# ── Test 7: Owner Task Management ────────────────────────────────────────────

def test_owner_add_task_with_explicit_pet_id():
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)
    task = Task("Walk", category="walk", duration=20, priority=3)

    owner.add_task(task, pet_id=pet.pet_id)
    assert len(pet.tasks) == 1


def test_owner_remove_task_removes_from_correct_pet():
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)
    task = Task("Walk", category="walk", duration=20, priority=3)
    pet.add_task(task)
    assert len(pet.tasks) == 1

    owner.remove_task(task.task_id)
    assert len(pet.tasks) == 0


def test_owner_edit_task_updates_across_pets():
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)
    task = Task("Walk", category="walk", duration=20, priority=3)
    pet.add_task(task)

    owner.edit_task(task.task_id, title="Long walk", duration=45, priority=5)
    assert task.title == "Long walk"
    assert task.duration == 45
    assert task.priority == 5


# ── Test 8: Task.update_details ───────────────────────────────────────────────

def test_task_update_details_changes_all_fields():
    task = Task("Walk", category="walk", duration=20, priority=3)

    task.update_details(title="Long walk", duration=45, priority=5)
    assert task.title == "Long walk"
    assert task.duration == 45
    assert task.priority == 5


def test_task_update_details_partial_update_leaves_others_unchanged():
    task = Task("Walk", category="walk", duration=20, priority=3)

    task.update_details(duration=30)
    assert task.title == "Walk"     # unchanged
    assert task.duration == 30
    assert task.priority == 3       # unchanged


# ── Test 9: Pet Health ────────────────────────────────────────────────────────

def test_add_medical_condition_appends_to_list():
    pet = Pet("Luna", species="cat", age=5)
    assert pet.medical_conditions == []

    pet.add_medical_condition("diabetes")
    assert pet.medical_conditions == ["diabetes"]

    pet.add_medical_condition("arthritis")
    assert pet.medical_conditions == ["diabetes", "arthritis"]


def test_add_allergy_appends_to_list():
    pet = Pet("Luna", species="cat", age=5)
    assert pet.allergies == []

    pet.add_allergy("chicken")
    assert pet.allergies == ["chicken"]


# ── Test 10: Scheduler Strategy Branching ────────────────────────────────────

def test_generate_plan_duration_strategy_picks_shortest_first():
    scheduler = Scheduler(strategy="duration")
    owner = Owner("Yesenia", daily_time_budget=30)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    long_task = Task("Long walk", category="walk", duration=25, priority=5)
    short_task = Task("Quick feed", category="feeding", duration=5, priority=1)
    pet.add_task(long_task)
    pet.add_task(short_task)

    plan = scheduler.generate_plan(owner)
    assert plan[0].title == "Quick feed"


def test_generate_plan_priority_strategy_picks_highest_priority_first():
    scheduler = Scheduler(strategy="priority")
    owner = Owner("Yesenia", daily_time_budget=60)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)

    low = Task("Grooming", category="grooming", duration=15, priority=1)
    high = Task("Medication", category="medication", duration=10, priority=5)
    pet.add_task(low)
    pet.add_task(high)

    plan = scheduler.generate_plan(owner)
    assert plan[0].title == "Medication"


def test_generate_plan_activity_boost_promotes_walk_for_high_activity_pet():
    scheduler = Scheduler(strategy="priority")
    owner = Owner("Yesenia", daily_time_budget=20)
    pet = Pet("Mochi", species="dog", age=3, activity_level="high")
    owner.add_pet(pet)

    # Walk priority 3 + ACTIVITY_BOOST 2 = effective 5; feed base priority 4
    walk = Task("Morning walk", category="walk", duration=20, priority=3)
    feed = Task("Breakfast", category="feeding", duration=20, priority=4)
    pet.add_task(walk)
    pet.add_task(feed)

    # budget fits only one task — boosted walk should win
    plan = scheduler.generate_plan(owner, pet=pet)
    assert len(plan) == 1
    assert plan[0].title == "Morning walk"


def test_filter_by_health_returns_tasks_unchanged():
    scheduler = Scheduler()
    pet = Pet("Luna", species="cat", age=5)
    tasks = [
        Task("Feed", category="feeding", duration=10, priority=4),
        Task("Walk", category="walk", duration=20, priority=3),
    ]

    result = scheduler.filter_by_health(tasks, pet)
    assert result == tasks