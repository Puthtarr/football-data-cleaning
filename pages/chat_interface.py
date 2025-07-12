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

            # get SQL from LLM build (maybe not appear)
            sql_query = result["intermediate_steps"][0] if "intermediate_steps" in result else "Can't Create SQL"
            final_answer = result["result"]

            st.subheader("🧠 SQL from AI:")
            st.code(sql_query, language="sql")

            st.subheader("✅ Answer:")
            st.success(final_answer)

        except Exception as e:
            st.error(f"An Error: {e}")
