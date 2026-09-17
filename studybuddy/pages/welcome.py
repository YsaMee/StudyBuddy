import streamlit as st


def render(app):
    st.title("📚 Welcome to StudyBuddy")
    st.write(
        "Organize your study schedule, discover resources, and "
        "collaborate with classmates — all in one place."
    )
    if st.button("Get Started ➜"):
        app.goto("auth")