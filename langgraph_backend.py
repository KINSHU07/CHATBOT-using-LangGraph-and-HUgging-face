from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Any, Iterator
from langchain_core.messages import BaseMessage, AIMessage, AIMessageChunk, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()

# ← works both locally (.env) and on Streamlit Cloud (Secrets)
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not token:
    try:
        import streamlit as st
        token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
    except Exception:
        raise ValueError("❌ HUGGINGFACEHUB_API_TOKEN not found! Add it to Streamlit Secrets.")

client = InferenceClient(
    model="Qwen/Qwen2.5-72B-Instruct",
    token=token
)

class StreamingHFChat(BaseChatModel):
    client: Any
    class Config:
        arbitrary_types_allowed = True
    @property
    def _llm_type(self): return "hf"

    def _convert_messages(self, messages):
        hf_msgs = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, SystemMessage):
                role = "system"
            else:
                continue
            if hf_msgs and hf_msgs[-1]["role"] == role:
                continue
            hf_msgs.append({"role": role, "content": msg.content})
        return hf_msgs

    def _generate(self, messages, **kwargs):
        hf_msgs = self._convert_messages(messages)
        res = self.client.chat_completion(hf_msgs, max_tokens=512)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=res.choices[0].message.content))])

    def _stream(self, messages, **kwargs) -> Iterator[ChatGenerationChunk]:
        hf_msgs = self._convert_messages(messages)
        for chunk in self.client.chat_completion(hf_msgs, max_tokens=512, stream=True):
            if not chunk.choices:
                continue
            token = chunk.choices[0].delta.content or ""
            if token:
                yield ChatGenerationChunk(message=AIMessageChunk(content=token))

llm = StreamingHFChat(client=client)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

checkpointer = InMemorySaver()
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# ```

# Only one thing changed — the token block at the top. Now go to Streamlit Cloud → **Manage app** → **Secrets** and make sure this is there exactly:
# ```
# HUGGINGFACEHUB_API_TOKEN = "hf_xxxxxxxxxxxxxxxx"