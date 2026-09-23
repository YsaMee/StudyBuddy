"""
StudyBuddyApp — the application controller. Owns session state, shared
data, and routes to the right page module for the current step of the
User Journey.
"""

import streamlit as st
from typing import Optional
from .data import StudyBuddyData
from .models import User
from .pages import welcome, profile, dashboard, study_plans, resources, sessions


class StudyBuddyApp:

    PAGES = {
        "welcome": welcome,
        "profile": profile,
        "dashboard": dashboard,
        "study_plans": study_plans,
        "resources": resources,
        "sessions": sessions,
    }

    def __init__(self):
        if "data" not in st.session_state:
            st.session_state.data = StudyBuddyData()
        if "page" not in st.session_state:
            st.session_state.page = "welcome"
        if "current_user" not in st.session_state:
            st.session_state.current_user = None

        self.data: StudyBuddyData = st.session_state.data

    # -- navigation helpers -----------------------------------------
    def goto(self, page: str):
        st.session_state.page = page
        st.rerun()

    @property
    def user(self) -> Optional[User]:
        return st.session_state.current_user

    def logout(self):
        st.session_state.current_user = None
        self.goto("welcome")

    def sidebar_nav(self):
        with st.sidebar:
            st.markdown("## 📚 **Study**Buddy")
            if self.user:
                st.caption(f"Logged in as **{self.user.username}**")
                st.markdown("**WORKSPACE**")
                labels = {
                    "dashboard": "🗂️ Dashboard",
                    "study_plans": "✅ Study plans",
                    "resources": "📄 Resources",
                    "sessions": "🎯 Study sessions",
                }
                for page, label in labels.items():
                    if st.button(label, use_container_width=True, key=f"nav_{page}"):
                        self.goto(page)
                st.markdown("**ACCOUNT**")
                if st.button("👤 My profile", use_container_width=True, key="nav_profile"):
                    self.goto("profile")
                st.divider()
                if st.button("🚪 Log out", use_container_width=True):
                    self.logout()
            else:
                st.caption("Not logged in yet.")

    # -- main dispatcher -----------------------------------------------
    def run(self):
        st.set_page_config(page_title="StudyBuddy", page_icon="📚", layout="centered")
        self.sidebar_nav()

        page = st.session_state.page
        if page != "welcome" and not self.user:
            st.warning("Please log in first.")
            page = "welcome"
            st.session_state.page = page

        self.PAGES[page].render(self)
