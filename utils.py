import logging
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    # # Initialize FAISS vector store
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
