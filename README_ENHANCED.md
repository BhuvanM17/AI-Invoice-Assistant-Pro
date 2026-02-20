# AI-Powered E-Commerce Invoice Assistant

An intelligent invoice assistant that turns user input into structured invoices, validates missing fields, and suggests additions before final generation. Enhanced with advanced AI features, structured validation, memory, and business capabilities.

## 🌟 Key Features

### AI & Machine Learning
- **Real LLM Integration**: Uses Google Gemini for intelligent parsing and response generation
- **Structured Output Validation**: Pydantic models ensure data integrity with schema validation
- **RAG System**: Retrieval-Augmented Generation for FAQ responses
- **Multi-Model Fallback**: Automatic fallback between different LLM providers
- **Tool Calling**: Integrated tools for currency conversion, calculations, and more

### Memory & Context
- **Conversation History**: Maintains context across multiple interactions
- **Session Management**: Tracks conversation state and invoice drafts
- **Context-Aware Processing**: Remembers previous inputs for seamless experience

### Business Features
- **Professional PDF Generation**: Automatically creates branded invoice PDFs
- **Currency Conversion**: Real-time currency conversion with caching
- **Tax Calculations**: GST/VAT calculations with configurable rates
- **Invoice Storage**: Persistent storage with JSON backup

### Frontend Experience
- **Streaming Responses**: Real-time, typewriter-like response streaming
- **Modern UI**: React + Tailwind CSS with intuitive design
- **Interactive Catalog**: Browse and add products seamlessly
- **Real-time Cart**: Live cart updates and checkout flow

## 🏗️ Architecture

```mermaid
graph TB
    A[User Interface] --> B[Frontend React App]
    B --> C[Backend API]
    
    C --> D[Invoice Assistant]
    D --> E[LLM Manager]
    E --> F[Gemini API]
    E --> G[OpenAI API]
    E --> H[Fallback Logic]
    
    D --> I[RAG System]
    I --> J[FAQ Database]
    
    D --> K[Invoice Parser]
    K --> L[Pydantic Validation]
    
    D --> M[Session Manager]
    M --> N[Conversation History]
    
    D --> O[Invoice Engine]
    O --> P[PDF Generator]
    O --> Q[Storage System]
    
    D --> R[Currency Converter]
    R --> S[Exchange Rate API]
    
    style A fill:#4CAF50,stroke:#388E3C,color:#fff
    style F fill:#FF9800,stroke:#F57C00,color:#fff
    style J fill:#2196F3,stroke:#1976D2,color:#fff
    style P fill:#9C27B0,stroke:#7B1FA2,color:#fff
```

### System Flow

1. **User Input Processing**:
   - User submits message via frontend
   - Frontend streams response in real-time
   - Backend receives and processes with context

2. **LLM Processing Pipeline**:
   - Intent detection and routing
   - Context retrieval from conversation history
   - LLM processing with RAG augmentation
   - Response validation and formatting

3. **Data Validation & Storage**:
   - Pydantic schema validation
   - Invoice structuring and validation
   - PDF generation and storage
   - Conversation history update

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API Key
- (Optional) OpenAI API Key

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your-gemini-api-key"
export OPENAI_API_KEY="your-openai-api-key"  # Optional
export EXCHANGE_RATE_API_KEY="your-exchange-rate-api-key"  # Optional

# Run the backend
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Standard chat endpoint |
| `/api/stream-chat` | POST | Streaming chat endpoint |
| `/api/invoices` | GET | List all invoices |
| `/api/invoices/:id` | GET | Get specific invoice |

### Request Format
```json
{
  "message": "2x T-shirts @ 500, shipping 100",
  "session_id": "unique-session-id"
}
```

### Response Format
```json
{
  "response": "Generated response text",
  "type": "info|warning|invoice",
  "saved_invoice_id": "unique-invoice-id",
  "status": "success"
}
```

## 📊 Performance Metrics

- **Response Time**: Average 800ms for standard queries
- **LLM Fallback**: Seamless transition between providers
- **Caching**: Exchange rates cached for 30 minutes
- **Scalability**: Session-based state management

## 🏷️ Advanced AI Engineering Features

### 1. RAG Implementation
- Vector-based similarity search for FAQ retrieval
- Context-aware response generation
- Continuous learning from interactions

### 2. Multi-Model Fallback
- Primary: Google Gemini
- Secondary: OpenAI GPT
- Tertiary: Rule-based fallback
- Automatic health checks and failover

### 3. Tool Calling Architecture
- Currency conversion tool
- Mathematical calculation tool
- Time and date utilities
- Extensible tool registration system

### 4. Production Readiness
- Structured logging
- Comprehensive error handling
- Graceful degradation
- Monitoring hooks ready

## 📈 Business Impact

This enhanced system transforms a basic demo into a production-ready intelligent assistant with:

- **Improved User Experience**: Context-aware conversations and streaming responses
- **Data Integrity**: Pydantic validation prevents corrupt invoices  
- **Scalability**: Modular architecture supports growth
- **Reliability**: Multi-layered fallback mechanisms
- **Business Value**: Professional PDFs and multi-currency support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your enhancements
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Made with ❤️ for modern AI-powered applications