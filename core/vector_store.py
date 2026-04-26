"""
core/vector_store.py
─────────────────────
Builds and manages FAISS vector stores using HuggingFace embeddings.

Embedding model: sentence-transformers/all-MiniLM-L6-v2
  • Runs locally (no API key needed)
  • Fast and accurate for semantic search
  • 384-dim vectors
"""

from __future__ import annotations

import os
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever

EMBED_MODEL   = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RETRIEVER_K   = int(os.getenv("RETRIEVER_K", "4"))
FAISS_PERSIST = "faiss_index"

# ── Embeddings (cached at module level) ───────────────────────────────────────
_embeddings: Optional[HuggingFaceEmbeddings] = None

def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def build_vectorstore(docs: List[Document]) -> FAISS:
    """
    Embed a list of chunked Documents and store them in FAISS.
    Returns the FAISS vectorstore.
    """
    embeddings = _get_embeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore


def get_retriever(vectorstore: FAISS, k: int = RETRIEVER_K) -> VectorStoreRetriever:
    """Return an MMR-based retriever for diverse, relevant chunks."""
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": k * 3, "lambda_mult": 0.6},
    )


def save_vectorstore(vectorstore: FAISS, path: str = FAISS_PERSIST) -> None:
    vectorstore.save_local(path)


def load_vectorstore(path: str = FAISS_PERSIST) -> Optional[FAISS]:
    if not os.path.exists(path):
        return None
    embeddings = _get_embeddings()
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)