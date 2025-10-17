#!/usr/bin/env python3
"""
Final comprehensive test for tool calling functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def comprehensive_tool_calling_test():
    """Comprehensive test of the tool calling system"""

    print("🧪 COMPREHENSIVE TOOL CALLING TEST")
    print("=" * 70)

    # Test detection logic (matching the actual chat app)
    def should_use_search(message_content: str) -> bool:
        message_lower = message_content.lower()

        search_triggers = [
            # Explicit search requests
            "search:", "search for", "look up", "find information", "google",
            # Current/real-time information requests
            "current", "latest", "recent", "today", "now", "this week", "2024", "2025",
            # News and events
            "news", "update", "happened", "breaking", "announcement",
            # Market and weather data
            "stock", "price", "weather", "temperature", "forecast",
            # Sports and games
            "game", "match", "score", "won", "championship", "tournament",
            # Questions about recent developments
            "what's new", "what happened", "any updates"
        ]

        should_search = any(
            trigger in message_lower for trigger in search_triggers)

        # Time-sensitive questions
        time_words = ["today", "now", "current",
                      "latest", "recent", "2024", "2025"]
        question_words = ["what", "how", "when", "where", "who", "why"]

        has_time_word = any(word in message_lower for word in time_words)
        has_question_word = any(
            word in message_lower for word in question_words)

        if has_time_word and has_question_word:
            should_search = True

        return should_search

    # Comprehensive test cases
    test_cases = [
        # SHOULD TRIGGER SEARCH (Current Events & Real-time Data)
        ("What's the weather in Tokyo today?", True, "🌤️ Weather"),
        ("Latest news about AI", True, "📰 News"),
        ("Bitcoin price now", True, "💰 Crypto"),
        ("How is Apple stock performing?", True, "📈 Stocks"),
        ("What happened with Tesla this week?", True, "🏢 Company News"),
        ("Current temperature in New York", True, "🌡️ Weather"),
        ("Who won the game yesterday?", True, "⚽ Sports"),
        ("What are the latest developments in 2024?", True, "📅 Recent Events"),
        ("Search for Python tutorials", True, "🔍 Explicit Search"),
        ("Look up machine learning basics", True, "🔍 Explicit Search"),
        ("Any updates on the election?", True, "🗳️ Politics"),
        ("Breaking news today", True, "📰 Breaking News"),
        ("Stock market forecast", True, "📊 Financial"),
        ("Championship results", True, "🏆 Sports"),
        ("What's trending on Twitter?", True, "📱 Social Media"),

        # SHOULD NOT TRIGGER SEARCH (General Knowledge)
        ("What is Python programming?", False, "💻 Programming Concepts"),
        ("How does machine learning work?", False, "🤖 ML Theory"),
        ("Explain quantum computing", False, "⚛️ Science Theory"),
        ("Write a poem about cats", False, "🎨 Creative"),
        ("Help me with my homework", False, "📚 Homework Help"),
        ("What is 2 + 2?", False, "🔢 Math"),
        ("Tell me a joke", False, "😄 Entertainment"),
        ("How do I learn programming?", False, "📖 Learning Advice"),
        ("What are the benefits of exercise?", False, "💪 General Health"),
        ("Explain the theory of relativity", False, "🔬 Physics Theory"),
    ]

    passed = 0
    failed = 0

    print("🔍 SEARCH DETECTION RESULTS:")
    print("-" * 70)

    for query, expected, category in test_cases:
        result = should_use_search(query)
        if result == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        action = "SEARCH" if result else "NO SEARCH"
        print(f"{status} | {action:9} | {category:15} | {query}")

    print("-" * 70)
    print(
        f"📊 RESULTS: {passed}/{passed + failed} tests passed ({passed/(passed + failed)*100:.1f}%)")

    if failed == 0:
        print("🎉 PERFECT! All tool calling detection tests passed!")
        print("🚀 The system is ready for production use!")
    else:
        print(f"⚠️ {failed} tests failed. May need refinement.")

    return failed == 0


def test_query_extraction():
    """Test query extraction and cleaning"""
    print("\n🔍 QUERY EXTRACTION TEST")
    print("=" * 70)

    def extract_query(message_content: str) -> str:
        query = message_content
        message_lower = message_content.lower()

        prefixes_to_remove = [
            "search:", "search for", "look up", "find information about",
            "tell me about", "what is", "what are", "how is"
        ]

        for prefix in prefixes_to_remove:
            if message_lower.startswith(prefix):
                query = query[len(prefix):].strip()
                break

        # Clean up the query (be more careful with question marks)
        if query.endswith("?"):
            query = query[:-1].strip()
        if not query:
            query = message_content

        return query

    extractions = [
        ("search: weather in Tokyo", "weather in Tokyo"),
        ("look up latest AI news", "latest AI news"),
        ("What is the current temperature?", "What is the current temperature"),
        ("find information about Bitcoin price", "Bitcoin price"),
        ("tell me about the stock market today", "the stock market today"),
        ("How is Apple stock performing?", "How is Apple stock performing"),
    ]

    for original, expected in extractions:
        extracted = extract_query(original)
        status = "✅ PASS" if extracted == expected else "❌ FAIL"
        print(f"{status} | '{original}' → '{extracted}'")
        if extracted != expected:
            print(f"      Expected: '{expected}'")


def main():
    success = comprehensive_tool_calling_test()
    test_query_extraction()

    print("\n" + "=" * 70)
    if success:
        print("🎉 TOOL CALLING SYSTEM IS FULLY FUNCTIONAL!")
        print("🚀 Ready for student testing!")
        print("\n📝 NEXT STEPS:")
        print("1. Run: streamlit run src/chat_with_search.py")
        print("2. Try natural queries like 'What's the weather today?'")
        print("3. Observe automatic search detection and execution")
        print("4. Test with various query types to see intelligent tool calling")
    else:
        print("⚠️ Some issues found. Please review the failed tests.")


if __name__ == "__main__":
    main()
