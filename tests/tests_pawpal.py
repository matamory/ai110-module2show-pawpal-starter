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