import pandas as pd
from datetime import datetime
import os
import streamlit as st
from utils.logger import get_logger

logger = get_logger(__name__)

class QuizManager:
    """
    Manager de Sessão Industrial.
    Responsável por coordenar a geração, avaliação e persistência dos dados do quiz.
    """
    def __init__(self):
        self.questions = []
        self.results = []
        # Define um caminho de exportação seguro (padrão Linux/Container)
        self.export_path = "/tmp/quiz_results.csv"

    def generate_questions(self, generator, topic, question_type, difficulty, num_questions):
        """
        Orquestra o QuestionGenerator para criar a lista de questões.
        Este é o método exato que o seu app.py está tentando chamar.
        """
        self.questions = [] # Limpa o estado para um novo quiz
        
        for i in range(num_questions):
            try:
                if question_type == "Multiple Choice":
                    # Chama o método do seu QuestionGenerator
                    q = generator.generate_mcq(topic, difficulty)
                    q_data = q.dict() if hasattr(q, 'dict') else q
                    q_data['type'] = 'MCQ'
                else:
                    q = generator.generate_fill_blank(topic, difficulty)
                    q_data = q.dict() if hasattr(q, 'dict') else q
                    q_data['type'] = 'FIB'
                
                self.questions.append(q_data)
                logger.info(f"Questão {i+1} adicionada ao manager.")
                
            except Exception as e:
                logger.error(f"Erro ao processar questão {i+1}: {str(e)}")
                raise e

    def evaluate_quiz(self, user_responses):
        """
        Compara as respostas do usuário com o gabarito da IA.
        """
        self.results = []
        for i, q in enumerate(self.questions):
            user_ans = user_responses[i]
            # Lógica de correção (MCQ usa índice/texto, FIB usa texto direto)
            is_correct = str(user_ans).strip().lower() == str(q['correct_answer']).strip().lower()
            
            self.results.append({
                'question': q['question'],
                'user_answer': user_ans,
                'correct_answer': q['correct_answer'],
                'explanation': q.get('explanation', 'Sem explicação disponível.'),
                'is_correct': is_correct,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    def save_to_csv(self):
        """
        Persiste os resultados para monitoramento (DataOps).
        """
        if not self.results:
            return None
            
        try:
            df = pd.DataFrame(self.results)
            # Se o arquivo já existe, anexa (append), se não, cria novo
            if not os.path.isfile(self.export_path):
                df.to_csv(self.export_path, index=False)
            else:
                df.to_csv(self.export_path, mode='a', header=False, index=False)
                
            logger.info(f"Resultados exportados com sucesso para {self.export_path}")
            return self.export_path
        except Exception as e:
            logger.error(f"Falha na exportação DataOps: {str(e)}")
            return None

def rerun():
    """Helper para compatibilidade de versões do Streamlit."""
    st.rerun()