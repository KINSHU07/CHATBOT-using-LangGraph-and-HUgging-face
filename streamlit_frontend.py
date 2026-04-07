import streamlit as st
from langgraph_backend import chatbot, load_threads, save_thread, delete_thread
from langchain_core.messages import HumanMessage, BaseMessage
from datetime import datetime
import uuid

st.set_page_config(
    page_title="ThrashChats",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:           #09090B;
    --sidebar-bg:   #0D0D10;
    --surface:      #141417;
    --surface2:     #1C1C20;
    --border:       rgba(255,255,255,0.07);
    --border-hover: rgba(255,255,255,0.14);
    --text:         #FAFAFA;
    --text-dim:     #A1A1AA;
    --text-mute:    #52525B;
    --accent:       #7C6AF7;
    --accent-soft:  rgba(124,106,247,0.12);
    --accent-glow:  rgba(124,106,247,0.25);
    --user-bg:      #1A1A2E;
    --user-border:  rgba(124,106,247,0.3);
    --green:        #22C55E;
    --amber:        #F59E0B;
    --radius:       12px;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Sora', sans-serif;
    color: var(--text);
}

[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
#MainMenu, footer, header { display: none !important; }

.main .block-container {
    max-width: 760px !important;
    padding: 0 1.5rem 6rem !important;
    margin: 0 auto !important;
}

/* ══ SIDEBAR ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

.sb-logo-wrap {
    padding: 1.4rem 1.2rem 1.2rem;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 0.65rem;
}
.sb-icon {
    width: 32px; height: 32px; border-radius: 8px;
    background: var(--accent); display: flex;
    align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    box-shadow: 0 0 16px var(--accent-glow);
}
.sb-brand { font-size: 0.9rem; font-weight: 600; color: var(--text); letter-spacing: -0.01em; }
.sb-version { font-size: 0.6rem; color: var(--text-mute); font-family: 'JetBrains Mono', monospace; margin-top: 2px; }
.sb-section-label {
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--text-mute);
    padding: 1rem 1.2rem 0.4rem;
}

/* All sidebar buttons */
div[data-testid="stButton"] > button {
    background: transparent !important;
    color: var(--text-dim) !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    padding: 0.55rem 0.9rem !important;
    width: 100% !important;
    text-align: left !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    margin-bottom: 1px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    box-shadow: none !important;
    outline: none !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: none !important;
    box-shadow: none !important;
}
div[data-testid="stButton"] > button:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* ── New Chat (first button) ── */
div[data-testid="stButton"]:first-of-type > button {
    background: var(--accent-soft) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(124,106,247,0.25) !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    text-align: center !important;
    padding: 0.65rem 1rem !important;
    margin-bottom: 0.4rem !important;
    letter-spacing: 0 !important;
}
div[data-testid="stButton"]:first-of-type > button:hover {
    background: rgba(124,106,247,0.2) !important;
    box-shadow: 0 0 18px var(--accent-glow) !important;
}

/* ══ TOPBAR ═══════════════════════════════════════════════════════════ */
.topbar {
    position: sticky; top: 0; z-index: 50;
    background: linear-gradient(to bottom, var(--bg) 75%, transparent);
    padding: 1.6rem 0 1rem; margin-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
}
.topbar-title {
    font-size: 0.88rem; font-weight: 500; color: var(--text-dim);
    letter-spacing: -0.01em;
    max-width: 360px; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
}
.topbar-pills { display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap; }
.pill {
    font-size: 0.6rem; font-family: 'JetBrains Mono', monospace;
    color: var(--text-mute); background: var(--surface);
    border: 1px solid var(--border); border-radius: 99px;
    padding: 0.2rem 0.6rem; letter-spacing: 0.04em; white-space: nowrap;
}
.pill-live {
    color: var(--green) !important; border-color: rgba(34,197,94,0.25) !important;
    background: rgba(34,197,94,0.07) !important;
    display: inline-flex; align-items: center; gap: 0.3rem;
}
.pill-smith {
    color: var(--amber) !important; border-color: rgba(245,158,11,0.25) !important;
    background: rgba(245,158,11,0.07) !important;
    display: inline-flex; align-items: center; gap: 0.3rem;
}
.live-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: currentColor; flex-shrink: 0;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* ══ WELCOME ══════════════════════════════════════════════════════════ */
.welcome {
    padding: 5rem 0 3rem;
    display: flex; flex-direction: column; align-items: center;
    animation: fadeUp 0.5s ease both;
}
.welcome-logo {
    width: 54px; height: 54px; border-radius: 15px;
    background: var(--accent); display: flex;
    align-items: center; justify-content: center;
    font-size: 1.6rem; margin-bottom: 1.5rem;
    box-shadow: 0 0 48px var(--accent-glow);
}
.welcome-title {
    font-size: 1.85rem; font-weight: 600; color: var(--text);
    letter-spacing: -0.03em; margin-bottom: 0.5rem; text-align: center;
}
.welcome-sub {
    font-size: 0.88rem; color: var(--text-mute);
    margin-bottom: 2.5rem; text-align: center; line-height: 1.6;
}
.prompt-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 0.6rem; width: 100%; max-width: 560px;
}
.prompt-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 0.9rem 1.1rem;
    cursor: pointer; transition: all 0.2s ease;
}
.prompt-card:hover {
    border-color: var(--border-hover); background: var(--surface2);
    transform: translateY(-1px);
}
.prompt-label {
    font-size: 0.62rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 0.35rem;
}
.prompt-text { font-size: 0.82rem; color: var(--text-dim); line-height: 1.5; }

/* ══ MESSAGES ═════════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 1rem 0 !important;
    gap: 1rem !important; animation: fadeUp 0.25s ease both;
}
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
    width: 28px !important; height: 28px !important;
    min-width: 28px !important; border-radius: 7px !important;
    font-size: 0.75rem !important; margin-top: 4px !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: var(--accent) !important; border: none !important;
    box-shadow: 0 0 12px var(--accent-glow) !important;
}
[data-testid="chatAvatarIcon-user"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border-hover) !important;
    box-shadow: none !important;
}
[data-testid="stChatMessageContent"] {
    background: transparent !important; border: none !important; padding: 0 !important;
}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--user-bg) !important;
    border: 1px solid var(--user-border) !important;
    border-radius: 14px 14px 4px 14px !important;
    padding: 0.75rem 1.1rem !important;
    max-width: 78% !important; margin-left: auto !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: var(--text) !important; font-size: 0.9rem !important;
    line-height: 1.7 !important; font-family: 'Sora', sans-serif !important;
}

/* Assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: transparent !important; border: none !important; padding: 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p {
    color: var(--text) !important; font-size: 0.9rem !important;
    line-height: 1.85 !important; font-family: 'Sora', sans-serif !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 1.2rem !important;
}

/* Code */
[data-testid="stChatMessage"] code {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 5px !important; padding: 0.15rem 0.45rem !important;
    font-size: 0.8rem !important; color: #A78BFA !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stChatMessage"] pre {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-left: 2px solid var(--accent) !important; border-radius: 8px !important;
    padding: 1rem 1.2rem !important; overflow-x: auto !important; margin: 0.5rem 0 !important;
}

/* ══ INPUT BAR ════════════════════════════════════════════════════════ */
[data-testid="stBottom"] {
    background: linear-gradient(to top, var(--bg) 65%, transparent) !important;
    padding: 0.5rem 0 1.5rem !important;
}
[data-testid="stChatInput"] {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 14px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(124,106,247,0.45) !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.08), 0 4px 24px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; border: none !important;
    color: var(--text) !important; font-family: 'Sora', sans-serif !important;
    font-size: 0.88rem !important; padding: 0.9rem 1.1rem !important;
    caret-color: var(--accent) !important; line-height: 1.6 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-mute) !important; }
[data-testid="stChatInputSubmitButton"] button {
    background: var(--accent) !important; border: none !important;
    border-radius: 9px !important; box-shadow: 0 0 14px var(--accent-glow) !important;
    transition: all 0.15s ease !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    box-shadow: 0 0 26px var(--accent-glow) !important;
    transform: scale(1.06) !important;
}

/* ══ SCROLLBAR ════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.1); }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════
if "threads" not in st.session_state:
    st.session_state["threads"] = load_threads()

if not st.session_state["threads"]:
    first_id = str(uuid.uuid4())
    now = datetime.now().strftime("%H:%M")
    st.session_state["threads"] = {
        first_id: {"title": "New Chat", "messages": [], "created_at": now}
    }
    save_thread(first_id, "New Chat", now, [])

if "active_thread" not in st.session_state:
    st.session_state["active_thread"] = next(iter(st.session_state["threads"]))

# Safety guard — active thread must still exist
if st.session_state["active_thread"] not in st.session_state["threads"]:
    st.session_state["active_thread"] = next(iter(st.session_state["threads"]))


# ══════════════════════════════════════════════════════════════════════
#  CALLBACKS — on_click runs BEFORE Streamlit reruns (fixes switch bug)
# ══════════════════════════════════════════════════════════════════════
def switch_thread(tid: str) -> None:
    st.session_state["active_thread"] = tid

def new_session() -> None:
    new_id = str(uuid.uuid4())
    now = datetime.now().strftime("%H:%M")
    st.session_state["threads"][new_id] = {
        "title": "New Chat", "messages": [], "created_at": now
    }
    save_thread(new_id, "New Chat", now, [])
    st.session_state["active_thread"] = new_id


# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo-wrap">
      <div class="sb-icon">⚡</div>
      <div>
        <div class="sb-brand">ThrashChats</div>
        <div class="sb-version">v3.0 · gemma-3-27b · langsmith</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0.8rem 0.8rem 0.3rem">', unsafe_allow_html=True)
    st.button(
        "＋  New Chat",
        key="new_chat",
        on_click=new_session,
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section-label">Recents</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 0.5rem 1rem">', unsafe_allow_html=True)

    for tid, tdata in list(st.session_state["threads"].items()):
        is_active = tid == st.session_state["active_thread"]
        label = tdata["title"]
        short = (label[:26] + "…") if len(label) > 26 else label
        display = f"● {short}" if is_active else f"  {short}"

        st.button(
            display,
            key=f"thread_{tid}",
            on_click=switch_thread,
            args=(tid,),
            use_container_width=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  RESOLVE ACTIVE THREAD
# ══════════════════════════════════════════════════════════════════════
active_id   = st.session_state["active_thread"]
active_data = st.session_state["threads"][active_id]
CONFIG      = {"configurable": {"thread_id": active_id}}

# Sanitise title for safe HTML injection
safe_title = (
    active_data["title"]
    .replace("&", "&amp;")
    .replace("<", "&lt;")
    .replace(">", "&gt;")
    .replace('"', "&quot;")
)

# ══════════════════════════════════════════════════════════════════════
#  TOPBAR
# ══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="topbar">
    <span class="topbar-title">{safe_title}</span>
    <div class="topbar-pills">
        <span class="pill pill-live"><span class="live-dot"></span>online</span>
        <span class="pill pill-smith"><span class="live-dot"></span>LangSmith</span>
        <span class="pill">gemma-3-27b</span>
        <span class="pill">SQLite</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  WELCOME SCREEN  (empty thread only)
# ══════════════════════════════════════════════════════════════════════
if not active_data["messages"]:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-logo">⚡</div>
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-sub">Ask anything — code, research, writing, analysis.</div>
        <div class="prompt-grid">
            <div class="prompt-card">
                <div class="prompt-label">Science</div>
                <div class="prompt-text">Explain quantum entanglement in simple terms</div>
            </div>
            <div class="prompt-card">
                <div class="prompt-label">Code</div>
                <div class="prompt-text">Write a Python web scraper with BeautifulSoup</div>
            </div>
            <div class="prompt-card">
                <div class="prompt-label">Write</div>
                <div class="prompt-text">Draft a cold outreach email for a startup</div>
            </div>
            <div class="prompt-card">
                <div class="prompt-label">Plan</div>
                <div class="prompt-text">Create a 7-day travel itinerary for Japan</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  CONVERSATION HISTORY
# ══════════════════════════════════════════════════════════════════════
for msg in active_data["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ══════════════════════════════════════════════════════════════════════
#  CHAT INPUT
# ══════════════════════════════════════════════════════════════════════
user_input = st.chat_input("Message ThrashChats...")

if user_input:
    # Auto-title on first message
    if active_data["title"] == "New Chat":
        active_data["title"] = user_input[:40]

    # Show & store user message
    active_data["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Stream assistant response
    with st.chat_message("assistant"):
        placeholder   = st.empty()
        full_response = ""

        try:
            # stream_mode="messages" yields (chunk, metadata) tuples
            for chunk, _meta in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # chunk can be a BaseMessage or plain string depending on version
                content = (
                    chunk.content
                    if isinstance(chunk, BaseMessage)
                    else str(chunk)
                )
                if content:
                    full_response += content
                    placeholder.markdown(full_response + "▌")

        except Exception as e:
            full_response = f"⚠️ Error: {e}"

        placeholder.markdown(full_response)

    # Persist
    active_data["messages"].append({"role": "assistant", "content": full_response})
    save_thread(
        active_id,
        active_data["title"],
        active_data["created_at"],
        active_data["messages"],
    )