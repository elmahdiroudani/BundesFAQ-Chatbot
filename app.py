from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os
import json
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from enum import Enum

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
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],  
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

persist_directory = "./src/backend/chroma_db"

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

# API Models matching frontend expectations
class RetrievalMode(str, Enum):
    hybrid = "hybrid"
    vectors = "vectors"
    text = "text"

class ChatAppRequestOverrides(BaseModel):
    retrieval_mode: Optional[RetrievalMode] = None
    semantic_ranker: Optional[bool] = None
    query_rewriting: Optional[bool] = None
    reasoning_effort: Optional[str] = "medium"
    temperature: Optional[float] = 0.1
    top: Optional[int] = 3
    suggest_followup_questions: Optional[bool] = True
    send_text_sources: bool = True
    send_image_sources: bool = False
    search_text_embeddings: bool = True
    search_image_embeddings: bool = False
    language: str = "de"
    use_agentic_retrieval: bool = False

class ResponseMessage(BaseModel):
    content: str
    role: str

class Thoughts(BaseModel):
    title: str
    description: Any

class DataPoints(BaseModel):
    text: List[str]
    images: List[str]
    citations: List[str]

class ResponseContext(BaseModel):
    data_points: DataPoints
    followup_questions: Optional[List[str]]
    thoughts: List[Thoughts]

class ChatAppRequestContext(BaseModel):
    overrides: Optional[ChatAppRequestOverrides] = None

class ChatAppRequest(BaseModel):
    messages: List[ResponseMessage]
    context: Optional[ChatAppRequestContext] = None
    session_state: Optional[Any] = None

class ChatAppResponse(BaseModel):
    message: ResponseMessage
    delta: ResponseMessage
    context: ResponseContext
    session_state: Optional[Any] = None

class Config(BaseModel):
    defaultReasoningEffort: str = "medium"
    showMultimodalOptions: bool = False
    showSemanticRankerOption: bool = True
    showQueryRewritingOption: bool = True
    showReasoningEffortOption: bool = False
    streamingEnabled: bool = True
    showVectorOption: bool = True
    showUserUpload: bool = False  # Deaktiviert
    showLanguagePicker: bool = False  # Deaktiviert - nur Deutsch
    showSpeechInput: bool = False
    showSpeechOutputBrowser: bool = False
    showSpeechOutputAzure: bool = False
    showChatHistoryBrowser: bool = True
    showChatHistoryCosmos: bool = False
    showAgenticRetrievalOption: bool = False
    ragSearchTextEmbeddings: bool = True
    ragSearchImageEmbeddings: bool = False
    ragSendTextSources: bool = True
    ragSendImageSources: bool = False

class HealthResponse(BaseModel):
    status: str
    vectorstore_loaded: bool
    vectorstore_path: str

# Helper functions
def generate_followup_questions(answer: str) -> List[str]:
    """Generate follow-up questions based on the answer"""
    followup_questions = [
        "Können Sie mehr Details dazu erklären?",
        "Gibt es weitere Informationen zu diesem Thema?",
        "Welche rechtlichen Aspekte sind wichtig?"
    ]
    return followup_questions

def create_chat_response(answer: str, sources: List[str], followup_questions: List[str]) -> ChatAppResponse:
    """Create a standardized chat response"""
    return ChatAppResponse(
        message=ResponseMessage(content=answer, role="assistant"),
        delta=ResponseMessage(content="", role="assistant"),
        context=ResponseContext(
            data_points=DataPoints(
                text=sources,
                images=[],
                citations=sources
            ),
            followup_questions=followup_questions,
            thoughts=[
                Thoughts(
                    title="Recherche",
                    description=f"Gefunden {len(sources)} relevante Dokumente in der Wissensdatenbank"
                )
            ]
        ),
        session_state=None
    )

# API Routes
@app.get("/", tags=["Root"])
async def root():
    """Basis-Endpoint für API-Info"""
    return {
        "message": "BundesFAQ RAG Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/config", response_model=Config, tags=["Configuration"])
async def get_config():
    """Get configuration settings for the frontend"""
    return Config()

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Gesundheitscheck der API und ChromaDB"""
    return HealthResponse(
        status="healthy" if rag_chain else "degraded",
        vectorstore_loaded=vectorstore is not None,
        vectorstore_path=persist_directory
    )

@app.post("/ask", response_model=ChatAppResponse, tags=["Chat"])
async def ask(request: ChatAppRequest):
    """Single question-answer endpoint (non-streaming)"""
    if not rag_chain:
        raise HTTPException(
            status_code=503,
            detail="RAG system not available. ChromaDB not loaded."
        )
    
    try:
        # Get the last message content
        last_message = request.messages[-1] if request.messages else None
        if not last_message:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        question = last_message.content
        
        # Get response from RAG chain
        response = rag_chain.invoke({"input": question})
        
        # Get source documents
        docs = retriever.invoke(question)
        sources = [doc.page_content[:200] + "..." for doc in docs]
        
        # Generate follow-up questions
        followup_questions = generate_followup_questions(response["answer"])
        
        return create_chat_response(response["answer"], sources, followup_questions)
        
    except Exception as e:
        logger.error(f"Error processing ask request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatAppRequest):
    """Streaming chat endpoint"""
    if not rag_chain:
        raise HTTPException(
            status_code=503,
            detail="RAG system not available. ChromaDB not loaded."
        )
    
    try:
        # Get the last message content
        last_message = request.messages[-1] if request.messages else None
        if not last_message:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        question = last_message.content
        
        def generate_stream():
            try:
                # Get response from RAG chain
                response = rag_chain.invoke({"input": question})
                answer = response["answer"]
                
                # Get source documents
                docs = retriever.invoke(question)
                sources = [doc.page_content[:200] + "..." for doc in docs]
                
                # Generate follow-up questions
                followup_questions = generate_followup_questions(answer)
                
                # Stream the answer word by word
                words = answer.split()
                accumulated_content = ""
                
                for i, word in enumerate(words):
                    accumulated_content += word + " "
                    
                    chunk_response = ChatAppResponse(
                        message=ResponseMessage(content=accumulated_content.strip(), role="assistant"),
                        delta=ResponseMessage(content=word + " ", role="assistant"),
                        context=ResponseContext(
                            data_points=DataPoints(
                                text=sources if i == len(words) - 1 else [],
                                images=[],
                                citations=sources if i == len(words) - 1 else []
                            ),
                            followup_questions=followup_questions if i == len(words) - 1 else None,
                            thoughts=[
                                Thoughts(
                                    title="Streaming Response",
                                    description=f"Wort {i+1} von {len(words)}"
                                )
                            ] if i == 0 else []
                        ),
                        session_state=None
                    )
                    
                    yield f"{json.dumps(chunk_response.model_dump())}\n"
                    
            except Exception as e:
                error_response = {
                    "error": f"Error generating response: {str(e)}"
                }
                yield f"{json.dumps(error_response)}\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing streaming chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
