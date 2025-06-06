# angel-rag [WIP]

This repository is a simple RAG chatbot application to answer AngelOne Support questions using AI.


### Installation
```bash
git clone https://github.com/adybose/angel-rag.git
cd angel-rag
virtualenv angelenv
source angelenv/bin/activate
pip install -r requirements.txt
```
Add your OpenAI API key in a `.env` file like:
`OPENAI_API_KEY=sk-proj-pqxx****YB9A`


### Usage
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

### Deployment
To deploy the FastAPI app, we are using Vercel for it's ease of use for a project of this scale.

To deploy the Streamlit chatbot frontend, we are using Streamlit Community Cloud with the API endpoint configured based on the FastAPI application URL generated after the Vercel deployment.
