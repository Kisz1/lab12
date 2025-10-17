"""
Chat Application with RAG (Retrieval Augmented Generation)
Demonstrates document-based question answering with vector search
"""


import streamlit as st
import sys
import os
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
 
from utils import LLMClient, SimpleRAGSystem, get_available_models, load_sample_documents, load_sample_documents_for_demo

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = None
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = None
    if "rag_initialized" not in st.session_state:
        st.session_state.rag_initialized = False


def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("context_used", False):
                st.markdown("📚 *Used document context*")
            st.markdown(message["content"])


def display_documents():
    """Display documents in the RAG system"""
    if st.session_state.rag_system:
        docs = st.session_state.rag_system.list_documents()

        if docs and not any("error" in doc for doc in docs):
            st.subheader("📄 Documents in Knowledge Base")
            for doc in docs:
                with st.expander(f"📄 {doc.get('doc_id', 'Unknown')} ({doc.get('chunks', 0)} chunks)"):
                    st.json(doc.get('metadata', {}))
                    if st.button(f"Delete {doc['doc_id']}", key=f"delete_{doc['doc_id']}"):
                        result = st.session_state.rag_system.delete_document(
                            doc['doc_id'])
                        st.success(result)
                        st.rerun()
        else:
            st.info("No documents in knowledge base yet.")


def main():
    st.set_page_config(
        page_title="Chat with RAG",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 Chat with RAG (Retrieval Augmented Generation)")
    st.markdown(
        "AI chat with document-based knowledge retrieval - Enterprise-ready starter code!")

    # Initialize session state
    init_session_state()

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Model selection
        available_models = get_available_models()
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            index=0,
            help="Choose the language model to use"
        )

        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in responses"
        )

        # Max tokens
        max_tokens = st.slider(
            "Max Tokens",
            min_value=50,
            max_value=4000,
            value=2000,
            step=50,
            help="Maximum length of response"
        )

        # RAG settings
        st.subheader("📚 RAG Settings")
        context_max_tokens = st.slider(
            "Context Max Tokens",
            min_value=500,
            max_value=3000,
            value=1500,
            step=100,
            help="Maximum tokens for context"
        )

        n_results = st.slider(
            "Search Results",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of document chunks to retrieve"
        )

        # Initialize systems
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🤖 Init Model") or st.session_state.llm_client is None:
                with st.spinner("Initializing model..."):
                    st.session_state.llm_client = LLMClient(
                        model=selected_model,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                st.success("Model ready!")

        with col2:
            if st.button("📚 Init RAG") or st.session_state.rag_system is None:
                with st.spinner("Initializing RAG system..."):
                    st.session_state.rag_system = SimpleRAGSystem()
                    if not st.session_state.rag_initialized:
                        load_sample_documents_for_demo(st.session_state.rag_system)
                        st.session_state.rag_initialized = True
                st.success("RAG ready!")

        st.divider()

        # Document management
        st.subheader("📁 Document Management")

        # File upload
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=["txt", "pdf"],
            accept_multiple_files=True,
            help="Upload text or PDF files to add to knowledge base"
        )

        if uploaded_files and st.session_state.rag_system:
            for uploaded_file in uploaded_files:
                if st.button(f"Add {uploaded_file.name}", key=f"add_{uploaded_file.name}"):
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name

                        try:
                            if uploaded_file.type == "application/pdf":
                                result = st.session_state.rag_system.add_pdf_document(
                                    tmp_path,
                                    uploaded_file.name.split('.')[0]
                                )
                            else:
                                # Text file
                                content = uploaded_file.getvalue().decode("utf-8")
                                st.session_state.rag_system.add_text_document(
                                    content,
                                    uploaded_file.name.split('.')[0],
                                    {"source": uploaded_file.name,
                                        "type": "uploaded"}
                                )
                                result = f"Successfully added text file: {uploaded_file.name}"

                            st.success(result)
                        except Exception as e:
                            st.error(
                                f"Error processing {uploaded_file.name}: {str(e)}")
                        finally:
                            # Clean up temp file
                            os.unlink(tmp_path)

                        st.rerun()

        # Add text document
        with st.expander("✍️ Add Text Document"):
            doc_title = st.text_input("Document Title")
            doc_content = st.text_area("Document Content", height=200)

            if st.button("Add Text Document") and doc_title and doc_content and st.session_state.rag_system:
                st.session_state.rag_system.add_text_document(
                    doc_content,
                    doc_title.lower().replace(" ", "_"),
                    {"title": doc_title, "type": "manual_entry"}
                )
                st.success(f"Added document: {doc_title}")
                st.rerun()

        # Load sample documents
        if st.button("📖 Load Sample Docs") and st.session_state.rag_system:
            result = load_sample_documents(st.session_state.rag_system)
            st.success(result)
            st.rerun()

        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.markdown("### 📚 About")
        st.markdown("""
        This RAG-enabled chat app demonstrates:
        - Document ingestion and vectorization
        - Semantic search and retrieval
        - Context-aware responses
        - Knowledge base management
        
        **Features:**
        - Upload PDF and text files
        - Semantic search across documents
        - Contextual AI responses
        - Document management
        
        **For Students:**
        - Experiment with different embedding models
        - Implement advanced chunking strategies
        - Add metadata filtering
        - Create document summarization
        - Build citation systems
        """)

    # Main interface - Two tabs
    tab1, tab2 = st.tabs(["💬 Chat", "📄 Documents"])

    with tab1:
        # Main chat interface
        if not st.session_state.llm_client or not st.session_state.rag_system:
            st.warning(
                "⚠️ Please initialize both Model and RAG system in the sidebar first!")
            return

        # Display existing chat messages
        display_chat_messages()

        # Example queries
        st.markdown("### 💡 Try these example queries:")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🧠 What is artificial intelligence?"):
                st.session_state.example_query = "What is artificial intelligence and how does it work?"

        with col2:
            if st.button("🤖 Explain large language models"):
                st.session_state.example_query = "How do large language models work and what are their capabilities?"

        with col3:
            if st.button("🌐 Tell me about Streamlit"):
                st.session_state.example_query = "What is Streamlit and how do I use it for building apps?"

        # Chat input
        prompt = st.chat_input("Ask me anything about the documents...")

        # Handle example query
        if hasattr(st.session_state, 'example_query'):
            prompt = st.session_state.example_query
            delattr(st.session_state, 'example_query')

        if prompt:
            # Add user message to chat history
            st.session_state.messages.append(
                {"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Searching documents and generating response..."):
                    # Get relevant context from RAG system
                    context = st.session_state.rag_system.get_context_for_query(
                        prompt, max_context_length=2000)

                    # Create enhanced prompt with context
                    enhanced_prompt = f"""
                    Based on the following information from the knowledge base, please answer the user's question:

                    {context}

                    User Question: {prompt}

                    Please provide a comprehensive answer based on the information provided above. If the information is not sufficient or not found in the knowledge base, please mention that clearly.
                    """

                    # Prepare messages for LLM
                    messages = []
                    # Add conversation history (excluding current question)
                    for msg in st.session_state.messages[:-1]:
                        messages.append(
                            {"role": msg["role"], "content": msg["content"]})

                    # Add the enhanced prompt
                    messages.append(
                        {"role": "user", "content": enhanced_prompt})

                    # Get response from LLM
                    response = st.session_state.llm_client.chat(messages)

                    # Display response
                    st.markdown(response)

                    # Show retrieved context in expander
                    with st.expander("📄 Retrieved Context"):
                        st.markdown(context)

                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "context_used": True
                    })

    with tab2:
        # Document management tab
        display_documents()


if __name__ == "__main__":
    main()
