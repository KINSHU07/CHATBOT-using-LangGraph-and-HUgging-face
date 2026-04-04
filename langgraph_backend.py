from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Any, Iterator
from langchain_core.messages import (
    BaseMessage, AIMessage, AIMessageChunk,
    HumanMessage, SystemMessage
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────
DB_PATH = "thrashchats.db"

# ── HuggingFace Token ─────────────────────────────────────────────────
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not token:
    try:
        import streamlit as st
        token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
    except Exception:
        raise ValueError("❌ HUGGINGFACEHUB_API_TOKEN not found in .env or Streamlit secrets.")

# ── HuggingFace Inference Client ──────────────────────────────────────
hf_client = InferenceClient(
    model="google/gemma-3-27b-it",
    token=token
)

# ── Streaming LangChain-compatible LLM wrapper ────────────────────────
class StreamingHFChat(BaseChatModel):
    client: Any

    class Config:
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        return "streaming-hf-chat"

    def _convert_messages(self, messages: list[BaseMessage]) -> list[dict]:
        """Convert LangChain messages → HuggingFace chat format.
        Skips consecutive same-role messages to avoid API errors."""
        result = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, SystemMessage):
                role = "system"
            else:
                continue
            # Deduplicate consecutive same-role messages
            if result and result[-1]["role"] == role:
                continue
            result.append({"role": role, "content": msg.content})
        return result

    def _generate(self, messages: list[BaseMessage], **kwargs) -> ChatResult:
        hf_msgs = self._convert_messages(messages)
        response = self.client.chat_completion(hf_msgs, max_tokens=512)
        content = response.choices[0].message.content
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    def _stream(self, messages: list[BaseMessage], **kwargs) -> Iterator[ChatGenerationChunk]:
        hf_msgs = self._convert_messages(messages)
        stream = self.client.chat_completion(hf_msgs, max_tokens=512, stream=True)
        for chunk in stream:
            if not chunk.choices:
                continue
            token_text = chunk.choices[0].delta.content or ""
            if token_text:
                yield ChatGenerationChunk(message=AIMessageChunk(content=token_text))

llm = StreamingHFChat(client=hf_client)

# ── LangGraph State & Node ────────────────────────────────────────────
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ── Graph ─────────────────────────────────────────────────────────────
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# ── SQLite: shared connection for checkpointer + thread metadata ───────
# check_same_thread=False is required for Streamlit's threaded environment
db_conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# Create thread_meta table in the same DB file as LangGraph's checkpointer
db_conn.execute("""
    CREATE TABLE IF NOT EXISTS thread_meta (
        thread_id  TEXT PRIMARY KEY,
        title      TEXT NOT NULL,
        created_at TEXT NOT NULL,
        messages   TEXT NOT NULL DEFAULT '[]'
    )
""")
db_conn.commit()

# ── LangGraph compiled chatbot with SQLite checkpointer ───────────────
checkpointer = SqliteSaver(db_conn)
chatbot = graph.compile(checkpointer=checkpointer)

# ── Thread metadata helpers (used by the Streamlit frontend) ──────────
import json
from datetime import datetime

def load_threads() -> dict:
    """Return all threads ordered newest-first as {thread_id: {...}}."""
    rows = db_conn.execute(
        "SELECT thread_id, title, created_at, messages FROM thread_meta ORDER BY created_at DESC"
    ).fetchall()
    return {
        row[0]: {
            "title":      row[1],
            "created_at": row[2],
            "messages":   json.loads(row[3]),
        }
        for row in rows
    }

def save_thread(thread_id: str, title: str, created_at: str, messages: list) -> None:
    """Upsert a thread's metadata into SQLite."""
    db_conn.execute(
        """
        INSERT INTO thread_meta (thread_id, title, created_at, messages)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(thread_id) DO UPDATE SET
            title      = excluded.title,
            messages   = excluded.messages
        """,
        (thread_id, title, created_at, json.dumps(messages)),
    )
    db_conn.commit()

def delete_thread(thread_id: str) -> None:
    """Remove a thread's metadata (LangGraph checkpoint rows stay for safety)."""
    db_conn.execute("DELETE FROM thread_meta WHERE thread_id = ?", (thread_id,))
    db_conn.commit()