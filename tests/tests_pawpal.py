import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pawpal_system import Pet, Task


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
    assert task.pet_id == pet.pet_id     # stamped with pet's ID after adding
