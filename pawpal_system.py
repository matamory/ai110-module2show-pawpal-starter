"""
PawPal+ — Core system classes
Pet and Task use dataclasses for clean, lightweight object definitions.
Owner and Scheduler use regular classes since they manage state and behavior.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    activity_level: str = "medium"         # "low", "medium", "high"
    health_notes: str = ""
    tasks: list[Task] = field(default_factory=list)
    pet_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update_health_notes(self, notes: str) -> None:
        """Append new health notes to existing notes."""
        self.health_notes = (self.health_notes + "\n" + notes).strip()

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and stamp it with this pet's ID."""
        task.pet_id = self.pet_id
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet by task_id."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def edit_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> None:
        """Find a task by ID and delegate to task.update_details()."""
        for task in self.tasks:
            if task.task_id == task_id:
                task.update_details(title=title, duration=duration, priority=priority)
                return


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    category: str                           # e.g. "walk", "feeding", "medication"
    duration: int                           # in minutes
    priority: int                           # 1 (low) to 5 (high)
    scheduled_time: Optional[str] = None    # e.g. "08:00" (24-hour HH:MM)
    due_today: bool = True
    completed: bool = False
    pet_id: Optional[str] = None            # links this task to a specific Pet
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def update_details(
        self,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> None:
        """Update one or more fields on this task. Only provided values are changed."""
        if title is not None:
            self.title = title
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, daily_time_budget: int):
        self.owner_id: str = str(uuid.uuid4())
        self.name: str = name
        self.daily_time_budget: int = daily_time_budget  # minutes available per day
        self.preferences: dict = {}         # e.g. {"prefer_time": "morning", "avoid_category": "grooming"}
        self.pets: list[Pet] = []

    @property
    def tasks(self) -> list[Task]:
        """Aggregate all tasks across every pet this owner has."""
        return [task for pet in self.pets for task in pet.tasks]

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """
        Add a task to the matching pet (looked up by task.pet_id).
        Raises ValueError if no matching pet is found.
        """
        for pet in self.pets:
            if pet.pet_id == task.pet_id:
                pet.add_task(task)
                return
        raise ValueError(
            f"No pet found with pet_id '{task.pet_id}'. "
            "Set task.pet_id to a valid pet before calling add_task."
        )

    def edit_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> None:
        """Find a task by ID across all pets and delegate to task.update_details()."""
        for pet in self.pets:
            for task in pet.tasks:
                if task.task_id == task_id:
                    task.update_details(title=title, duration=duration, priority=priority)
                    return

    def remove_task(self, task_id: str) -> None:
        """Remove a task by ID from whichever pet owns it."""
        for pet in self.pets:
            pet.remove_task(task_id)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    # Priority boost applied to walk tasks for high-activity pets.
    ACTIVITY_BOOST = 2

    def __init__(self, strategy: str = "priority"):
        self.strategy: str = strategy       # e.g. "priority", "duration", "balanced"

    def generate_plan(self, owner: Owner, pet: Optional[Pet] = None) -> list[Task]:
        """
        Build a daily task plan for the owner.
        If pet is provided, only that pet's tasks are considered;
        otherwise all tasks across all owner's pets are used.
        High-activity pets get a priority boost on walk tasks.
        Returns tasks sorted by effective priority that fit the time budget.
        """
        tasks = pet.tasks if pet else owner.tasks
        due = self.filter_due_tasks(tasks)

        # Determine activity boost: high-activity pets boost walk task scores.
        boost_walks = pet is not None and pet.activity_level == "high"

        def effective_priority(task: Task) -> int:
            bonus = self.ACTIVITY_BOOST if (boost_walks and task.category == "walk") else 0
            return task.priority + bonus

        sorted_tasks = self.sort_tasks(due, key_func=effective_priority, reverse=True)
        return self.fit_to_time_budget(sorted_tasks, owner.daily_time_budget)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return a new list of tasks sorted from highest to lowest priority."""
        return sorted(tasks, key=lambda t: t.priority, reverse=True)

    def sort_tasks(
        self,
        tasks: list[Task],
        key: str = "priority",
        reverse: bool = False,
        key_func=None,
    ) -> list[Task]:
        """
        Sort tasks by a single key or by a provided key function.

        Supported keys:
        - "priority"  (default)
        - "duration"
        - "title"
        """
        if key_func is not None:
            return sorted(tasks, key=key_func, reverse=reverse)

        if key == "priority":
            return sorted(tasks, key=lambda t: t.priority, reverse=reverse)
        if key == "duration":
            return sorted(tasks, key=lambda t: t.duration, reverse=reverse)
        if key == "title":
            return sorted(tasks, key=lambda t: t.title.lower(), reverse=reverse)

        raise ValueError(f"Unsupported sort key '{key}'.")

    def filter_due_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return only tasks that are due today and not yet completed."""
        return [t for t in tasks if t.due_today and not t.completed]

    def filter_tasks(
        self,
        tasks: list[Task],
        pet_id: Optional[str] = None,
        status: Optional[str] = None,
        due_today_only: bool = False,
    ) -> list[Task]:
        """
        Filter tasks by pet and/or status.

        Supported status values:
        - "completed"
        - "incomplete"
        """
        filtered = tasks

        if pet_id is not None:
            filtered = [t for t in filtered if t.pet_id == pet_id]

        if status is not None:
            if status == "completed":
                filtered = [t for t in filtered if t.completed]
            elif status == "incomplete":
                filtered = [t for t in filtered if not t.completed]
            else:
                raise ValueError("status must be 'completed' or 'incomplete'.")

        if due_today_only:
            filtered = [t for t in filtered if t.due_today]

        return filtered

    def detect_time_conflicts(self, tasks: list[Task]) -> list[str]:
        """
        Lightweight conflict detection by exact scheduled_time match.
        Returns warning messages and never raises for conflicts.

        A conflict exists when 2+ due, incomplete tasks share the same time.
        """
        grouped: dict[str, list[Task]] = {}
        for task in tasks:
            if not task.scheduled_time:
                continue
            if task.completed or not task.due_today:
                continue
            grouped.setdefault(task.scheduled_time, []).append(task)

        warnings: list[str] = []
        for time_slot, slot_tasks in grouped.items():
            if len(slot_tasks) < 2:
                continue

            pet_ids = {task.pet_id for task in slot_tasks}
            conflict_scope = "same pet" if len(pet_ids) == 1 else "different pets"
            titles = ", ".join(task.title for task in slot_tasks)
            warnings.append(
                f"⚠️ Conflict at {time_slot} ({conflict_scope}): {titles}"
            )

        return warnings

    def format_conflict_warnings(self, tasks: list[Task]) -> str:
        """Return a printable warning block for any detected time conflicts."""
        warnings = self.detect_time_conflicts(tasks)
        if not warnings:
            return "No scheduling conflicts detected."
        return "\n".join(warnings)

    def fit_to_time_budget(self, tasks: list[Task], minutes: int) -> list[Task]:
        """
        Greedily select tasks until the time budget is exhausted.
        IMPORTANT: tasks must already be sorted by priority (highest first)
        before calling this method so short high-priority tasks are not
        blocked by long low-priority ones.
        Returns the subset of tasks that fit within the budget.
        """
        plan: list[Task] = []
        remaining = minutes
        for task in tasks:
            if task.duration <= remaining:
                plan.append(task)
                remaining -= task.duration
        return plan

    def explain_plan(self, plan: list[Task]) -> str:
        """
        Return a human-readable explanation of the generated plan,
        listing each task with its priority, duration, and category.
        """
        if not plan:
            return "No tasks were scheduled. Either nothing is due today or the time budget is too small."

        total = sum(t.duration for t in plan)
        lines = [f"Scheduled {len(plan)} task(s) totalling {total} minute(s):\n"]
        for i, task in enumerate(plan, start=1):
            lines.append(
                f"  {i}. [{task.category.upper()}] {task.title} "
                f"— {task.duration} min, priority {task.priority}/5"
            )
        return "\n".join(lines)
