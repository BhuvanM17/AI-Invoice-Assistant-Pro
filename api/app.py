import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.core.agent import InvoiceAssistantChatbot

app = Flask(__name__)
CORS(app)

# Initialize chatbot with error handling
try:
    chatbot = InvoiceAssistantChatbot()
    print("✅ Chatbot initialized successfully")
except Exception as e:
    print(f"❌ Error initializing chatbot: {e}")
    chatbot = None

@app.get('/api/health')
def health_check():
    return jsonify({
        "status": "healthy" if chatbot else "degraded",
        "service": "AI-Powered E-Commerce Invoice Assistant API",
        "vercel": bool(os.environ.get("VERCEL")),
        "ai_ready": bool(os.environ.get("GOOGLE_API_KEY"))
    })


@app.post('/api/chat')
def chat():
    if not chatbot:
        return jsonify({"error": "Chatbot not initialized. Check server logs."}), 500
        
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = chatbot.process_message(user_message)
        return jsonify({
            "response": response["text"],
            "type": response.get("type", "info"),
            "saved_invoice_id": response.get("saved_invoice_id"),
            "status": "success"
        })
    except Exception as error:
        print(f"Chat error: {error}")
        return jsonify({
            "error": "Internal server error", 
            "details": str(error),
            "hint": "Ensure GOOGLE_API_KEY is configured in Vercel environment variables"
        }), 500
