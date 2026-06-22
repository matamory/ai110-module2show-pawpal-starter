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
    breed: Optional[str] = None
    weight: Optional[float] = None          # in kg
    activity_level: str = "medium"          # "low", "medium", "high"
    medical_conditions: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    time_budget: Optional[int] = None       # max minutes per day for this pet
    pet_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_medical_condition(self, condition: str) -> None:
        self.medical_conditions.append(condition)

    def add_allergy(self, allergy: str) -> None:
        self.allergies.append(allergy)

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
    times_skipped: int = 0                  # bumped by record_skipped(); raises effective priority
    must_follow: Optional[str] = None       # task_id that must appear before this task in the plan
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

    def add_task(self, task: Task, pet_id: Optional[str] = None) -> None:
        """
        Add a task to the matching pet.
        Pass pet_id explicitly or pre-set task.pet_id before calling.
        Raises ValueError if no matching pet is found.
        """
        target_id = pet_id or task.pet_id
        pet = self.get_pet(target_id)
        if pet is None:
            raise ValueError(
                f"No pet found with pet_id '{target_id}'. "
                "Pass pet_id explicitly or set task.pet_id before calling add_task."
            )
        pet.add_task(task)

    def edit_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> None:
        """Find a task by ID across all pets and delegate to task.update_details()."""
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task:
            task.update_details(title=title, duration=duration, priority=priority)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by ID from whichever pet owns it."""
        pet = next(
            (p for p in self.pets if any(t.task_id == task_id for t in p.tasks)),
            None,
        )
        if pet:
            pet.remove_task(task_id)

    def get_pet(self, pet_id: str) -> Optional[Pet]:
        """Return the Pet with the given pet_id, or None if not found."""
        return next((p for p in self.pets if p.pet_id == pet_id), None)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet (and all its tasks) from this owner."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    ACTIVITY_BOOST = 2

    _SORT_KEYS: dict = {
        "priority": lambda t: t.priority,
        "duration": lambda t: t.duration,
        "title":    lambda t: t.title.lower(),
    }
    _STATUS_PREDICATES: dict = {
        "completed":  lambda t: t.completed,
        "incomplete": lambda t: not t.completed,
    }
    _TIME_WINDOWS: dict = {
        "morning":   (6, 12),
        "afternoon": (12, 18),
        "evening":   (18, 24),
    }

    def __init__(self, strategy: str = "priority", fairness: bool = False):
        self.strategy: str = strategy       # "priority", "duration", "balanced"
        self.fairness: bool = fairness      # when True, guarantees each pet at least its top task

    # ── Private helpers ────────────────────────────────────────────────────

    def _time_to_minutes(self, time_str: str) -> int:
        """Parse 'HH:MM' into total minutes since midnight."""
        h, m = time_str.split(":")
        return int(h) * 60 + int(m)

    def _preference_bonus(self, task: Task, preferences: dict) -> int:
        """
        Return a priority adjustment based on owner preferences.
        prefer_time ("morning" / "afternoon" / "evening") adds +1 to tasks in that window.
        avoid_category subtracts 1 from tasks of that category.
        """
        bonus = 0
        prefer_time = preferences.get("prefer_time")
        if prefer_time and task.scheduled_time:
            hour = self._time_to_minutes(task.scheduled_time) // 60
            window = self._TIME_WINDOWS.get(prefer_time)
            if window and window[0] <= hour < window[1]:
                bonus += 1
        if preferences.get("avoid_category") == task.category:
            bonus -= 1
        return bonus

    def _apply_pet_budgets(self, owner: Owner) -> list[Task]:
        """
        Aggregate due tasks across all pets. For any pet with time_budget set,
        keep only its highest-priority tasks that fit within that budget.
        """
        result = []
        for pet in owner.pets:
            pet_tasks = self.filter_due_tasks(pet.tasks)
            if pet.time_budget is not None:
                by_priority = sorted(pet_tasks, key=lambda t: t.priority, reverse=True)
                pet_tasks = self.fit_to_time_budget(by_priority, pet.time_budget)
            result.extend(pet_tasks)
        return result

    def _fair_select(
        self,
        tasks: list[Task],
        owner: Owner,
        score_func=None,
    ) -> list[Task]:
        """
        Round-robin selection: give each pet its highest-scoring task first,
        then fill the remaining budget with the best leftover tasks (knapsack).
        tasks must be pre-sorted by descending score.
        """
        remaining = owner.daily_time_budget
        scheduled_ids: set[str] = set()
        plan: list[Task] = []

        # Round 1: one top task per pet
        for pet in owner.pets:
            top = next(
                (t for t in tasks if t.pet_id == pet.pet_id and t.task_id not in scheduled_ids),
                None,
            )
            if top and top.duration <= remaining:
                plan.append(top)
                scheduled_ids.add(top.task_id)
                remaining -= top.duration

        # Round 2: fill remaining budget (knapsack with same scoring)
        leftover = [t for t in tasks if t.task_id not in scheduled_ids]
        plan += self.fit_to_time_budget(leftover, remaining, score_func=score_func)
        return plan

    def _enforce_ordering(self, plan: list[Task]) -> list[Task]:
        """
        Reorder plan tasks so that must_follow constraints are satisfied —
        each task appears after the task it depends on.
        Dependency cycles are silently ignored.
        """
        task_map = {t.task_id: t for t in plan}
        ordered: list[Task] = []
        visited: set[str] = set()

        def visit(task: Task) -> None:
            if task.task_id in visited:
                return
            if task.must_follow and task.must_follow in task_map:
                visit(task_map[task.must_follow])
            visited.add(task.task_id)
            ordered.append(task)

        for task in plan:
            visit(task)
        return ordered

    # ── Public API ─────────────────────────────────────────────────────────

    def generate_plan(self, owner: Owner, pet: Optional[Pet] = None) -> list[Task]:
        """
        Build a daily task plan for the owner.

        Candidate tasks:
        - Per-pet time_budget is applied first when no specific pet is given.
        - filter_by_health screens tasks against the pet's health profile.

        Scoring (priority / balanced strategy):
        - Effective score = base priority + times_skipped + activity boost + preference bonus.
        - times_skipped provides automatic urgency escalation for repeatedly missed tasks.
        - High-activity pets receive ACTIVITY_BOOST on walk tasks.
        - owner.preferences ("prefer_time", "avoid_category") shift scores up or down.

        Selection:
        - fairness=True guarantees each pet at least its top-scoring task (round-robin),
          then fills remaining budget with the best leftover tasks.
        - fairness=False uses pure knapsack to maximise total effective priority.

        Ordering:
        - must_follow constraints are enforced after selection.
        """
        # 1. Gather and pre-filter candidate tasks
        if pet:
            tasks = self.filter_due_tasks(pet.tasks)
            tasks = self.filter_by_health(tasks, pet)
        else:
            tasks = self._apply_pet_budgets(owner)

        if not tasks:
            return []

        # 2. Build effective scoring function
        boost_walks = pet is not None and pet.activity_level == "high"

        def score(task: Task) -> int:
            s = task.priority + task.times_skipped
            if boost_walks and task.category == "walk":
                s += self.ACTIVITY_BOOST
            s += self._preference_bonus(task, owner.preferences)
            return s

        # 3. Sort by strategy
        if self.strategy == "duration":
            sorted_tasks = self.sort_tasks(tasks, key="duration", reverse=False)
        else:  # "priority" or "balanced"
            sorted_tasks = self.sort_tasks(tasks, key_func=score, reverse=True)

        # 4. Select within budget
        if self.fairness and not pet:
            plan = self._fair_select(sorted_tasks, owner, score_func=score)
        else:
            plan = self.fit_to_time_budget(
                sorted_tasks, owner.daily_time_budget, score_func=score
            )

        # 5. Enforce task ordering constraints
        return self._enforce_ordering(plan)

    def sort_tasks(
        self,
        tasks: list[Task],
        key: str = "priority",
        reverse: bool = False,
        key_func=None,
    ) -> list[Task]:
        """
        Sort tasks by a single key or by a provided key function.
        Supported keys: "priority", "duration", "title"
        """
        if key_func is not None:
            return sorted(tasks, key=key_func, reverse=reverse)
        if key not in self._SORT_KEYS:
            raise ValueError(f"Unsupported sort key '{key}'.")
        return sorted(tasks, key=self._SORT_KEYS[key], reverse=reverse)

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
        Supported status values: "completed", "incomplete"
        """
        filtered = tasks
        if pet_id is not None:
            filtered = [t for t in filtered if t.pet_id == pet_id]
        if status is not None:
            if status not in self._STATUS_PREDICATES:
                raise ValueError("status must be 'completed' or 'incomplete'.")
            filtered = [t for t in filtered if self._STATUS_PREDICATES[status](t)]
        if due_today_only:
            filtered = [t for t in filtered if t.due_today]
        return filtered

    def filter_by_health(self, tasks: list[Task], pet: Pet) -> list[Task]:
        """Filter out tasks that conflict with the pet's allergies or medical conditions."""
        return tasks

    def detect_time_conflicts(self, tasks: list[Task]) -> list[str]:
        """
        Overlap-aware conflict detection: flags any two due, incomplete tasks
        whose time windows (scheduled_time to scheduled_time + duration) overlap.
        Returns warning messages; never raises.
        """
        scheduled = sorted(
            [t for t in tasks if t.scheduled_time and not t.completed and t.due_today],
            key=lambda t: (self._time_to_minutes(t.scheduled_time), -t.priority),
        )

        warnings: list[str] = []
        for i, t1 in enumerate(scheduled):
            t1_end = self._time_to_minutes(t1.scheduled_time) + t1.duration
            for t2 in scheduled[i + 1:]:
                t2_start = self._time_to_minutes(t2.scheduled_time)
                if t2_start >= t1_end:
                    break  # sorted by start time — no further overlaps with t1
                pet_ids = {t1.pet_id, t2.pet_id}
                scope = "same pet" if len(pet_ids) == 1 else "different pets"
                warnings.append(
                    f"⚠️ Conflict at {t1.scheduled_time} ({scope}): {t1.title}, {t2.title}"
                )

        return warnings

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        """
        Auto-resolve scheduling conflicts by bumping overlapping tasks forward:
        each task is pushed to start when the preceding task ends.
        Mutates scheduled_time on affected tasks in-place.
        Returns tasks sorted by resolved time (unscheduled/completed appended last).
        Note: single-pass — call again if cascading bumps create new overlaps.
        """
        scheduled = sorted(
            [t for t in tasks if t.scheduled_time and not t.completed and t.due_today],
            key=lambda t: (self._time_to_minutes(t.scheduled_time), -t.priority),
        )
        for prev, curr in zip(scheduled, scheduled[1:]):
            prev_end = self._time_to_minutes(prev.scheduled_time) + prev.duration
            if self._time_to_minutes(curr.scheduled_time) < prev_end:
                curr.scheduled_time = f"{prev_end // 60:02d}:{prev_end % 60:02d}"

        unscheduled = [
            t for t in tasks if not t.scheduled_time or t.completed or not t.due_today
        ]
        return scheduled + unscheduled

    def record_skipped(self, plan: list[Task], all_tasks: list[Task]) -> None:
        """
        Increment times_skipped on every due, incomplete task not in the plan.
        Call this after generate_plan each day so urgency escalates automatically.
        """
        plan_ids = {t.task_id for t in plan}
        for task in all_tasks:
            if task.task_id not in plan_ids and task.due_today and not task.completed:
                task.times_skipped += 1

    def fit_to_time_budget(
        self,
        tasks: list[Task],
        minutes: int,
        score_func=None,
    ) -> list[Task]:
        """
        Select tasks that maximise total effective score within the time budget (0/1 knapsack).
        score_func(task) -> int provides the value per task; defaults to task.priority.
        Preserves the relative input order of selected tasks in the output.
        """
        n = len(tasks)
        if n == 0 or minutes <= 0:
            return []

        scores = [score_func(t) if score_func else t.priority for t in tasks]

        dp = [[0] * (minutes + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            task_duration = tasks[i - 1].duration
            task_score = scores[i - 1]
            for w in range(minutes + 1):
                dp[i][w] = dp[i - 1][w]
                if task_duration <= w:
                    dp[i][w] = max(dp[i][w], dp[i - 1][w - task_duration] + task_score)

        selected: list[Task] = []
        w = minutes
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                selected.append(tasks[i - 1])
                w -= tasks[i - 1].duration

        return list(reversed(selected))

    def format_conflict_warnings(self, tasks: list[Task]) -> str:
        """Return a printable warning block for any detected time conflicts."""
        warnings = self.detect_time_conflicts(tasks)
        if not warnings:
            return "No scheduling conflicts detected."
        return "\n".join(warnings)

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
