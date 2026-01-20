from langchain_core.prompts import PromptTemplate

# 1. Define as diretrizes de sistema para garantir consistência
SYSTEM_RULES = (
    "You are an expert Educational Content Creator.\n"
    "Your goal is to generate high-quality study materials.\n"
    "RULES:\n"
    "1. Respond ONLY in the same language as the requested {topic}.\n"
    "2. Provide detailed educational explanations.\n"
    "3. Ensure the JSON is perfectly valid and matches the schema requirements.\n"
)

# 2. Template de Múltipla Escolha (MCQ)
mcq_prompt_template = PromptTemplate(
    template=(
        SYSTEM_RULES +
        "\nGenerate a {difficulty} multiple-choice question about the topic: {topic}.\n\n"
        "FIELDS REQUIRED:\n"
        "- 'question': Clear and challenging enunciado.\n"
        "- 'options': List with EXACTLY 4 options.\n"
        # MUDANÇA AQUI: Reforço semântico para evitar apenas a letra
        "- 'correct_answer': The EXACT text content of the correct option. "
        "DO NOT return just a letter (like 'A' or 'B'), you MUST return the full string as it appears in the options list.\n"
        "- 'explanation': A teaching paragraph explaining why the answer is correct.\n"
        "- 'difficulty': Must be '{difficulty}'.\n\n"
        "Return ONLY the JSON object."
    ),
    input_variables=["topic", "difficulty"]
)

# 3. Template de Preenchimento de Lacuna
fill_blank_prompt_template = PromptTemplate(
    template=(
        SYSTEM_RULES +
        "\nGenerate a {difficulty} fill-in-the-blank question about the topic: {topic}.\n\n"
        "FIELDS REQUIRED:\n"
        "- 'question': A sentence where '___' represents the missing part.\n"
        "- 'answer': The precise word or phrase for the blank.\n"
        "- 'explanation': Why this answer is the most appropriate.\n\n"
        "Return ONLY the JSON object."
    ),
    input_variables=["topic", "difficulty"]
)