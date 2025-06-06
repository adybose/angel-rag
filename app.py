from fastapi import FastAPI, HTTPException


# Initialize FastAPI app
app = FastAPI(title="RAG Chatbot API")

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}
