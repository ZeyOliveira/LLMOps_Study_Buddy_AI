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
    Responsável por orquestrar a geração, avaliação e exportação de dados (MLOps).
    """
    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.results = []

    # ... (métodos generate_questions e evaluate_quiz permanecem iguais)

    def save_to_csv(self, filename_prefix="quiz_results"):
        """Saves results to a CSV file for future monitoring and fine-tuning."""
        if not self.results:
            st.warning("No results to save.")
            return None
        
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{filename_prefix}_{timestamp}.csv"

        # TRUQUE DE MESTRE: Alteramos o local de salvamento para /tmp
        # Isso evita o PermissionError sem precisar reconstruir a imagem Docker.
        output_dir = '/tmp/monitoring/results' 
        
        try:
            # Criamos o diretório no /tmp, onde o myuser tem permissão total
            os.makedirs(output_dir, exist_ok=True)
            full_path = os.path.join(output_dir, unique_filename)
            
            df.to_csv(full_path, index=False)
            logger.info(f"Quiz results exported successfully to {full_path}")
            return full_path
        except Exception as e:
            # Em produção, se o /tmp falhar, registramos o erro crítico
            logger.error(f"Failed to save CSV in {output_dir}: {str(e)}")
            st.error(f"Error saving results: {str(e)}")
            return None