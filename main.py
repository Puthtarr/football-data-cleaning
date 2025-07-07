import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="DeepPlayr", layout="centered")

# Background
st.markdown(
    """
    <style>
    body {
        background-color: #000000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Show logo
logo_path = os.path.join("images", "DeepPlayr_logo.png")
st.image(logo_path, width=750)

# Welcome
st.title("Welcome to DeepPlayr")
st.subheader("⚽ Choose a feature from the sidebar on the left ⬅️")
