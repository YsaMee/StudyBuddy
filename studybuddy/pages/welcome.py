"""Journey steps 1 & 2 combined: landing page with register/login right on
it, so there's no extra click between opening the app and signing in."""

import streamlit as st
from .. import accounts


def render(app):
    st.title("📚 Welcome to StudyBuddy")
    st.write(
        "Organize your study schedule, discover resources, and "
        "collaborate with classmates — all in one place."
    )
    st.divider()

    tab_login, tab_register = st.tabs(["Log In", "Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In"):
            user = app.data.find_user(email)
            if user and user.check_password(password):
                st.session_state.current_user = user
                app.data.seed_demo_classmates()
                app.data.seed_demo_session(user)
                app.goto("dashboard")
            else:
                st.error("Invalid email or password.")

    with tab_register:
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Choose a password", type="password", key="reg_pass")
        st.caption("Password needs 8+ characters, one number, and one uppercase letter.")

        if st.button("Create Account"):
            errors = []
            if not accounts.is_valid_email(new_email):
                errors.append("Enter a valid email address (e.g. name@school.edu).")
            pw_issues = accounts.password_issues(new_password)
            if pw_issues:
                errors.append("Password needs " + ", ".join(pw_issues) + ".")
            if app.data.find_user(new_email):
                errors.append("An account with that email already exists.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                user = app.data.register(new_email, new_password)
                st.session_state.current_user = user
                if not app.data.persist_accounts():
                    st.warning(
                        "Account created, but it couldn't be saved to disk — "
                        "it'll only last for this session. Check the app's "
                        "terminal/log output for the reason (likely a "
                        "read-only or permissions issue where the app is running)."
                    )
                app.data.seed_demo_classmates()
                app.goto("profile")
