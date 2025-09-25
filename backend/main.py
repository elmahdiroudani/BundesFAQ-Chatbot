"""
BundesFAQ Chatbot - Main Application
Authors: Mehdi & Soufiane

Frontend Location: src/frontend/
Backend Location: src/backend/ (to be implemented)

Frontend Status: ✅ Ready for backend integration
Frontend URL: http://127.0.0.1:5173/ (development)

To start frontend: cd src/frontend && npm run dev
To build frontend: cd src/frontend && npm run build
"""

def main():
    """Main application entry point"""
    print("🤖 BundesFAQ Chatbot")
    print("=" * 50)
    print("📁 Frontend: src/frontend/ (✅ Ready)")
    print("📁 Backend:  src/backend/ (⏳ Implement required)")
    print("")
    print("🚀 Frontend Development:")
    print("   cd src/frontend")
    print("   npm run dev")
    print("   → http://127.0.0.1:5173/")
    print("")
    print("🔗 Backend Integration:")
    print("   See BACKEND_INTEGRATION.md for details")
    print("   Required endpoints: /config, /auth_setup, /ask, /chat/stream")
    print("")
    print("✅ Frontend is ready for your backend!")

if __name__ == "__main__":
    main()