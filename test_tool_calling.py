#!/usr/bin/env python3
"""
Test script for automatic tool calling detection
"""


def should_use_search(message_content: str) -> bool:
    """Determine if web search should be used based on the message content"""
    message_lower = message_content.lower()

    # Current/real-time information indicators
    current_info = [
        "current", "latest", "recent", "today", "now", "this week", "this month",
        "2024", "2025", "right now", "at the moment"
    ]

    # News and events
    news_events = [
        "news", "breaking", "update", "happened", "event", "announcement",
        "trending", "viral", "headlines"
    ]

    # Market and financial data
    market_finance = [
        "stock", "price", "market", "trading", "bitcoin", "cryptocurrency"
    ]

    # Weather requests
    weather = [
        "weather", "temperature", "forecast", "rain", "sunny", "cloudy"
    ]

    # Sports scores and results
    sports = [
        "score", "game", "match", "championship", "tournament", "league"
    ]

    all_indicators = current_info + news_events + market_finance + weather + sports

    # Check for explicit indicators
    for indicator in all_indicators:
        if indicator in message_lower:
            return True

    # Check for time-sensitive questions
    time_words = ["today", "now", "current",
                  "latest", "recent", "2024", "2025"]
    question_words = ["what", "how", "when", "where", "who", "why", "which"]

    has_time_word = any(word in message_lower for word in time_words)
    has_question_word = any(word in message_lower for word in question_words)

    if has_time_word and has_question_word:
        return True

    return False


def main():
    print("🧪 Testing Automatic Tool Calling Detection")
    print("=" * 50)

    test_cases = [
        # Should trigger search
        ("What is the weather in Tokyo today?", True),
        ("Latest news about AI", True),
        ("Bitcoin price now", True),
        ("How is Apple stock performing?", True),
        ("What happened with Tesla this week?", True),
        ("Current temperature in New York", True),
        ("Who won the game yesterday?", True),
        ("What are the latest developments in 2024?", True),

        # Should NOT trigger search
        ("What is Python programming?", False),
        ("How does machine learning work?", False),
        ("Explain quantum computing", False),
        ("Write a poem about cats", False),
        ("Help me with my homework", False),
        ("What is 2 + 2?", False),
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

    print("=" * 50)
    print(
        f"Results: {correct}/{total} tests passed ({correct/total*100:.1f}%)")

    if correct == total:
        print("🎉 All tests passed! Automatic tool calling is working correctly.")
    else:
        print("⚠️ Some tests failed. The detection logic may need refinement.")


if __name__ == "__main__":
    main()
