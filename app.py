import streamlit as st
import json
import os

# ------------------- FILE PATHS -------------------
DATA_DIR = "data"
STATE_DIR = "state"
os.makedirs(STATE_DIR, exist_ok=True)

TOPIC_FILES = {
    "Python": "Python.json",
    "Machine Learning": "Machine_Learning.json",
    "Deep Learning": "Deep_Learning.json",
    "Statistics": "Statistics.json",
    "Special": "Special.json"  # NEW
}

IMPORTANT_FILE = os.path.join(STATE_DIR, "important.json")
REVISION_FILE = os.path.join(STATE_DIR, "revision.json")

# ------------------- HELPERS -------------------
def load_data():
    questions = []
    for topic, filename in TOPIC_FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for q in data:
                    if topic == "Special":
                        # Special.json format
                        questions.append({
                            "id": f"special-{len(questions)+1}",
                            "question": q["question"],
                            "answer": q["answer"],
                            "explanation": q["answer"],  # fallback
                            "topic": topic,
                            "difficulty": "N/A"
                        })
                    else:
                        # Standard format
                        questions.append({
                            "id": q["id"],
                            "question": q["question"],
                            "answer": q["explanation"],  # use explanation as descriptive answer
                            "explanation": q["explanation"],
                            "topic": topic,
                            "difficulty": q.get("difficulty", "N/A")
                        })
    return questions

def load_state(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_state(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f)

# ------------------- LOAD DATA -------------------
all_questions = load_data()

# ------------------- SESSION STATE -------------------
if "index" not in st.session_state:
    st.session_state.index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# Persistent states
if "important" not in st.session_state:
    st.session_state.important = load_state(IMPORTANT_FILE)
if "revision" not in st.session_state:
    st.session_state.revision = load_state(REVISION_FILE)

# ------------------- SIDEBAR FILTERS -------------------
st.sidebar.title("🔍 Filters")

topics = st.sidebar.multiselect(
    "Select Topics:",
    options=list(TOPIC_FILES.keys()),
    default=list(TOPIC_FILES.keys())
)

difficulties = st.sidebar.multiselect(
    "Select Difficulty:",
    options=["Easy", "Medium", "Hard"],
    default=["Easy", "Medium", "Hard"]
)

# ------------------- APPLY FILTERS -------------------
filtered_questions = [
    q for q in all_questions
    if q["topic"] in topics and (q["topic"] == "Special" or q["difficulty"] in difficulties)
]

if not filtered_questions:
    st.warning("No questions match the selected filters.")
    st.stop()

# Keep index in range
if st.session_state.index >= len(filtered_questions):
    st.session_state.index = 0

current_q = filtered_questions[st.session_state.index]

# ------------------- DISPLAY QUESTION -------------------
st.markdown(f"### ❓ Question {st.session_state.index+1}/{len(filtered_questions)}")
st.write(current_q["question"])
st.caption(f"**Topic:** {current_q['topic']} | **Difficulty:** {current_q['difficulty']}")

# Show Answer
if st.button("Show Answer"):
    st.session_state.show_answer = not st.session_state.show_answer

if st.session_state.show_answer:
    st.markdown("**✅ Answer:**")
    st.write(current_q["answer"])

# ------------------- ACTION BUTTONS -------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Previous") and st.session_state.index > 0:
        st.session_state.index -= 1
        st.session_state.show_answer = False

with col2:
    if st.button("Next") and st.session_state.index < len(filtered_questions)-1:
        st.session_state.index += 1
        st.session_state.show_answer = False

with col3:
    if current_q["id"] in st.session_state.important:
        if st.button("⭐ Unmark Important"):
            st.session_state.important.remove(current_q["id"])
            save_state(IMPORTANT_FILE, st.session_state.important)
    else:
        if st.button("⭐ Mark Important"):
            st.session_state.important.append(current_q["id"])
            save_state(IMPORTANT_FILE, st.session_state.important)

with col4:
    if current_q["id"] in st.session_state.revision:
        if st.button("📝 Unmark Revision"):
            st.session_state.revision.remove(current_q["id"])
            save_state(REVISION_FILE, st.session_state.revision)
    else:
        if st.button("📝 Mark Revision"):
            st.session_state.revision.append(current_q["id"])
            save_state(REVISION_FILE, st.session_state.revision)

# ------------------- VIEW MARKED -------------------
st.sidebar.subheader("⭐ Marked Important")
for qid in st.session_state.important:
    st.sidebar.write(f"- {qid}")

st.sidebar.subheader("📝 Marked for Revision")
for qid in st.session_state.revision:
    st.sidebar.write(f"- {qid}")
