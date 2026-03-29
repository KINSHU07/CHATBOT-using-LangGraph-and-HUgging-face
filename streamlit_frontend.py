import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Assistant",
    page_icon="✦",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root & Background ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f0f0f;
    color: #e8e6e1;
    font-family: 'Sora', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 50%, #1a1025 0%, #0f0f0f 60%);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer { visibility: hidden; }

/* ── Main container ── */
.main .block-container {
    max-width: 760px;
    padding: 2rem 1.5rem 8rem;
    margin: 0 auto;
}

/* ── Header ── */
.chat-header {
    text-align: center;
    padding: 3rem 0 2rem;
    border-bottom: 1px solid #1e1e1e;
    margin-bottom: 2rem;
}
.chat-header h1 {
    font-size: 1.6rem;
    font-weight: 600;
    color: #f0ede8;
    letter-spacing: -0.03em;
    margin: 0 0 0.3rem;
}
.chat-header p {
    font-size: 0.82rem;
    color: #5a5a5a;
    margin: 0;
    font-weight: 300;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Message bubbles ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
    margin-bottom: 0.25rem !important;
    gap: 0.75rem !important;
}

/* User messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: #1e1a2e !important;
    border: 1px solid #2d2540 !important;
    color: #d4cfe8 !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 0.75rem 1rem !important;
    max-width: 82% !important;
    margin-left: auto !important;
    font-size: 0.92rem !important;
    line-height: 1.6 !important;
}

/* Assistant messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: #161616 !important;
    border: 1px solid #222 !important;
    color: #e0ddd8 !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 0.85rem 1.1rem !important;
    max-width: 90% !important;
    font-size: 0.92rem !important;
    line-height: 1.75 !important;
}

/* Avatar icons */
[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, #6c3fd4, #9b59f5) !important;
    border-radius: 50% !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    font-size: 0.75rem !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: #1e1e1e !important;
    border: 1px solid #333 !important;
    border-radius: 50% !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    font-size: 0.75rem !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 100% !important;
    max-width: 760px !important;
    padding: 1rem 1.5rem 1.5rem !important;
    background: linear-gradient(to top, #0f0f0f 70%, transparent) !important;
    border: none !important;
    backdrop-filter: blur(12px) !important;
    z-index: 999 !important;
}

[data-testid="stChatInput"] textarea {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 14px !important;
    color: #e8e6e1 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.85rem 1rem !important;
    transition: border-color 0.2s ease !important;
    resize: none !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #6c3fd4 !important;
    box-shadow: 0 0 0 3px rgba(108, 63, 212, 0.12) !important;
    outline: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #444 !important;
}

/* Send button */
[data-testid="stChatInputSubmitButton"] button {
    background: linear-gradient(135deg, #6c3fd4, #9b59f5) !important;
    border: none !important;
    border-radius: 10px !important;
    transition: opacity 0.2s ease !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    opacity: 0.85 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #3a3a3a;
}
.empty-state .icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
    opacity: 0.4;
}
.empty-state p {
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 300;
}

/* ── Suggested prompts ── */
.suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1.5rem;
}
.suggestion-chip {
    background: #161616;
    border: 1px solid #222;
    color: #666;
    border-radius: 20px;
    padding: 0.4rem 0.9rem;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: 'Sora', sans-serif;
}
.suggestion-chip:hover {
    border-color: #6c3fd4;
    color: #9b59f5;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
    <h1>✦ AI Assistant</h1>
    <p>Powered by LangGraph · Llama · HuggingFace</p>
</div>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────
CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# ── Empty State ───────────────────────────────────────────────────────
if not st.session_state['message_history']:
    st.markdown("""
    <div class="empty-state">
        <span class="icon">◈</span>
        <p>Start a conversation</p>
        <div class="suggestions">
            <span class="suggestion-chip">Explain quantum computing</span>
            <span class="suggestion-chip">Write a Python function</span>
            <span class="suggestion-chip">Recipe for pasta</span>
            <span class="suggestion-chip">Plan my week</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Conversation History ───────────────────────────────────────────────
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# ── Chat Input ────────────────────────────────────────────────────────
user_input = st.chat_input('Message AI Assistant...')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    with st.chat_message('assistant'):
        placeholder = st.empty()
        full_response = ""

        for message_chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        ):
            if message_chunk.content:
                full_response += message_chunk.content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    st.session_state['message_history'].append({'role': 'assistant', 'content': full_response})