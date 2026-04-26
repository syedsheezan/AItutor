"""
core/llm_setup.py
─────────────────
Initialises the HuggingFace LLM via the modern InferenceClient
with Inference Providers (huggingface_hub >= 1.x).

Uses chat_completion (conversational) task. 
Implemented as a BaseChatModel for better compatibility with LangChain 0.3 chains.
"""

from __future__ import annotations

import os
import functools
from typing import Any, List, Optional, Iterator

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ChatMessage, AIMessageChunk
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun

load_dotenv()

# ── env vars ──────────────────────────────────────────────────────────────────
HF_TOKEN       = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
PRIMARY_MODEL  = os.getenv("PRIMARY_MODEL",  "Qwen/Qwen2.5-72B-Instruct")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "Qwen/Qwen2.5-7B-Instruct")

# System prompt injected into every call
SYSTEM_PROMPT = """You are an enthusiastic, warm, and patient AI Tutor for school students.
Your job is to explain concepts clearly, use examples and analogies appropriate for kids,
encourage curiosity, and always be supportive. When solving math or science problems,
show step-by-step reasoning. Use simple language unless the student asks for more depth.
You have access to web search results and math tools when needed — use them to provide 
accurate and up-to-date information! Never give up on a student."""


def _convert_message_to_dict(message: BaseMessage) -> dict:
    if isinstance(message, ChatMessage):
        return {"role": message.role, "content": message.content}
    elif isinstance(message, HumanMessage):
        return {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        return {"role": "assistant", "content": message.content}
    elif isinstance(message, SystemMessage):
        return {"role": "system", "content": message.content}
    else:
        return {"role": "user", "content": message.content}


class HFInferenceChat(BaseChatModel):
    """
    LangChain-compatible Chat Model using huggingface_hub InferenceClient.
    Routes through HF Inference Providers (provider='auto').
    """
    model: str = PRIMARY_MODEL
    hf_token: str = ""
    max_new_tokens: int = 1024
    temperature: float = 0.6

    class Config:
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        return "huggingface_chat_inference_provider"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        client = InferenceClient(
            provider="auto",
            api_key=self.hf_token or None,
        )
        
        hf_messages = [_convert_message_to_dict(m) for m in messages]
        # Ensure system prompt is present if not already
        if not any(m["role"] == "system" for m in hf_messages):
            hf_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

        try:
            response = client.chat_completion(
                messages=hf_messages,
                model=self.model,
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
            )
            text = response.choices[0].message.content or ""
        except Exception as e:
            text = f"[Chat Error: {e}]"

        message = AIMessage(content=text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        client = InferenceClient(
            provider="auto",
            api_key=self.hf_token or None,
        )
        
        hf_messages = [_convert_message_to_dict(m) for m in messages]
        if not any(m["role"] == "system" for m in hf_messages):
            hf_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

        for chunk in client.chat_completion(
            messages=hf_messages,
            model=self.model,
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            stream=True,
        ):
            if not chunk.choices:
                continue
            token = chunk.choices[0].delta.content or ""
            yield ChatGenerationChunk(message=AIMessageChunk(content=token))

    @property
    def _identifying_params(self) -> dict:
        return {"model": self.model}


@functools.lru_cache(maxsize=1)
def get_llm() -> HFInferenceChat:
    """Return a cached Chat Model instance using HF Inference Providers."""
    return HFInferenceChat(
        model=PRIMARY_MODEL,
        hf_token=HF_TOKEN,
        max_new_tokens=1024,
        temperature=0.6,
    )


def get_system_prompt() -> str:
    return SYSTEM_PROMPT