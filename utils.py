import logging
import os
import boto3
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Download FAISS index from S3
def download_faiss_index(bucket, prefix):
    s3 = boto3.client("s3")
    os.makedirs("faiss_index", exist_ok=True)
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if "Contents" not in response:
            logger.error("No FAISS index files found in S3")
            raise FileNotFoundError("No FAISS index files found in S3")
        for obj in response["Contents"]:
            s3.download_file(bucket, obj["Key"], f"faiss_index/{os.path.basename(obj['Key'])}")
        logger.info("FAISS index downloaded from S3")
    except Exception as e:
        logger.error(f"Failed to download FAISS index: {str(e)}")
        raise


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
    # Download FAISS index from S3 if not present
    # if not os.path.exists("faiss_index"):
    #     download_faiss_index("angel-vector-store-index", "faiss_index/")
    # vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

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
