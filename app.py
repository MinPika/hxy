import streamlit as st
import json
import os

# ------------------- PATHS -------------------
DATA_DIR = "data"
PROGRESS_PATH = os.path.join(DATA_DIR, "user_progress.json")

# ------------------- LOAD DATA -------------------
questions = []
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".json") and filename != "user_progress.json":
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            file_data = json.load(f)
            questions.extend(file_data)

if not questions:
    st.error("❌ No questions found in data/ folder")
    st.stop()

# Extract all unique topics
all_topics = sorted({q["topic"] for q in questions})

# ------------------- LOAD / INIT PROGRESS -------------------
if os.path.exists(PROGRESS_PATH):
    with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
        progress = json.load(f)
else:
    progress = {"important": [], "revision": []}

# ------------------- SESSION STATE -------------------
if "index" not in st.session_state:
    st.session_state.index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# ------------------- HELPER FUNCTIONS -------------------
def save_progress():
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

def next_question(filtered):
    if st.session_state.index < len(filtered) - 1:
        st.session_state.index += 1
    else:
        st.session_state.index = 0
    st.session_state.show_answer = False

def prev_question(filtered):
    if st.session_state.index > 0:
        st.session_state.index -= 1
    else:
        st.session_state.index = len(filtered) - 1
    st.session_state.show_answer = False

def toggle_answer():
    st.session_state.show_answer = not st.session_state.show_answer

def mark_important(qid):
    if qid not in progress["important"]:
        progress["important"].append(qid)
        save_progress()

def mark_revision(qid):
    if qid not in progress["revision"]:
        progress["revision"].append(qid)
        save_progress()

# ------------------- UI -------------------
st.set_page_config(page_title="DS Question Bank", layout="centered")

st.title("📘 DS Question Bank (Descriptive)")

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_topics = st.sidebar.multiselect(
    "Select Topics:", options=all_topics, default=all_topics
)

# Apply filter
if selected_topics:
    filtered_questions = [q for q in questions if q["topic"] in selected_topics]
else:
    filtered_questions = questions

if not filtered_questions:
    st.warning("⚠️ No questions found for the selected filters.")
    st.stop()

# Ensure current index stays in bounds
st.session_state.index = min(st.session_state.index, len(filtered_questions) - 1)

q = filtered_questions[st.session_state.index]

st.subheader(f"Q{q['id']}: {q['question']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.button("⬅️ Previous", on_click=prev_question, args=(filtered_questions,))
with col2:
    st.button("Show/Hide Answer", on_click=toggle_answer)
with col3:
    st.button("➡️ Next", on_click=next_question, args=(filtered_questions,))

if st.session_state.show_answer:
    st.markdown(
        f"""<div style='padding:10px; background:#f0f8ff; border-radius:10px;'>
        <b>Answer:</b><br>{q['answer']}
        </div>""",
        unsafe_allow_html=True
    )

st.markdown("---")
col4, col5 = st.columns(2)
with col4:
    if st.button("⭐ Mark as Important"):
        mark_important(q["id"])
        st.success("Marked as Important")
with col5:
    if st.button("📝 Mark for Revision"):
        mark_revision(q["id"])
        st.info("Marked for Revision")

# ------------------- Sidebar Navigation -------------------
st.sidebar.header("📑 Navigation")
st.sidebar.write(f"Question {st.session_state.index+1} of {len(filtered_questions)}")

if progress["important"]:
    st.sidebar.subheader("⭐ Important Questions")
    for qid in progress["important"]:
        st.sidebar.write(f"Q{qid}")

if progress["revision"]:
    st.sidebar.subheader("📝 Revision List")
    for qid in progress["revision"]:
        st.sidebar.write(f"Q{qid}")
