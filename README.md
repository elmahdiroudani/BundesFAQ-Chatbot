# BundesFAQ-Chatbot

A comprehensive Retrieval-Augmented Generation (RAG) chatbot system designed for German federal FAQ data, offering two primary deployment approaches and automated document processing capabilities.

## Project Overview

This project provides two main implementation approaches:

1. **FastAPI + React Stack** - Full-stack web application with modern UI
2. **N8N Workflow Automation** - No-code solution with cloud integrations

## Project Structure

```
BundesFAQ-Chatbot/
├── src/
│   ├── backend/               # FastAPI backend components
│   │   ├── chroma_db/        # Vector database storage
│   │   └── faq_rag_semantic_chunking.ipynb  # Development notebook
│   └── frontend/             # React application
├── n8n workflows/            # N8N automation workflows
├── data/                     # Source FAQ documents
├── app.py                   # Main FastAPI application
└── requirements.txt         # Python dependencies
```

## Development Branches

- **main** - Stable production branch
- **mehdi** - N8N workflow development
- **soufiane_dev** - FastAPI + React development

---

## Option 1: FastAPI + React Application

This approach provides a complete web application with a FastAPI backend and React frontend, designed for self-hosted deployments with full control over the system.

### Architecture Overview

The FastAPI + React stack offers a production-ready web application featuring:

- **FastAPI Backend**: High-performance Python web framework handling API requests
- **ChromaDB Integration**: Local vector database for document embeddings and retrieval
- **LangChain Framework**: Orchestrates the RAG pipeline with document retrieval and response generation  
- **React Frontend**: Modern TypeScript-based user interface with streaming chat capabilities
- **German Localization**: Complete German language support with localized UI and responses

### Key Features

- **Streaming Chat Interface**: Real-time response streaming for improved user experience
- **Semantic Search**: Vector-based document retrieval using OpenAI embeddings
- **Context-Aware Responses**: Maintains conversation context with follow-up question suggestions
- **Document Citations**: Shows source documents used in generating responses
- **Clean Architecture**: Separation of concerns with clear API boundaries

### Technical Stack

- **Backend**: FastAPI, LangChain, ChromaDB, OpenAI GPT-3.5-turbo
- **Frontend**: React 18, TypeScript, Vite, Fluent UI components
- **Database**: ChromaDB vector database with OpenAI text-embedding-3-small
- **Deployment**: Local development server with production-ready configuration

### Setup Instructions

1. **Environment Setup**
```bash
git clone https://github.com/elmahdiroudani/BundesFAQ-Chatbot.git
cd BundesFAQ-Chatbot
git checkout soufiane_dev
```

2. **Backend Configuration**
```bash
python -m venv .venv311
.venv311\Scripts\activate
pip install -r requirements.txt
```

3. **Environment Variables**
Create `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Initialize Database**
Run the notebook to create vector embeddings:
```bash
jupyter notebook src/backend/faq_rag_semantic_chunking.ipynb
```

5. **Start Services**
```bash
# Backend (Terminal 1)
python app.py

# Frontend (Terminal 2)
cd src/frontend
npm install
npm run dev
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/config` | GET | Frontend configuration settings |
| `/health` | GET | System health and database status |
| `/ask` | POST | Single question endpoint |
| `/chat/stream` | POST | Streaming chat responses |

---

## Option 2: N8N Workflow Automation

The N8N implementation provides a no-code solution with cloud integrations, ideal for teams preferring visual workflow design and automated document processing.

### Architecture Overview

The N8N approach leverages cloud services and visual workflow design to create a fully automated RAG system with minimal code requirements. This solution is particularly suited for organizations already using N8N for automation or those preferring cloud-native architectures.

### Key Advantages

- **No-Code Implementation**: Visual workflow design requires no programming knowledge
- **Cloud Integration**: Built-in connectors for Google Drive, Pinecone, and OpenAI
- **Automatic Scaling**: Cloud infrastructure handles load management
- **Real-time Updates**: Automatic document processing when files change
- **Enterprise Ready**: Built-in monitoring, logging, and error handling

### Workflow Components

#### 1. AI Chat Workflow

![RAG1](https://github.com/user-attachments/assets/7138db4d-f799-44ab-a0f9-fa0eb500315e)

**Workflow Features:**
- **Chat Trigger**: Webhook-based interface for receiving user messages
- **AI Agent**: Manages conversation context, memory, and response routing
- **OpenAI GPT-4.1-mini**: Advanced language model for response generation
- **Memory Management**: Maintains conversation history and context
- **Vector Search Integration**: Retrieves relevant documents using semantic search
- **Pinecone Database**: Cloud vector storage for high-performance retrieval

**Advanced Capabilities:**
- Conversation context preservation across multiple exchanges
- Dynamic response routing based on query type
- Fallback handling for out-of-scope questions
- Response streaming for improved user experience
- Automatic source attribution in responses

#### 2. Document Processing Workflow

![RAG2](https://github.com/user-attachments/assets/de17bc02-5f63-4b16-bf53-7719a5878b9c)

**Automated Pipeline:**
- **Google Drive Monitor**: Real-time file change detection with configurable polling
- **Document Extraction**: Automatic download and content parsing
- **Intelligent Chunking**: Recursive text splitting optimized for semantic coherence  
- **Embedding Generation**: OpenAI embeddings with batch processing for efficiency
- **Vector Storage**: Automated Pinecone indexing with metadata preservation

**Processing Features:**
- Support for PDF, DOCX, and TXT file formats
- Automatic duplicate detection and handling
- Batch processing for large document sets
- Error recovery and retry mechanisms
- Processing status notifications

### Setup Requirements

**Prerequisites:**
- N8N Cloud account or self-hosted instance
- OpenAI API access with sufficient credits
- Pinecone account with configured index
- Google Drive for document storage

**Configuration Steps:**
1. Import workflow JSON files into N8N
2. Configure API credentials for all services
3. Set up Google Drive monitoring folder
4. Configure Pinecone index parameters
5. Activate workflows and test integration

### Technical Architecture

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Workflow Engine** | N8N | Visual automation and orchestration |
| **Chat Interface** | N8N Webhook | Message handling and response delivery |
| **Language Model** | OpenAI GPT-4.1-mini | Response generation and reasoning |
| **Vector Database** | Pinecone | Semantic search and retrieval |
| **Document Storage** | Google Drive | Source document management |
| **Embeddings** | OpenAI text-embedding-3-small | Document vectorization |
| **Memory System** | N8N Simple Memory | Conversation context management |

### Deployment Options

- **N8N Cloud**: Fully managed service with automatic scaling
- **Self-Hosted**: Docker-based deployment for full control
- **Hybrid**: Cloud workflows with on-premise data processing

---

## Development Environment

For development and experimentation, a Jupyter notebook is available at `src/backend/faq_rag_semantic_chunking.ipynb` that demonstrates the core RAG concepts and ChromaDB integration used in the FastAPI implementation.

---

## Configuration

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Example Usage

**German FAQ Questions:**
- "Was ist GovData.de und welche Daten sind verfügbar?"
- "Welche Lizenzen gibt es für offene Verwaltungsdaten?"
- "Wie kann ich offene Daten der Bundesregierung nutzen?"

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open Pull Request

---

## Team

- **Mehdi**: N8N workflow development and cloud integrations
- **Soufiane**: FastAPI backend and React frontend development


