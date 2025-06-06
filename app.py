import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import initialize_rag  # Import the RAG initialization function


# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI(title="AngelOne Support Chatbot API")

# Pydantic model for request body
class ChatRequest(BaseModel):
    question: str
    chat_history: list = []


# Initialize RAG chain at startup
rag_chain = initialize_rag()


# API endpoint for chat
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Format chat history for LangChain (list of [human, ai] pairs)
        formatted_history = []
        for human, ai in request.chat_history:
            formatted_history.append(("human", human))
            formatted_history.append(("ai", ai))

        # Invoke RAG chain
        response = rag_chain.invoke({
            "question": request.question,
            "chat_history": formatted_history
        })

        return {
            "answer": response["answer"],
            "chat_history": request.chat_history + [[request.question, response["answer"]]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "AngelOne Support Chatbot API is running"}
