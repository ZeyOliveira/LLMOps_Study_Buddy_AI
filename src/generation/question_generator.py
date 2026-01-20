from langchain_core.output_parsers import PydanticOutputParser
from src.models.schema import MCQQuestion, FillBlankQuestion
from src.prompts.templates import mcq_prompt_template, fill_blank_prompt_template
from src.llm.llm_client import LLMClient
from utils.logger import get_logger
from utils.custom_exception import AppException

class QuestionGenerator:
    """
    Industrial-grade Question Generator Service.
    
    This class orchestrates the interaction between LLM providers, 
    prompt templates, and Pydantic schemas to produce validated 
    educational content with high reliability.
    """

    def __init__(self, max_retries: int = 3):
        # We use our agnostic LLMClient factory
        self.llm_client = LLMClient()
        self.llm = self.llm_client.get_llm()
        self.logger = get_logger(self.__class__.__name__)
        self.max_retries = max_retries

    def _generate_with_retry(self, prompt_template, parser, topic: str, difficulty: str):
        """
        Internal logic to handle LLM non-determinism with retry mechanisms.
        """
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{self.max_retries} | Generating {topic} ({difficulty})")
                
                # Formatting prompt and calling the LLM
                formatted_prompt = prompt_template.format(topic=topic, difficulty=difficulty)
                response = self.llm.invoke(formatted_prompt)
                
                # Parsing string content into a Pydantic Object
                return parser.parse(response.content)
            
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Generation failed after {self.max_retries} attempts for topic: {topic}")
                    raise AppException("LLM Generation Final Failure", e)

    def generate_mcq(self, topic: str, difficulty: str = 'Medium') -> MCQQuestion:
        """
        Generates a validated Multiple Choice Question.
        """
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)
            question = self._generate_with_retry(mcq_prompt_template, parser, topic, difficulty)
            
            # Semantic validation is handled internally by the MCQQuestion schema
            self.logger.info("Successfully generated MCQ Question")
            return question
        
        except Exception as e:
            raise AppException(f"Failed to deliver valid MCQ for topic {topic}", e)

    def generate_fill_blank(self, topic: str, difficulty: str = 'Medium') -> FillBlankQuestion:
        """
        Generates a validated Fill in the Blanks Question.
        """
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)
            question = self._generate_with_retry(fill_blank_prompt_template, parser, topic, difficulty)
            
            self.logger.info("Successfully generated Fill-Blank Question")
            return question
        
        except Exception as e:
            raise AppException(f"Failed to deliver valid Fill-Blank for topic {topic}", e)