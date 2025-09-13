import sqlite3
import streamlit as st
from pathlib import Path

BASE_PATH = Path(__file__).resolve(strict=True).parent
DB_PATH = BASE_PATH / "../shared/db/programming_languages.db"


@st.cache_data
def load_concepts():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, description FROM concepts")
        return cur.fetchall()


@st.cache_data
def load_languages():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM languages")
        return cur.fetchall()


@st.cache_data
def load_examples(concept_id, language_ids=None):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        if language_ids:
            placeholders = ",".join("?" for _ in language_ids)
            query = f"""
                SELECT l.name, e.code_snippet, e.explanation
                FROM examples e
                JOIN languages l ON e.language_id = l.id
                WHERE e.concept_id = ? AND e.language_id IN ({placeholders})
            """
            cur.execute(query, (concept_id, *language_ids))
        else:
            cur.execute("""
                    SELECT l.name, e.code_snippet, e.explanation
                    FROM examples e
                    JOIN languages l ON e.language_id = l.id
                    WHERE e.concept_id = ?
                """, (concept_id,))
        return cur.fetchall()


st.set_page_config(
    page_title="Programming Concept Explorer",
    layout="wide"  # This enables full-width content area
)
st.title("📚 Programming Concept Explorer")
concepts = load_concepts()
concept_options = {name: cid for cid, name, _ in concepts}
selected_concept_name = st.selectbox(
    "Choose a concept", list(concept_options.keys()))
concept_id = concept_options[selected_concept_name]

languages = load_languages()
selected_language_ids = []
with st.expander("Filter by language"):
    for lang_id, lang_name in languages:
        if st.checkbox(lang_name, key=f"lang_{lang_id}"):
            selected_language_ids.append(lang_id)

examples = load_examples(
    concept_id, selected_language_ids if selected_language_ids else None)

st.subheader(f"Examples for: {selected_concept_name}")

if not examples:
    st.info("No examples found for the selected filters.")
else:
    cols = st.columns(3)

    for idx, (lang, code, expl) in enumerate(examples):
        with cols[idx % 3]:
            st.markdown(f"#### {lang}")
            st.code(code, language=lang.lower())
            if expl:
                st.caption(expl)
