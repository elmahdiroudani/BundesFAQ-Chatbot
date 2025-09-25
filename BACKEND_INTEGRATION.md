# 🔧 Backend Integration Guide

## 🎯 **Frontend Status: Ready for Backend Integration**

The frontend is now **100% ready** for backend integration! All components are working, authentication is properly handled, and the structure is optimized for your project.

## 📁 **New Project Structure**

```
BundesFAQ-Chatbot/
├── src/
│   ├── backend/           # Your backend code goes here
│   └── frontend/          # ✅ Frontend moved here (working)
│       ├── src/           # React application source
│       ├── package.json   # Dependencies & scripts
│       ├── vite.config.ts # Build configuration
│       └── README.md      # Frontend documentation
├── main.py               # Updated placeholder
└── requirements.txt      # Your current requirements
```

## 🔗 **Required Backend Endpoints**

Your backend needs to implement these API endpoints that the frontend expects:

### **1. Configuration Endpoint**
```
GET /config
```
**Purpose:** App configuration and feature toggles
**Response Example:**
```json
{
    "defaultReasoningEffort": "medium",
    "showMultimodalOptions": false,
    "showSemanticRankerOption": true,
    "showQueryRewritingOption": true,
    "streamingEnabled": true,
    "showVectorOption": true,
    "showUserUpload": true,
    "showLanguagePicker": true,
    "showSpeechInput": false,
    "showSpeechOutputBrowser": false,
    "showSpeechOutputAzure": false,
    "showChatHistoryBrowser": true,
    "showChatHistoryCosmos": false,
    "showAgenticRetrievalOption": false,
    "ragSearchTextEmbeddings": true,
    "ragSearchImageEmbeddings": false,
    "ragSendTextSources": true,
    "ragSendImageSources": false
}
```

### **2. Authentication Setup Endpoint**
```
GET /auth_setup
```
**Purpose:** Authentication configuration (optional if you want to disable login)
**Response Example:**
```json
{
    "useLogin": false,
    "requireAccessControl": false,
    "enableUnauthenticatedAccess": true,
    "msalConfig": {
        "auth": {
            "clientId": "your-client-id",
            "authority": "https://login.microsoftonline.com/your-tenant",
            "redirectUri": "/",
            "postLogoutRedirectUri": "/",
            "navigateToLoginRequestUrl": false
        },
        "cache": {
            "cacheLocation": "sessionStorage",
            "storeAuthStateInCookie": false
        }
    },
    "loginRequest": {
        "scopes": ["openid", "profile", "email"]
    },
    "tokenRequest": {
        "scopes": ["openid", "profile", "email"]
    }
}
```

### **3. Chat Endpoints**

#### Single Question Endpoint
```
POST /ask
```
**Purpose:** Answer single questions
**Request Body:**
```json
{
    "messages": [
        {
            "content": "What are German federal laws about data protection?",
            "role": "user"
        }
    ],
    "context": {
        "overrides": {
            "retrieval_mode": "hybrid",
            "semantic_ranker": true,
            "top": 3,
            "temperature": 0.3,
            "language": "de"
        }
    },
    "session_state": null
}
```

**Response Example:**
```json
{
    "message": {
        "content": "German federal data protection laws include...",
        "role": "assistant"
    },
    "context": {
        "data_points": {
            "text": ["source1", "source2"],
            "images": [],
            "citations": ["citation1", "citation2"]
        },
        "followup_questions": [
            "What about GDPR compliance?",
            "How does this affect businesses?"
        ],
        "thoughts": [
            {
                "title": "Document Analysis",
                "description": "Found relevant information in federal law databases"
            }
        ]
    },
    "session_state": "session_data_here"
}
```

#### Streaming Chat Endpoint
```
POST /chat/stream
```
**Purpose:** Streaming chat responses
**Request:** Same as `/ask`
**Response:** NDJSON stream of chat chunks

### **4. File Upload Endpoints (Optional)**
```
POST /upload          # Upload files
GET /list_uploaded    # List uploaded files
DELETE /delete_uploaded # Delete uploaded files
```

## ⚙️ **Backend Setup Instructions**

### **1. Serve Static Files**
Configure your backend to serve the built frontend from:
```
src/backend/static/
```

### **2. Build the Frontend**
To build the frontend for production:
```bash
cd src/frontend
npm run build
```
This creates optimized files in `src/backend/static/`

### **3. Development Setup**
For development, run both:
```bash
# Terminal 1: Backend server on port 50505
python your_backend_server.py

# Terminal 2: Frontend dev server on port 5173
cd src/frontend
npm run dev
```

### **4. CORS Configuration**
If backend and frontend run on different ports, configure CORS:
```python
# Example for FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 **Quick Start Commands**

### **Frontend Development:**
```bash
cd src/frontend
npm run dev
# Opens on http://127.0.0.1:5173/
```

### **Production Build:**
```bash
cd src/frontend
npm run build
# Outputs to src/backend/static/
```

### **Backend Integration:**
```bash
# Your backend should run on http://localhost:50505
# The frontend will proxy API calls to this address
```

## 🔧 **Customization Options**

### **1. API Endpoints**
Update proxy configuration in `src/frontend/vite.config.ts`:
```typescript
server: {
    proxy: {
        "/api": "http://localhost:8000",  // Change backend URL
        "/auth": "http://localhost:8000"
    }
}
```

### **2. Authentication**
Disable authentication by returning `useLogin: false` in `/auth_setup`

### **3. Features**
Control UI features through the `/config` endpoint response

## ✅ **Current Status**

- ✅ **Frontend fully working** with mock responses
- ✅ **All components functional** (chat, upload, settings, history)
- ✅ **Authentication handled** (disabled for development)
- ✅ **Responsive design** works on all devices
- ✅ **Error handling** with fallbacks
- ✅ **Ready for backend integration**

## 🤝 **Next Steps for Your Friend**

1. **Implement the required API endpoints** listed above
2. **Test with the frontend** using the URLs provided
3. **Configure authentication** if needed
4. **Build and deploy** both frontend and backend together

The frontend is 100% ready and waiting for the backend! All the hard work is done - just need to implement the API endpoints and you'll have a fully functional BundesFAQ chatbot! 🎉

---

*Frontend prepared by Mehdi - Ready for backend integration! 🚀*