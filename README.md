# angel-rag

This repository is a simple RAG chatbot application to answer AngelOne Support questions using AI. The application is built with FastAPI to provide a RESTful backend API which uses Langchain to serves answers to user queries based on documents stored in a FAISS Vector Database and generate answers using an LLM.
The frontend is a simple chatbot client built using Streamlit.


## Architecture Overview

### Backend API (FastAPI)

The backend is a FastAPI application (app.py) that exposes a /chat endpoint for user queries.
On startup, it initializes a RAG pipeline using LangChain, OpenAI, and FAISS (see utils.py).

### Document Processing & Vector Store

Text documents are scraped into the documents directory.
On initialization, all `.txt` files in documents are loaded and split into chunks.
Each chunk is embedded using OpenAI's embedding model.
Embeddings are stored in a FAISS vector database for efficient similarity search.

### RAG Chain (LangChain)

When a user asks a question, the system retrieves relevant document chunks from FAISS using vector similarity.
The retrieved context is passed to an OpenAI LLM (via LangChain) to generate a conversational answer.
Conversation history is managed using LangChain's ConversationBufferMemory.

### Frontend (Streamlit)

The chatbot frontend is deployed separately (e.g., on Streamlit Community Cloud) and communicates with the FastAPI backend via HTTP API calls.

The main benefits of this architecture is that it enables efficient, context-aware question answering over custom documents, with a clear separation between the API backend and the user-facing frontend. The application is built with modular components (LangChain, OpenAI, FAISS), making it easy to swap models or add features.



## Installation
```bash
git clone https://github.com/adybose/angel-rag.git
cd angel-rag
virtualenv angelenv
source angelenv/bin/activate
pip install -r requirements.txt
```
Add your OpenAI API key in a `.env` file like:
`OPENAI_API_KEY=sk-proj-pqxx****YB9A`


## Usage
Scrape the data from https://angeone.in/support into /documents:
```bash
python scrape.py
```
Run the FastAPI app:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```
Query the API via `curl`:
```bash
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"question": "How to add funds", "chat_history": []}'
```

## Deployment
To deploy the FastAPI app, we are using Railway for it's ease of use.

To deploy the chatbot frontend, we are using Streamlit Community Cloud with the API endpoint configured based on the FastAPI application URL generated after the Vercel deployment.
