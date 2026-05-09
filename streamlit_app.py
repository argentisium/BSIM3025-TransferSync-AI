import streamlit as st
from streamlit_calendar import calendar
import requests
import random
import datetime

# ====================== CONFIG ======================
st.set_page_config(page_title="TransferSync AI", page_icon="🧠", layout="wide")

st.title("🧠 TransferSync AI")
st.caption("Your personal time-management coach for HK senior year entry students")

DIFY_API_URL = "https://api.dify.ai/v1/workflows/run"
DIFY_API_KEY = st.secrets["DIFY_API_KEY"]

# ====================== SESSION STATE ======================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "events" not in st.session_state:
    st.session_state.events = []
if "learning_style" not in st.session_state:
    st.session_state.learning_style = None
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = None

# ====================== TOP TABS ======================
tab_quiz, tab_learn = st.tabs([
    "📝 Take Learning Style Quiz", 
    "📚 Learn the 4 Learning Styles"
])

# ====================== QUIZ TAB ======================
with tab_quiz:
    st.subheader("📝 Quick Learning Style Check")
    st.caption("Answer 12 questions to get your learning style (optional)")

    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "quiz_results" not in st.session_state:
        st.session_state.quiz_results = None

    # 1. Start button
    if not st.session_state.quiz_started and st.session_state.quiz_results is None:
        if st.button("🚀 Start 12-Question Quiz", type="primary", use_container_width=True):
            all_questions = [
                {"id": 1,  "text": "I realize that it is not clear to me what I have to remember and what I do not have to remember.", "style": "undirected"},
                {"id": 2,  "text": "I doubt whether this is the right subject area for me.", "style": "undirected"},
                {"id": 3,  "text": "I notice that it is difficult for me to determine whether I have mastered the subject matter sufficiently.", "style": "undirected"},
                {"id": 4,  "text": "I experience the introductions, objectives, instructions, assignments and test items given by the teacher as indispensable guidelines for my studies.", "style": "reproduction"},
                {"id": 5,  "text": "The main goal I pursue in my studies is to pass exams.", "style": "reproduction"},
                {"id": 6,  "text": "I prefer a type of instruction in which I am told exactly what I need to know for an exam.", "style": "reproduction"},
                {"id": 7,  "text": "I try to relate new subject matter to knowledge I already have about the topic concerned.", "style": "meaning"},
                {"id": 8,  "text": "When I have a choice, I opt for courses that suit my personal interests.", "style": "meaning"},
                {"id": 9,  "text": "To me, learning means trying to approach a problem from many different angles, including aspects that were previously unknown to me.", "style": "meaning"},
                {"id": 10, "text": "I pay particular attention to those parts of a course that have practical utility.", "style": "application"},
                {"id": 11, "text": "When I have a choice, I opt for courses that seem useful to me for my present or future profession.", "style": "application"},
                {"id": 12, "text": "To me, learning is providing myself with information that I can use immediately or in the longer term.", "style": "application"},
            ]
            random.shuffle(all_questions)
            st.session_state.shuffled_questions = all_questions
            st.session_state.quiz_answers = {}
            st.session_state.current_index = 0
            st.session_state.quiz_started = True
            st.rerun()

    # 2. Show results after submission
    elif st.session_state.quiz_results is not None:
        result = st.session_state.quiz_results
        dominant = result["dominant"]
        
        st.success(f"**Your dominant learning style: {dominant}**")
        
        # ← NEW: Short description in bullet points
        st.info("**What this means for you:**")
        descriptions = {
            "Undirected": [
                "• You often feel unsure about what or how to study",
                "• You can feel lost or overwhelmed with study tasks",
                "• You benefit greatly from clear structure and guidance"
            ],
            "Reproduction-directed": [
                "• You prefer clear instructions and well-defined goals",
                "• You focus on memorizing and reproducing knowledge for exams",
                "• You work best when you know exactly what is expected"
            ],
            "Meaning-directed": [
                "• You like to deeply understand the material",
                "• You connect new ideas to what you already know",
                "• You study because of personal interest and curiosity"
            ],
            "Application-directed": [
                "• You want to apply what you learn to real life or your future career",
                "• You focus on the practical usefulness of the material",
                "• You learn best when you see real-world relevance"
            ]
        }
        
        for bullet in descriptions.get(dominant, ["• No description available"]):
            st.write(bullet)
        
        # ← NEW MESSAGE
        st.info(f"🎯 Your AI Coach will now tailor its advice and suggestions to your **{dominant}** learning style!")
        
        st.write("### Your scores:")
        for style, score in result["scores"].items():
            st.write(f"- **{style}**: {score:.2f} / 5")
        
        if st.button("Take Quiz Again"):
            st.session_state.quiz_results = None
            st.rerun()

    # 3. Quiz in progress
    else:
        q = st.session_state.shuffled_questions[st.session_state.current_index]
        progress = f"Question {st.session_state.current_index + 1} of 12"
        st.write(f"**{progress}**")
        st.write(q["text"])

        st.write("**How much does this statement apply to you?**")

        # 5 Rating buttons
        cols = st.columns(5)
        current_rating = st.session_state.quiz_answers.get(q["id"])

        for rating in range(1, 6):
            with cols[rating-1]:
                label = f"**{rating}**"
                if current_rating == rating:
                    label = f"**{rating}**"
                if st.button(label,
                             key=f"rate_{q['id']}_{rating}",
                             type="primary" if current_rating == rating else "secondary",
                             use_container_width=True):
                    st.session_state.quiz_answers[q["id"]] = rating
                    st.rerun()

        # Prevent skipping
        answered = q["id"] in st.session_state.quiz_answers
        # Navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.session_state.current_index > 0:
                if st.button("← Previous", use_container_width=True):
                    st.session_state.current_index -= 1
                    st.rerun()

        with col2:
            if st.session_state.current_index < 11:
                # Only allow Next if current question is answered
                if answered:
                    if st.button("Next →", use_container_width=True):
                        st.session_state.current_index += 1
                        st.rerun()
                else:
                    st.button("Next →", disabled=True, use_container_width=True)
            else:
                # Last question - only allow Submit if ALL questions answered
                all_answered = len(st.session_state.quiz_answers) == 12
                if all_answered:
                    if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                        answers = st.session_state.quiz_answers
                        undirected   = (answers.get(1,0) + answers.get(2,0) + answers.get(3,0)) / 3
                        reproduction = (answers.get(4,0) + answers.get(5,0) + answers.get(6,0)) / 3
                        meaning      = (answers.get(7,0) + answers.get(8,0) + answers.get(9,0)) / 3
                        application  = (answers.get(10,0) + answers.get(11,0) + answers.get(12,0)) / 3

                        scores = {
                            "Undirected": undirected,
                            "Reproduction-directed": reproduction,
                            "Meaning-directed": meaning,
                            "Application-directed": application
                        }
                        dominant = max(scores, key=scores.get)

                        st.session_state.quiz_results = {"dominant": dominant, "scores": scores}
                        st.session_state.learning_style = dominant
                        st.session_state.quiz_started = False
                        st.rerun()
                else:
                    st.button("✅ Submit Quiz", disabled=True, use_container_width=True)

        if st.button("Cancel Quiz"):
            st.session_state.quiz_started = False
            st.rerun()

# ====================== LEARN STYLES TAB ======================
with tab_learn:
    st.subheader("📚 Vermunt (1996)’s 4 Learning Styles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🟡 Undirected**")
        st.write("• Feel unsure about what or how to study")
        st.write("• Often feel lost or overwhelmed")
        st.write("• Benefit greatly from clear structure and guidance")
        
        st.markdown("**🔴 Reproduction-directed**")
        st.write("• Prefer clear instructions and well-defined goals")
        st.write("• Focus on memorizing and reproducing knowledge for exams")
        st.write("• Work best when you know exactly what is expected")
    
    with col2:
        st.markdown("**🟢 Meaning-directed**")
        st.write("• Want to deeply understand the material")
        st.write("• Connect new ideas to what you already know")
        st.write("• Study because of personal interest and curiosity")
        
        st.markdown("**🔵 Application-directed**")
        st.write("• Want to apply what you learn to real life or future career")
        st.write("• Focus on the practical usefulness of the material")
        st.write("• Learn best when you see real-world relevance")

    st.markdown("---")
    st.subheader("How the Quiz Calculates Your Results")
    st.markdown("""
    The quiz is based on **Vermunt (1994)’s Inventory of Learning Styles (ILS)**.

    - You rate **12 statements** from 1 to 5.
    - The statements are divided into 4 groups of 3.
    - We calculate the **average** for each group.
    - The group with the **highest average** becomes your dominant learning style.

    This gives you a quick, research-based snapshot of your preferred way of learning.
    """)
        
    st.info("**Tip:** Take the quiz in the first tab to discover *your* dominant style!")

# ====================== MAIN LAYOUT (side-by-side) ======================
st.markdown("---")

col_ai, col_cal = st.columns([3, 2])   # 3:2 ratio — AI Coach gets more space

# ====================== LEFT COLUMN: AI COACH ======================
with col_ai:
    st.subheader("💬 Chat with your AI Coach")

    # Quick start buttons
    st.write("**Quick start suggestions** (click to send)")
    cols = st.columns(3)
    with cols[0]:
        if st.button("😟 I feel lost and overwhelmed", use_container_width=True):
            prompt = "I feel lost and overwhelmed"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()
    with cols[1]:
        if st.button("📚 I have too many assignments", use_container_width=True):
            prompt = "I have too many assignments to handle"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()
    with cols[2]:
        if st.button("🔥 I want to study more effectively", use_container_width=True):
            prompt = "I want to study more effectively"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # === CLEAN AI RESPONSE (handles latest Dify 'text' wrapper) ===
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        prompt = st.session_state.messages[-1]["content"]
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                headers = {
                    "Authorization": f"Bearer {DIFY_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "inputs": {
                        "query": prompt,
                        "learning_style": st.session_state.learning_style or ""
                    },
                    "response_mode": "blocking",
                    "user": "streamlit_user"
                }
                try:
                    resp = requests.post(DIFY_API_URL, json=payload, headers=headers, timeout=30)
                    resp.raise_for_status()
                    response_json = resp.json()
                    data = response_json.get("data", {})
                    outputs = data.get("outputs", {})

                    # === NEW ROBUST EXTRACTION ===
                    reply_text = ""

                    if isinstance(outputs, dict):
                        # New format you're seeing now
                        if "text" in outputs and outputs["text"]:
                            reply_text = outputs["text"]
                        
                        # Previous format (structured_output)
                        elif "structured_output" in outputs:
                            structured = outputs["structured_output"]
                            if isinstance(structured, dict) and "reply" in structured:
                                reply_text = structured["reply"]
                            else:
                                reply_text = str(structured)
                        
                        # Other fallbacks
                        elif "reply" in outputs:
                            reply_text = outputs["reply"]

                    # Final safety net
                    reply_text = str(reply_text).strip()
                    if reply_text in ["{}", "", "None", "null"]:
                        reply_text = "Got it! I've noted that down."

                    st.write(reply_text)
                    st.session_state.messages.append({"role": "assistant", "content": reply_text})

                except Exception as e:
                    st.error(f"Connection error: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't process that right now."})
                    
    # Normal chat input
    if prompt := st.chat_input("Describe your plans, stress, or ask for schedule help..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# ====================== RIGHT COLUMN: CALENDAR ======================
with col_cal:
    st.subheader("📅 Your Calendar")
    st.write("Add your first calendar event!")
    
    st.caption(f"📊 Events currently stored: {len(st.session_state.events)}")
    
    # === MANUAL ADD EVENT FORM ===
    with st.expander("➕ Add Event Manually", expanded=False):
        with st.form("add_event_form"):
            title = st.text_input("Event Title *", placeholder="Assignment Sprint", key="manual_title")
            if not title:
                st.warning("Please enter an event title")
            col_date, col_time = st.columns(2)
            with col_date:
                date = st.date_input("Date", value=datetime.date.today())
            with col_time:
                time = st.time_input("Time", value=datetime.time(15, 0))
            
            duration = st.number_input("Duration (hours)", min_value=0.25, value=1.5, step=0.25)
            description = st.text_area("Description (optional)", height=80)
            
            submitted = st.form_submit_button("Add to Calendar")
            if submitted and title:
                start_str = f"{date.strftime('%Y-%m-%d')} {time.strftime('%H:%M')}"
                new_event = {
                    "title": title,
                    "start": start_str,
                    "duration_hours": float(duration),
                    "description": description or ""
                }
                st.session_state.events.append(new_event)
                st.success("✅ Event added!")
                st.rerun()
    
    calendar_options = {
        "initialView": "timeGridWeek",
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "timeGridWeek,dayGridMonth"}
    }
    
    # Safe event cleaning for display
    calendar_events = []
    for i, e in enumerate(st.session_state.events):
        if isinstance(e, dict) and e.get("title") and e.get("start"):
            calendar_events.append({
                "id": str(i),
                "title": str(e.get("title")),
                "start": str(e.get("start")),
                "allDay": False
            })
    
    try:
        calendar(calendar_events, options=calendar_options, key="calendar_main")
    except Exception as calendar_error:
        st.error(f"Calendar render error: {calendar_error}")
    
    # Current events list with delete buttons
    if st.session_state.events:
        st.write("**Current Events**")
        for i, event in enumerate(st.session_state.events):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{event.get('title')}** — {event.get('start')} ({event.get('duration_hours')}h)")
            with col2:
                if st.button("🗑️", key=f"del_{i}"):
                    del st.session_state.events[i]
                    st.rerun()

# Footer
st.caption("Powered by Dify + Vermunt's ILS • Web interface generated with Grok")
st.caption("Vermunt, J. D. H. M. (1994). Inventory of Learning Styles (ILS) [Database record]. APA PsycTests. https://doi.org/10.1037/t14424-000")
st.caption("Vermunt, J. D. (1996). Metacognitive, Cognitive and Affective Aspects of Learning Styles and Strategies: A Phenomenographic Analysis. Higher Education, 31(1), 25–50. https://doi.org/10.1007/bf00129106")