import os
import math
import hashlib
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


DEFAULT_DIM = 256  # dimensão pequena e suficiente p/ demo


def _hash_to_vector(text: str, dim: int = DEFAULT_DIM) -> List[float]:
    """
    Embedding local (determinístico) baseado em hashing.
    Não depende de internet nem de API key.
    Serve para busca semântica "boa o bastante" em um MVP.
    """
    if not text:
        return [0.0] * dim

    vec = [0.0] * dim
    tokens = [t.strip().lower() for t in text.split() if t.strip()]

    for tok in tokens:
        h = hashlib.sha256(tok.encode("utf-8")).digest()
        # usa bytes para distribuir energia no vetor
        for i in range(0, len(h), 2):
            idx = (h[i] << 8) + h[i + 1]
            pos = idx % dim
            val = ((h[i] / 255.0) - 0.5)  # [-0.5, 0.5]
            vec[pos] += val

    # normalização L2
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def get_embedding(text: str, dim: int = DEFAULT_DIM) -> List[float]:
    """
    Se houver OPENAI_API_KEY: tenta usar embeddings da OpenAI.
    Caso contrário: usa embedding local determinístico.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _hash_to_vector(text, dim=dim)

    # OpenAI embeddings (opcional). Se falhar, cai para local.
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # modelo de embedding pode ser ajustado por env var
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        resp = client.embeddings.create(model=model, input=text)
        return resp.data[0].embedding  # type: ignore
    except Exception:
        return _hash_to_vector(text, dim=dim)


class ChromaEmbeddingFunction:
    """
    Interface compatível com ChromaDB.
    Chroma chamará esta classe para gerar embeddings.
    """

    def __init__(self, dim: int = DEFAULT_DIM):
        self.dim = dim

    def __call__(self, texts: List[str]) -> List[List[float]]:
        return [get_embedding(t, dim=self.dim) for t in texts]