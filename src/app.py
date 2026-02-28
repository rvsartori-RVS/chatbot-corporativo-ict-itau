import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from .rag import SimpleRAG
from .prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()

# ========================
# Configuração de Logging
# ========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("chatbot")

app = FastAPI(
    title="Chatbot Corporativo - ICT Itaú",
    description="Protótipo de chatbot interno com arquitetura RAG simplificada.",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] | None = None
    mode: str


# Inicializa RAG
RAG = SimpleRAG(collection_name="ict_itau_kb", persist_dir=".chroma", embedding_dim=256)
BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "base_exemplo.txt")
BASE_PATH = os.path.abspath(BASE_PATH)

try:
    indexed = RAG.index_file(BASE_PATH, source_name="base_exemplo")
    logger.info(f"Base indexada com {indexed} novos chunks.")
except Exception as e:
    logger.error(f"Erro ao indexar base: {e}")


def _local_answer(question: str, retrieved_texts: list[str]) -> str:
    if not retrieved_texts:
        return (
            "Não encontrei referência suficiente na base documental. "
            "Sugestão: encaminhar ao canal oficial responsável."
        )
    best = retrieved_texts[0].strip()
    return f"Com base na base documental, segue a orientação:\n\n{best}"


def _llm_answer(question: str, context: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não configurada")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    user_prompt = build_user_prompt(question=question, context=context)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content or ""


@app.get("/")
def health_check():
    return {"status": "running", "service": "chatbot-corporativo"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        logger.warning("Pergunta vazia recebida.")
        return ChatResponse(
            answer="Pergunta vazia. Envie um texto com sua dúvida.",
            sources=[],
            mode="validation_error",
        )

    logger.info(f"Pergunta recebida: {question}")

    retrieved = RAG.retrieve(question, top_k=3)
    context = "\n\n".join([f"- ({r.source}) {r.text}" for r in retrieved])
    sources = sorted(list({r.source for r in retrieved}))

    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        try:
            answer = _llm_answer(question=question, context=context)
            logger.info("Resposta gerada via LLM.")
            return ChatResponse(answer=answer, sources=sources, mode="llm_rag")
        except Exception as e:
            logger.error(f"Erro no LLM: {e}. Caindo para modo local.")

    answer = _local_answer(question=question, retrieved_texts=[r.text for r in retrieved])
    logger.info("Resposta gerada via RAG local.")
    return ChatResponse(answer=answer, sources=sources, mode="local_rag")