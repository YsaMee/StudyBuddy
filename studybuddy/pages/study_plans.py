import streamlit as st
from datetime import date, timedelta
from ..models import Task
from ..priority import PriorityEngine


def render(app):
    st.title("Plans & Tasks")
    st.caption("Turn big goals into small, doable steps.")
    user = app.user
    all_subjects = app.data.subjects
    if not all_subjects:
        st.info("No subjects are available yet.")
        return

    subject_name = st.selectbox("Subject", [subject.name for subject in all_subjects])
    subject = next(subject for subject in all_subjects if subject.name == subject_name)
    plan = user.plan_for(subject)
    if plan is None:
        user.select_subjects(user.subjects + [subject])
        plan = user.plan_for(subject)

    with st.form("add_task_form"):
        title = st.text_input("Task")
        deadline = st.date_input("Deadline", value=date.today() + timedelta(days=7))
        difficulty = st.selectbox("Difficulty", Task.DIFFICULTIES, index=1)
        goal = st.text_input("Study goal (optional)")
        if st.form_submit_button("Add Task") and title:
            plan.add_task(Task(title, deadline, difficulty, goal))
            st.success(f"Added task '{title}'.")

    st.subheader(f"{subject.name} — {int(plan.progress() * 100)}% complete")
    st.progress(plan.progress())

    st.markdown("**Task list** · sorted by smart priority")
    sorted_tasks = sorted(plan.tasks, key=PriorityEngine.task_score, reverse=True)
    for task in sorted_tasks:
        with st.container(border=True):
            column1, column2, column3 = st.columns([3, 1, 1])
            column1.write(
                f"{task.status_icon()} **{task.title}**  \n"
                f"{task.difficulty} · due {task.deadline}"
                + (f" · {task.goal}" if task.goal else "")
            )
            column2.write(str(PriorityEngine.task_score(task)) if not task.completed else "-")
            if not task.completed and column3.button("Complete", key=f"complete_{task.id}"):
                task.mark_complete()
                st.rerun()
