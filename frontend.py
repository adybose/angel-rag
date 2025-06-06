import streamlit as st
import requests

st.title("AngelOne Support Chatbot")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.text_input("Ask a question:")
if st.button("Send"):
    response = requests.post(
        "https://angel-rag-production.up.railway.app/chat",
        json={"question": question, "chat_history": st.session_state.chat_history}
    ).json()
    if "answer" in response:
        st.write(f"**Answer**: \n{response['answer']}")
        st.session_state.chat_history = response["chat_history"]
    elif "detail" in response:
        st.error(f"Error: {response['detail']}")
    else:
        st.error("Unexpected response from server.")
