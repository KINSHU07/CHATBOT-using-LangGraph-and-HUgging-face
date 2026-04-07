# ── Load env FIRST — before any LangChain imports ────────────────────
from dotenv import load_dotenv
load_dotenv()

import os

# ── LangSmith observability ───────────────────────────────────────────
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"]   = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"]    = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "ThrashChats")

# ── SqliteSaver: try both import paths (handles all langgraph versions) ─
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    try:
        from langgraph_checkpoint_sqlite import SqliteSaver
    except ImportError:
        raise ImportError(
            "SQLite checkpointer not found.\n"
            "Run: pip install langgraph-checkpoint-sqlite"
        )

# ── LangChain / LangGraph imports ─────────────────────────────────────
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import (
    BaseMessage, AIMessage, AIMessageChunk,
    HumanMessage, SystemMessage,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import RunnableConfig
from huggingface_hub import InferenceClient
from typing import TypedDict, Annotated, Any, Iterator
import sqlite3
import json

# ── Config ────────────────────────────────────────────────────────────
DB_PATH = "thrashchats.db"

# ── HuggingFace token ─────────────────────────────────────────────────
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not token:
    try:
        import streamlit as st
        token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
    except Exception:
        raise ValueError(
            "❌ HUGGINGFACEHUB_API_TOKEN not found in .env or Streamlit secrets."
        )

# ── HuggingFace Inference Client ──────────────────────────────────────
hf_client = InferenceClient(
    model="google/gemma-3-27b-it",
    token=token,
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
        """Convert LangChain messages → HuggingFace format.
        Deduplicates consecutive same-role messages to avoid API errors."""
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
            # Skip consecutive duplicate roles
            if result and result[-1]["role"] == role:
                continue
            result.append({"role": role, "content": msg.content})
        return result

    def _generate(self, messages: list[BaseMessage], **kwargs) -> ChatResult:
        hf_msgs = self._convert_messages(messages)
        response = self.client.chat_completion(hf_msgs, max_tokens=1024)
        content = response.choices[0].message.content
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))]
        )

    def _stream(self, messages: list[BaseMessage], **kwargs) -> Iterator[ChatGenerationChunk]:
        hf_msgs = self._convert_messages(messages)
        stream = self.client.chat_completion(hf_msgs, max_tokens=1024, stream=True)
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield ChatGenerationChunk(message=AIMessageChunk(content=delta))

llm = StreamingHFChat(client=hf_client)

# ── LangGraph state ───────────────────────────────────────────────────
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ── Chat node ─────────────────────────────────────────────────────────
def chat_node(state: ChatState) -> dict:
    response = llm.invoke(
        state["messages"],
        config=RunnableConfig(run_name="ThrashChats · gemma-3-27b"),
    )
    return {"messages": [response]}

# ── Build graph ───────────────────────────────────────────────────────
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# ── Shared SQLite connection ──────────────────────────────────────────
# isolation_level=None → autocommit; check_same_thread=False for Streamlit
db_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
db_conn.execute("PRAGMA journal_mode=WAL")   # prevents DB locked errors

# Thread metadata table (shares the same DB file as LangGraph checkpoints)
db_conn.execute("""
    CREATE TABLE IF NOT EXISTS thread_meta (
        thread_id  TEXT PRIMARY KEY,
        title      TEXT NOT NULL,
        created_at TEXT NOT NULL,
        messages   TEXT NOT NULL DEFAULT '[]'
    )
""")
db_conn.commit()

# ── LangGraph chatbot ─────────────────────────────────────────────────
checkpointer = SqliteSaver(db_conn)
chatbot = graph.compile(checkpointer=checkpointer)

# ── Thread metadata helpers ───────────────────────────────────────────
def load_threads() -> dict:
    """Return all threads ordered newest-first as {thread_id: {...}}."""
    rows = db_conn.execute(
        "SELECT thread_id, title, created_at, messages "
        "FROM thread_meta ORDER BY created_at DESC"
    ).fetchall()
    return {
        row[0]: {
            "title":      row[1],
            "created_at": row[2],
            "messages":   json.loads(row[3]),
        }
        for row in rows
    }

def save_thread(
    thread_id: str,
    title: str,
    created_at: str,
    messages: list,
) -> None:
    """Upsert thread metadata into SQLite."""
    db_conn.execute(
        """
        INSERT INTO thread_meta (thread_id, title, created_at, messages)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(thread_id) DO UPDATE SET
            title    = excluded.title,
            messages = excluded.messages
        """,
        (thread_id, title, created_at, json.dumps(messages)),
    )
    db_conn.commit()

def delete_thread(thread_id: str) -> None:
    """Remove a thread's metadata row."""
    db_conn.execute(
        "DELETE FROM thread_meta WHERE thread_id = ?", (thread_id,)
    )
    db_conn.commit()