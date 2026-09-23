"""Journey step 5 & 7: Browse/search resources, upload a PDF, and get an
AI-generated summary of it (via ai_summary.py + pdf_utils.py)."""

import streamlit as st
from .. import ai_summary, pdf_utils
from ..models import Resource


def _upload_section(app):
    u = app.user
    st.markdown("#### 📤 Upload a PDF")

    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
    all_names = [s.name for s in app.data.subjects]
    my_names = [s.name for s in u.subjects]
    ordered_names = my_names + [n for n in all_names if n not in my_names]
    subject_name = st.selectbox("Subject for this file", ordered_names)

    if uploaded_file and st.button("Add to Resource Library"):
        subject = next(s for s in app.data.subjects if s.name == subject_name)
        u.add_subject(subject)  # so it shows up in their study plans too
        text = pdf_utils.extract_text(uploaded_file)
        resource = Resource(
            title=uploaded_file.name, subject=subject, kind="PDF",
            link="", blurb="Uploaded by you", content_text=text,
        )
        app.data.resources.append(resource)
        st.success(f"Added '{uploaded_file.name}' to the library.")
        if not pdf_utils.PDF_LIB_AVAILABLE:
            st.warning("`pypdf` isn't installed, so no text could be extracted "
                       "— the file was saved but can't be summarized yet.")
        st.rerun()


def render(app):
    st.title("🔎 Resource Library")
    st.caption("Curated materials matched to your subjects and current tasks.")
    u = app.user

    with st.expander("+ Upload a resource"):
        _upload_section(app)

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

            if r.content_text:
                if r.ai_summary:
                    st.info(f"**AI summary:** {r.ai_summary}")
                else:
                    if st.button("✨ Summarize with Gemini", key=f"summarize_{r.id}"):
                        with st.spinner("Summarizing..."):
                            summary = ai_summary.summarize_text(r.content_text)
                        r.set_summary(summary)
                        st.rerun()

    if u.saved_resources:
        st.markdown("#### 💾 Saved resources")
        for r in u.saved_resources:
            st.write(f"- {r}")
