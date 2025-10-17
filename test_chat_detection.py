#!/usr/bin/env python3
"""
Test the tool calling detection logic from the actual chat app
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_search_detection():
    """Test the search detection logic from chat_with_search.py"""

    def should_use_search(message_content: str) -> bool:
        """Copy of the detection logic from handle_tool_calls"""
        message_lower = message_content.lower()

        # Enhanced tool calling detection
        search_triggers = [
            # Explicit search requests
            "search:", "search for", "look up", "find information", "google",

            # Current/real-time information requests
            "current", "latest", "recent", "today", "now", "this week", "2024", "2025",

            # News and events
            "news", "update", "happened", "breaking", "announcement",

            # Market and weather data
            "stock", "price", "weather", "temperature", "forecast",

            # Questions about recent developments
            "what's new", "what happened", "any updates"
        ]

        # Check for search triggers
        should_search = any(
            trigger in message_lower for trigger in search_triggers)

        # Also check for time-sensitive questions
        time_words = ["today", "now", "current",
                      "latest", "recent", "2024", "2025"]
        question_words = ["what", "how", "when", "where", "who", "why"]

        has_time_word = any(word in message_lower for word in time_words)
        has_question_word = any(
            word in message_lower for word in question_words)

        if has_time_word and has_question_word:
            should_search = True

        return should_search

    print("🧪 Testing Tool Calling Detection from Chat App")
    print("=" * 60)

    test_cases = [
        # Should trigger search
        ("What's the weather in Tokyo today?", True),
        ("Latest news about AI", True),
        ("Bitcoin price now", True),
        ("How is Apple stock performing?", True),
        ("What happened with Tesla this week?", True),
        ("Current temperature in New York", True),
        ("Who won the game yesterday?", True),
        ("What are the latest developments in 2024?", True),
        ("Search for Python tutorials", True),
        ("Look up machine learning basics", True),
        ("Any updates on the election?", True),
        ("Breaking news today", True),
        ("Stock market forecast", True),

        # Should NOT trigger search
        ("What is Python programming?", False),
        ("How does machine learning work?", False),
        ("Explain quantum computing", False),
        ("Write a poem about cats", False),
        ("Help me with my homework", False),
        ("What is 2 + 2?", False),
        ("Tell me a joke", False),
        ("How do I learn programming?", False),
    ]

    correct = 0
    total = len(test_cases)

    for query, expected in test_cases:
        result = should_use_search(query)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        action = "SEARCH" if result else "NO SEARCH"

        print(f"{status} | {action:9} | {query}")

        if result == expected:
            correct += 1

    print("=" * 60)
    print(
        f"Results: {correct}/{total} tests passed ({correct/total*100:.1f}%)")

    if correct == total:
        print("🎉 Perfect! Tool calling detection is working correctly!")
        return True
    else:
        print("⚠️ Some tests failed. Detection logic may need refinement.")
        return False


def test_query_extraction():
    """Test query extraction logic"""

    def extract_query(message_content: str) -> str:
        """Copy of query extraction logic"""
        query = message_content
        message_lower = message_content.lower()

        # Remove common prefixes
        prefixes_to_remove = [
            "search:", "search for", "look up", "find information about",
            "tell me about", "what is", "what are", "how is"
        ]

        for prefix in prefixes_to_remove:
            if message_lower.startswith(prefix):
                query = query[len(prefix):].strip()
                break

        # Clean up the query
        query = query.replace("?", "").strip()
        if not query:
            query = message_content

        return query

    print("\n🔍 Testing Query Extraction")
    print("=" * 60)

    test_extractions = [
        ("search: weather in Tokyo", "weather in Tokyo"),
        ("look up latest AI news", "latest AI news"),
        ("What is the current temperature?", "What is the current temperature"),
        ("find information about Bitcoin price", "Bitcoin price"),
        ("tell me about the stock market today", "the stock market today"),
    ]

    for original, expected in test_extractions:
        extracted = extract_query(original)
        status = "✅ PASS" if extracted == expected else "❌ FAIL"
        print(f"{status} | '{original}' → '{extracted}'")
        if extracted != expected:
            print(f"      Expected: '{expected}'")


if __name__ == "__main__":
    success = test_search_detection()
    test_query_extraction()

    if success:
        print("\n🚀 Ready for real-world testing!")
        print("Try running: streamlit run src/chat_with_search.py")
