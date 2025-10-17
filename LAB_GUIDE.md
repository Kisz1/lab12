# CS203 Lab: Building LLM-Powered Chat Applications

## Lab Overview
This lab provides hands-on experience with three progressively complex chat applications using Large Language Models (LLMs). You'll learn about API integration, tool calling, and Retrieval-Augmented Generation (RAG) systems.

## 🎯 Learning Objectives
By the end of this lab, you will understand:
- **Streamlit fundamentals**: Chat interfaces, session state, and reactive programming
- **LLM API integration**: Using LiteLLM for multiple provider support
- **Tool calling implementation**: Automatic web search integration
- **RAG systems**: Vector embeddings and document retrieval with FAISS
- **Best practices**: Error handling, optimization, and AI application development

---

## 📁 Repository Structure

```
CS203_w12_lab/
├── app.py                 # Main navigation hub
├── src/                   # Source code for applications
│   ├── echo_bot.py        # Task 0: Basic Streamlit chat interface
│   ├── basic_chat.py      # Basic LLM chat interface
│   ├── chat_with_search.py # Chat with web search tools
│   └── chat_with_rag.py   # Chat with document retrieval
├── utils/                 # Utility modules
│   ├── llm_client.py      # LLM API wrapper
│   ├── search_tools.py    # Web search integration
│   └── rag_system.py      # RAG implementation
├── requirements.txt       # Python dependencies
└── .env                   # API keys configuration
```

---

## 🚀 Setup Instructions

### Step 1: Environment Setup
```bash
# Clone or download the repository
cd CS203_w12_lab

# Install required packages
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Step 2: Configure API Keys
Edit `.env` file with your API keys:
```bash
# LLM Provider Keys (choose at least one)
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here

# Search API Keys (for web search functionality)
SERPER_API_KEY=your_serper_key_here
TAVILY_API_KEY=your_tavily_key_here
```

### Step 3: Launch the Application
```bash
streamlit run app.py
```

---

## �‍♂️ Task 0: Understanding Streamlit Basics with Echo Bot

### 🎯 Learning Focus
Before diving into LLM applications, let's understand the fundamentals of Streamlit chat interfaces. This task introduces you to:
- Streamlit chat components
- Session state management
- Basic user interaction patterns
- Chat message flow

### 📝 The Echo Bot (`src/echo_bot.py`)

The Echo Bot is the simplest possible chat application - it just repeats back whatever you type. While simple, it demonstrates all the core concepts you'll need for building AI chat applications.

#### Complete Code Analysis

```python
import streamlit as st

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
```

### 🔍 Step-by-Step Breakdown

#### 1. **App Title**
```python
st.title("Echo Bot")
```
- Sets the main heading of your web application
- Appears at the top of the page

#### 2. **Session State Initialization**
```python
if "messages" not in st.session_state:
    st.session_state.messages = []
```

**Why is this critical?**
- Streamlit reruns your entire script every time a user interacts with it
- Without session state, your chat history would disappear on each rerun
- `st.session_state` persists data between reruns
- We initialize an empty list to store chat messages

#### 3. **Display Chat History**
```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

**What's happening:**
- Loop through all stored messages
- `st.chat_message(role)` creates a chat bubble with proper styling
- `role` can be "user" or "assistant" (determines left/right alignment and styling)
- `st.markdown()` renders the message content

#### 4. **Handle User Input**
```python
if prompt := st.chat_input("What is up?"):
```

**The Walrus Operator (`:=`):**
- This is Python 3.8+ syntax for assignment expressions
- Equivalent to: `prompt = st.chat_input("What is up?"); if prompt:`
- `st.chat_input()` creates a text input box at the bottom of the screen
- Returns the user's input when they press Enter, or `None` if no input

#### 5. **Process and Display Messages**
```python
# Display user message
st.chat_message("user").markdown(prompt)
st.session_state.messages.append({"role": "user", "content": prompt})

# Generate and display response
response = f"Echo: {prompt}"
with st.chat_message("assistant"):
    st.markdown(response)
st.session_state.messages.append({"role": "assistant", "content": response})
```

**Message Flow:**
1. Display user message immediately (for instant feedback)
2. Store user message in session state (for persistence)
3. Generate response (in this case, just echo the input)
4. Display response in assistant chat bubble
5. Store response in session state

### 🛠 Hands-On Exercise 0.1: Run the Echo Bot

1. **Launch the Echo Bot:**
   ```bash
   streamlit run src/echo_bot.py
   ```

2. **Test the functionality:**
   - Type "Hello World" and press Enter
   - Try typing multiple messages
   - Refresh the page - notice the messages persist!

3. **Experiment with modifications:**
   - Change the title to "My First Chat Bot"
   - Modify the response format (e.g., `f"You said: {prompt}"`)
   - Add emoji to responses

### 🧪 Hands-On Exercise 0.2: Enhance the Echo Bot

**Task**: Add the following features to understand Streamlit components better:

#### A. Add a Clear Chat Button
```python
# Add this after the title
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()  # Refresh the app to show cleared chat
```

#### B. Add Message Counter
```python
# Add this in the sidebar
st.sidebar.write(f"Total messages: {len(st.session_state.messages)}")
```

#### C. Add Response Variations
```python
import random

# Replace the simple echo response with:
responses = [
    f"Echo: {prompt}",
    f"You said: {prompt}",
    f"I heard: {prompt}",
    f"Repeating: {prompt}"
]
response = random.choice(responses)
```

### 🔍 Key Concepts Learned

#### 1. **Streamlit's Reactive Model**
- Your script runs from top to bottom on every interaction
- State management is crucial for persistent data
- UI updates happen automatically when variables change

#### 2. **Chat Interface Components**
- `st.chat_input()`: Creates input field for user messages
- `st.chat_message(role)`: Creates styled chat bubbles
- `st.markdown()`: Renders text with formatting support

#### 3. **Session State Pattern**
```python
# Initialize
if "key" not in st.session_state:
    st.session_state.key = default_value

# Use
st.session_state.key.append(new_item)

# Display
for item in st.session_state.key:
    st.write(item)
```

### 🚀 Ready for Real AI?

Now that you understand:
- ✅ How Streamlit chat interfaces work
- ✅ Session state management
- ✅ Message flow and persistence
- ✅ User input handling

You're ready to move on to **Application 1: Basic Chat** where we'll replace the simple echo with actual AI responses!

### 💡 Pro Tips for Streamlit Development

1. **Use `st.rerun()`** when you need to refresh the app programmatically
2. **Session state keys** should be descriptive (e.g., `"chat_messages"` not `"msgs"`)
3. **Always initialize session state** before using it
4. **Use `with st.chat_message():`** for multi-line content in chat bubbles

---

## �📚 Application Deep Dive

## Application 1: Basic Chat (`src/basic_chat.py`)

### 🎯 Learning Focus
- LLM API integration
- Session state management
- Streamlit UI components
- Error handling

### 🔍 Key Components Analysis

#### 1. LLM Client Integration
```python
from utils import LLMClient, get_available_models

# Initialize LLM client with configuration
st.session_state.llm_client = LLMClient(
    model=selected_model,
    temperature=temperature,
    max_tokens=max_tokens
)
```

**What's happening here?**
- `LLMClient` is a wrapper around LiteLLM that provides unified access to multiple LLM providers
- Configuration parameters control model behavior:
  - `temperature`: Controls randomness (0.0 = deterministic, 2.0 = very random)
  - `max_tokens`: Limits response length

#### 2. Session State Management
```python
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = None
```

**Why is this important?**
- Streamlit reruns the entire script on each interaction
- Session state preserves data between reruns
- Essential for maintaining chat history and configurations

#### 3. Message Flow
```python
# Add user message
st.session_state.messages.append({"role": "user", "content": prompt})

# Get LLM response
response = st.session_state.llm_client.chat(st.session_state.messages)

# Add assistant response
st.session_state.messages.append({"role": "assistant", "content": response})
```

### 🛠 Hands-On Exercise 1
**Task**: Modify the basic chat to add message timestamps

1. Update the message structure to include timestamps
2. Display timestamps in the chat interface
3. Add a "Clear Chat" button

**Hint**: Use `datetime.now()` and modify the `display_chat_messages()` function.

---

## Application 2: Chat with Search (`src/chat_with_search.py`)

### 🎯 Learning Focus
- Tool calling concepts
- Web search API integration
- Intelligent function calling detection
- Context enhancement for LLMs

### 🔍 Key Components Analysis

#### 1. Intelligent Tool Detection
```python
def should_use_search(message_content: str) -> bool:
    message_lower = message_content.lower()
    
    search_triggers = [
        # Current/real-time information requests
        "current", "latest", "recent", "today", "now",
        # News and events
        "news", "update", "happened", "breaking",
        # Market and weather data
        "stock", "price", "weather", "temperature",
    ]
    
    return any(trigger in message_lower for trigger in search_triggers)
```

**What makes this intelligent?**
- Automatically detects when current information is needed
- No need for explicit "search:" commands
- Combines keyword detection with context analysis

#### 2. Search Integration
```python
def execute_search(query: str, num_results: int = 5):
    results = st.session_state.search_tool.search(query, num_results)
    return format_search_results(results)
```

**Search APIs supported:**
- **Serper**: Google Search API with JSON results
- **Tavily**: AI-optimized search with relevant content extraction

#### 3. Context Enhancement
```python
def handle_tool_calls(message_content: str):
    if should_use_search(message_content):
        search_query = extract_search_query(message_content)
        search_results = execute_search(search_query, 5)
        
        enhanced_prompt = f"""
        User Query: {message_content}
        
        I have searched the web and found the following current information:
        {search_results}
        
        Please provide a comprehensive answer based on this information.
        """
        return enhanced_prompt, True
    
    return message_content, False
```

**Why enhance the prompt?**
- LLMs have knowledge cutoffs and can't access real-time information
- Search results provide current, relevant context
- Enhanced prompts lead to more accurate and up-to-date responses

### 🛠 Hands-On Exercise 2
**Task**: Add a new tool for currency conversion

1. Create a currency conversion function using a free API (e.g., exchangerate-api.com)
   `utils/conversion_tools.py`
2. Add detection triggers for currency-related queries
3. Integrate the tool into the `handle_tool_calls` function

**Example queries to handle:**
- "Convert 100 USD to EUR"
- "What's the current exchange rate for Bitcoin?"

---

## Application 3: Chat with RAG (`src/chat_with_rag.py`)

### 🎯 Learning Focus
- Retrieval-Augmented Generation (RAG) concepts
- Vector embeddings and similarity search
- Document processing and chunking
- FAISS vector database

### 🔍 Key Components Analysis

#### 1. RAG System Architecture
```python
class SimpleRAGSystem:
    def __init__(self, data_dir: str = "rag_data", embedding_model: str = "all-MiniLM-L6-v2"):
        self.model = None  # Lazy loading for SentenceTransformer
        self.index = None  # FAISS index
        self.documents = []  # Document chunks
        self.metadata = []  # Document metadata
```

**Key components:**
- **Embedding Model**: Converts text to numerical vectors (384 dimensions)
- **FAISS Index**: Efficient similarity search over embeddings
- **Document Store**: Manages chunks and metadata
- **Lazy Loading**: Prevents PyTorch conflicts with Streamlit

#### 2. Document Processing Pipeline
```python
def add_text_document(self, text: str, doc_id: str, metadata: Optional[Dict] = None):
    # 1. Split text into chunks
    chunks = self._chunk_text(text)
    
    for i, chunk in enumerate(chunks):
        # 2. Generate embeddings
        embedding = self.model.encode([chunk])
        
        # 3. Normalize for cosine similarity
        faiss.normalize_L2(embedding)
        
        # 4. Add to FAISS index
        self.index.add(embedding.astype('float32'))
        
        # 5. Store chunk and metadata
        self.documents.append(chunk)
        self.metadata.append(chunk_metadata)
```

**Why chunk documents?**
- Large documents exceed LLM context windows
- Smaller chunks provide more focused retrieval
- Overlapping chunks prevent information loss at boundaries

#### 3. Similarity Search
```python
def search(self, query: str, n_results: int = 5):
    # 1. Generate query embedding
    query_embedding = self.model.encode([query])
    faiss.normalize_L2(query_embedding)
    
    # 2. Search FAISS index
    scores, indices = self.index.search(query_embedding.astype('float32'), n_results)
    
    # 3. Return ranked results
    search_results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:
            search_results.append({
                "content": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(score)
            })
    
    return search_results
```

**How similarity search works:**
1. Query is converted to the same vector space as documents
2. FAISS finds the most similar document chunks
3. Results are ranked by similarity score
4. Top matches provide context for the LLM

#### 4. Context Integration
```python
def get_context_for_query(self, query: str, max_context_length: int = 2000):
    search_results = self.search(query, n_results=5)
    
    context_parts = []
    current_length = 0
    
    for result in search_results:
        content = result["content"]
        doc_id = result["metadata"].get("doc_id", "unknown")
        
        context_piece = f"[Source: {doc_id}]\n{content}\n"
        
        if current_length + len(context_piece) > max_context_length:
            break
            
        context_parts.append(context_piece)
        current_length += len(context_piece)
    
    return "Relevant context:\n\n" + "\n---\n".join(context_parts)
```

### 🛠 Hands-On Exercise 3
**Task**: Implement semantic search improvements

1. Add relevance score thresholds to filter low-quality matches 

**Advanced Challenge**: Implement hybrid search combining keyword and semantic search.

---

## 🔧 Understanding the Utils Package

### LLM Client (`utils/llm_client.py`)

```python
class LLMClient:
    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        self.model = model
        self.client_config = kwargs
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                **self.client_config
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
```

**Benefits of the wrapper:**
- Unified interface for multiple LLM providers
- Built-in error handling
- Easy configuration management
- Consistent message format

### Search Tools (`utils/search_tools.py`)

```python
class WebSearchTool:
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        if self.serper_api_key:
            return self._search_serper(query, num_results)
        elif self.tavily_api_key:
            return self._search_tavily(query, num_results)
        else:
            return [{"error": "No search API configured"}]
```

**Key features:**
- Multiple search provider support
- Fallback mechanisms
- Structured result formatting
- Rate limiting and error handling

---

## 🧪 Testing and Validation

### Automated Testing
Run the provided test scripts to validate functionality:

```bash
# Test tool calling detection
python test_final_tool_calling.py

# Test RAG system functionality
python -c "
from utils import SimpleRAGSystem
rag = SimpleRAGSystem()
print('RAG system working:', len(rag.list_documents()) >= 0)
"
```

### Manual Testing Scenarios

#### Basic Chat Testing
1. Test different temperature settings (0.1, 0.7, 1.5)
2. Try various model providers (OpenAI, Groq)
3. Test with long conversations (10+ messages)

#### Search Integration Testing
1. **Current events**: "What's the latest news about climate change?"
2. **Real-time data**: "Current Bitcoin price"
3. **Weather queries**: "Weather in Tokyo today"
4. **Stock information**: "Apple stock performance this week"

#### RAG System Testing
1. Upload various document types (text, PDF)
2. Ask questions that require cross-document knowledge
3. Test with documents in different languages
4. Verify source attribution in responses

---

## 🚨 Troubleshooting Guide

### Common Issues and Solutions

#### 1. API Key Issues
**Problem**: "Authentication failed" or "Invalid API key"
```python
# Debug API key configuration
import os
from dotenv import load_dotenv
load_dotenv()

print("OpenAI key:", os.getenv("OPENAI_API_KEY")[:10] + "..." if os.getenv("OPENAI_API_KEY") else "Not set")
```

#### 2. Import Errors
**Problem**: "ModuleNotFoundError: No module named 'utils'"
```python
# Check Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

#### 3. PyTorch/Streamlit Conflicts
**Problem**: "RuntimeError: Tried to instantiate class '__path__._path'"
- This is a known compatibility issue
- **Solution**: The error is non-critical; the application still works
- **Workaround**: Set environment variables:
```bash
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
```

#### 4. FAISS Installation Issues
**Problem**: ImportError with FAISS
```bash
# Install FAISS for your system
pip install faiss-cpu  # For CPU-only systems
# or
pip install faiss-gpu  # For GPU-enabled systems
```

#### 5. Memory Issues with Large Documents
**Problem**: Out of memory when processing large PDFs
```python
# Adjust chunk size in RAG system
rag = SimpleRAGSystem()
# Default chunk_size=500, try smaller values like 300
```

---

## 🎓 Extension Projects

### Beginner Level
1. **Theme Customization**: Modify Streamlit themes and styling
2. **Message Export**: Add functionality to export chat history
3. **Usage Statistics**: Track and display API usage statistics

### Intermediate Level
1. **Multi-Language Support**: Add translation capabilities
2. **Voice Interface**: Integrate speech-to-text and text-to-speech
3. **Custom Embeddings**: Implement domain-specific embedding models

### Advanced Level
1. **Multi-Modal RAG**: Support for images and videos in documents
2. **Agent Framework**: Build autonomous agents with multiple tools
3. **Production Deployment**: Deploy to cloud platforms with monitoring

---

## 📖 Additional Resources

### Documentation
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FAISS Documentation](https://faiss.ai/index.html)
- [SentenceTransformers Documentation](https://www.sbert.net/)

### Research Papers
- **RAG**: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
- **Tool Calling**: "Toolformer: Language Models Can Teach Themselves to Use Tools" (Schick et al., 2023)
- **Vector Search**: "Billion-scale similarity search with GPUs" (Johnson et al., 2017)

### API Resources
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Groq API Documentation](https://console.groq.com/docs)
- [Serper API Documentation](https://serper.dev/api-documentation)
- [Tavily API Documentation](https://tavily.com/docs)

---  

## 🤝 Submission
- Clone CS203_w12_lab
- Add collaborator `kitt-cmu`
- Commit changes with clear messages for each task:
  - **Task 0**: `echo_bot.py` with clear chat button and message counter enhancements
  - **Task 1**: `basic_chat.py` with message timestamp and clear button
  - **Task 2**: `utils/conversion_tools.py` and modification in `chat_with_search.py` for conversion tools handling
  - **Task 3**: `chat_with_rag.py` `rag_system.py` with relevance score filter for document retrieval
- Push to your github repository

### Code Style Guidelines
- Follow PEP 8 for Python code formatting
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include type hints where appropriate

---

**Happy coding! 🚀**

*This lab sheet is designed to provide comprehensive understanding of modern LLM application development. Take your time to understand each concept and don't hesitate to experiment with the code!*