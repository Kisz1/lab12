"""
Main Streamlit Application Hub
Navigation hub for all chat application demos
"""

import streamlit as st
from pathlib import Path


def main():
    st.set_page_config(
        page_title="LLM Chat Demo Hub",
        page_icon="🚀",
        layout="wide"
    )

    # Header
    st.title("🚀 LLM Chat Application Demo Hub")
    st.markdown(
        "### CS203 Week 12 Lab - Advanced LLM Integration with Streamlit")

    st.markdown("""
    Welcome to the comprehensive LLM chat application demos! This project demonstrates
    three different approaches to building chat applications with Large Language Models,
    progressing from basic chat to advanced RAG systems.
    """)

    # Navigation cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 💬 Basic Chat
        **Perfect for beginners**
        
        Features:
        - Simple chat interface
        - LiteLLM integration
        - Model configuration
        - Session management
        
        **Learning Goals:**
        - Understand LLM APIs
        - Streamlit basics
        - Chat state management
        """)

        if st.button("🚀 Launch Basic Chat", type="primary", key="basic"):
            st.markdown("**Run this command in terminal:**")
            st.code("streamlit run src/basic_chat.py", language="bash")

    with col2:
        st.markdown("""
        ### 🔍 Chat with Web Search
        **Intermediate level**
        
        Features:
        - Real-time web search
        - Tool calling concepts
        - Current information retrieval
        - Enhanced context
        
        **Learning Goals:**
        - Function calling
        - API integration
        - Tool orchestration
        """)

        if st.button("🚀 Launch Search Chat", type="primary", key="search"):
            st.markdown("**Run this command in terminal:**")
            st.code("streamlit run src/chat_with_search.py", language="bash")

    with col3:
        st.markdown("""
        ### 📚 Chat with RAG
        **Advanced level**
        
        Features:
        - Document ingestion
        - Vector search
        - Knowledge retrieval
        - Enterprise-ready
        
        **Learning Goals:**
        - Vector databases
        - Semantic search
        - Document processing
        """)

        if st.button("🚀 Launch RAG Chat", type="primary", key="rag"):
            st.markdown("**Run this command in terminal:**")
            st.code("streamlit run src/chat_with_rag.py", language="bash")

    st.divider()

    # Setup instructions
    st.markdown("## 🛠️ Setup Instructions")

    setup_col1, setup_col2 = st.columns(2)

    with setup_col1:
        st.markdown("""
        ### 📦 Installation
        
        1. **Install dependencies:**
        ```bash
        pip install -r requirements.txt
        ```
        
        2. **Configure environment:**
        ```bash
        cp .env.example .env
        # Edit .env with your API keys
        ```
        
        3. **Run applications:**
        ```bash
        # Basic chat
        streamlit run src/basic_chat.py
        
        # Search chat
        streamlit run src/chat_with_search.py
        
        # RAG chat
        streamlit run src/chat_with_rag.py
        ```
        """)

    with setup_col2:
        st.markdown("""
        ### 🔑 Required API Keys
        
        **For all apps:**
        - OpenAI API key (or other LLM provider)
        
        **For search functionality:**
        - Serper API key (recommended)
        - Or Tavily API key (alternative)
        
        **Get API keys:**
        - OpenAI: [platform.openai.com](https://platform.openai.com)
        - Serper: [serper.dev](https://serper.dev)
        - Tavily: [tavily.com](https://tavily.com)
        
        **Supported Models:**
        - GPT-3.5 Turbo, GPT-4
        - Claude 3 (Sonnet, Haiku)
        - Gemini Pro, Gemini 1.5 Pro
        """)

    st.divider()

    # Project structure
    st.markdown("## 📁 Project Structure")

    st.code("""
CS203_w12_lab/
├── src/
│   ├── basic_chat.py           # Basic chat application
│   ├── chat_with_search.py     # Chat with web search
│   └── chat_with_rag.py        # Chat with RAG system
├── utils/
│   ├── llm_client.py           # LiteLLM wrapper
│   ├── search_tools.py         # Web search utilities
│   ├── rag_system.py           # RAG implementation
│   └── __init__.py
├── data/                       # Data storage (created automatically)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .env                       # Your API keys (create this)
└── README.md                  # Project documentation
    """, language="text")

    st.divider()

    # Learning path
    st.markdown("## 🎓 Recommended Learning Path")

    learning_steps = [
        {
            "step": 1,
            "title": "Start with Basic Chat",
            "description": "Understand LLM integration and Streamlit basics",
            "tasks": [
                "Run the basic chat app",
                "Experiment with different models",
                "Modify temperature and max tokens",
                "Add system messages"
            ]
        },
        {
            "step": 2,
            "title": "Explore Web Search Integration",
            "description": "Add real-time information capabilities",
            "tasks": [
                "Set up search API keys",
                "Test search functionality",
                "Understand tool calling concepts",
                "Implement custom search triggers"
            ]
        },
        {
            "step": 3,
            "title": "Master RAG Systems",
            "description": "Build knowledge-based chat systems",
            "tasks": [
                "Upload and process documents",
                "Understand vector embeddings",
                "Experiment with different document types",
                "Build custom knowledge bases"
            ]
        },
        {
            "step": 4,
            "title": "Advanced Customization",
            "description": "Enhance and extend the applications",
            "tasks": [
                "Add streaming responses",
                "Implement chat history persistence",
                "Create custom tools",
                "Build evaluation systems"
            ]
        }
    ]

    for step_info in learning_steps:
        with st.expander(f"Step {step_info['step']}: {step_info['title']}"):
            st.markdown(f"**{step_info['description']}**")
            st.markdown("**Tasks to complete:**")
            for task in step_info['tasks']:
                st.markdown(f"- {task}")

    st.divider()

    # Footer
    st.markdown("""
    ### 📚 Additional Resources
    
    - **LiteLLM Documentation:** [docs.litellm.ai](https://docs.litellm.ai)
    - **Streamlit Documentation:** [docs.streamlit.io](https://docs.streamlit.io)
    - **Vector Databases:** Learn about ChromaDB, Pinecone, Weaviate
    - **RAG Techniques:** Explore advanced chunking and retrieval strategies
    
    ---
    
    **Happy coding! 🚀**
    
    *This demo provides a solid foundation for building production-ready LLM applications.
    Use it as starter code for your own projects and experiments.*
    """)


if __name__ == "__main__":
    main()
