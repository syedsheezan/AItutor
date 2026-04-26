"""
core/chains.py
───────────────
Two chains built with LangChain 0.3 LCEL:

1. build_rag_chain()   → Retrieval-Augmented Generation using uploaded docs
2. build_agent_chain() → Direct LLM chain with optional DuckDuckGo + Math tools

The chains now support streaming and provide status updates for a better UI experience.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List, Tuple, Iterator

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.chains import LLMMathChain

from .llm_setup import get_llm, get_system_prompt

# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM = get_system_prompt()


def _format_history(history: List[Tuple[str, str]]) -> str:
    """Convert list of (human, ai) tuples to a readable string."""
    if not history:
        return ""
    lines = []
    for h, a in history[-4:]:          # last 4 turns for context
        lines.append(f"Student: {h}")
        lines.append(f"Tutor: {a}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 1. RAG CHAIN  (document Q&A)
# ─────────────────────────────────────────────────────────────────────────────

RAG_SYSTEM = f"""{_SYSTEM}

You have been given excerpts from the student's study document as context.
Answer the student's question based on the provided context AND the previous conversation history.
If the answer is not in the context, but you can answer it from your general knowledge or the conversation history,
say "I couldn't find that in your document, but here's what I know:" and then provide the answer.

Always stay in character as a helpful tutor.

Context:
{{context}}
"""


def build_rag_chain(retriever):
    """
    RAG chain that returns chunks for streaming.
    """
    llm = get_llm()

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", RAG_SYSTEM),
        ("human",  "Previous chat:\n{chat_history_str}\n\nStudent question: {input}"),
    ])

    # Stuff-documents chain (summarises retrieved docs into context)
    # Using StrOutputParser to ensure we get strings back
    combine_docs_chain = create_stuff_documents_chain(llm, qa_prompt) | StrOutputParser()

    # LCEL pipeline
    rag_chain = (
        RunnableMap({
            "context":         RunnableLambda(lambda x: x["input"]) | retriever,
            "input":           RunnableLambda(lambda x: x["input"]),
            "chat_history_str": RunnableLambda(lambda x: _format_history(x.get("chat_history", []))),
        })
        | RunnableMap({
            "answer":  combine_docs_chain,
            "context": RunnableLambda(lambda x: x["context"]),
        })
    )

    return rag_chain


# ─────────────────────────────────────────────────────────────────────────────
# 2. DIRECT CHAIN  (search + LLM)
# ─────────────────────────────────────────────────────────────────────────────

_DIRECT_PROMPT_TEMPLATE = """Today's date: {date}

You are an AI Tutor with web search capabilities.
{search_context}
Use the search results above to answer the student's question if they are relevant.
If no results are found, explain that you tried searching but couldn't find a definitive answer.

Previous conversation:
{chat_history_str}

Student question: {question}
Tutor answer:"""

# Keywords that suggest a web search will help
_SEARCH_TRIGGERS = [
    "syllabus", "exam", "board", "result", "news", "current", "latest",
    "2024", "2025", "2026", "today", "price", "who is", "when did",
    "schedule", "date", "admit card", "notification", "mp board",
    "cbse", "icse", "ncert", "class 10", "class 12", "10th", "12th",
    "look up", "search", "website", "who won", "match", "score", "game",
    "who is", "what is", "tell me about", "history", "recent", "latest",
    "biography", "details", "information", "news", "update", "result",
]

# Keywords that suggest a math calculation
_MATH_TRIGGERS = [
    "calculate", "compute", "evaluate", "solve", "what is",
    "square root", "integral", "derivative", "%", "percent",
]


def _needs_search(question: str) -> bool:
    q = question.lower()
    return any(t in q for t in _SEARCH_TRIGGERS)


def _needs_math(question: str) -> bool:
    q = question.lower()
    has_operator = any(op in question for op in ["+", "-", "*", "/", "^"])
    has_trigger   = any(t in q for t in _MATH_TRIGGERS)
    return has_operator or has_trigger


def _deep_search(question: str) -> str:
    """Unified search that tries DuckDuckGo and Wikipedia with multiple queries."""
    import wikipedia as wp
    search_data = ""
    
    # 1. Broaden keywords for better search
    q_lower = question.lower()
    event_query = None
    if "misfits" in q_lower:
        event_query = "Misfits Boxing X Series 2026 results"
    elif "ufc" in q_lower:
        event_query = "UFC 2026 results"
    
    queries = [question.lower().replace("tell me", "").strip()]
    if event_query:
        queries.append(event_query)
    
    # 2. DuckDuckGo strategy
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        ddg = DuckDuckGoSearchRun()
        for dq in queries:
            res = ddg.run(dq)
            if "No good DuckDuckGo Search Result was found" not in res:
                search_data += f"--- Web Search ({dq}) ---\n{res}\n\n"
            if len(search_data) > 1000: break
    except Exception: pass

    # 3. Wikipedia Strategy (More aggressive)
    try:
        # Search for page titles
        search_titles = wp.search(question, results=3)
        if event_query:
            search_titles.extend(wp.search(event_query, results=2))
            
        for title in set(search_titles):
            try:
                page = wp.page(title, auto_suggest=False)
                search_data += f"--- Wikipedia: {title} ---\n{page.summary}\n"
                if "boxing" in q_lower or "result" in q_lower:
                    search_data += page.content[:1500] + "\n"
            except Exception: continue
            if len(search_data) > 5000: break
    except Exception: pass

    return search_data if search_data else "I searched extensively but found no results. The event might be very recent."


def _run_search(question: str) -> str:
    return _deep_search(question)


def _run_wikipedia(question: str) -> str:
    return _deep_search(question)


def _run_math(question: str, llm) -> str | None:
    try:
        chain = LLMMathChain.from_llm(llm=llm, verbose=False)
        return chain.run(question)
    except Exception:
        return None


def _run_wikipedia(question: str) -> str:
    try:
        wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        results = wiki.run(question)
        return f"--- Wikipedia Results ---\n{results}\n--- End of Wikipedia Results ---\n\n"
    except Exception:
        return ""


class DirectChain:
    """
    Enhanced chain that supports status updates and streaming.
    """

    def __init__(self, llm, history_str: str):
        self.llm = llm
        self.history_str = history_str

    def stream(self, inputs: dict) -> Iterator[dict]:
        question = inputs.get("input", "")

        # 1. Math check
        if _needs_math(question):
            yield {"status": "🧮 Calculating math..."}
            math_ans = _run_math(question, self.llm)
            if math_ans:
                yield {"chunk": math_ans}
                return

        # 2. Web search check
        search_ctx = ""
        if _needs_search(question):
            yield {"status": "🌐 Searching the web for latest info..."}
            search_ctx = _run_search(question)
            
            # If search_ctx is still very short or empty, try a broader term
            if len(search_ctx) < 50:
                 yield {"status": "📚 Checking Wikipedia for additional context..."}
                 search_ctx += _run_wikipedia(question)

        # 3. Final generation
        now = _dt.datetime.now().strftime("%A, %d %B %Y")
        prompt = _DIRECT_PROMPT_TEMPLATE.format(
            date=now,
            search_context=search_ctx,
            chat_history_str=self.history_str,
            question=question,
        )

        yield {"status": "🤔 Thinking and drafting answer..."}
        # Using StrOutputParser or just string chunks from ChatModel
        for chunk in self.llm.stream(prompt):
            content = chunk.content if hasattr(chunk, "content") else str(chunk)
            yield {"chunk": content}

    def invoke(self, inputs: dict) -> dict:
        """Compatibility method: just collects the stream."""
        full_text = ""
        for event in self.stream(inputs):
            if "chunk" in event:
                full_text += event["chunk"]
        return {"output": full_text}


def build_agent_chain(chat_history: List[Tuple[str, str]]) -> DirectChain:
    llm         = get_llm()
    history_str = _format_history(chat_history)
    return DirectChain(llm=llm, history_str=history_str)