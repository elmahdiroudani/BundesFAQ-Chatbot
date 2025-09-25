from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
from typing import Optional, AsyncGenerator

############################
# Logging & Environment
############################
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

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

############################
# OpenAI / Embeddings Setup
############################
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
else:
    logger.info(f"OPENAI_API_KEY loaded: {OPENAI_API_KEY[:5]}***")

embedding = OpenAIEmbeddings(model=EMBED_MODEL)

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

llm = ChatOpenAI(model=MODEL, temperature=0.1)

if retriever:
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)
else:
    rag_chain = None

############################
# API Models (Frontend-kompatibel)
############################

class ResponseMessage(BaseModel):
    content: str
    role: str

class DataPoints(BaseModel):
    text: list[str]
    images: list[str]
    citations: list[str]

class ResponseContext(BaseModel):
    data_points: DataPoints
    followup_questions: list[str] | None
    thoughts: list[dict]

class ChatAppRequestOverrides(BaseModel):
    retrieval_mode: str | None = None
    semantic_ranker: bool | None = None
    semantic_captions: bool | None = None
    query_rewriting: bool | None = None
    reasoning_effort: str | None = None
    include_category: str | None = None
    exclude_category: str | None = None
    seed: int | None = None
    top: int | None = None
    results_merge_strategy: str | None = None
    temperature: float | None = None
    minimum_search_score: float | None = None
    minimum_reranker_score: float | None = None
    prompt_template: str | None = None
    prompt_template_prefix: str | None = None
    prompt_template_suffix: str | None = None
    suggest_followup_questions: bool | None = None
    use_oid_security_filter: bool | None = None
    use_groups_security_filter: bool | None = None
    send_text_sources: bool | None = None
    send_image_sources: bool | None = None
    search_text_embeddings: bool | None = None
    search_image_embeddings: bool | None = None
    language: str | None = None
    use_agentic_retrieval: bool | None = None

class ChatAppRequestContext(BaseModel):
    overrides: ChatAppRequestOverrides | None = None

class ChatAppRequest(BaseModel):
    messages: list[ResponseMessage]
    context: ChatAppRequestContext | None = None
    session_state: dict | None = None

class ChatAppResponse(BaseModel):
    message: ResponseMessage
    delta: ResponseMessage
    context: ResponseContext
    session_state: dict | None = None

class HealthResponse(BaseModel):
    status: str
    vectorstore_loaded: bool
    vectorstore_path: str
    model: str
    embedding_model: str
    collection_name: Optional[str]
    retriever_k: Optional[int]
    log_level: str

class ConfigResponse(BaseModel):
    defaultReasoningEffort: str
    showMultimodalOptions: bool
    showSemanticRankerOption: bool
    showQueryRewritingOption: bool
    showReasoningEffortOption: bool
    streamingEnabled: bool
    showVectorOption: bool
    showUserUpload: bool
    showLanguagePicker: bool
    showSpeechInput: bool
    showSpeechOutputBrowser: bool
    showSpeechOutputAzure: bool
    showChatHistoryBrowser: bool
    showChatHistoryCosmos: bool
    showAgenticRetrievalOption: bool
    ragSearchTextEmbeddings: bool
    ragSearchImageEmbeddings: bool
    ragSendTextSources: bool
    ragSendImageSources: bool

def build_response(answer: str, sources: list[str]) -> ChatAppResponse:
    dp = DataPoints(text=sources if sources else [], images=[], citations=[])
    ctx = ResponseContext(data_points=dp, followup_questions=None, thoughts=[])
    msg = ResponseMessage(content=answer, role="assistant")
    delta = ResponseMessage(content="", role="assistant")
    return ChatAppResponse(message=msg, delta=delta, context=ctx, session_state=None)

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
    """Gesundheitscheck der API, Modelle & Vektorstore."""
    return HealthResponse(
        status="healthy" if rag_chain else "degraded",
        vectorstore_loaded=vectorstore is not None,
        vectorstore_path=persist_directory,
        model=MODEL,
        embedding_model=EMBED_MODEL,
        collection_name="bundesfaq_rag_collection" if vectorstore else None,
        retriever_k=3 if retriever else None,
        log_level=LOG_LEVEL
    )

@app.post("/chat", response_model=ChatAppResponse, tags=["Chat"], summary="RAG Chat im Frontend Format")
async def chat(request: ChatAppRequest):
    if not rag_chain:
        raise HTTPException(status_code=503, detail="RAG system not available. ChromaDB not loaded.")
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    user_msg = request.messages[-1].content
    try:
        result = rag_chain.invoke({"input": user_msg})
        docs = retriever.get_relevant_documents(user_msg)
        sources = [d.page_content[:160] for d in docs]
        return build_response(result["answer"], sources)
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


############################
# Additional Planned Endpoints (Stubs / Minimal)
############################

@app.get("/config", response_model=ConfigResponse, tags=["Config"])
async def get_config():
    return ConfigResponse(
        defaultReasoningEffort="medium",
        showMultimodalOptions=False,
        showSemanticRankerOption=True,
        showQueryRewritingOption=True,
        showReasoningEffortOption=False,
        streamingEnabled=True,
        showVectorOption=True,
        showUserUpload=True,
        showLanguagePicker=True,
        showSpeechInput=False,
        showSpeechOutputBrowser=False,
        showSpeechOutputAzure=False,
        showChatHistoryBrowser=True,
        showChatHistoryCosmos=False,
        showAgenticRetrievalOption=False,
        ragSearchTextEmbeddings=True,
        ragSearchImageEmbeddings=False,
        ragSendTextSources=True,
        ragSendImageSources=False
    )


@app.get("/auth_setup", tags=["Auth"], summary="Auth Setup (stub)")
async def auth_setup():
    """Stub-Endpunkt für zukünftige Authentifizierungskonfiguration."""
    return {"auth": False, "provider": None}


@app.post("/ask", response_model=ChatAppResponse, tags=["Chat"], summary="Alias zu /chat")
async def ask(request: ChatAppRequest):
    return await chat(request)


@app.post("/chat/stream", tags=["Chat"], summary="NDJSON Streaming kompatibel zum Frontend")
async def chat_stream(request: ChatAppRequest):
    if not rag_chain:
        raise HTTPException(status_code=503, detail="RAG system not available. ChromaDB not loaded.")
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    user_msg = request.messages[-1].content

    async def ndjson_stream() -> AsyncGenerator[bytes, None]:
        try:
            result = rag_chain.invoke({"input": user_msg})
            full_text = result["answer"]
            tokens = full_text.split()
            built: list[str] = []
            import json
            for t in tokens:
                built.append(t)
                chunk = build_response(" ".join(built), [])
                chunk.delta.content = t + " "
                yield (json.dumps(chunk.model_dump()) + "\n").encode("utf-8")
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            import json
            yield (json.dumps({"error": "stream_failed"}) + "\n").encode("utf-8")

    return StreamingResponse(ndjson_stream(), media_type="application/x-ndjson")


@app.post("/upload", tags=["Upload"], summary="Dokumenten-Upload (noch nicht implementiert)")
async def upload_file(file: UploadFile = File(...)):
    # Placeholder: In Zukunft hier Pipeline zum Einfügen neuer Dokumente in den Vectorstore
    logger.info(f"Received upload: {file.filename} (ignored - not implemented)")
    raise HTTPException(status_code=501, detail="Upload not implemented yet")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
