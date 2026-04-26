# 🎓 AI Tutor — Educational Assistant for School Kids

A warm, intelligent AI tutor powered by **HuggingFace LLMs**, **LangChain 0.3 LCEL**, and **Streamlit**.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🤖 HuggingFace LLM | Mistral-7B-Instruct (primary) / Flan-T5 (fallback) |
| 📄 Document Q&A | Upload PDF or TXT → RAG via FAISS + LCEL |
| 🌐 Live Search | DuckDuckGo for latest news & web results |
| 📚 Wikipedia | Encyclopaedic answers via Wikipedia tool |
| 🔢 Calculator | LLMMathChain for maths problem solving |
| 💾 Memory | Persistent JSON-based conversational memory per student |
| 🎨 UI | Streamlit with custom dark-themed CSS |

---

## 🚀 Quick Start

### 1. Clone / extract the project
```bash
cd ai_tutor
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
```bash
cp .env.example .env
# Edit .env and add your HUGGINGFACEHUB_API_TOKEN
```

### 5. Run
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 📁 Project Structure

```
ai_tutor/
├── app.py                    # Streamlit entry point + UI
├── requirements.txt          # All Python dependencies
├── .env.example              # Environment variable template
├── README.md
└── core/
    ├── __init__.py
    ├── llm_setup.py          # HuggingFace LLM initialisation
    ├── document_loader.py    # PDF/TXT → LangChain Documents
    ├── vector_store.py       # FAISS vectorstore + HF embeddings
    ├── chains.py             # LCEL RAG chain + ReAct Agent
    └── memory.py             # Persistent JSON chat memory
```

---

## 🧠 Architecture

```
Student Input
     │
     ▼
 [Streamlit UI]
     │
     ├─── Has uploaded doc? ──YES──▶ [FAISS Retriever]
     │                                      │
     │                               [RunnableMap LCEL]
     │                                      │
     │                              [Stuff Documents Chain]
     │                                      │
     │◀─────────────────────────── [HuggingFace LLM]
     │
     └─── No doc ─────────────────▶ [ReAct Agent]
                                         │
                              ┌──────────┼──────────┐
                              ▼          ▼          ▼
                         [DuckDuckGo] [Wikipedia] [Calculator]
                              │          │          │
                              └──────────┼──────────┘
                                         │
                                  [HuggingFace LLM]
                                         │
                                  [JSON Memory Save]
```

---

## 🔑 Getting a Free HuggingFace Token

1. Go to https://huggingface.co/join
2. Create a free account
3. Visit https://huggingface.co/settings/tokens
4. Create a new **Read** token
5. Paste it in your `.env` file

---

## 📚 Subjects Covered

- Mathematics (arithmetic, algebra, geometry, calculus)
- Science (physics, chemistry, biology)
- History & Geography
- English & Grammar
- Computer Science / Coding
- Current Affairs (via DuckDuckGo live search)
- Any topic in uploaded textbooks / notes

---

## 🛠️ Key Technologies

- **LangChain 0.3** — LCEL, RunnableMap, RunnablePassthrough
- **FAISS** — Fast vector similarity search
- **HuggingFace Hub** — LLM + Sentence Transformers
- **DuckDuckGo Search** — Live web search
- **Wikipedia API** — Encyclopaedic knowledge
- **LLMMathChain** — Safe maths evaluation
- **Streamlit** — Frontend & deployment
- **RecursiveCharacterTextSplitter** — Smart document chunking