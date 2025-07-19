import streamlit as st
import uuid
from sidebar import display_sidebar
from chat_interface import display_chat_interface

st.title("Langchain RAG Chatbot")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state or st.session_state.session_id is None:
    st.session_state.session_id = str(uuid.uuid4())

# Display the sidebar and chat interface
display_sidebar()
display_chat_interface()
