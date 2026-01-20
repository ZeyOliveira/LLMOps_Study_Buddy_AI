from typing import List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class MCQQuestion(BaseModel):
    """
    Modelo Industrial para Questões de Múltipla Escolha (MCQ).
    """
    question: str = Field(..., min_length=10, description="O enunciado da pergunta")
    options: List[str] = Field(..., min_length=4, max_length=4, description="Lista obrigatória de 4 opções")
    correct_answer: str = Field(..., description="A resposta correta (deve estar entre as opções)")
    explanation: str = Field(..., description="Explicação detalhada da resposta para fins pedagógicos")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field("Medium", description="Nível de dificuldade da questão")

    @field_validator('question', mode='before')
    @classmethod
    def clean_question(cls, v):
        # Trata casos onde o LLM envia objetos em vez de strings.
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v)

    @model_validator(mode='after')
    def validate_answer_in_options(self) -> 'MCQQuestion':
        # Validação Semântica: Garante integridade entre resposta e opções
        if self.correct_answer not in self.options:
            raise ValueError(f"A resposta correta '{self.correct_answer}' deve estar presente na lista de opções.")
        return self


class FillBlankQuestion(BaseModel):
    """
    Modelo Industrial para Questões de Preenchimento de Lacuna.
    """
    question: str = Field(..., description="Enunciado contendo '___' para a lacuna")
    answer: str = Field(..., description="A palavra ou frase correta para a lacuna")
    explanation: str = Field(..., description="Por que esta resposta completa a frase corretamente")

    @field_validator('question')
    @classmethod
    def check_blank_exists(cls, v):
        if "___" not in v:
            raise ValueError("O enunciado deve conter '___' para representar a lacuna.")
        return v