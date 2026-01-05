from flask import Flask, request, jsonify
from flask_cors import CORS
from core.agent import BizzHubChatbot
import os
import sys

# Add the backend directory to sys.path so we can import core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent import BizzHubChatbot

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Initialize Chatbot
chatbot = BizzHubChatbot()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "BizzHub Chatbot API"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get response from the agent
        # The agent returns a formatted string with markdown-like syntax (*, •)
        response_text = chatbot.process_message(user_message)
        
        return jsonify({
            "response": response_text,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == '__main__':
    print("🚀 BizzHub Chatbot Server Running on http://localhost:5000")
    app.run(debug=True, port=5000)
