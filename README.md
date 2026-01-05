# BizzHub Intelligent Chatbot

A professional, AI-powered chatbot for BizzHub Workspaces. It handles queries about pricing, locations, facilities, and contact information with a modern, glassmorphism-styled web interface.

## 📁 Project Structure

```
BizzHub-Chatbot/
├── backend/            # Python Flask Backend
│   ├── core/           # Chatbot Logic
│   │   └── agent.py    # Main Intelligence
│   ├── scripts/        # Utility Scripts
│   │   └── create_pdf.py
│   ├── app.py          # API Server
│   └── requirements.txt
├── data/               # Knowledge Base Data
│   ├── *.pdf           # Source Documents
│   └── *.pkl/*.npy     # Vector Store Cache
├── frontend/           # Web Interface
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

## 🚀 Getting Started

### 1. Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python app.py
   ```
   The API will start at `http://localhost:5000`.

### 2. Frontend Setup

1. Navigate to the `frontend` directory.
2. Open `index.html` in your browser.
   
   *Tip: For the best experience, use a local server (like Live Server in VS Code) to avoid CORS issues with some browsers, although the backend is configured to allow CORS.*

## 🌟 Features

- **Intelligent Intent Parsing**: Understands pricing, location, and facility queries.
- **Dynamic Responses**: Provides contextual answers based on user input.
- **Modern UI**: Glassmorphism design with responsive layout.
- **Markdown Support**: Renders rich text (bold lists) in chat bubbles.

## 🛠 Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS (Glassmorphism), Google Fonts (Outfit), Remix Icons

## 📝 Usage Examples

- "What is the price for a dedicated desk?"
- "Do you have parking at the Whitefield center?"
- "I want to schedule a site visit."
