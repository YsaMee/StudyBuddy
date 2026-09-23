"""Journey step 8: View study progress and recommended resources/sessions.

Also hosts the Smart Priority feature (PriorityEngine) that recommends
which subject/task to focus on next.
"""

import streamlit as st
from ..priority import PriorityEngine


def render(app):
    u = app.user
    st.title(f"Good morning, {u.full_name.split()[0] if u.full_name else u.username} 👋")
    st.subheader("Ready to make progress?")

    if st.button("+ New study plan"):
        app.goto("study_plans")

    recs = PriorityEngine.subject_recommendations(u.study_plans)

    if recs:
        top = recs[0]
        st.markdown("#### ✨ Smart Priority")
        with st.container(border=True):
            st.markdown(f"**Study this first: {top['top_task'].title}** ({top['subject'].name})")
            st.write(top["reason"])
            c1, c2 = st.columns([1, 1])
            if c1.button("Start task ➜", key="start_top_task"):
                app.goto("study_plans")
            c2.write(f"Priority score **{top['score']}/100**")
    else:
        st.info("Add subjects and tasks to get a personalized study priority.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks completed", f"{u.completed_tasks()} / {u.total_tasks()}")
    open_count = sum(len(p.open_tasks()) for p in u.study_plans)
    col2.metric("Open tasks", open_count)
    upcoming = [t for p in u.study_plans for t in p.open_tasks() if 0 <= t.days_left() <= 7]
    col3.metric("Deadlines this week", len(upcoming))

    if recs:
        st.markdown("#### 🎯 Your focus queue")
        st.caption("Prioritized by deadline, difficulty and progress")
        for row in recs[:5]:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{row['top_task'].title}**  \n{row['subject'].name} · {row['reason']}")
                c2.write(f"Score **{row['score']}**")
                if c3.button("Complete", key=f"dash_complete_{row['top_task'].id}"):
                    row["top_task"].mark_complete()
                    st.rerun()

        st.markdown("#### 📌 Recommended for you")
        top_subject = recs[0]["subject"]
        for r in app.data.resources_for_subjects([top_subject])[:2]:
            st.write(f"- **{r.title}** ({r.kind}) — {r.blurb}")

    if u.study_plans:
        st.markdown("#### 📊 Your subject progress")
        st.caption("Subjects are ranked by how urgently they need attention.")
        for row in recs:
            plan = row["plan"]
            st.write(f"{plan.subject.name} — {int(plan.progress()*100)}%  ·  *{row['reason']}*")
            st.progress(plan.progress())
        done_subjects = [p for p in u.study_plans if not p.open_tasks() and p.tasks]
        for plan in done_subjects:
            st.write(f"{plan.subject.name} — 100% ✅ All caught up")
            st.progress(1.0)
