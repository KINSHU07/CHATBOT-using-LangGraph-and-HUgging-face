import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Load conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here...')

if user_input:
    # Show user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Stream assistant response token by token
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
                placeholder.markdown(full_response + "▌")  # typing cursor effect

        placeholder.markdown(full_response)  # final clean render

    st.session_state['message_history'].append({'role': 'assistant', 'content': full_response})