# CS203 Lab: LLM Chat Applications

🎯 **Lab Objective**: Build three progressive chat applications using Streamlit and LiteLLM to understand LLM integration, tool calling, and RAG systems.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for your chosen LLM provider
- (Optional) Search API keys for web search functionality

### Installation

1. **Clone or download this project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

# 2. Configure API keys in .env
cp .env.example .env
# Edit .env with your API keys

# 3. Launch the application
streamlit run app.py
```

## 📱 Applications

| Application | Port | Purpose | Key Learning |
|-------------|------|---------|--------------|
| **Basic Chat** | 8501 | Simple LLM interaction | API integration, session management |
| **Chat with Search** | 8503 | Web search tool calling | Intelligent tool detection, context enhancement |
| **Chat with RAG** | 8505 | Document-based knowledge retrieval | Vector embeddings, similarity search |

## 📁 Key Files

- `app.py` - Main navigation hub
- `src/basic_chat.py` - Basic LLM chat interface
- `src/chat_with_search.py` - Chat with automatic web search
- `src/chat_with_rag.py` - Chat with document retrieval
- `utils/` - Reusable components (LLM client, search tools, RAG system)

## 🔑 Required API Keys

Choose at least one LLM provider:
- **OpenAI**: `OPENAI_API_KEY`
- **Groq**: `GROQ_API_KEY`

For web search functionality:
- **Serper**: `SERPER_API_KEY` 
- **Tavily**: `TAVILY_API_KEY`

## 🧪 Testing

```bash
# Test tool calling detection
python test_final_tool_calling.py

---

**Ready to build the future of AI chat applications? Let's get started! �**

## 🤝 Contributing

This project is designed as educational starter code. Students and educators are encouraged to:

- Fork and modify for your own projects
- Add new features and capabilities
- Share improvements and variations
- Create additional example applications

## 📄 License

This project is provided as educational material. Feel free to use, modify, and distribute for learning purposes.

## 🎓 Educational Use

This project is specifically designed for:
- Computer Science courses
- AI/ML workshops and labs
- Self-learning projects
- Prototyping and experimentation

Each application builds upon the previous one, providing a clear learning progression from basic LLM integration to advanced RAG systems.

**Happy coding!** 🚀