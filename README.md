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
