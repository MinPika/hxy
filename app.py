import streamlit as st
import json
import random
import os
from datetime import datetime

# --------------------------------------
# Load Questions
# --------------------------------------
@st.cache_data
def load_data():
    files = os.listdir("data")
    questions = []
    index = 0
    for file in files:
        with open(os.path.join("data", file), "r") as f:
            Q = json.load(f)
            topic = " ".join(file.split(".")[0].split("_"))
            for q in Q:
                q["id"] = index
                q["topic"] = topic
                questions.append(q)
                index += 1
    return questions

questions = load_data()

# --------------------------------------
# Sidebar Filters
# --------------------------------------
topics = sorted(set(q["topic"] for q in questions))
difficulties = sorted(set(q["difficulty"] for q in questions))

st.sidebar.title("⚙️ Quiz Settings")
selected_topic = st.sidebar.selectbox("Filter by Topic", ["All"] + topics)
selected_difficulty = st.sidebar.selectbox("Filter by Difficulty", ["All"] + difficulties)

if st.sidebar.button("🔄 Reset Filters"):
    st.session_state.shuffled_questions = None
    st.session_state.q_index = 0
    st.session_state.submitted = False
    st.session_state.selected_option = None
    st.session_state.score = 0
    st.session_state.attempted = 0
    st.session_state.quiz_ended = False
    st.rerun()

# Filter questions
filtered_questions = [
    q for q in questions
    if (selected_topic == "All" or q["topic"] == selected_topic)
    and (selected_difficulty == "All" or q["difficulty"] == selected_difficulty)
]

# --------------------------------------
# Session State Init
# --------------------------------------
if "shuffled_questions" not in st.session_state:
    st.session_state.shuffled_questions = filtered_questions.copy()
    random.shuffle(st.session_state.shuffled_questions)
elif st.session_state.shuffled_questions is None:
    st.session_state.shuffled_questions = filtered_questions.copy()
    random.shuffle(st.session_state.shuffled_questions)

for key, default in {
    "q_index": 0,
    "submitted": False,
    "selected_option": None,
    "score": 0,
    "attempted": 0,
    "quiz_ended": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------------------------
# Title + Intro
# --------------------------------------
st.markdown(
    """
    <div style="text-align:center; padding: 20px; background-color:#f0f2f6; border-radius:12px;">
        <h1 style="color:#4CAF50;">📊 Data Science Quiz</h1>
        <p style="font-size:18px;">Sharpen your skills in <b>Machine Learning</b>, <b>Statistics</b>, <b>Deep Learning</b>, and <b>Python</b>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# --------------------------------------
# Main Quiz Logic
# --------------------------------------
if not filtered_questions:
    st.info("No questions match your filters.")
elif st.session_state.q_index >= len(filtered_questions):
    st.success("🎉 You’ve completed all available questions.")
    st.info(f"🏁 Final Score: {st.session_state.score} / {st.session_state.attempted}")
elif st.session_state.quiz_ended:
    st.markdown("## 🧾 Quiz Summary")
    st.write(f"✅ **Score:** {st.session_state.score}")
    st.write(f"📊 **Questions Attempted:** {st.session_state.attempted}")
    st.write(f"⏭️ **Questions Skipped:** {st.session_state.q_index - st.session_state.attempted}")

    if st.button("🔄 Restart"):
        for key in ["shuffled_questions", "q_index", "submitted", "selected_option", "score", "attempted", "quiz_ended"]:
            st.session_state[key] = None if key == "shuffled_questions" else 0 if isinstance(st.session_state.get(key), int) else False
        st.rerun()
else:
    q = st.session_state.shuffled_questions[st.session_state.q_index]
    st.markdown(f"###### Topic: **{q['topic']}**  |  Difficulty: **{q['difficulty']}**")
    st.markdown(f"### {st.session_state.q_index + 1}. {q['question']}")

    options_map = {f"{k}. {v}": k for k, v in q["options"].items()}
    selected_display = st.radio(
        "Select an option:",
        list(options_map.keys()),
        key=f"radio_{q['id']}",
        label_visibility="collapsed",
    )
    st.session_state.selected_option = options_map[selected_display]

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("✅ Submit", use_container_width=True):
            if not st.session_state.submitted:
                st.session_state.submitted = True
                st.session_state.attempted += 1
                if st.session_state.selected_option == q["answer"]:
                    st.session_state.score += 1
                    st.success("🎉 Correct! " + q["explanation"])
                else:
                    correct_text = q["options"][q["answer"]]
                    st.error(
                        f"❌ Incorrect. Correct answer is **{q['answer']}. {correct_text}**\n\n💡 {q['explanation']}"
                    )

    with col2:
        if not st.session_state.submitted:
            if st.button("⏭️ Skip", use_container_width=True):
                st.session_state.q_index += 1
                st.rerun()
        else:
            if st.button("➡️ Next", use_container_width=True):
                st.session_state.q_index += 1
                st.session_state.submitted = False
                st.session_state.selected_option = None
                st.rerun()

    with col3:
        if st.button("🛑 End Quiz", use_container_width=True):
            st.session_state.quiz_ended = True
            st.rerun()

    # Show score only AFTER submission
    if st.session_state.submitted:
        st.markdown(
            f"<div style='text-align:center; font-size:18px; margin-top:15px;'>📈 Score: <b>{st.session_state.score}</b> / {st.session_state.attempted}</div>",
            unsafe_allow_html=True,
        )
