import streamlit as st
import sqlite3, json, pandas as pd
from langgraph_backend import DB_PATH

conn = sqlite3.connect(DB_PATH, check_same_thread=False)

st.title("🗄️ DB Inspector")

st.subheader("thread_meta")
rows = conn.execute("SELECT thread_id, title, created_at, messages FROM thread_meta").fetchall()
for row in rows:
    with st.expander(f"{row[1]} — {row[2]}"):
        st.json(json.loads(row[3]))

st.subheader("checkpoints (LangGraph)")
df = pd.read_sql("SELECT thread_id, checkpoint_id, created_at FROM checkpoints", conn)
st.dataframe(df)