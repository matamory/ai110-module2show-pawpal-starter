"""
PawPal+ — Core system classes
Pet and Task use dataclasses for clean, lightweight object definitions.
Owner and Scheduler use regular classes since they manage state and behavior.
"""

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
    pet_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update_health_notes(self, notes: str) -> None:
        """Replace or append health notes for this pet."""
        pass


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    category: str                           # e.g. "walk", "feeding", "medication"
    duration: int                           # in minutes
    priority: int                           # 1 (low) to 5 (high)
    due_today: bool = True
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        pass

    def update_details(
        self,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> None:
        """Update one or more fields on this task."""
        pass


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, daily_time_budget: int):
        self.owner_id: str = str(uuid.uuid4())
        self.name: str = name
        self.daily_time_budget: int = daily_time_budget  # minutes available per day
        self.preferences: list[str] = []
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        pass

    def add_task(self, task: Task) -> None:
        """Add a new task to this owner's task list."""
        pass

    def edit_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> None:
        """Find a task by ID and update its details."""
        pass

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this owner's task list by ID."""
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, strategy: str = "priority"):
        self.strategy: str = strategy       # e.g. "priority", "duration", "balanced"

    def generate_plan(self, owner: Owner, pet: Pet) -> list[Task]:
        """
        Build a daily task plan for the owner and pet.
        Returns an ordered list of tasks that fit within the time budget.
        """
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted from highest to lowest priority."""
        pass

    def filter_due_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return only tasks that are due today and not yet completed."""
        pass

    def fit_to_time_budget(self, tasks: list[Task], minutes: int) -> list[Task]:
        """
        Greedily select tasks until the time budget is exhausted.
        Returns the subset of tasks that fit.
        """
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        """
        Return a human-readable explanation of why each task was included
        and how the plan was constructed.
        """
        pass
