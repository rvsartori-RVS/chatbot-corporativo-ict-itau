import os
from dataclasses import dataclass
from typing import List, Tuple

import chromadb
from chromadb.config import Settings

from .embeddings import ChromaEmbeddingFunction


@dataclass
class RetrievedChunk:
    text: str
    source: str
    score: float  # quanto maior, melhor (aproximação)


def _chunk_text(raw: str, max_chars: int = 450) -> List[str]:
    """
    Quebra um texto em "blocos" simples por parágrafos,
    limitando tamanho para facilitar recuperação.
    """
    parts = [p.strip() for p in raw.split("\n\n") if p.strip()]
    chunks: List[str] = []

    for p in parts:
        if len(p) <= max_chars:
            chunks.append(p)
        else:
            # fatiamento simples
            for i in range(0, len(p), max_chars):
                chunks.append(p[i : i + max_chars].strip())

    return [c for c in chunks if c]


class SimpleRAG:
    """
    RAG simplificado:
    - Indexa um arquivo local (data/base_exemplo.txt)
    - Armazena em Chroma persistente (./.chroma)
    - Recupera top_k trechos por similaridade
    """

    def __init__(
        self,
        collection_name: str = "ict_itau_kb",
        persist_dir: str = ".chroma",
        embedding_dim: int = 256,
    ):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embedding_fn = ChromaEmbeddingFunction(dim=embedding_dim)

        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def index_file(self, file_path: str, source_name: str = "base_exemplo") -> int:
        """
        Indexa o arquivo caso ainda não esteja indexado.
        Retorna quantidade de chunks adicionados.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read().strip()

        chunks = _chunk_text(raw)
        if not chunks:
            return 0

        # Evita duplicar indexação: checa se já existem IDs com o prefixo
        existing = self.collection.get(include=["ids"])
        existing_ids = set(existing.get("ids", []))

        ids = []
        docs = []
        metas = []

        for i, chunk in enumerate(chunks):
            cid = f"{source_name}_{i}"
            if cid in existing_ids:
                continue
            ids.append(cid)
            docs.append(chunk)
            metas.append({"source": source_name})

        if ids:
            self.collection.add(ids=ids, documents=docs, metadatas=metas)

        return len(ids)

    def retrieve(self, query: str, top_k: int = 3) -> List[RetrievedChunk]:
        res = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        docs = res.get("documents", [[]])[0] or []
        metas = res.get("metadatas", [[]])[0] or []
        dists = res.get("distances", [[]])[0] or []

        out: List[RetrievedChunk] = []
        for doc, meta, dist in zip(docs, metas, dists):
            # em cosine distance: menor é melhor
            score = 1.0 - float(dist) if dist is not None else 0.0
            out.append(
                RetrievedChunk(
                    text=str(doc),
                    source=str(meta.get("source", "kb")),
                    score=score,
                )
            )

        return out