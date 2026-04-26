# 🎓 AI Tutor - Your Smart Study Companion

A powerful, high-performance AI Tutor built with **Streamlit**, **LangChain**, and **Hugging Face Inference Providers**. This app combines document-based Q&A (RAG), web search (DuckDuckGo + Wikipedia), and mathematical solving into a single, seamless educational interface.

## 🚀 Features

- **📄 Document Q&A (RAG)**: Upload PDFs or TXT files to ask questions directly about your study material.
- **🌐 Deep Web Search**: Real-time access to DuckDuckGo and Wikipedia for latest information and general knowledge.
- **🧮 Math Expert**: Step-by-step mathematical problem solving.
- **🧠 Conversation Memory**: Remembers previous context to provide coherent, human-like tutoring.
- **⚡ Streaming Output**: Answers are streamed in real-time for a premium UX.
- **🎨 Modern UI**: High-contrast, responsive design with "Thinking" status updates.

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **LLM**: Qwen/Qwen2.5-72B-Instruct (via Hugging Face Inference Providers)
- **Framework**: LangChain 0.3 (LCEL)
- **Vector Store**: FAISS
- **Embeddings**: Hugging Face Sentence Transformers

## 📥 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Udemy
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
   PRIMARY_MODEL=Qwen/Qwen2.5-72B-Instruct
   ```

## 🚀 Running Locally

```bash
streamlit run app.py
```

## 🌐 Deployment (Streamlit Cloud)

1. Push your code to a **GitHub** repository.
2. Go to [Streamlit Cloud](https://share.streamlit.io/).
3. Connect your GitHub account and select this repository.
4. Add your `HUGGINGFACEHUB_API_TOKEN` to the **Secrets** section in Streamlit Cloud settings.
5. Click **Deploy**!

---
*Created with ❤️ by Syed Sheezan*
