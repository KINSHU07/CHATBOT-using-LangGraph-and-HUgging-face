import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

st.set_page_config(
    page_title="ThrashChats",        # ← changed
    page_icon="⬡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:        #1C1917;
    --bg2:       #231F1C;
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
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu, footer, header { display: none !important; visibility: hidden !important; }
.main .block-container { max-width: 720px !important; padding: 0 1.25rem 7rem !important; margin: 0 auto !important; }

.topbar { position: sticky; top: 0; z-index: 100; background: linear-gradient(to bottom, var(--bg) 80%, transparent); padding: 1.5rem 0 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between; }
.topbar-brand { display: flex; align-items: center; gap: 0.6rem; }
.topbar-icon { width: 30px; height: 30px; background: linear-gradient(135deg, var(--accent), var(--accent2)); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; }
.topbar-name { font-family: 'Instrument Serif', serif; font-size: 1.15rem; color: var(--text); letter-spacing: -0.01em; }
.topbar-badge { font-size: 0.68rem; color: var(--text-mute); background: var(--surface); border: 1px solid var(--border); padding: 0.2rem 0.6rem; border-radius: 20px; letter-spacing: 0.04em; text-transform: uppercase; font-weight: 500; }

.welcome { padding: 3.5rem 0 2rem; text-align: center; animation: fadeUp 0.5s ease both; }
.welcome-title { font-family: 'Instrument Serif', serif; font-size: 2.4rem; color: var(--text); letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 0.6rem; }
.welcome-title em { color: var(--accent); font-style: italic; }
.welcome-sub { font-size: 0.88rem; color: var(--text-mute); font-weight: 300; letter-spacing: 0.01em; }
.suggestion-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-top: 2.5rem; text-align: left; }
.suggestion-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 0.85rem 1rem; cursor: pointer; transition: border-color 0.2s, background 0.2s; }
.suggestion-card:hover { border-color: var(--accent); background: var(--user-bg); }
.suggestion-card .s-icon { font-size: 1rem; margin-bottom: 0.3rem; }
.suggestion-card .s-text { font-size: 0.82rem; color: var(--text-dim); line-height: 1.4; font-weight: 400; }

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

[data-testid="stBottom"] { background: linear-gradient(to top, var(--bg) 75%, transparent) !important; padding: 1rem 0 1.5rem !important; }
[data-testid="stChatInput"] { background: var(--surface) !important; border: 1px solid var(--border2) !important; border-radius: 14px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important; transition: border-color 0.2s, box-shadow 0.2s !important; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent) !important; box-shadow: 0 4px 24px rgba(217,123,79,0.12) !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; border: none !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; font-weight: 300 !important; padding: 0.8rem 1rem !important; caret-color: var(--accent) !important; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-mute) !important; }
[data-testid="stChatInputSubmitButton"] button { background: linear-gradient(135deg, var(--accent), var(--accent2)) !important; border: none !important; border-radius: 9px !important; transition: opacity 0.2s !important; }
[data-testid="stChatInputSubmitButton"] button:hover { opacity: 0.8 !important; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="topbar-brand">
        <div class="topbar-icon">⬡</div>
        <span class="topbar-name">ThrashChats</span>  <!-- ← changed -->
    </div>
    <span class="topbar-badge">LangGraph · Qwen · HF</span>
</div>
""", unsafe_allow_html=True)

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if not st.session_state['message_history']:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-title">Welcome to <em>ThrashChats</em></div>  <!-- ← changed -->
        <div class="welcome-sub">Ask me anything — I think, I reason, I help.</div>
        <div class="suggestion-grid">
            <div class="suggestion-card"><div class="s-icon">✦</div><div class="s-text">Explain quantum entanglement simply</div></div>
            <div class="suggestion-card"><div class="s-icon">⌘</div><div class="s-text">Write a Python web scraper</div></div>
            <div class="suggestion-card"><div class="s-icon">◈</div><div class="s-text">Draft a professional email</div></div>
            <div class="suggestion-card"><div class="s-icon">◎</div><div class="s-text">Plan a 7-day Italy itinerary</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input('Message ThrashChats...')   # ← changed

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