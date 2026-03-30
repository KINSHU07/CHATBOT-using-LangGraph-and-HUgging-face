import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid
from datetime import datetime

st.set_page_config(
    page_title="ThrashChats",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:        #1C1917;
    --sidebar:   #161412;
    --surface:   #2A2522;
    --border:    #3A3330;
    --border2:   #4A4340;
    --text:      #E8E0D5;
    --text-dim:  #8A7F78;
    --text-mute: #5A5250;
    --accent:    #D97B4F;
    --accent2:   #E8A87C;
    --user-bg:   #2D2420;
    --user-bdr:  #4A3528;
}

html, body { background: var(--bg) !important; }
[data-testid="stAppViewContainer"] { background: var(--bg) !important; font-family: 'DM Sans', sans-serif; }
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu, footer, header { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

.sidebar-header {
    padding: 1.4rem 1.1rem 0.8rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.sidebar-brand {
    display: flex; align-items: center; gap: 0.5rem;
}
.sidebar-icon {
    width: 26px; height: 26px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem;
}
.sidebar-name {
    font-family: 'Instrument Serif', serif;
    font-size: 1rem;
    color: var(--text);
}

.sidebar-section {
    padding: 0.8rem 0.8rem 0.4rem;
}
.sidebar-label {
    font-size: 0.68rem;
    color: var(--text-mute);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
    padding: 0 0.3rem;
    margin-bottom: 0.4rem;
}

.thread-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.7rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.15s;
    margin-bottom: 0.15rem;
}
.thread-item:hover { background: var(--surface); }
.thread-item.active { background: var(--user-bg); border: 1px solid var(--user-bdr); }
.thread-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--text-mute);
    flex-shrink: 0;
}
.thread-item.active .thread-dot { background: var(--accent); }
.thread-title {
    font-size: 0.82rem;
    color: var(--text-dim);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
}
.thread-item.active .thread-title { color: var(--text); }
.thread-time {
    font-size: 0.68rem;
    color: var(--text-mute);
    flex-shrink: 0;
}

/* ── Main area ── */
.main .block-container {
    max-width: 740px !important;
    padding: 0 1.5rem 7rem !important;
    margin: 0 auto !important;
}

.topbar {
    position: sticky; top: 0; z-index: 100;
    background: linear-gradient(to bottom, var(--bg) 80%, transparent);
    padding: 1.4rem 0 0.8rem;
    margin-bottom: 0.5rem;
    display: flex; align-items: center; justify-content: space-between;
}
.topbar-title {
    font-family: 'Instrument Serif', serif;
    font-size: 1rem; color: var(--text-dim);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    max-width: 400px;
}
.topbar-badge {
    font-size: 0.68rem; color: var(--text-mute);
    background: var(--surface); border: 1px solid var(--border);
    padding: 0.2rem 0.6rem; border-radius: 20px;
    letter-spacing: 0.04em; text-transform: uppercase; font-weight: 500;
    white-space: nowrap;
}

/* ── Welcome ── */
.welcome { padding: 3.5rem 0 2rem; text-align: center; animation: fadeUp 0.5s ease both; }
.welcome-title { font-family: 'Instrument Serif', serif; font-size: 2.4rem; color: var(--text); letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 0.6rem; }
.welcome-title em { color: var(--accent); font-style: italic; }
.welcome-sub { font-size: 0.88rem; color: var(--text-mute); font-weight: 300; }
.suggestion-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-top: 2.5rem; text-align: left; }
.suggestion-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 0.85rem 1rem; cursor: pointer; transition: border-color 0.2s, background 0.2s; }
.suggestion-card:hover { border-color: var(--accent); background: var(--user-bg); }
.suggestion-card .s-icon { font-size: 1rem; margin-bottom: 0.3rem; }
.suggestion-card .s-text { font-size: 0.82rem; color: var(--text-dim); line-height: 1.4; }

/* ── Messages ── */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0.6rem 0 !important; gap: 0.8rem !important; animation: fadeUp 0.3s ease both; }
[data-testid="chatAvatarIcon-user"],[data-testid="chatAvatarIcon-assistant"] { width: 28px !important; height: 28px !important; min-width: 28px !important; border-radius: 6px !important; font-size: 0.75rem !important; margin-top: 2px !important; }
[data-testid="chatAvatarIcon-assistant"] { background: linear-gradient(135deg, var(--accent), var(--accent2)) !important; border: none !important; }
[data-testid="chatAvatarIcon-user"] { background: var(--surface) !important; border: 1px solid var(--border2) !important; }
[data-testid="stChatMessageContent"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { flex-direction: row-reverse !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] { background: var(--user-bg) !important; border: 1px solid var(--user-bdr) !important; border-radius: 16px 16px 4px 16px !important; padding: 0.7rem 1rem !important; max-width: 85% !important; margin-left: auto !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p { color: var(--text) !important; font-size: 0.9rem !important; line-height: 1.6 !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] { background: transparent !important; border: none !important; padding: 0.2rem 0 !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p { color: var(--text) !important; font-size: 0.9rem !important; line-height: 1.75 !important; }
[data-testid="stChatMessage"] code { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 5px !important; padding: 0.15rem 0.4rem !important; font-size: 0.82rem !important; color: var(--accent2) !important; }
[data-testid="stChatMessage"] pre { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; padding: 1rem !important; overflow-x: auto !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { border-bottom: 1px solid var(--border) !important; padding-bottom: 1rem !important; margin-bottom: 0.25rem !important; }

/* ── Input ── */
[data-testid="stBottom"] { background: linear-gradient(to top, var(--bg) 75%, transparent) !important; padding: 1rem 0 1.5rem !important; }
[data-testid="stChatInput"] { background: var(--surface) !important; border: 1px solid var(--border2) !important; border-radius: 14px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent) !important; box-shadow: 0 4px 24px rgba(217,123,79,0.12) !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; border: none !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; padding: 0.8rem 1rem !important; caret-color: var(--accent) !important; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-mute) !important; }
[data-testid="stChatInputSubmitButton"] button { background: linear-gradient(135deg, var(--accent), var(--accent2)) !important; border: none !important; border-radius: 9px !important; }

/* ── New Chat button ── */
div[data-testid="stButton"] > button {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    padding: 0.45rem 0.9rem !important;
    transition: border-color 0.2s, background 0.2s !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: var(--accent) !important;
    background: var(--user-bg) !important;
    color: var(--text) !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────
if 'threads' not in st.session_state:
    # threads = { thread_id: { 'title': str, 'messages': [], 'created_at': str } }
    first_id = str(uuid.uuid4())
    st.session_state['threads'] = {
        first_id: {'title': 'New Chat', 'messages': [], 'created_at': datetime.now().strftime('%H:%M')}
    }
    st.session_state['active_thread'] = first_id

if 'active_thread' not in st.session_state:
    st.session_state['active_thread'] = list(st.session_state['threads'].keys())[0]

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-brand">
            <div class="sidebar-icon">⬡</div>
            <span class="sidebar-name">ThrashChats</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    # New Chat button
    if st.button("＋  New Chat", key="new_chat"):
        new_id = str(uuid.uuid4())
        st.session_state['threads'][new_id] = {
            'title': 'New Chat',
            'messages': [],
            'created_at': datetime.now().strftime('%H:%M')
        }
        st.session_state['active_thread'] = new_id
        st.rerun()

    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label" style="padding:0 0.4rem">Conversations</div>', unsafe_allow_html=True)

    # Thread list
    for tid, tdata in reversed(list(st.session_state['threads'].items())):
        is_active = tid == st.session_state['active_thread']
        active_cls = "active" if is_active else ""
        label = tdata['title'][:28] + "…" if len(tdata['title']) > 28 else tdata['title']

        if st.button(f"{'●' if is_active else '○'}  {label}", key=f"thread_{tid}"):
            st.session_state['active_thread'] = tid
            st.rerun()

# ── Active thread data ────────────────────────────────────────────────
active_id   = st.session_state['active_thread']
active_data = st.session_state['threads'][active_id]
CONFIG      = {'configurable': {'thread_id': active_id}}

# ── Topbar ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <span class="topbar-title">{active_data['title']}</span>
    <span class="topbar-badge">LangGraph · Qwen · HF</span>
</div>
""", unsafe_allow_html=True)

# ── Welcome / Empty State ─────────────────────────────────────────────
if not active_data['messages']:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-title">Welcome to <em>ThrashChats</em></div>
        <div class="welcome-sub">Ask me anything — I think, I reason, I help.</div>
        <div class="suggestion-grid">
            <div class="suggestion-card"><div class="s-icon">✦</div><div class="s-text">Explain quantum entanglement simply</div></div>
            <div class="suggestion-card"><div class="s-icon">⌘</div><div class="s-text">Write a Python web scraper</div></div>
            <div class="suggestion-card"><div class="s-icon">◈</div><div class="s-text">Draft a professional email</div></div>
            <div class="suggestion-card"><div class="s-icon">◎</div><div class="s-text">Plan a 7-day Italy itinerary</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Conversation ──────────────────────────────────────────────────────
for message in active_data['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# ── Input ─────────────────────────────────────────────────────────────
user_input = st.chat_input('Message ThrashChats...')

if user_input:
    # Auto-title the thread from first message
    if active_data['title'] == 'New Chat':
        active_data['title'] = user_input[:40]

    active_data['messages'].append({'role': 'user', 'content': user_input})
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

    active_data['messages'].append({'role': 'assistant', 'content': full_response})