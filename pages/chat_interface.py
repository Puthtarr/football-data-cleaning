import streamlit as st
from src.llm_chat_engine import get_llm_chain

st.set_page_config(page_title="DeepPlayr AI Chat", layout="wide")
st.title("⚽ DeepPlayr AI Chat Interface")

user_question = st.text_input("Ask AI ได้เลย:")

if user_question:
    with st.spinner("Processing..."):
        try:
            chain = get_llm_chain()
            result = chain(user_question)

            # ✅ ตอบกลับเฉพาะ SQL Query
            sql_query = result["result"]

            st.subheader("🧠 SQL from AI:")
            st.code(sql_query, language="sql")

        except Exception as e:
            st.error(f"An Error: {e}")
