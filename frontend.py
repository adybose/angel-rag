import streamlit as st
import requests
import json

# Streamlit app configuration
st.set_page_config(page_title="AngelOne Support Chatbot", page_icon="🤖")
st.title("AngelOne Support Chatbot")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input for API URL
api_url = "https://angel-rag-production.up.railway.app/chat"

# User input for question
question = st.text_input("Ask a question:", key="question_input")

# Send button
if st.button("Send"):
    if question:
        try:
            # Prepare payload
            payload = {
                "question": question,
                "chat_history": st.session_state.chat_history
            }

            # Send POST request to FastAPI /chat endpoint
            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )

            # Check response status
            if response.status_code == 200:
                result = response.json()
                st.session_state.chat_history = result["chat_history"]
                st.success(f"Answer: {result['answer']}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API: {str(e)}")
    else:
        st.warning("Please enter a question and valid API URL.")

# Display chat history
if st.session_state.chat_history:
    st.subheader("Chat History")
    for human, ai in st.session_state.chat_history[-2::-1]:
        st.write(f"**Question**: {human}")
        st.write(f"**Answer**: {ai}")
        st.markdown("---")
