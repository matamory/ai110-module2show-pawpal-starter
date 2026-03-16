import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pawpal_system import Pet, Task, Scheduler


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