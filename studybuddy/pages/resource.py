import streamlit as st


def render(app):
    st.title("🔎 Resource Library")
    st.caption("Curated materials matched to your subjects and current tasks.")
    u = app.user
    query = st.text_input("Search by topic, subject or keyword")
    candidates = app.data.resources_for_subjects(u.subjects) or app.data.resources
    if query:
        candidates = [r for r in candidates if query.lower() in r.title.lower()]

    for r in candidates:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{r.title}**  \n{r.kind.upper()} · {r.subject.name}  \n{r.blurb}")
            already = r in u.saved_resources
            if c2.button("Saved ✓" if already else "Save", key=f"save_{r.id}", disabled=already):
                u.save_resource(r)
                st.rerun()

    if u.saved_resources:
        st.markdown("#### 💾 Saved resources")
        for r in u.saved_resources:
            st.write(f"- {r}")
