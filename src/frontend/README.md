# Frontend - Azure OpenAI Chat Application

This frontend is copied from the Azure OpenAI sample and configured for your BundesFAQ-Chatbot project.

## 🚀 Quick Start

### Prerequisites
- Node.js >= 20.0.0 (check your version with `node --version`)
- npm (comes with Node.js)

### Installation & Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```
   The application will be available at: http://127.0.0.1:5173/

3. **Build for production:**
   ```bash
   npm run build
   ```
   Built files will be output to `../src/backend/static/` (configured in vite.config.ts)

## 🏗️ Architecture

### Tech Stack
- **React 18** with TypeScript
- **Vite** for build tooling and dev server
- **Fluent UI** for Microsoft-style components
- **Azure MSAL** for authentication (optional)
- **React Router** for navigation
- **i18next** for internationalization

### Key Components

#### Pages
- `/` - Main chat interface
- `/qa` - Q&A interface
- `*` - 404 page

#### Core Components
- `Chat` - Main chat interface
- `AnalysisPanel` - Document analysis display
- `Answer` - AI response formatting
- `QuestionInput` - User input interface
- `Settings` - Configuration panel
- `HistoryPanel` - Chat history management

### Features
- **Real-time Chat** - Interactive chat with AI
- **File Upload** - Document upload and processing
- **Chat History** - Persistent conversation history
- **Settings Panel** - Configurable options
- **Responsive Design** - Works on desktop and mobile
- **Authentication** - Optional Azure AD integration
- **Internationalization** - Multi-language support

## ⚙️ Configuration

### Backend Integration
The frontend expects these API endpoints on the backend:
- `/ask` - Single question endpoint
- `/chat` - Chat conversation endpoint
- `/config` - Application configuration
- `/upload` - File upload
- `/chat_history` - Chat history management

### Vite Configuration
- **Dev Server:** Proxies API calls to `http://localhost:50505`
- **Build Output:** `../src/backend/static/`
- **Host:** `127.0.0.1` (configurable)

### Environment Variables
Create a `.env` file in the frontend directory:
```env
VITE_AZURE_OPENAI_ENDPOINT=your_endpoint
VITE_AZURE_OPENAI_API_KEY=your_api_key
# Add other environment variables as needed
```

## 🎨 Customization

### Styling
- Fluent UI provides the component library
- Custom styles in `src/index.css`
- Component-specific styles in component folders

### Authentication
Authentication is controlled by `src/authConfig.ts`:
- Set `useLogin = false` to disable authentication
- Configure Azure AD settings when authentication is enabled

### API Integration
API calls are centralized in `src/api/` directory:
- Modify endpoints in the API files
- Update proxy configuration in `vite.config.ts`

## 🛠️ Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Project Structure
```
frontend/
├── src/
│   ├── api/           # API integration
│   ├── components/    # Reusable components
│   ├── pages/         # Page components
│   ├── assets/        # Static assets
│   ├── locales/       # Translations
│   └── i18n/          # Internationalization config
├── public/            # Public assets
└── package.json       # Dependencies and scripts
```

## 🔄 Backend Integration

To connect this frontend with your backend:

1. **Update your backend to serve the built frontend files**
2. **Implement the required API endpoints**
3. **Configure CORS if needed**
4. **Update proxy settings in vite.config.ts for development**

## 📚 Useful Resources

- [Fluent UI Components](https://developer.microsoft.com/en-us/fluentui#/controls/web)
- [React Router Documentation](https://reactrouter.com/)
- [Vite Documentation](https://vitejs.dev/)
- [Azure MSAL React](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react)

---

*Frontend successfully copied and configured from azure-frontend project*