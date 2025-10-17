"""
RAG System using FAISS for vector similarity search.
Simple and educational implementation for             try:
                # Ensure model is loaded
                self._ensure_model_loaded()
                # Create embeddings for the chunk
                embedding = self.model.encode([chunk])03 lab.
"""

import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import tempfile

# Suppress PyTorch warnings that conflict with Streamlit
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

import faiss  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore

# Optional imports - will gracefully handle if not available
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class SimpleRAGSystem:
    """
    A simple RAG system using FAISS for vector similarity search.
    Educational implementation with clear, understandable code.
    """
    
    def __init__(self, data_dir: str = "rag_data", embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG system.
        
        Args:
            data_dir: Directory to store FAISS index and metadata
            embedding_model: SentenceTransformer model name
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Lazy initialization to avoid PyTorch conflicts with Streamlit
        self.model = None
        self.embedding_model = embedding_model
        self.embedding_dimension = None
        self.index = None
        
        # Storage for documents and metadata
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        
        # Try to load existing data
        self.load_index()
    
    def _ensure_model_loaded(self):
        """Lazy load the model to avoid PyTorch conflicts with Streamlit."""
        if self.model is None:
            print(f"Loading embedding model: {self.embedding_model}")
            self.model = SentenceTransformer(self.embedding_model)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            
            if self.index is None:
                # Initialize FAISS index (L2 distance)
                self.index = faiss.IndexFlatL2(self.embedding_dimension)  # type: ignore

    def add_text_document(self, text: str, doc_id: str, metadata: Optional[Dict] = None):
        """
        Add a text document to the RAG system

        Args:
            text: The document text to add
            doc_id: Unique identifier for the document
            metadata: Optional metadata dictionary
        """
        # Split text into chunks for better retrieval
        chunks = self._chunk_text(text, chunk_size=500, overlap=50)

        for i, chunk in enumerate(chunks):
            try:
                # Create embedding for the chunk
                embedding = self.model.encode([chunk])
                # Normalize for cosine similarity
                faiss.normalize_L2(embedding)  # type: ignore

                # Add to FAISS index
                self.index.add(embedding.astype('float32'))  # type: ignore
            except Exception as e:
                print(f"Error processing chunk {i} of document {doc_id}: {e}")
                continue

            # Store document text and metadata
            self.documents.append(chunk)
            chunk_metadata = metadata or {}
            chunk_metadata.update({
                "doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_id": f"{doc_id}_chunk_{i}"
            })
            self.metadata.append(chunk_metadata)

        # Save updated data
        self._save_data()
        print(f"Added document '{doc_id}' with {len(chunks)} chunks")

    def add_pdf_document(self, pdf_path: str, doc_id: Optional[str] = None):
        """
        Add a PDF document to the RAG system

        Args:
            pdf_path: Path to the PDF file
            doc_id: Optional document ID (uses filename if not provided)

        Returns:
            str: Success or error message
        """
        if not PYPDF_AVAILABLE:
            return "Error: pypdf not available. Install with: pip install pypdf"

        if doc_id is None:
            doc_id = Path(pdf_path).stem

        try:
            reader = pypdf.PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            metadata = {
                "source": pdf_path,
                "type": "pdf",
                "pages": len(reader.pages)
            }

            self.add_text_document(text, doc_id, metadata)
            return f"Successfully added PDF: {pdf_path}"
        except Exception as e:
            return f"Error processing PDF {pdf_path}: {str(e)}"

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using FAISS

        Args:
            query: Search query text
            n_results: Number of results to return

        Returns:
            List of search results with content and metadata
        """
        try:
            if len(self.documents) == 0:
                return [{"error": "No documents in the system"}]

            # Ensure model is loaded
            self._ensure_model_loaded()
            # Create embedding for query
            query_embedding = self.model.encode([query])
            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)  # type: ignore

            # Search using FAISS
            # Don't search for more than available
            n_results = min(n_results, len(self.documents))
            scores, indices = self.index.search(  # type: ignore
                query_embedding.astype('float32'), n_results)

            search_results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0:  # Valid index
                    search_results.append({
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        # Cosine similarity score
                        "similarity_score": float(score),
                        "rank": i + 1
                    })

            return search_results
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]

    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get relevant context for a query"""
        results = self.search(query, n_results=10)

        context = "Relevant information:\n\n"
        current_tokens = 0

        for result in results:
            if "error" in result:
                continue

            content = result["content"]
            # Rough token estimation (4 chars = 1 token)
            content_tokens = len(content) // 4

            if current_tokens + content_tokens > max_tokens:
                break

            context += f"- {content}\n\n"
            current_tokens += content_tokens

        return context

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

            if i + chunk_size >= len(words):
                break

        return chunks

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the RAG system

        Returns:
            List of document information with metadata
        """
        try:
            # Group by doc_id
            docs = {}
            for metadata in self.metadata:
                doc_id = metadata.get('doc_id', 'unknown')

                if doc_id not in docs:
                    docs[doc_id] = {
                        "doc_id": doc_id,
                        "chunks": 0,
                        "metadata": {k: v for k, v in metadata.items() if k not in ['doc_id', 'chunk_index', 'total_chunks']}
                    }

                docs[doc_id]["chunks"] += 1

            return list(docs.values())
        except Exception as e:
            return [{"error": f"Failed to list documents: {str(e)}"}]

    def delete_document(self, doc_id: str) -> str:
        """
        Delete a document and all its chunks

        Args:
            doc_id: Document ID to delete

        Returns:
            str: Success or error message
        """
        try:
            # Find indices of chunks belonging to this document
            indices_to_remove = []
            for i, metadata in enumerate(self.metadata):
                if metadata.get('doc_id') == doc_id:
                    indices_to_remove.append(i)

            if not indices_to_remove:
                return f"No document found with ID: {doc_id}"

            # Remove from back to front to maintain indices
            for i in reversed(indices_to_remove):
                del self.documents[i]
                del self.metadata[i]

            # Rebuild the FAISS index (simple approach for educational purposes)
            self._rebuild_index()

            # Save updated data
            self._save_data()

            return f"Successfully deleted document: {doc_id} ({len(indices_to_remove)} chunks)"
        except Exception as e:
            return f"Error deleting document {doc_id}: {str(e)}"

    def _rebuild_index(self):
        """Rebuild the FAISS index from current documents"""
        # Ensure model is loaded
        self._ensure_model_loaded()
        # Create new index
        self.index = faiss.IndexFlatIP(self.embedding_dimension)  # type: ignore

        if self.documents:
            # Generate embeddings for all documents
            embeddings = self.model.encode(self.documents)
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)  # type: ignore
            # Add to index
            self.index.add(embeddings.astype('float32'))  # type: ignore

    def _save_data(self):
        """Save documents, metadata, and FAISS index to disk"""
        try:
            # Save documents and metadata
            data = {
                'documents': self.documents,
                'metadata': self.metadata
            }
            with open(self.data_dir / 'documents.pkl', 'wb') as f:
                pickle.dump(data, f)

            # Save FAISS index
            faiss.write_index(self.index, str(
                self.data_dir / 'faiss_index.bin'))
        except Exception as e:
            print(f"Warning: Could not save data: {e}")

    def _load_data(self):
        """Load documents, metadata, and FAISS index from disk"""
        try:
            # Load documents and metadata
            doc_file = self.data_dir / 'documents.pkl'
            if doc_file.exists():
                with open(doc_file, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.metadata = data.get('metadata', [])

            # Load FAISS index
            index_file = self.data_dir / 'faiss_index.bin'
            if index_file.exists() and self.documents:
                self.index = faiss.read_index(str(index_file))

            print(f"Loaded {len(self.documents)} document chunks from storage")
        except Exception as e:
            print(f"Note: Could not load existing data: {e}. Starting fresh.")
            self.documents = []
            self.metadata = []


def load_sample_documents(rag_system: SimpleRAGSystem, data_dir: str = "./data"):
    """Load sample documents for demonstration"""
    data_path = Path(data_dir)
    data_path.mkdir(exist_ok=True)

    # Create sample documents
    sample_docs = [
        {
            "id": "ai_basics",
            "title": "Introduction to Artificial Intelligence",
            "content": """
            Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines 
            that can perform tasks that typically require human intelligence. These tasks include learning, reasoning, 
            problem-solving, perception, and language understanding.
            
            Machine Learning is a subset of AI that focuses on the development of algorithms that can learn and 
            improve from experience without being explicitly programmed. Deep Learning is a further subset of 
            machine learning that uses neural networks with multiple layers to model and understand complex patterns.
            
            Natural Language Processing (NLP) is another important area of AI that deals with the interaction 
            between computers and human language. It enables machines to understand, interpret, and generate 
            human language in a valuable way.
            """
        },
        {
            "id": "llm_guide",
            "title": "Large Language Models Guide",
            "content": """
            Large Language Models (LLMs) are AI systems trained on vast amounts of text data to understand and 
            generate human-like text. Examples include GPT, Claude, and Gemini.
            
            LLMs work by predicting the next word in a sequence based on the context of previous words. They use 
            transformer architecture, which allows them to process and understand long-range dependencies in text.
            
            Key capabilities of LLMs include:
            - Text generation and completion
            - Question answering
            - Summarization
            - Translation
            - Code generation
            - Creative writing
            
            Fine-tuning allows LLMs to be adapted for specific tasks or domains by training on specialized datasets.
            Prompt engineering is the practice of crafting effective prompts to get better results from LLMs.
            """
        },
        {
            "id": "streamlit_basics",
            "title": "Streamlit Development Guide",
            "content": """
            Streamlit is an open-source Python library that makes it easy to create and share beautiful, 
            custom web apps for machine learning and data science.
            
            Key features of Streamlit:
            - Simple Python scripts turn into web apps
            - No frontend experience required
            - Interactive widgets for user input
            - Built-in support for data visualization
            - Easy deployment options
            
            Basic Streamlit components:
            - st.write(): Display text, data, charts
            - st.text_input(): Text input widget
            - st.button(): Button widget
            - st.selectbox(): Dropdown selection
            - st.slider(): Slider widget
            - st.chat_message(): Chat interface components
            - st.chat_input(): Chat input widget
            
            Streamlit apps run from top to bottom on every user interaction, making them reactive and interactive.
            """
        }
    ]

    for doc in sample_docs:
        rag_system.add_text_document(
            text=doc["content"],
            doc_id=doc["id"],
            metadata={"title": doc["title"], "type": "sample_document"}
        )

    return f"Loaded {len(sample_docs)} sample documents into RAG system"
