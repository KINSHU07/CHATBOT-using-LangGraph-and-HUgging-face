import streamlit as st
from langgraph_backend import chatbot, load_threads, save_thread, delete_thread
from langchain_core.messages import HumanMessage
from datetime import datetime
import uuid

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="ThrashChats",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:         #06070D;
    --sidebar:    #080910;
    --surface:    #0F1120;
    --surface2:   #141628;
    --border:     #1A1D35;
    --text:       #E2E8F0;
    --text-dim:   #7A8499;
    --text-mute:  #3A4055;
    --neon:       #00FF88;
    --neon2:      #00CCFF;
    --user-bg:    #0D1F2D;
}

html, body { background: var(--bg) !important; }
[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(rgba(0,255,136,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,136,0.015) 1px, transparent 1px),
        var(--bg) !important;
    background-size: 40px 40px, 40px 40px !important;
    font-family: 'Rajdhani', sans-serif;
}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
#MainMenu, footer, header { display: none !important; }
.main .block-container { max-width: 800px !important; padding: 0 1.5rem 7rem !important; margin: 0 auto !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 270px !important; max-width: 270px !important;
    position: relative;
}
[data-testid="stSidebar"]::before {
    content: ''; position: absolute; top: 0; right: 0;
    width: 1px; height: 100%;
    background: linear-gradient(to bottom, transparent, var(--neon), transparent);
    opacity: 0.4;
}
[data-testid="stSidebar"]::after {
    content: ''; position: absolute; inset: 0;
    background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,136,0.008) 2px,rgba(0,255,136,0.008) 4px);
    pointer-events: none; z-index: 0;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

.sb-wrap   { position: relative; z-index: 1; }
.sb-header { padding: 1.5rem 1.2rem 1rem; border-bottom: 1px solid var(--border); }
.sb-logo   { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.2rem; }
.sb-logo-icon {
    width: 32px; height: 32px; border: 1px solid var(--neon); border-radius: 6px;
    display: flex; align-items: center; justify-content: center; font-size: 1rem;
    box-shadow: 0 0 12px rgba(0,255,136,0.3);
    animation: pulse-glow 3s ease-in-out infinite;
}
@keyframes pulse-glow {
    0%,100% { box-shadow: 0 0 12px rgba(0,255,136,0.3); }
    50%      { box-shadow: 0 0 22px rgba(0,255,136,0.55); }
}
.sb-logo-name {
    font-family: 'Orbitron', monospace; font-size: 0.85rem; font-weight: 700;
    color: var(--neon); letter-spacing: 0.1em; text-shadow: 0 0 10px rgba(0,255,136,0.5);
}
.sb-tagline {
    font-size: 0.65rem; color: var(--text-mute); letter-spacing: 0.15em;
    text-transform: uppercase; font-family: 'Share Tech Mono', monospace;
    padding-left: 2.6rem;
}
.sb-db-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.6rem; color: var(--neon2);
    background: rgba(0,204,255,0.06); border: 1px solid rgba(0,204,255,0.2);
    padding: 0.15rem 0.5rem; border-radius: 3px;
    font-family: 'Share Tech Mono', monospace;
    margin-left: 2.6rem; margin-top: 0.3rem; letter-spacing: 0.08em;
}
.sb-db-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: var(--neon2); box-shadow: 0 0 4px var(--neon2);
    animation: blink 2s ease-in-out infinite;
}
.sb-label {
    font-size: 0.62rem; color: var(--neon); text-transform: uppercase;
    letter-spacing: 0.2em; font-family: 'Share Tech Mono', monospace;
    opacity: 0.6; margin-bottom: 0.5rem; padding: 0 0.2rem;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Sidebar buttons */
div[data-testid="stButton"] > button {
    background: transparent !important; color: var(--text-dim) !important;
    border: 1px solid var(--border) !important; border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important; font-size: 0.75rem !important;
    padding: 0.5rem 0.8rem !important; width: 100% !important;
    text-align: left !important; transition: all 0.2s !important;
    letter-spacing: 0.02em !important; margin-bottom: 0.25rem !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--surface) !important; border-color: var(--neon) !important;
    color: var(--neon) !important; box-shadow: 0 0 12px rgba(0,255,136,0.15) !important;
    text-shadow: 0 0 8px rgba(0,255,136,0.4) !important;
}
/* New session button (first button) */
div[data-testid="stButton"]:first-of-type > button {
    border: 1px solid var(--neon) !important; color: var(--neon) !important;
    text-align: center !important; text-shadow: 0 0 8px rgba(0,255,136,0.4) !important;
    box-shadow: 0 0 12px rgba(0,255,136,0.1) !important;
    letter-spacing: 0.1em !important; font-weight: 600 !important; margin-bottom: 0.8rem !important;
}
div[data-testid="stButton"]:first-of-type > button:hover {
    background: rgba(0,255,136,0.08) !important;
    box-shadow: 0 0 20px rgba(0,255,136,0.25) !important;
}

/* ── TOPBAR ── */
.topbar {
    position: sticky; top: 0; z-index: 100;
    background: linear-gradient(to bottom, var(--bg) 70%, transparent);
    padding: 1.4rem 0 1rem; margin-bottom: 0.8rem;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid var(--border);
}
.topbar-left  { display: flex; align-items: center; gap: 0.8rem; }
.topbar-indicator {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--neon); box-shadow: 0 0 8px var(--neon);
    animation: blink 2s ease-in-out infinite;
}
.topbar-title {
    font-family: 'Share Tech Mono', monospace; font-size: 0.82rem;
    color: var(--text-dim); letter-spacing: 0.05em;
    max-width: 380px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.topbar-right { display: flex; align-items: center; gap: 0.5rem; }
.topbar-badge {
    font-size: 0.62rem; color: var(--neon2);
    background: rgba(0,204,255,0.06); border: 1px solid rgba(0,204,255,0.2);
    padding: 0.2rem 0.6rem; border-radius: 4px;
    letter-spacing: 0.08em; text-transform: uppercase;
    font-family: 'Share Tech Mono', monospace;
}

/* ── WELCOME ── */
.welcome { padding: 4rem 0 2.5rem; text-align: center; animation: fadeUp 0.6s ease both; }
.welcome-glitch {
    font-family: 'Orbitron', monospace; font-size: 2.8rem; font-weight: 900;
    color: var(--text); letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 0.5rem;
}
.welcome-glitch span { color: var(--neon); text-shadow: 0 0 20px rgba(0,255,136,0.6), 0 0 40px rgba(0,255,136,0.3); }
.welcome-sub {
    font-size: 0.85rem; color: var(--text-mute); font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 2.5rem;
}
.welcome-sub::before { content: '> '; color: var(--neon); opacity: 0.6; }
.suggestion-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; text-align: left; }
.suggestion-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.9rem 1rem; cursor: pointer;
    transition: all 0.2s; position: relative; overflow: hidden;
}
.suggestion-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 3px; height: 100%; background: var(--neon); opacity: 0; transition: opacity 0.2s;
}
.suggestion-card:hover { border-color: rgba(0,255,136,0.3); background: var(--surface2); }
.suggestion-card:hover::before { opacity: 1; }
.s-tag  { font-size: 0.62rem; color: var(--neon); font-family: 'Share Tech Mono', monospace; letter-spacing: 0.1em; margin-bottom: 0.35rem; opacity: 0.7; }
.s-text { font-size: 0.85rem; color: var(--text-dim); line-height: 1.4; }

/* ── MESSAGES ── */
[data-testid="stChatMessage"] {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 0.8rem 0 !important;
    gap: 0.9rem !important; animation: fadeUp 0.3s ease both;
}
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
    width: 30px !important; height: 30px !important; min-width: 30px !important;
    border-radius: 6px !important; font-size: 0.8rem !important; margin-top: 3px !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: transparent !important; border: 1px solid var(--neon) !important;
    box-shadow: 0 0 10px rgba(0,255,136,0.25) !important;
}
[data-testid="chatAvatarIcon-user"] {
    background: transparent !important; border: 1px solid var(--neon2) !important;
    box-shadow: 0 0 10px rgba(0,204,255,0.2) !important;
}
[data-testid="stChatMessageContent"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { flex-direction: row-reverse !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--user-bg) !important; border: 1px solid rgba(0,204,255,0.25) !important;
    border-radius: 12px 12px 4px 12px !important; padding: 0.75rem 1.1rem !important;
    max-width: 82% !important; margin-left: auto !important;
    box-shadow: 0 0 20px rgba(0,204,255,0.06) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: var(--text) !important; font-size: 0.92rem !important;
    line-height: 1.65 !important; font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: transparent !important; border-left: 2px solid rgba(0,255,136,0.3) !important;
    border-radius: 0 !important; padding: 0.3rem 0 0.3rem 1.1rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p {
    color: var(--text) !important; font-size: 0.92rem !important;
    line-height: 1.8 !important; font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stChatMessage"] code {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 4px !important; padding: 0.15rem 0.45rem !important;
    font-size: 0.82rem !important; color: var(--neon) !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stChatMessage"] pre {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-left: 3px solid var(--neon) !important; border-radius: 6px !important;
    padding: 1rem 1.2rem !important; overflow-x: auto !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 1.2rem !important; margin-bottom: 0.2rem !important;
}

/* ── INPUT ── */
[data-testid="stBottom"] {
    background: linear-gradient(to top, var(--bg) 70%, transparent) !important;
    padding: 1rem 0 1.5rem !important;
}
[data-testid="stChatInput"] {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; box-shadow: 0 0 30px rgba(0,0,0,0.5) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0,255,136,0.4) !important;
    box-shadow: 0 0 0 1px rgba(0,255,136,0.1), 0 0 30px rgba(0,255,136,0.08) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; border: none !important;
    color: var(--text) !important; font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.88rem !important; padding: 0.85rem 1rem !important;
    caret-color: var(--neon) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-mute) !important; }
[data-testid="stChatInputSubmitButton"] button {
    background: var(--neon) !important; border: none !important;
    border-radius: 6px !important; box-shadow: 0 0 12px rgba(0,255,136,0.3) !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    box-shadow: 0 0 22px rgba(0,255,136,0.5) !important; transform: scale(1.05) !important;
}

::-webkit-scrollbar       { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,255,136,0.2); border-radius: 2px; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)


# ── Session State bootstrap ───────────────────────────────────────────
if "threads" not in st.session_state:
    st.session_state["threads"] = load_threads()

# If the DB was empty, seed a first thread
if not st.session_state["threads"]:
    first_id  = str(uuid.uuid4())
    now       = datetime.now().strftime("%H:%M")
    st.session_state["threads"] = {
        first_id: {"title": "New Session", "messages": [], "created_at": now}
    }
    save_thread(first_id, "New Session", now, [])

if "active_thread" not in st.session_state:
    st.session_state["active_thread"] = next(iter(st.session_state["threads"]))

# Guard: active thread must still exist
if st.session_state["active_thread"] not in st.session_state["threads"]:
    st.session_state["active_thread"] = next(iter(st.session_state["threads"]))


# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-wrap">
      <div class="sb-header">
        <div class="sb-logo">
          <div class="sb-logo-icon">⚡</div>
          <span class="sb-logo-name">THRASHCHATS</span>
        </div>
        <div class="sb-tagline">AI · v3.0 · gemma · online</div>
        <div class="sb-db-badge">
          <span class="sb-db-dot"></span> SQLite · persistent
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:0.7rem"></div>', unsafe_allow_html=True)

    # ── New session button ──────────────────────────────────────────
    if st.button("⚡  INIT NEW SESSION", key="new_chat"):
        new_id = str(uuid.uuid4())
        now    = datetime.now().strftime("%H:%M")
        st.session_state["threads"][new_id] = {
            "title": "New Session", "messages": [], "created_at": now
        }
        save_thread(new_id, "New Session", now, [])
        st.session_state["active_thread"] = new_id
        st.rerun()

    # ── Thread list ─────────────────────────────────────────────────
    st.markdown(
        '<div class="sb-label" style="padding:0 0.2rem;margin-top:0.5rem">// SESSION LOG</div>',
        unsafe_allow_html=True,
    )

    for tid, tdata in list(st.session_state["threads"].items()):
        is_active = tid == st.session_state["active_thread"]
        prefix    = "▶" if is_active else "·"
        label     = tdata["title"]
        short     = (label[:24] + "…") if len(label) > 24 else label

        if st.button(
            f"{prefix}  {short}  [{tdata['created_at']}]",
            key=f"thread_{tid}",
        ):
            st.session_state["active_thread"] = tid
            st.rerun()


# ── Active thread refs ────────────────────────────────────────────────
active_id   = st.session_state["active_thread"]
active_data = st.session_state["threads"][active_id]
CONFIG      = {"configurable": {"thread_id": active_id}}
short_id    = active_id[:8].upper()


# ── TOPBAR ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-indicator"></div>
        <span class="topbar-title">// {active_data['title'].upper()}</span>
    </div>
    <div class="topbar-right">
        <span class="topbar-badge">SID:{short_id}</span>
        <span class="topbar-badge">GEMMA · HF · SQLITE</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── WELCOME (shown only on empty threads) ─────────────────────────────
if not active_data["messages"]:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-glitch">THRASH<span>CHATS</span></div>
        <div class="welcome-sub">initialize your query. system ready.</div>
        <div class="suggestion-grid">
            <div class="suggestion-card">
                <div class="s-tag">// SCIENCE</div>
                <div class="s-text">Explain quantum entanglement in simple terms</div>
            </div>
            <div class="suggestion-card">
                <div class="s-tag">// CODE</div>
                <div class="s-text">Write a Python web scraper with BeautifulSoup</div>
            </div>
            <div class="suggestion-card">
                <div class="s-tag">// WRITE</div>
                <div class="s-text">Draft a cold outreach email for a startup</div>
            </div>
            <div class="suggestion-card">
                <div class="s-tag">// PLAN</div>
                <div class="s-text">Create a 7-day travel itinerary for Japan</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Render conversation history ───────────────────────────────────────
for message in active_data["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ── Chat input ────────────────────────────────────────────────────────
user_input = st.chat_input("> initialize query...")

if user_input:
    # Auto-title the thread on first message
    if active_data["title"] == "New Session":
        active_data["title"] = user_input[:38]

    # Append & display user message
    active_data["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Stream assistant response
    with st.chat_message("assistant"):
        placeholder   = st.empty()
        full_response = ""

        for chunk, _meta in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages",
        ):
            if chunk.content:
                full_response += chunk.content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    # Append & persist assistant message
    active_data["messages"].append({"role": "assistant", "content": full_response})
    save_thread(
        active_id,
        active_data["title"],
        active_data["created_at"],
        active_data["messages"],
    )