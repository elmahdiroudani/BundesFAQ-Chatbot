# 🤖 BundesFAQ-Chatbot

A modern, responsive chatbot for German federal laws and regulations, built with Azure OpenAI integration.

## 🚀 Features

- **Modern React Frontend** - Built with TypeScript, Fluent UI, and Vite
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **Azure OpenAI Integration** - Ready for GPT-4 and other Azure AI services
- **Multi-language Support** - Internationalization with i18next
- **Authentication Ready** - Optional Azure AD/MSAL integration
- **File Upload Support** - Document processing capabilities
- **Chat History** - Persistent conversation management
- **Real-time Streaming** - Streaming chat responses

## 📁 Project Structure (After Restructure)

```
BundesFAQ-Chatbot/
├── backend/
│   ├── app.py                # FastAPI application (RAG endpoints + stubs)
│   ├── chat_terminal.py      # Simple terminal client
│   ├── requirements.txt      # Python dependencies (moved here)
│   ├── pyproject.toml        # (optional packaging / uv config)
│   ├── uv.lock               # uv lockfile
│   ├── data/                 # Source & processed FAQ data
│   ├── vectorstore/          # Chroma persistence (active)
│   └── notebooks/
│       └── faq_rag_semantic_chunking.ipynb
├── frontend/                 # React + Vite + TS application
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── api/
│       ├── i18n/
│       └── assets/
├── README.md                 # Root documentation (this file)
├── LICENSE
└── .gitignore
```

Legacy `src/` directory has been flattened: former `src/frontend` merged into top-level `frontend/`; backend code centralized in `backend/`.

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.10+**
- **Node.js 20.0.0+**
- **npm** or **yarn**

### Frontend Setup

```bash
cd frontend
npm install
npm run dev          # http://127.0.0.1:5173/
npm run build        # (adjust dist handling as needed)
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt   # or: uv pip install -r requirements.txt

# Run FastAPI (dev)
uvicorn app:app --reload --port 8000

# Terminal client (optional)
python chat_terminal.py
```

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm run dev
```
The frontend runs on port 5173 and proxies API calls to port 50505.

### Backend Development
Your backend should implement these endpoints:
- `GET /config` - Application configuration
- `GET /auth_setup` - Authentication setup
- `POST /ask` - Single question answering
- `POST /chat/stream` - Streaming chat
- `POST /upload` - File upload (optional)

See `BACKEND_INTEGRATION.md` for detailed API specifications.

### Rebuild / Update Vectorstore
Use the helper script to (re)generate the Chroma vectorstore from the provided PDF or text export.

```bash
# From repository root
python backend/scripts/build_vectorstore.py --pdf backend/data/faq.pdf --reset

# Or from text version
python backend/scripts/build_vectorstore.py --text backend/data/FAQtxt.txt --reset

# Custom output directory
VECTORSTORE_DIR=./backend/vectorstore_alt \
python backend/scripts/build_vectorstore.py --pdf backend/data/faq.pdf
```

Flags:
- `--reset`  Wipes existing directory before building
- `--pdf` / `--text`  Exactly one is required
- `--out`  Override output directory (else uses VECTORSTORE_DIR or default)

The API (`app.py`) will pick up the vectorstore from:
```
VECTORSTORE_DIR env var OR ./backend/vectorstore (default)
```

If you previously had a legacy store under `src/backend/chroma_db/…`, its
contents are no longer used after the restructure—rebuild using the script
above to ensure consistency.

## 🧩 API & Integration

Implemented & planned endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Service + Vectorstore + Modellstatus |
| `/chat` | POST | RAG Antwort auf Nutzerfrage |
| `/config` | GET | UI Feature Flags (Stub) |
| `/auth_setup` | GET | Auth Konfiguration (Stub) |
| `/ask` | POST | Vereinfachtes Q&A (Alias) |
| `/chat/stream` | POST | Token-Streaming (Stub) |
| `/upload` | POST | Datei-Upload (501 / not implemented) |

### Example `/config` Response
```json
{
	"showVectorOption": true,
	"streamingEnabled": true,
	"showLanguagePicker": true,
	"ragSearchTextEmbeddings": true
}
```

### Chat Request Schema (`/chat` / `/ask`)
```json
{
	"messages": [{"role": "user", "content": "Was ist GovData.de?"}],
	"context": {"overrides": {"retrieval_mode": "hybrid", "top": 3, "language": "de"}},
	"session_state": null
}
```

All prior integration documents have been merged into this single README for clarity.

## 🔐 Environment Variables

Create a local `.env` (see `.env.example`):
```
OPENAI_API_KEY=your_real_key
VECTORSTORE_DIR=./backend/vectorstore
MODEL=gpt-3.5-turbo
EMBED_MODEL=text-embedding-3-small
LOG_LEVEL=INFO
```

Optional (Azure / Auth / DB):
```
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_CLIENT_ID=...
AZURE_TENANT_ID=...
DATABASE_URL=...
```

## 🤝 Contributing

### Team
- **Mehdi** - Frontend Development
- **Soufiane** - Backend Development

### Branches
- `main` - Production branch
- `Mehdi` - Mehdi's development branch
- `soufiane_dev` - Soufiane's development branch

### Development Workflow
1. Create feature branches from your dev branch
2. Implement features with tests
3. Create PR to merge into main
4. Code review and merge

## 🚀 Deployment

### Production Build (Draft)
```bash
# Frontend
cd frontend
npm run build

# Backend (ensure VECTORSTORE_DIR set if custom)
cd ../backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Environment Variables
Configure these for production:
```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key

# Database (if using)
DATABASE_URL=your_database_url

# Authentication (if enabled)
AZURE_CLIENT_ID=your_client_id
AZURE_TENANT_ID=your_tenant_id
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
1. Check existing [documentation](BACKEND_INTEGRATION.md)
2. Review [frontend fixes](FRONTEND_FIXED.md)
3. Create an issue in the repository

---

**Status**: Frontend ✅ Complete | Backend ⏳ In Development

*Built with ❤️ for German legal information accessibility*