
import streamlit as st
import os
import json
import time
from pathlib import Path

st.set_page_config(
    page_title="AI Tutor 🎓",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Space+Mono&display=swap');

:root {
    --primary: #4F46E5;
    --secondary: #7C3AED;
    --accent: #F59E0B;
    --bg: #F5F5FA;
    --card: #FFFFFF;
    --card2: #EEF0FB;
    --text: #1A1A2E;
    --muted: #444466;
    --success: #10B981;
    --danger: #EF4444;
}

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    background-color: var(--bg);
    color: var(--text) !important;
}

.stApp { background: linear-gradient(135deg, #F5F5FA 0%, #EEF0FB 50%, #F5F5FA 100%); }

/* Force all Streamlit text to be dark */
.stApp, .stApp p, .stApp span, .stApp label, .stApp div,
.stMarkdown, .stMarkdown p, .stText, [data-testid="stMarkdownContainer"] p {
    color: #1A1A2E !important;
}

/* Header & Menu Visibility */
header[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0) !important;
}
header[data-testid="stHeader"] svg {
    fill: #4F46E5 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid rgba(79,70,229,0.3);
}
[data-testid="stSidebar"] * {
    color: #1A1A2E !important;
}

/* Mobile Sidebar Button */
[data-testid="stSidebarCollapsedControl"] {
    background-color: #4F46E5 !important;
    color: white !important;
    border-radius: 0 10px 10px 0 !important;
    opacity: 0.9;
}
[data-testid="stSidebarCollapsedControl"] svg {
    fill: white !important;
}

/* Chat bubbles */
.user-bubble {
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px 60px;
    box-shadow: 0 4px 15px rgba(79,70,229,0.3);
    font-size: 15px;
    line-height: 1.6;
    animation: fadeSlideIn 0.3s ease;
}

.tutor-bubble {
    background: linear-gradient(135deg, #FFFFFF, #EEF0FB);
    color: #1A1A2E;
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 60px 8px 0;
    border: 1px solid rgba(79,70,229,0.2);
    box-shadow: 0 4px 15px rgba(79,70,229,0.1);
    font-size: 15px;
    line-height: 1.6;
    animation: fadeSlideIn 0.3s ease;
}

.avatar-tutor {
    font-size: 26px;
    margin-right: 8px;
    vertical-align: middle;
}
.avatar-user {
    font-size: 26px;
    margin-left: 8px;
    vertical-align: middle;
    float: right;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Header */
.tutor-header {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    padding: 20px 28px;
    border-radius: 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 8px 32px rgba(79,70,229,0.4);
}

.tutor-header h1 { font-size: 28px; font-weight: 800; margin: 0; color: white; }
.tutor-header p  { font-size: 14px; color: rgba(255,255,255,0.8); margin: 4px 0 0; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(79,70,229,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79,70,229,0.5) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(79,70,229,0.5) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    background: rgba(79,70,229,0.05) !important;
}

/* Input */
[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    border: 1px solid rgba(79,70,229,0.4) !important;
    border-radius: 12px !important;
    color: #1A1A2E !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 15px !important;
    padding: 12px 16px !important;
}

/* Source badge */
.source-badge {
    display: inline-block;
    background: rgba(79,70,229,0.15);
    border: 1px solid rgba(79,70,229,0.3);
    color: #A5B4FC;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 20px;
    margin: 2px;
    font-family: 'Space Mono', monospace;
}

/* Mode chip */
.mode-chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin: 2px;
}

/* Info card */
.info-card {
    background: var(--card);
    border: 1px solid rgba(79,70,229,0.2);
    border-radius: 12px;
    padding: 14px;
    margin: 8px 0;
    color: #1A1A2E;
}

/* Scrollable chat */
.chat-container {
    max-height: 520px;
    overflow-y: auto;
    padding: 8px;
    scrollbar-width: thin;
    scrollbar-color: #4F46E5 transparent;
}

.stSpinner { color: #4F46E5 !important; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, var(--card), var(--card2));
    border-radius: 12px;
    padding: 16px;
    border: 1px solid rgba(79,70,229,0.2);
    text-align: center;
    color: #1A1A2E;
}

.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #4F46E5; }

/* Ensure all text in markdown and other elements is dark */
.stMarkdown, .stMarkdown * { color: #1A1A2E; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #4F46E5 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Imports (lazy to speed up cold start) ───────────────────────────────────
from core.llm_setup      import get_llm
from core.vector_store   import build_vectorstore, get_retriever
from core.chains         import build_rag_chain, build_agent_chain
from core.memory         import load_memory, save_memory, clear_memory
from core.document_loader import load_uploaded_file

# ─── Session State Init ──────────────────────────────────────────────────────
if "chat_history"   not in st.session_state: st.session_state.chat_history   = []
if "vectorstore"    not in st.session_state: st.session_state.vectorstore    = None
if "doc_loaded"     not in st.session_state: st.session_state.doc_loaded     = False
if "doc_name"       not in st.session_state: st.session_state.doc_name       = ""
if "student_name"   not in st.session_state: st.session_state.student_name   = ""
if "mode"           not in st.session_state: st.session_state.mode           = "agent"
if "session_id"     not in st.session_state: st.session_state.session_id     = "student_default"

if "memory_loaded" not in st.session_state:
    st.session_state.chat_history = load_memory(st.session_state.session_id)
    st.session_state.memory_loaded = True

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 AI Tutor")
    st.markdown("---")

    name = st.text_input("👤 Your Name", value=st.session_state.student_name, placeholder="Enter your name...")
    if name: st.session_state.student_name = name

    st.markdown("---")
    st.markdown("### 📂 Upload Study Material")
    uploaded_file = st.file_uploader(
        "Upload PDF or TXT",
        type=["pdf", "txt"],
        help="Upload your textbook chapter, notes, or any document!"
    )

    if uploaded_file:
        if not st.session_state.doc_loaded or st.session_state.doc_name != uploaded_file.name:
            with st.spinner("📖 Reading your document..."):
                docs = load_uploaded_file(uploaded_file)
                if docs is None:
                    st.error("Could not read file due to an error.")
                elif len(docs) == 0:
                    st.error("Could not read file. The document appears to have no text (it might be scanned images).")
                else:
                    vs = build_vectorstore(docs)
                    st.session_state.vectorstore = vs
                    st.session_state.doc_loaded  = True
                    st.session_state.doc_name    = uploaded_file.name
                    st.session_state.mode        = "rag"
                    st.success(f"✅ Loaded: {uploaded_file.name} ({len(docs)} chunks)")

    if st.session_state.doc_loaded:
        st.markdown(f"""<div class="info-card">
            📄 <b>{st.session_state.doc_name}</b><br/>
            <span style="color:#10B981;font-size:12px;">✅ Active for Q&A</span>
        </div>""", unsafe_allow_html=True)
        if st.button("🗑️ Remove Document"):
            st.session_state.vectorstore = None
            st.session_state.doc_loaded  = False
            st.session_state.doc_name    = ""
            st.session_state.mode        = "agent"
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔧 Mode")
    mode_label = "📄 Document Q&A" if st.session_state.mode == "rag" else "🌐 Search + Tools"
    st.markdown(f'<span class="mode-chip" style="background:rgba(79,70,229,0.2);border:1px solid #4F46E5;color:#A5B4FC;">{mode_label}</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💾 Memory")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save"):
            save_memory(st.session_state.session_id, st.session_state.chat_history)
            st.success("Saved!")
    with col2:
        if st.button("🗑️ Clear"):
            clear_memory(st.session_state.session_id)
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Stats")
    turns = len(st.session_state.chat_history)
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:28px;font-weight:800;color:#A5B4FC;">{turns}</div>
        <div style="font-size:12px;color:#8888AA;">Messages</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style="font-size:11px;color:#8888AA;text-align:center;">
        🤖 Powered by HuggingFace LLM<br/>LangChain 0.3 · FAISS · DuckDuckGo
    </div>""", unsafe_allow_html=True)

# ─── Main Area ────────────────────────────────────────────────────────────────
greeting = f"Hey {st.session_state.student_name}! 🌟" if st.session_state.student_name else "Hey there! 🌟"
st.markdown(f"""
<div class="tutor-header">
    <span style="font-size:48px;">🎓</span>
    <div>
        <h1>AI Tutor</h1>
        <p>{greeting} I'm here to help you learn anything — ask me anything!</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick topic chips
st.markdown("**Quick Topics:**")
cols = st.columns(6)
topics = ["🔢 Maths", "🔬 Science", "📚 History", "🌍 Geography", "💻 Coding", "✏️ English"]
quick_q = None
for i, (col, topic) in enumerate(zip(cols, topics)):
    with col:
        if st.button(topic, key=f"chip_{i}"):
            quick_q = f"Help me with {topic.split(' ',1)[1]}"

st.markdown("---")

# ─── Chat Display ─────────────────────────────────────────────────────────────
chat_html = '<div class="chat-container">'
if not st.session_state.chat_history:
    chat_html += """
    <div style="text-align:center;padding:40px;color:#8888AA;">
        <div style="font-size:52px;margin-bottom:12px;">🤖</div>
        <div style="font-size:18px;font-weight:700;color:#A5B4FC;">Hi! I'm your AI Tutor!</div>
        <div style="font-size:14px;margin-top:8px;">Ask me anything — Maths, Science, History, or upload your notes!</div>
    </div>"""
else:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_html += f'<div class="user-bubble">👦 {msg["content"]}</div>'
        else:
            content = msg["content"]
            sources = msg.get("sources", [])
            src_html = ""
            if sources:
                src_html = "<br/><div style='margin-top:8px;'>"
                for s in sources[:3]:
                    src_html += f'<span class="source-badge">📎 {s}</span>'
                src_html += "</div>"
            chat_html += f'<div class="tutor-bubble">🎓 {content}{src_html}</div>'

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# ─── Input ────────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        "Ask your question...",
        value=quick_q or "",
        placeholder="e.g. Explain photosynthesis in simple words...",
        label_visibility="collapsed",
        key="user_input"
    )
with col_btn:
    send = st.button("Send 🚀", use_container_width=True)

# ─── Chain Invocation ─────────────────────────────────────────────────────────
def run_query_stream(question: str):
    """Generator that yields status updates and text chunks."""
    # Robust history parsing: find (user, assistant) pairs
    history_pairs = []
    for i in range(len(st.session_state.chat_history)):
        msg = st.session_state.chat_history[i]
        if msg["role"] == "user" and i + 1 < len(st.session_state.chat_history):
            next_msg = st.session_state.chat_history[i+1]
            if next_msg["role"] == "assistant":
                history_pairs.append((msg["content"], next_msg["content"]))
    
    # Keep only last 5 turns for prompt efficiency
    history_pairs = history_pairs[-5:]

    # Import triggers from chains to decide routing
    from core.chains import _needs_search, _needs_math
    
    use_rag = st.session_state.mode == "rag" and st.session_state.vectorstore
    
    # If it's a search/math question, prioritize the Agent even in RAG mode
    if _needs_search(question) or _needs_math(question):
        use_rag = False

    sources = []
    if use_rag:
        yield {"status": "📂 Searching through your document..."}
        retriever = get_retriever(st.session_state.vectorstore)
        
        # We manually fetch docs first to show sources and status
        relevant_docs = retriever.invoke(question)
        for doc in relevant_docs:
            src = doc.metadata.get("source", "Document")
            if src not in sources: sources.append(src)
        
        yield {"sources": sources}
        yield {"status": "📖 Reading context and drafting answer..."}
        
        chain = build_rag_chain(retriever)
        # Streaming the RAG chain (it yields dicts with 'answer' chunks)
        for event in chain.stream({"input": question, "chat_history": history_pairs}):
            if "answer" in event:
                yield {"chunk": event["answer"]}
    else:
        agent = build_agent_chain(history_pairs)
        for event in agent.stream({"input": question}):
            yield event


if (send or quick_q) and user_input.strip():
    question = user_input.strip()
    st.session_state.chat_history.append({"role": "user", "content": question})

    # Display the current conversation with the new user bubble before streaming starts
    st.rerun() if not send else None # Force UI update if from chip

    full_answer = ""
    sources = []
    
    with st.status("🤔 Thinking...") as status:
        placeholder = st.empty()
        
        try:
            for event in run_query_stream(question):
                if "status" in event:
                    status.update(label=event["status"])
                if "sources" in event:
                    sources = event["sources"]
                if "chunk" in event:
                    full_answer += event["chunk"]
                    # Render the answer live in the custom bubble
                    placeholder.markdown(f'<div class="tutor-bubble">🎓 {full_answer}</div>', unsafe_allow_html=True)
            
            status.update(label="✅ Answered!", state="complete")
        except Exception as e:
            full_answer = f"Oops! I ran into a problem: {str(e)}. Please try again!"
            placeholder.markdown(f'<div class="tutor-bubble">🎓 {full_answer}</div>', unsafe_allow_html=True)
            status.update(label="❌ Error", state="error")

    st.session_state.chat_history.append({
        "role":    "assistant",
        "content": full_answer,
        "sources": sources,
    })

    save_memory(st.session_state.session_id, st.session_state.chat_history)
    st.rerun()