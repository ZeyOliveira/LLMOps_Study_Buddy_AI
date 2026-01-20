import os
import yaml
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from utils.logger import get_logger
from utils.custom_exception import AppException

class LLMClient:
    """
    LLM Provider Factory (Industrial Agnosticism).
    
    This class centralizes the creation of Chat objects, allowing the 
    QuestionGenerator to switch 'brains' via YAML configuration 
    without changing the generation logic.
    """

    def __init__(self, config_path: str = "config/llm.yaml"):
        self.logger = get_logger(self.__class__.__name__)
        self.config = self._load_config(config_path)
        self.provider = self.config.get("default_provider", "groq")
        self.llm = self._setup_llm()

    def _load_config(self, path: str) -> dict:
        """Loads definitions from the YAML configuration file."""
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as exc:
            self.logger.error(f"Critical failure while loading config file: {path}")
            raise AppException("Infrastructure Configuration Error", exc)

    def _setup_llm(self):
        """
        Instantiates the configured provider.
        Returns an object compatible with the LangChain interface (.invoke).
        """
        conf = self.config["providers"][self.provider]
        model_conf = conf["model"]
        
        self.logger.info(f"Initializing LLM Provider | provider: {self.provider} | model: {model_conf['name']}")

        if self.provider == "groq":
            return ChatGroq(
                model_name=model_conf["name"],
                temperature=model_conf["temperature"],
                max_tokens=model_conf["max_tokens"],
                api_key=os.getenv("GROQ_API_KEY")
            )
        elif self.provider == "openai":
            return ChatOpenAI(
                model_name=model_conf["name"],
                temperature=model_conf["temperature"],
                max_tokens=model_conf["max_tokens"],
                api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            self.logger.error(f"Unsupported provider requested: {self.provider}")
            raise AppException(f"Provider not supported by infrastructure: {self.provider}")

    def get_llm(self):
        """
        Exports the instantiated LLM object to be consumed by the QuestionGenerator.
        """
        return self.llm