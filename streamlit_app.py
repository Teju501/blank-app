import streamlit as st
import PyPDF2
import json
import time
import re
from groq import Groq
from datetime import datetime
from io import BytesIO

# ─────────────────────────────────────────
#  Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
#  Custom CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #13131a;
    --surface2: #1c1c28;
    --border: #2a2a3d;
    --accent: #6c63ff;
    --accent2: #ff6584;
    --accent3: #43e97b;
    --text: #e8e8f0;
    --muted: #6b6b8a;
}

* { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: var(--bg);
    color: var(--text);
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Hero Header */
.hero {
    text-align: center;
    padding: 2rem 0 1rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6c63ff, #ff6584, #43e97b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -1px;
}
.hero p {
    color: var(--muted);
    font-size: 1.1rem;
    margin-top: 0.5rem;
    font-weight: 300;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
}

/* Chat messages */
.chat-user {
    background: linear-gradient(135deg, #1e1e35, #252540);
    border: 1px solid var(--accent);
    border-radius: 16px 16px 4px 16px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    margin-left: 3rem;
}
.chat-user .label {
    font-size: 0.72rem;
    color: var(--accent);
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.chat-ai {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 16px 16px 16px 4px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    margin-right: 3rem;
}
.chat-ai .label {
    font-size: 0.72rem;
    color: var(--accent3);
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.chat-ai .answer { line-height: 1.7; color: var(--text); }

/* Confidence badge */
.conf-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 0.6rem;
}
.conf-high { background: rgba(67,233,123,0.15); color: #43e97b; border: 1px solid rgba(67,233,123,0.3); }
.conf-mid  { background: rgba(255,193,7,0.15);  color: #ffc107; border: 1px solid rgba(255,193,7,0.3); }
.conf-low  { background: rgba(255,101,132,0.15); color: #ff6584; border: 1px solid rgba(255,101,132,0.3); }

/* Timestamp */
.timestamp { font-size: 0.7rem; color: var(--muted); margin-top: 0.4rem; }

/* Metric cards */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
}
.metric-card {
    flex: 1;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-card .val {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
}
.metric-card .lbl { font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem; }

/* Upload zone */
.upload-zone {
    border: 2px dashed var(--border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    color: var(--muted);
    transition: border-color 0.3s;
}

/* Streamlit overrides */
.stTextInput input, .stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.2) !important;
}

.stButton button {
    background: linear-gradient(135deg, var(--accent), #8b85ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton button:hover { opacity: 0.85 !important; }

div[data-testid="stFileUploader"] {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.5rem;
}

.stSelectbox select, div[data-baseweb="select"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
}

hr { border-color: var(--border) !important; }

.stSpinner { color: var(--accent) !important; }

/* Scrollable chat area */
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Session State
# ─────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0
if "groq_client" not in st.session_state:
    st.session_state.groq_client = None

# ─────────────────────────────────────────
#  Helper Functions
# ─────────────────────────────────────────

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return None


def get_confidence(answer: str) -> tuple:
    """Estimate confidence based on answer content."""
    not_found_phrases = [
        "not available", "not found", "not mentioned",
        "not provided", "cannot find", "no information"
    ]
    answer_lower = answer.lower()
    if any(p in answer_lower for p in not_found_phrases):
        return "low", "Low Confidence", "conf-low"
    word_count = len(answer.split())
    if word_count > 40:
        return "high", "High Confidence", "conf-high"
    elif word_count > 15:
        return "mid", "Medium Confidence", "conf-mid"
    else:
        return "low", "Low Confidence", "conf-low"


def answer_question(question: str, document_text: str, model: str) -> str:
    """Answer question using Groq with full document context."""
    client = st.session_state.groq_client

    # Build conversation context from history
    messages = [
        {
            "role": "system",
            "content": f"""You are DocuMind AI, an expert document analyst. 
Answer questions STRICTLY based on the document provided. 
Do NOT use external knowledge.
If the answer is not in the document, say: "This information is not available in the document."
Be concise, accurate, and helpful.

DOCUMENT CONTENT:
{document_text}"""
        }
    ]

    # Add chat history for context (last 6 exchanges)
    for chat in st.session_state.chat_history[-6:]:
        messages.append({"role": "user", "content": chat["question"]})
        messages.append({"role": "assistant", "content": chat["answer"]})

    # Add current question
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()


def generate_download_text() -> str:
    """Generate plain text for download."""
    lines = []
    lines.append("=" * 60)
    lines.append("       DocuMind AI - QA Session Report")
    lines.append("=" * 60)
    lines.append(f"Document: {st.session_state.doc_name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total Questions: {len(st.session_state.chat_history)}")
    lines.append("=" * 60 + "\n")

    for i, chat in enumerate(st.session_state.chat_history, 1):
        lines.append(f"Q{i}: {chat['question']}")
        lines.append(f"A{i}: {chat['answer']}")
        lines.append(f"Confidence: {chat['confidence_label']}")
        lines.append(f"Time: {chat['timestamp']}")
        lines.append("-" * 60)

    return "\n".join(lines)


def generate_download_json() -> str:
    """Generate JSON for download."""
    data = {
        "document": st.session_state.doc_name,
        "generated_at": datetime.now().isoformat(),
        "total_questions": len(st.session_state.chat_history),
        "qa_pairs": st.session_state.chat_history
    }
    return json.dumps(data, indent=2)

# ─────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <span style='font-family:Syne; font-size:1.4rem; font-weight:800; 
        background: linear-gradient(135deg, #6c63ff, #ff6584);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🧠 DocuMind AI
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # API Key
    st.markdown("**🔑 Groq API Key**")
    api_key = st.text_input("", placeholder="gsk_...", type="password", label_visibility="collapsed")
    if api_key:
        try:
            st.session_state.groq_client = Groq(api_key=api_key)
            st.success("✅ API Connected")
        except Exception as e:
            st.error("❌ Invalid API Key")

    st.markdown("---")

    # Model Selection
    st.markdown("**🤖 Model**")
    model = st.selectbox("", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ], label_visibility="collapsed")

    st.markdown("---")

    # PDF Upload
    st.markdown("**📄 Upload Document**")
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    if uploaded_file:
        with st.spinner("Reading PDF..."):
            text = extract_text_from_pdf(uploaded_file)
            if text:
                st.session_state.document_text = text
                st.session_state.doc_name = uploaded_file.name
                st.success(f"✅ {uploaded_file.name}")
                st.caption(f"{len(text):,} characters extracted")

    st.markdown("---")

    # Stats
    if st.session_state.document_text:
        words = len(st.session_state.document_text.split())
        pages = st.session_state.document_text.count("\n\n")
        st.markdown(f"""
        <div class='card' style='padding:1rem;'>
            <div style='font-size:0.75rem; color:#6b6b8a; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.8rem;'>Document Stats</div>
            <div style='display:flex; justify-content:space-between; margin-bottom:0.5rem;'>
                <span style='color:#6b6b8a; font-size:0.85rem;'>Words</span>
                <span style='color:#6c63ff; font-weight:600;'>{words:,}</span>
            </div>
            <div style='display:flex; justify-content:space-between; margin-bottom:0.5rem;'>
                <span style='color:#6b6b8a; font-size:0.85rem;'>Questions Asked</span>
                <span style='color:#43e97b; font-weight:600;'>{len(st.session_state.chat_history)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Clear chat
    if st.session_state.chat_history:
        st.markdown("---")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

# ─────────────────────────────────────────
#  Main Content
# ─────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <h1>DocuMind AI</h1>
    <p>Intelligent Document Q&A · In-Context Learning · No RAG</p>
</div>
""", unsafe_allow_html=True)

# ── Check prerequisites ──
if not st.session_state.groq_client:
    st.info("👈 Enter your **Groq API Key** in the sidebar to get started. Get a free key at [console.groq.com](https://console.groq.com)")
    st.stop()

if not st.session_state.document_text:
    st.info("👈 **Upload a PDF** in the sidebar to start asking questions.")
    st.stop()

# ── Metrics Row ──
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📄 Document", st.session_state.doc_name[:20] + "..." if len(st.session_state.doc_name) > 20 else st.session_state.doc_name)
with col2:
    st.metric("💬 Questions Asked", len(st.session_state.chat_history))
with col3:
    high_conf = sum(1 for c in st.session_state.chat_history if c.get("confidence") == "high")
    st.metric("✅ High Confidence", high_conf)
with col4:
    st.metric("🤖 Model", model.split("-")[0].upper())

st.markdown("---")

# ── Sample Questions ──
with st.expander("💡 Sample Questions to Try", expanded=False):
    sample_qs = [
        "What were the company's total revenues in 2024?",
        "What are the key strategic initiatives mentioned in the report?",
        "Who is the CEO of the company?",
        "What are the company's plans for sustainability?",
        "How did the company perform in terms of R&D investment?"
    ]
    cols = st.columns(2)
    for i, q in enumerate(sample_qs):
        with cols[i % 2]:
            if st.button(f"➤ {q}", key=f"sample_{i}"):
                st.session_state["prefill_question"] = q
                st.rerun()

# ── Question Input ──
prefill = st.session_state.pop("prefill_question", "")
col_input, col_btn = st.columns([5, 1])
with col_input:
    question = st.text_input(
        "Ask a question",
        value=prefill,
        placeholder="e.g. What were the total revenues in 2024?",
        label_visibility="collapsed"
    )
with col_btn:
    ask_btn = st.button("Ask →", use_container_width=True)

# ── Process Question ──
if ask_btn and question.strip():
    if not st.session_state.document_text:
        st.error("Please upload a document first!")
    else:
        with st.spinner("🧠 Analyzing document..."):
            try:
                start = time.time()
                answer = answer_question(question, st.session_state.document_text, model)
                elapsed = round(time.time() - start, 2)
                conf_key, conf_label, conf_class = get_confidence(answer)

                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer,
                    "confidence": conf_key,
                    "confidence_label": conf_label,
                    "confidence_class": conf_class,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "elapsed": elapsed,
                    "model": model
                })
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ── Chat History ──
if st.session_state.chat_history:
    st.markdown("### 💬 Conversation")

    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"""
        <div class='chat-user'>
            <div class='label'>You</div>
            <div>{chat['question']}</div>
        </div>
        <div class='chat-ai'>
            <div class='label'>DocuMind AI</div>
            <div class='answer'>{chat['answer']}</div>
            <span class='conf-badge {chat["confidence_class"]}'>{chat["confidence_label"]}</span>
            <div class='timestamp'>🕐 {chat['timestamp']} &nbsp;·&nbsp; ⚡ {chat.get('elapsed', '?')}s &nbsp;·&nbsp; 🤖 {chat.get('model', model)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Download Section ──
    st.markdown("### 📥 Download Session")
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
        txt_data = generate_download_text()
        st.download_button(
            label="📄 Download as TXT",
            data=txt_data,
            file_name=f"qa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with dl_col2:
        json_data = generate_download_json()
        st.download_button(
            label="📊 Download as JSON",
            data=json_data,
            file_name=f"qa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
