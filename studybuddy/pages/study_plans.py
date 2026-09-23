"""Journey step 4 & 7: Create a study plan, add tasks, track completion."""

import streamlit as st
from datetime import date, timedelta
from ..models import Task
from ..priority import PriorityEngine


def render(app):
    st.title("🗓️ Plans & Tasks")
    st.caption("Turn big goals into small, doable steps.")
    u = app.user

    st.markdown("**Pick a subject** — this is where you add subjects; there's no separate list to set up in your profile.")
    all_names = [s.name for s in app.data.subjects]
    my_names = [s.name for s in u.subjects]
    # subjects the user already has a plan for come first, for convenience
    ordered_names = my_names + [n for n in all_names if n not in my_names]
    subject_name = st.selectbox("Subject", ordered_names)
    subject = next(s for s in app.data.subjects if s.name == subject_name)
    plan = u.plan_for(subject)

    if plan is None:
        st.info(f"You haven't started a plan for **{subject.name}** yet.")
        if st.button(f"+ Start a plan for {subject.name}"):
            u.add_subject(subject)
            st.rerun()
        return

    with st.form("add_task_form"):
        title = st.text_input("Task")
        deadline = st.date_input("Deadline", value=date.today() + timedelta(days=7))
        difficulty = st.selectbox("Difficulty", Task.DIFFICULTIES, index=1)
        goal = st.text_input("Study goal (optional)")
        if st.form_submit_button("Add Task") and title:
            plan.add_task(Task(title, deadline, difficulty, goal))
            st.success(f"Added task '{title}'.")

    st.subheader(f"{subject.name} — {int(plan.progress()*100)}% complete")
    st.progress(plan.progress())

    st.markdown("**Task list** · sorted by smart priority")
    sorted_tasks = sorted(plan.tasks, key=lambda t: PriorityEngine.task_score(t), reverse=True)
    for t in sorted_tasks:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"{t.status_icon()} **{t.title}**  \n{t.difficulty} · due {t.deadline}"
                     + (f" · {t.goal}" if t.goal else ""))
            c2.write(f"{PriorityEngine.task_score(t)}" if not t.completed else "—")
            if not t.completed and c3.button("Complete", key=f"complete_{t.id}"):
                t.mark_complete()
                st.rerun()
