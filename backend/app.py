from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan Events
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("BundesFAQ RAG Chatbot API started")
    logger.info(f"ChromaDB Status: {'Loaded' if vectorstore else 'Not loaded'}")
    yield
    logger.info("BundesFAQ RAG Chatbot API stopped")

#  Init FastAPI
app = FastAPI(
    title="BundesFAQ RAG Chatbot API",
    description="RAG-basierter Chatbot für deutsche FAQ-Daten",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ENV & Models
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
else:
    logger.info(f"OPENAI_API_KEY loaded: {OPENAI_API_KEY[:5]}***")

embedding = OpenAIEmbeddings(model="text-embedding-3-small")

# Default Chroma persistence now lives in backend/vectorstore (configurable via VECTORSTORE_DIR)
# Location of the Chroma vectorstore. Override via env VAR VECTORSTORE_DIR if deploying elsewhere.
persist_directory = os.getenv("VECTORSTORE_DIR", "./backend/vectorstore")

if not os.path.exists(persist_directory):
    logger.warning(f"ChromaDB directory not found: {persist_directory}")
    logger.info("Bitte zuerst das Notebook ausfuehren, um die Vektordatenbank zu erstellen")

try:
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding,
        collection_name="bundesfaq_rag_collection"
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    logger.info(f"ChromaDB loaded successfully from {persist_directory}")
except Exception as e:
    logger.error(f"Failed to load ChromaDB: {e}")
    vectorstore = None
    retriever = None

# Prompt + LLM + Chain
system_prompt = """You are a helpful assistant for question-answering tasks.  
Use the retrieved context below to answer the user's question.  

- If the answer is not in the context, say: "I don't know based on the provided documents."  
- Be concise (max. 3 sentences).  
- Ground your answer in the context, don't invent facts.  

Context:
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

if retriever:
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)
else:
    rag_chain = None

# API Models
class ChatRequest(BaseModel):
    question: str

    class Config:
        json_schema_extra = {
            "example": {"question": "Was ist GovData.de?"}
        }

class ChatResponse(BaseModel):
    answer: str
    sources_count: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "GovData.de ist das zentrale Metadatenportal für offene Verwaltungsdaten...",
                "sources_count": 3
            }
        }

class HealthResponse(BaseModel):
    status: str
    vectorstore_loaded: bool
    vectorstore_path: str

# API Routes
@app.get("/", tags=["Root"])
async def root():
    """Basis-Endpoint für API-Info"""
    return {
        "message": "BundesFAQ RAG Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Gesundheitscheck der API und ChromaDB"""
    return HealthResponse(
        status="healthy" if rag_chain else "degraded",
        vectorstore_loaded=vectorstore is not None,
        vectorstore_path=persist_directory
    )

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """Hauptendpoint für RAG-basierte Chats"""
    if not rag_chain:
        raise HTTPException(
            status_code=503,
            detail="RAG system not available. ChromaDB not loaded."
        )
    try:
        response = rag_chain.invoke({"input": request.question})

        docs = retriever.get_relevant_documents(request.question)
        sources_count = len(docs)

        return ChatResponse(
            answer=response["answer"],
            sources_count=sources_count
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
