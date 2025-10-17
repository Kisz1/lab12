"""
Quick Test Script - Verify your setup
Run this to check if everything is working correctly
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")

    try:
        import streamlit as st
        print(f"✅ Streamlit {st.__version__}")
    except ImportError:
        print("❌ Streamlit not installed")
        return False

    try:
        import litellm
        print("✅ LiteLLM installed")
    except ImportError:
        print("❌ LiteLLM not installed")
        return False

    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

    try:
        import requests
        print("✅ requests installed")
    except ImportError:
        print("❌ requests not installed")
        return False

    # Optional dependencies
    try:
        import chromadb
        print("✅ ChromaDB installed")
    except ImportError:
        print("⚠️  ChromaDB not installed (needed for RAG)")

    try:
        import sentence_transformers
        print("✅ sentence-transformers installed")
    except ImportError:
        print("⚠️  sentence-transformers not installed (needed for RAG)")

    try:
        import pypdf
        print("✅ pypdf installed")
    except ImportError:
        print("⚠️  pypdf not installed (needed for PDF processing)")

    return True


def test_env_file():
    """Test environment file"""
    print("\n🔍 Testing environment configuration...")

    if not os.path.exists('.env'):
        print("❌ .env file not found. Copy .env.example to .env and add your API keys.")
        return False

    print("✅ .env file exists")

    from dotenv import load_dotenv
    load_dotenv()

    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')

    if openai_key and openai_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key configured")
    elif anthropic_key and anthropic_key != 'your_anthropic_api_key_here':
        print("✅ Anthropic API key configured")
    elif google_key and google_key != 'your_google_api_key_here':
        print("✅ Google API key configured")
    else:
        print("⚠️  No LLM API keys configured. Add at least one to .env file.")

    # Check search keys
    serper_key = os.getenv('SERPER_API_KEY')
    tavily_key = os.getenv('TAVILY_API_KEY')

    if serper_key and serper_key != 'your_serper_api_key_here':
        print("✅ Serper API key configured")
    elif tavily_key and tavily_key != 'your_tavily_api_key_here':
        print("✅ Tavily API key configured")
    else:
        print("⚠️  No search API keys configured (optional for search functionality)")

    return True


def test_utils():
    """Test utility functions"""
    print("\n🔍 Testing utility functions...")

    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.append(str(project_root))

        from utils.llm_client import LLMClient, get_available_models
        print("✅ LLM client utilities working")

        models = get_available_models()
        print(f"✅ Available models: {len(models)} models found")

    except Exception as e:
        print(f"❌ Utils error: {e}")
        return False

    return True


def main():
    print("🚀 CS203 W12 Lab - Setup Verification")
    print("=" * 40)

    success = True

    # Test imports
    if not test_imports():
        success = False

    # Test environment
    if not test_env_file():
        success = False

    # Test utils
    if not test_utils():
        success = False

    print("\n" + "=" * 40)

    if success:
        print("🎉 Setup verification complete!")
        print("\n📋 Ready to run:")
        print("- Main hub: streamlit run app.py")
        print("- Basic chat: streamlit run src/basic_chat.py")
        print("- Search chat: streamlit run src/chat_with_search.py")
        print("- RAG chat: streamlit run src/chat_with_rag.py")
    else:
        print("❌ Setup issues found. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("- Run: pip install -r requirements.txt")
        print("- Copy .env.example to .env and add your API keys")

    print("\n📚 Need help? Check README.md for detailed instructions.")


if __name__ == "__main__":
    main()
