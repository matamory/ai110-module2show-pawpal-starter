from pawpal_system import Owner, Pet, Task, Scheduler

# ── Setup ────────────────────────────────────────────────────────────────────

owner = Owner("Jordan", daily_time_budget=90)

mochi = Pet("Mochi", species="dog", age=3, activity_level="high")
luna  = Pet("Luna",  species="cat", age=5, activity_level="low")

owner.add_pet(mochi)
owner.add_pet(luna)

# ── Tasks for Mochi (dog) ────────────────────────────────────────────────────

mochi.add_task(Task("Morning walk",   category="walk",       duration=30, priority=5))
mochi.add_task(Task("Breakfast",      category="feeding",    duration=10, priority=5))
mochi.add_task(Task("Heartworm pill", category="medication", duration=5,  priority=4))
mochi.add_task(Task("Fetch in yard",  category="enrichment", duration=20, priority=3))

# ── Tasks for Luna (cat) ─────────────────────────────────────────────────────

luna.add_task(Task("Wet food serving", category="feeding",    duration=5,  priority=5))
luna.add_task(Task("Brush coat",       category="grooming",   duration=15, priority=2))
luna.add_task(Task("Laser pointer",    category="enrichment", duration=10, priority=3))

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
