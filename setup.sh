#!/bin/bash

# CS203 W12 Lab - LLM Chat Demo Setup Script

echo "🚀 CS203 Week 12 Lab - LLM Chat Demo Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip found"

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Requirements installed successfully"
else
    echo "❌ Failed to install requirements"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys."
else
    echo "✅ .env file already exists"
fi

# Create data directory
mkdir -p data
echo "✅ Data directory created"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: streamlit run app.py"
echo ""
echo "Individual apps:"
echo "- Basic Chat: streamlit run src/basic_chat.py"
echo "- Search Chat: streamlit run src/chat_with_search.py"
echo "- RAG Chat: streamlit run src/chat_with_rag.py"
echo ""
echo "Happy coding! 🚀"