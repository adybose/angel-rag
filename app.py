import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI(title="RAG Chatbot API")

# Pydantic model for request body
class ChatRequest(BaseModel):
    question: str
    chat_history: list = []

# Initialize vector store and RAG chain (run once at startup)
def initialize_rag():
    # Load and process text files
    documents = []
    docs_dir = "./documents"
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(docs_dir, filename))
            documents.extend(loader.load())

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    # Create embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    # Initialize FAISS vector store
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local("faiss_index")  # Save index to disk

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    # Initialize conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # Create RAG chain
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4}),
        memory=memory
    )

    return rag_chain

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
    return {"message": "RAG Chatbot API is running"}
