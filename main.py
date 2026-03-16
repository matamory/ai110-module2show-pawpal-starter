from pawpal_system import Owner, Pet, Task, Scheduler

# ── Setup ────────────────────────────────────────────────────────────────────

owner = Owner("Jordan", daily_time_budget=90)

mochi = Pet("Mochi", species="dog", age=3, activity_level="high")
luna  = Pet("Luna",  species="cat", age=5, activity_level="low")

owner.add_pet(mochi)
owner.add_pet(luna)

# ── Tasks for Mochi (dog) ────────────────────────────────────────────────────

mochi.add_task(Task("Fetch in yard",  category="enrichment", duration=20, priority=3, scheduled_time="17:30"))
mochi.add_task(Task("Heartworm pill", category="medication", duration=5,  priority=4, scheduled_time="08:00"))
mochi.add_task(Task("Morning walk",   category="walk",       duration=30, priority=5, scheduled_time="08:00"))
mochi.add_task(Task("Breakfast",      category="feeding",    duration=10, priority=5, scheduled_time="08:30"))

# ── Tasks for Luna (cat) ─────────────────────────────────────────────────────

luna.add_task(Task("Laser pointer",    category="enrichment", duration=10, priority=3, scheduled_time="18:00"))
luna.add_task(Task("Wet food serving", category="feeding",    duration=5,  priority=5, scheduled_time="08:00"))
luna.add_task(Task("Brush coat",       category="grooming",   duration=15, priority=2, scheduled_time="19:00"))
luna.add_task(Task("Vet follow-up",    category="medication", duration=10, priority=4, due_today=False, scheduled_time="08:00"))

# Mark one task complete to demonstrate status filtering.
luna.tasks[0].mark_complete()

# ── Generate schedule ────────────────────────────────────────────────────────

scheduler = Scheduler()
plan = scheduler.generate_plan(owner)

# ── Print Today's Schedule ───────────────────────────────────────────────────

print("=" * 48)
print("       🐾  PawPal+ — Today's Schedule")
print("=" * 48)
print(f"  Owner : {owner.name}")
print(f"  Pets  : {', '.join(p.name for p in owner.pets)}")
print(f"  Budget: {owner.daily_time_budget} min available")
print("-" * 48)

for i, task in enumerate(plan, start=1):
    pet_name = next(
        (p.name for p in owner.pets if p.pet_id == task.pet_id), "Unknown"
    )
    print(
        f"  {i}. [{pet_name}] {task.title:<22}"
        f"  {task.duration:>3} min   priority {task.priority}/5"
    )

print("-" * 48)
total = sum(t.duration for t in plan)
skipped = len(owner.tasks) - len(plan)
print(f"  Total scheduled : {total} min")
print(f"  Tasks skipped   : {skipped} (over budget or not due)")
print("=" * 48)
print()
print(scheduler.explain_plan(plan))

print()
print("=" * 48)
print("       ⚠️  Conflict Check")
print("=" * 48)
print(scheduler.format_conflict_warnings(owner.tasks))

# ── Demo: Filtering + Sorting helpers ───────────────────────────────────────

all_tasks = owner.tasks

print()
print("=" * 48)
print("       🔎  Filter + Sort Demo")
print("=" * 48)

print("All tasks (in insertion order):")
for task in all_tasks:
    pet_name = next((p.name for p in owner.pets if p.pet_id == task.pet_id), "Unknown")
    status = "completed" if task.completed else "incomplete"
    print(
        f"  - [{pet_name}] {task.title} "
        f"({task.duration} min, {status}, due_today={task.due_today}, time={task.scheduled_time})"
    )

mochi_incomplete = scheduler.filter_tasks(all_tasks, pet_id=mochi.pet_id, status="incomplete")
mochi_incomplete_by_duration = scheduler.sort_tasks(mochi_incomplete, key="duration")

print()
print("Filtered: Mochi + incomplete")
for task in mochi_incomplete:
    print(f"  - {task.title} ({task.duration} min)")

print()
print("Sorted (by duration asc): Mochi + incomplete")
for task in mochi_incomplete_by_duration:
    print(f"  - {task.title} ({task.duration} min)")

due_today_tasks = scheduler.filter_tasks(all_tasks, due_today_only=True)
due_today_by_priority = scheduler.sort_tasks(due_today_tasks, key="priority", reverse=True)

print()
print("Filtered: due today only")
for task in due_today_tasks:
    print(f"  - {task.title} (priority {task.priority})")

print()
print("Sorted (by priority desc): due today only")
for task in due_today_by_priority:
    print(f"  - {task.title} (priority {task.priority})")

print("=" * 48)
