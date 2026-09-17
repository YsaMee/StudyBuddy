import streamlit as st


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

    all_subjects = app.data.subjects
    current_names = [s.name for s in u.subjects]
    chosen = st.multiselect(
        "Your subjects",
        options=[s.name for s in all_subjects],
        default=current_names,
    )
    u.study_goal = st.text_area("Study goals", value=u.study_goal)

    if st.button("Save changes ➜"):
        selected = [s for s in all_subjects if s.name in chosen]
        u.select_subjects(selected)
        st.success("Profile updated.")
        app.goto("dashboard")

    st.divider()
    st.markdown("#### 🏫 Find schoolmates")

    if not u.school:
        st.info("Add your school above to find classmates studying the same subjects.")
        return

    mates = app.data.schoolmates(u)
    if not mates:
        st.caption(f"No one else from **{u.school}** on StudyBuddy yet.")
        return

    for mate in mates:
        shared = app.data.shared_subjects(u, mate)
        with st.container(border=True):
            st.write(f"**{mate.full_name}** · {mate.school}")
            if shared:
                st.caption("Shares: " + ", ".join(s.name for s in shared))
            else:
                st.caption("No shared subjects yet")
