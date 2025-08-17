import streamlit as st
import json
import os

# ------------------- PATHS -------------------
DATA_DIR = "data"
PROGRESS_PATH = os.path.join(DATA_DIR, "user_progress.json")

st.set_page_config(page_title="DS Question Bank", page_icon="📘", layout="centered")
st.title("📘 DS Question Bank (Descriptive)")

# ------------------- LOAD ALL QUESTIONS -------------------
questions = []
topic_map = {}  # filename -> topic label

for filename in os.listdir(DATA_DIR):
    if filename.endswith(".json") and filename != "user_progress.json":
        path = os.path.join(DATA_DIR, filename)
        base_topic = os.path.splitext(filename)[0].replace("_", " ")
        topic_map[base_topic] = base_topic  # keep only top-level JSONs
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for q in data:
                    q["topic"] = base_topic  # force topic from filename
                questions.extend(data)
        except Exception as e:
            st.error(f"Failed to load {filename}: {e}")

if not questions:
    st.error("❌ No questions found in the data/ folder.")
    st.stop()

# ------------------- LOAD / INIT PROGRESS -------------------
if os.path.exists(PROGRESS_PATH):
    try:
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            progress = json.load(f)
    except Exception:
        progress = {"important": [], "revision": []}
else:
    progress = {"important": [], "revision": []}

def save_progress():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

# ------------------- MARK FUNCTIONS -------------------
def mark_important(question_text):
    if question_text not in progress["important"]:
        progress["important"].append(question_text)
        save_progress()

def mark_revision(question_text):
    if question_text not in progress["revision"]:
        progress["revision"].append(question_text)
        save_progress()

# ------------------- SESSION STATE -------------------
if "index" not in st.session_state:
    st.session_state.index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

def next_question(filtered):
    if not filtered: 
        return
    st.session_state.index = (st.session_state.index + 1) % len(filtered)
    st.session_state.show_answer = False

def prev_question(filtered):
    if not filtered:
        return
    st.session_state.index = (st.session_state.index - 1) % len(filtered)
    st.session_state.show_answer = False

def toggle_answer():
    st.session_state.show_answer = not st.session_state.show_answer


# ------------------- FILTERS -------------------
st.sidebar.header("🔍 Filters")

# Topic filter (only JSON names)
selected_topics = st.sidebar.multiselect(
    "Topics:",
    options=list(topic_map.keys()),
    default=list(topic_map.keys())
)

# Difficulty filter
difficulties = sorted({q.get("difficulty", "Unknown") for q in questions})
selected_difficulties = st.sidebar.multiselect(
    "Difficulty:",
    options=difficulties,
    default=difficulties
)

# Apply filters
filtered_questions = [
    q for q in questions 
    if q.get("topic") in selected_topics and q.get("difficulty", "Unknown") in selected_difficulties
]

if not filtered_questions:
    st.warning("⚠️ No questions match your selected filters.")
    st.stop()

# Keep index in range for current filtered list
st.session_state.index = min(st.session_state.index, len(filtered_questions) - 1)

# ------------------- CURRENT QUESTION -------------------
q = filtered_questions[st.session_state.index]
qid = q.get("id", st.session_state.index + 1)  # fallback if no id

st.markdown(f"##### Topic: **{q.get('topic')}** | Difficulty: **{q.get('difficulty','Unknown')}**")
st.subheader(f"Q{qid}: {q.get('question', '—')}")

# Controls
c1, c2, c3 = st.columns(3)
with c1:
    st.button("⬅️ Previous", on_click=prev_question, args=(filtered_questions,))
with c2:
    st.button("Show/Hide Answer", on_click=toggle_answer)
with c3:
    st.button("➡️ Next", on_click=next_question, args=(filtered_questions,))

# ------------------- ANSWER PANEL (EXPLANATION FIRST) -------------------
if st.session_state.show_answer:
    explanation = q.get("explanation")
    if explanation and isinstance(explanation, str) and explanation.strip():
        answer_text = explanation
    else:
        ans_key = q.get("answer")
        opts = q.get("options", {})
        answer_text = opts.get(ans_key) if isinstance(opts, dict) else None
        if not answer_text:
            answer_text = str(ans_key) if ans_key else "No explanation available."

    st.markdown(
        f"""<div style="padding:12px;background:#eef6ff;border-radius:12px;">
        <b>Answer:</b><br>{answer_text}
        </div>""",
        unsafe_allow_html=True
    )

st.markdown("---")

m1, m2 = st.columns(2)
with m1:
    if st.button("⭐ Mark as Important"):
        mark_important(q.get("question", ""))
        st.success("Marked as Important")
with m2:
    if st.button("📝 Mark for Revision"):
        mark_revision(q.get("question", ""))
        st.info("Marked for Revision")

# ------------------- SIDEBAR NAV -------------------
st.sidebar.header("📑 Navigation")
st.sidebar.write(f"Question {st.session_state.index + 1} / {len(filtered_questions)}")

if progress["important"]:
    st.sidebar.subheader("⭐ Important")
    for q_text in progress["important"]:
        st.sidebar.caption(f"• {q_text}")

if progress["revision"]:
    st.sidebar.subheader("📝 Revision")
    for q_text in progress["revision"]:
        st.sidebar.caption(f"• {q_text}")