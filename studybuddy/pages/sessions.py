import streamlit as st
from datetime import date, timedelta
from ..data import StudySession


def render(app):
    st.title("🤝 Study Sessions")
    st.caption("You learn better with a little support.")
    u = app.user

    with st.expander("+ Create session"):
        if not u.subjects:
            st.info("Add subjects in **My profile** first.")
        else:
            with st.form("create_session_form"):
                subject_name = st.selectbox("Subject", [s.name for s in u.subjects])
                when = st.date_input("Session date", value=date.today() + timedelta(days=2))
                note = st.text_input("Note for participants", "")
                if st.form_submit_button("Create Session"):
                    subject = next(s for s in u.subjects if s.name == subject_name)
                    session = StudySession(subject, u, when, note)
                    app.data.sessions.append(session)
                    st.success("Session created!")
                    st.rerun()

    st.subheader("Sessions that match your goals")
    matches = app.data.sessions_for_subjects(u.subjects)
    matches.sort(key=lambda s: s.match_score(u.subjects), reverse=True)
    for s in matches:
        with st.container(border=True):
            st.write(f"**{s.subject.name}** — {s.match_score(u.subjects)}% match")
            st.caption(f"Hosted by {s.host.username} · {s.when} · {len(s.participants)} joined")
            if s.note:
                st.write(f"“{s.note}”")
            if u not in s.participants:
                if st.button("Request to join", key=f"join_{s.id}"):
                    s.join(u)
                    st.rerun()
            else:
                st.write("✅ Joined")
