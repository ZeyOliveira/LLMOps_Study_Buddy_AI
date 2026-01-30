import os
import streamlit as st
import pandas as pd
from datetime import datetime
from src.generation.question_generator import QuestionGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

def rerun():
    """Triggers a rerun in Streamlit session state."""
    st.session_state['rerun_trigger'] = not st.session_state.get('rerun_trigger', False)

class QuizManager:
    """
    Enterprise-grade Quiz Manager.
    
    Responsible for orchestrating question generation, tracking user answers,
    evaluating performance, and exporting data for monitoring (LLMOps).
    """
    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.results = []

    def generate_questions(self, generator: QuestionGenerator, topic: str, 
                           question_type: str, difficulty: str, num_questions: int):
        """Generates a list of questions and resets the quiz state."""
        self.questions = []
        self.user_answers = []
        self.results = []

        try:
            for i in range(num_questions):
                logger.info(f"Generating question {i+1}/{num_questions} | Type: {question_type}")
                
                if question_type == "Multiple Choice":
                    
                    question = generator.generate_mcq(topic, difficulty)
                    self.questions.append({
                        'type': 'MCQ',
                        'question': question.question,
                        'options': question.options,
                        'correct_answer': question.correct_answer,
                        'explanation': question.explanation 
                    })
                else:
                    question = generator.generate_fill_blank(topic, difficulty)
                    self.questions.append({
                        'type': 'Fill in the blank',
                        'question': question.question,
                        'correct_answer': question.answer,
                        'explanation': question.explanation 
                    })
        except Exception as e:
            logger.error(f"Critical error during quiz generation sequence: {str(e)}")
            st.error("Technical failure during question generation. Check logs for details.")

    def evaluate_quiz(self, user_inputs):
        """Compares user answers with ground truth and calculates results."""
        self.results = []
        for i, q in enumerate(self.questions):
            user_ans = user_inputs[i]
            
            result_dict = {
                'question': q['question'],
                'user_answer': user_ans,
                'correct_answer': q["correct_answer"],
                'explanation': q.get('explanation', "N/A"),
                'is_correct': False
            }

            if q['type'] == 'MCQ':
                result_dict['is_correct'] = (user_ans == q["correct_answer"])
            else:
                # Normalization for string comparison (lowercase and strip)
                result_dict['is_correct'] = (user_ans.strip().lower() == q['correct_answer'].strip().lower())

            self.results.append(result_dict)
        
        logger.info(f"Quiz evaluated. Total questions: {len(self.results)}")

    def save_to_csv(self, filename_prefix="quiz_results"):
        """Saves results to a CSV file for future monitoring and fine-tuning."""
        if not self.results:
            st.warning("No results to save.")
            return None
        
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{filename_prefix}_{timestamp}.csv"

        # Ensure directory exists (DataOps)
        output_dir = 'monitoring/results' 
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(output_dir, unique_filename)

        try:
            df.to_csv(full_path, index=False)
            logger.info(f"Quiz results exported successfully to {full_path}")
            return full_path
        except Exception as e:
            logger.error(f"Failed to save CSV: {str(e)}")
            st.error("Error saving results.")
            return None