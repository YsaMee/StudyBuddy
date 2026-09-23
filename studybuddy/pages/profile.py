"""Journey step 3: Set up a profile, change password, and find schoolmates
/ program mates. Subjects are NOT chosen here — a user's subjects are
whichever ones they've started a study plan for (see study_plans.py)."""

import streamlit as st
from .. import accounts, programs


def render(app):
    st.title("🧑‍🎓 My Profile")
    st.caption("Personalize StudyBuddy around the way you learn.")
    u = app.user

    u.full_name = st.text_input("Full name", value=u.full_name)
    years = ["Year 1", "Year 2", "Year 3", "Year 4"]
    u.academic_year = st.selectbox(
        "Academic year", years,
        index=years.index(u.academic_year) if u.academic_year in years else 0,
    )
    st.text_input("Email", value=u.email, disabled=True)
    u.school = st.text_input("School", value=u.school, placeholder="e.g. State University")

    categories = list(programs.PROGRAM_CATALOG.keys())
    current_category = programs.category_for(u.program) or categories[0]
    category = st.selectbox("Program category", categories, index=categories.index(current_category))
    options_in_category = programs.PROGRAM_CATALOG[category]
    default_index = options_in_category.index(u.program) if u.program in options_in_category else 0
    u.program = st.selectbox("Program", options_in_category, index=default_index)

    u.study_goal = st.text_area("Study goals", value=u.study_goal)

    if st.button("Save changes ➜"):
        if app.data.persist_accounts():
            st.success("Profile updated.")
        else:
            st.warning("Profile updated for this session, but couldn't be saved to disk "
                       "— it won't survive an app restart. Check the terminal/log for why.")
        app.goto("dashboard")

    st.divider()
    st.markdown("#### 🔑 Change password")
    with st.form("change_password_form"):
        current_pw = st.text_input("Current password", type="password")
        new_pw = st.text_input("New password", type="password")
        confirm_pw = st.text_input("Confirm new password", type="password")
        if st.form_submit_button("Update password"):
            if not u.check_password(current_pw):
                st.error("Current password is incorrect.")
            elif new_pw != confirm_pw:
                st.error("New passwords don't match.")
            else:
                issues = accounts.password_issues(new_pw)
                if issues:
                    st.error("Password needs " + ", ".join(issues) + ".")
                else:
                    u.password = new_pw
                    if app.data.persist_accounts():
                        st.success("Password updated.")
                    else:
                        st.warning("Password changed for this session, but couldn't be saved to disk "
                                   "— it'll revert on restart. Check the terminal/log for why.")

    st.divider()
    st.markdown("#### 🏫 Find schoolmates")
    if not u.school:
        st.info("Add your school above to find classmates from it.")
    else:
        mates = app.data.schoolmates(u)
        if not mates:
            st.caption(f"No one else from **{u.school}** on StudyBuddy yet.")
        for mate in mates:
            shared = app.data.shared_subjects(u, mate)
            with st.container(border=True):
                st.write(f"**{mate.full_name}** · {mate.school}")
                st.caption("Shares: " + ", ".join(s.name for s in shared) if shared else "No shared subjects yet")

    st.divider()
    st.markdown("#### 🎓 Find program mates")
    mates = app.data.programmates(u)
    if not mates:
        st.caption(f"No one else in **{u.program}** on StudyBuddy yet.")
    for mate in mates:
        shared = app.data.shared_subjects(u, mate)
        with st.container(border=True):
            st.write(f"**{mate.full_name}** · {mate.school or 'School not set'}")
            st.caption("Shares: " + ", ".join(s.name for s in shared) if shared else "No shared subjects yet")
