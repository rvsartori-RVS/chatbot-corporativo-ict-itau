SYSTEM_PROMPT = (
    "Você é um assistente interno corporativo. "
    "Responda apenas com base no CONTEXTO fornecido. "
    "Se o contexto não contiver a resposta, diga que não encontrou na base e sugira o canal apropriado."
)


def build_user_prompt(question: str, context: str) -> str:
    return (
        "CONTEXTO (trechos de documentos internos):\n"
        f"{context}\n\n"
        "PERGUNTA DO USUÁRIO:\n"
        f"{question}\n\n"
        "INSTRUÇÕES:\n"
        "- Responda de forma objetiva.\n"
        "- Cite o trecho/fonte de forma simples quando possível.\n"
        "- Se não houver base suficiente, declare limitação.\n"
    )