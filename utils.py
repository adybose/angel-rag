import logging
import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Custom prompt template to enforce document-based answers
CUSTOM_PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions strictly based on the provided context from documents. 
If the question is outside the scope of the context or no relevant information is found, respond with "I don't know".
Do not use any external knowledge or make assumptions beyond the context.

Context:
{context}

Question: {question}

Answer:
"""


# Initialize vector store and RAG chain (run once at startup)
def initialize_rag():
    # Load and process text files
    documents = []
    docs_dir = "./documents"
    if not os.path.exists(docs_dir):
        logger.error("Documents directory not found")
        raise FileNotFoundError("Documents directory not found")

    for filename in os.listdir(docs_dir):
        file_path = os.path.join(docs_dir, filename)
        try:
            if filename.endswith(".txt"):
                loader = TextLoader(file_path)
                documents.extend(loader.load())
            elif filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
                documents.extend(loader.load())
            else:
                logger.warning(f"Unsupported file type: {filename}")
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            continue
        
    if not documents:
        logger.error("No valid documents found in documents directory")
        raise ValueError("No valid documents found")

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
    # Create custom prompt
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=CUSTOM_PROMPT_TEMPLATE
    )

    # Create RAG chain
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    logger.info("RAG chain initialized successfully")
    return rag_chain
