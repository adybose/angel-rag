import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import initialize_rag, logger  # Import the RAG initialization function


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
        # Format chat history for LangChain
        formatted_history = []
        for human, ai in request.chat_history:
            formatted_history.append(("human", human))
            formatted_history.append(("ai", ai))

        # Invoke RAG chain
        response = rag_chain.invoke({
            "question": request.question,
            "chat_history": formatted_history
        })

        # Check if retrieved documents are relevant
        if not response["source_documents"] or not any(doc.page_content.strip() for doc in response["source_documents"]):
            logger.info(f"No relevant documents found for question: {request.question}")
            return {
                "answer": "I don't know",
                "chat_history": request.chat_history + [[request.question, "I don't know"]]
            }

        logger.info(f"Processed question: {request.question}")
        return {
            "answer": response["answer"],
            "chat_history": request.chat_history + [[request.question, response["answer"]]]
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "AngelOne Support Chatbot API is running"}
