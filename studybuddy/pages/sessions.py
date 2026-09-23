"""Journey step 6: Create or join a study session with other students.

Sessions carry a plain-text location and a public chat that any
participant can post to.
"""

import streamlit as st
from datetime import date, timedelta
from ..models import StudySession


def render(app):
    st.title("🤝 Study Sessions")
    st.caption("You learn better with a little support.")
    u = app.user

    with st.expander("+ Create session"):
        all_names = [s.name for s in app.data.subjects]
        my_names = [s.name for s in u.subjects]
        ordered_names = my_names + [n for n in all_names if n not in my_names]

        with st.form("create_session_form"):
            subject_name = st.selectbox("Subject", ordered_names)
            when = st.date_input("Session date", value=date.today() + timedelta(days=2))
            location_name = st.text_input("Location", placeholder="e.g. Library, Room 214 or Online (Zoom)")
            note = st.text_input("Note for participants", "")
            if st.form_submit_button("Create Session"):
                subject = next(s for s in app.data.subjects if s.name == subject_name)
                u.add_subject(subject)  # so it shows up in their study plans too
                session = StudySession(subject, u, when, note, location_name=location_name)
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
            if s.location_name:
                st.caption(f"📍 {s.location_name}")
            if s.note:
                st.write(f"“{s.note}”")

            if u not in s.participants:
                if st.button("Request to join", key=f"join_{s.id}"):
                    s.join(u)
                    st.rerun()
            else:
                st.write("✅ Joined")

            with st.expander(f"💬 Chat ({len(s.messages)})"):
                if u not in s.participants:
                    st.caption("Join this session to post in the chat.")
                for msg in s.messages[-20:]:
                    st.write(f"**{msg.sender.username}** · {msg.sent_at.strftime('%H:%M')}  \n{msg.text}")
                if u in s.participants:
                    new_msg = st.text_input("Message", key=f"chat_input_{s.id}")
                    if st.button("Send", key=f"chat_send_{s.id}") and new_msg.strip():
                        s.post_message(u, new_msg)
                        st.rerun()
