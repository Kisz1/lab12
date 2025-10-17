"""
Utility functions for LiteLLM integration
"""
import os
from typing import Dict, List, Any, Optional
import litellm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMClient:
    """Wrapper class for LiteLLM operations"""

    def __init__(self, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000):
        self.model = model or os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            os.environ["GOOGLE_API_KEY"] = google_key
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send a chat completion request

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for the completion

        Returns:
            str: The response content
        """
        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """
        Send a streaming chat completion request

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for the completion

        Yields:
            str: Chunks of the response content
        """
        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                stream=True,
                **kwargs
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"


def get_available_models() -> List[str]:
    """Get list of available models"""
    return [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview",
        #"claude-3-sonnet-20240229",
        #"claude-3-haiku-20240307",
        #"gemini-pro",
        #"gemini-1.5-pro",
        "groq/llama-3.3-70b-versatile"
    ]


def format_messages(chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Format chat history for LiteLLM"""
    formatted_messages = []
    for message in chat_history:
        formatted_messages.append({
            "role": message["role"],
            "content": message["content"]
        })
    return formatted_messages
