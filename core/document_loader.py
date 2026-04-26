"""
core/document_loader.py
────────────────────────
Loads uploaded PDF / TXT files into LangChain Documents.
Uses:
  • PyPDFLoader   → for .pdf files
  • TextLoader    → for .txt files
  • RecursiveCharacterTextSplitter → chunks with overlap
"""

from __future__ import annotations

import os
import tempfile
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ── Splitter config ────────────────────────────────────────────────────────────
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 120

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
    length_function=len,
)


def load_uploaded_file(uploaded_file) -> Optional[List[Document]]:
    """
    Accept a Streamlit UploadedFile object.
    Returns a list of chunked LangChain Documents, or None on failure.
    """
    suffix = f".{uploaded_file.name.rsplit('.',1)[-1].lower()}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyMuPDFLoader(tmp_path)
        elif suffix == ".txt":
            loader = TextLoader(tmp_path, encoding="utf-8")
        else:
            return None

        raw_docs = loader.load()
        # Tag source metadata
        for doc in raw_docs:
            doc.metadata["source"] = uploaded_file.name

        chunks = _splitter.split_documents(raw_docs)
        return chunks

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"[document_loader] Error loading file: {err_msg}")
        # Write to a file so I can easily read it
        with open("error_log.txt", "w") as f:
            f.write(err_msg)
        return None
    finally:
        os.unlink(tmp_path)


def load_raw_text(text: str, source_name: str = "paste") -> List[Document]:
    """Utility: chunk a raw string (for future use)."""
    doc = Document(page_content=text, metadata={"source": source_name})
    return _splitter.split_documents([doc])