import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from src.common.helpers import QuizManager, rerun
from src.generation.question_generator import QuestionGenerator
from utils.logger import get_logger

# Professional environment setup
logger = get_logger(__name__)

def main():
    st.set_page_config(
        page_title="Study Buddy AI | Industrial Edition", 
        page_icon="🎓", 
        layout="wide"
    )

    # Initialize Session State (Enterprise Pattern)
    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

    st.title("🎓 Study Buddy AI")
    st.markdown("---")

    # 1. Sidebar Configuration
    st.sidebar.header("🛠️ Quiz Configurations")
    
    topic = st.sidebar.text_input("Topic", placeholder="e.g., Quantum Physics, Python Programming")
    
    question_type = st.sidebar.selectbox(
        "Question Type",
        ["Multiple Choice", "Fill in the Blank"]
    )
    
    difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1
    )
    
    num_questions = st.sidebar.slider("Number of Questions", 1, 10, 3)

    # 2. Generation Logic
    if st.sidebar.button("Generate Quiz") and topic:
        with st.spinner(f"AI is crafting your {difficulty} quiz about {topic}..."):
            try:
                generator = QuestionGenerator()
                st.session_state.quiz_manager.generate_questions(
                    generator=generator,
                    topic=topic,
                    question_type=question_type,
                    difficulty=difficulty,
                    num_questions=num_questions
                )
                st.session_state.quiz_generated = True
                st.session_state.quiz_submitted = False
                logger.info(f"New quiz generated | Topic: {topic} | Qty: {num_questions}")
                rerun()
            except Exception as e:
                logger.error(f"Failed to initiate quiz generation: {str(e)}")
                st.error("We encountered an issue with the AI provider. Please try again.")

    # 3. Quiz Display and Interaction
    if st.session_state.quiz_generated and not st.session_state.quiz_submitted:
        st.subheader(f"📝 Quiz: {topic}")
        user_responses = []

        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_manager.questions):
                st.write(f"**Question {i+1}:** {q['question']}")
                
                if q['type'] == 'MCQ':
                    ans = st.radio(f"Select an option for Q{i+1}:", q['options'], key=f"q_{i}")
                else:
                    ans = st.text_input(f"Your answer for Q{i+1}:", key=f"q_{i}")
                
                user_responses.append(ans)
                st.markdown("---")

            if st.form_submit_button("Submit Answers"):
                st.session_state.quiz_manager.evaluate_quiz(user_responses)
                st.session_state.quiz_submitted = True
                logger.info("User submitted quiz for evaluation.")
                rerun()

    # 4. Results and Monitoring (Post-Submission)
    if st.session_state.quiz_submitted:
        st.subheader("📊 Your Performance")
        results = st.session_state.quiz_manager.results
        
        correct_count = sum(1 for r in results if r['is_correct'])
        score = (correct_count / len(results)) * 100
        
        col1, col2 = st.columns(2)
        col1.metric("Score", f"{score:.1f}%")
        col2.metric("Correct", f"{correct_count}/{len(results)}")

        for i, res in enumerate(results):
            with st.expander(f"Question {i+1} - {'✅ Correct' if res['is_correct'] else '❌ Incorrect'}"):
                st.write(f"**Question:** {res['question']}")
                st.write(f"**Your Answer:** {res['user_answer']}")
                st.write(f"**Correct Answer:** {res['correct_answer']}")
                st.info(f"**Explanation:** {res['explanation']}")

        # 5. DataOps: Export Results
        st.markdown("---")
        if st.button("💾 Export Results to CSV"):
            saved_path = st.session_state.quiz_manager.save_to_csv()
            if saved_path:
                with open(saved_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Dataset",
                        data=f,
                        file_name=os.path.basename(saved_path),
                        mime="text/csv"
                    )
                st.success(f"Results archived for monitoring in {saved_path}")

        if st.button("🔄 Take New Quiz"):
            st.session_state.quiz_generated = False
            st.session_state.quiz_submitted = False
            rerun()

if __name__ == "__main__":
    main()