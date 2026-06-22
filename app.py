from pawpal_system import Owner, Pet, Task, Scheduler
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("Pet care scheduling assistant")

# ── Session state init ────────────────────────────────────────────────────────

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", daily_time_budget=90)
if "plan" not in st.session_state:
    st.session_state.plan = []

owner: Owner = st.session_state.owner

# ── Owner Setup ───────────────────────────────────────────────────────────────

st.header("👤 Owner Setup")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=owner.name)
    owner.name = owner_name
with col2:
    budget = st.number_input(
        "Daily time budget (minutes)",
        min_value=10, max_value=480,
        value=owner.daily_time_budget, step=10,
    )
    owner.daily_time_budget = int(budget)

with st.expander("⚙️ Scheduling Preferences"):
    pc1, pc2 = st.columns(2)
    with pc1:
        prefer_time = st.selectbox(
            "Preferred time of day",
            ["(none)", "morning", "afternoon", "evening"],
        )
    with pc2:
        avoid_cat = st.text_input("Avoid category (e.g. grooming)", value="")
    prefs: dict = {}
    if prefer_time != "(none)":
        prefs["prefer_time"] = prefer_time
    if avoid_cat.strip():
        prefs["avoid_category"] = avoid_cat.strip()
    owner.preferences = prefs

st.divider()

# ── Pet Setup ─────────────────────────────────────────────────────────────────

st.header("🐶 Pets")

with st.form("add_pet_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        pet_name = st.text_input("Name", value="Mochi")
    with c2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with c3:
        age = st.number_input("Age", min_value=0, max_value=40, value=3)
    with c4:
        activity_level = st.selectbox("Activity level", ["low", "medium", "high"], index=1)
    add_pet = st.form_submit_button("➕ Add pet")

if add_pet:
    owner.add_pet(Pet(name=pet_name, species=species, age=int(age), activity_level=activity_level))
    st.success(f"Added **{pet_name}** to {owner.name}'s pets.")

if owner.pets:
    st.table([
        {
            "Name": p.name,
            "Species": p.species,
            "Age": p.age,
            "Activity": p.activity_level,
            "Tasks": len(p.tasks),
        }
        for p in owner.pets
    ])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Task Setup ────────────────────────────────────────────────────────────────

st.header("📋 Tasks")

if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            task_title = st.text_input("Task title", value="Morning walk")
            category = st.selectbox(
                "Category",
                ["walk", "feeding", "medication", "grooming", "enrichment", "other"],
            )
        with c2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            priority = st.slider("Priority (1–5)", min_value=1, max_value=5, value=3)
        with c3:
            pet_options = {p.name: p.pet_id for p in owner.pets}
            selected_pet_name = st.selectbox("Assign to pet", list(pet_options.keys()))
            scheduled_time = st.text_input("Scheduled time (HH:MM, optional)", value="")
            due_today = st.checkbox("Due today", value=True)
        add_task = st.form_submit_button("➕ Add task")

    if add_task:
        new_task = Task(
            title=task_title,
            category=category,
            duration=int(duration),
            priority=priority,
            scheduled_time=scheduled_time.strip() or None,
            due_today=due_today,
        )
        owner.add_task(new_task, pet_id=pet_options[selected_pet_name])
        st.success(f"Added **{task_title}** to {selected_pet_name}.")

    all_tasks = owner.tasks
    if all_tasks:
        pet_name_map = {p.pet_id: p.name for p in owner.pets}
        st.table([
            {
                "Pet": pet_name_map.get(t.pet_id, "—"),
                "Title": t.title,
                "Category": t.category,
                "Duration": f"{t.duration} min",
                "Priority": f"{t.priority}/5",
                "Time": t.scheduled_time or "—",
                "Due Today": "✓" if t.due_today else "✗",
                "Done": "✓" if t.completed else "—",
            }
            for t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ── Generate Schedule ─────────────────────────────────────────────────────────

st.header("📅 Today's Schedule")

sc1, sc2 = st.columns(2)
with sc1:
    strategy = st.selectbox("Strategy", ["priority", "duration", "balanced"])
with sc2:
    fairness = st.checkbox("Fairness mode (one task guaranteed per pet first)")

if st.button("🗓️ Generate Schedule", type="primary"):
    scheduler = Scheduler(strategy=strategy, fairness=fairness)
    st.session_state.plan = scheduler.generate_plan(owner)
    st.session_state.scheduler = scheduler

plan: list[Task] = st.session_state.plan
active_scheduler: Scheduler = st.session_state.get("scheduler", Scheduler())

if plan:
    pet_name_map = {p.pet_id: p.name for p in owner.pets}
    total_time = sum(t.duration for t in plan)
    due_incomplete = [t for t in owner.tasks if t.due_today and not t.completed]
    skipped = max(len(due_incomplete) - len(plan), 0)

    m1, m2, m3 = st.columns(3)
    m1.metric("Tasks Scheduled", len(plan))
    m2.metric("Total Time", f"{total_time} min")
    m3.metric("Tasks Skipped", skipped)

    st.table([
        {
            "#": i,
            "Pet": pet_name_map.get(t.pet_id, "—"),
            "Task": t.title,
            "Category": t.category,
            "Duration": f"{t.duration} min",
            "Priority": f"{t.priority}/5",
            "Time": t.scheduled_time or "—",
        }
        for i, t in enumerate(plan, start=1)
    ])

    st.subheader("⚠️ Conflict Check")
    conflicts = active_scheduler.detect_time_conflicts(owner.tasks)
    if conflicts:
        for c in conflicts:
            st.warning(c)
    else:
        st.success("No scheduling conflicts detected.")

elif owner.pets and owner.tasks:
    st.info("Click 'Generate Schedule' to build today's plan.")

st.divider()

# ── Filter & Sort ─────────────────────────────────────────────────────────────

st.header("🔎 Filter & Sort Tasks")

if not owner.tasks:
    st.info("Add tasks to use filtering and sorting.")
else:
    scheduler_fs = Scheduler()
    pet_name_map = {p.pet_id: p.name for p in owner.pets}
    pet_filter_options: dict = {"All pets": None} | {p.name: p.pet_id for p in owner.pets}

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        filter_pet = st.selectbox("Pet", list(pet_filter_options.keys()), key="filter_pet")
    with fc2:
        filter_status = st.selectbox("Status", ["all", "completed", "incomplete"], key="filter_status")
    with fc3:
        filter_due = st.checkbox("Due today only", key="filter_due")
    with fc4:
        sort_key = st.selectbox("Sort by", ["priority", "duration", "title"], key="sort_key")
    sort_desc = st.checkbox("Descending", value=True, key="sort_desc")

    filtered = scheduler_fs.filter_tasks(
        owner.tasks,
        pet_id=pet_filter_options[filter_pet],
        status=filter_status if filter_status != "all" else None,
        due_today_only=filter_due,
    )
    sorted_tasks = scheduler_fs.sort_tasks(filtered, key=sort_key, reverse=sort_desc)

    if sorted_tasks:
        st.caption(f"Showing {len(sorted_tasks)} of {len(owner.tasks)} task(s)")
        for t in sorted_tasks:
            pet_label = pet_name_map.get(t.pet_id, "Unknown")
            base = f"**[{pet_label}]** {t.title} — {t.duration} min · priority {t.priority}/5"
            if t.completed:
                st.success(base + " ✓ completed")
            elif not t.due_today:
                st.info(base + " (not due today)")
            elif t.times_skipped > 0:
                st.warning(base + f" ⚠️ skipped {t.times_skipped}×")
            else:
                st.write(base)
    else:
        st.info("No tasks match the selected filters.")
