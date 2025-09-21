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

## 📁 Project Structure

```
BundesFAQ-Chatbot/
├── src/
│   ├── backend/           # Backend implementation (to be developed)
│   └── frontend/          # React TypeScript frontend
│       ├── src/
│       │   ├── components/  # React components
│       │   ├── pages/      # App pages
│       │   ├── api/        # API integration
│       │   └── assets/     # Static assets
│       ├── package.json    # Frontend dependencies
│       └── vite.config.ts  # Build configuration
├── data/                  # Data files and datasets
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
└── main.py               # Application entry point
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.10+**
- **Node.js 20.0.0+**
- **npm** or **yarn**

### Frontend Setup

```bash
# Install frontend dependencies
cd src/frontend
npm install

# Start development server
npm run dev
# Opens on http://127.0.0.1:5173/

# Build for production
npm run build
# Outputs to src/backend/static/
```

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run main application
python main.py
```

## 🔧 Development

### Frontend Development
```bash
cd src/frontend
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

## 📚 Documentation

- **[Backend Integration Guide](BACKEND_INTEGRATION.md)** - Complete API specification
- **[Frontend Documentation](src/frontend/README.md)** - Frontend-specific docs
- **[Frontend Fixes](FRONTEND_FIXED.md)** - Recent issue resolutions

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

### Production Build
```bash
# Build frontend
cd src/frontend
npm run build

# Frontend assets will be in src/backend/static/
# Deploy backend with built frontend assets
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