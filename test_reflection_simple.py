#!/usr/bin/env python3
"""
Simple test for the reflection agent functionality
"""

from app.agents.reflection import reflect

def test_reflection():
    # Test case 1: User preference for short bullet points
    conversation1 = """
    🧠 USER: I prefer short bullet point answers.
    🤖 AGENT: Here are the potential risks related to supply chain management mentioned in the context:
    • Loss, addition, or change of a supplier
    • Lack of control over product quantity, quality, and delivery schedules
    """

    memory1 = reflect(conversation1)
    print("Test 1 - Short bullet preference:")
    print(f"Input: {conversation1}")
    print(f"Memory extracted: {memory1}")
    print()

    # Test case 2: User preference for detailed answers
    conversation2 = """
    🧠 USER: I prefer detailed comprehensive answers.
    🤖 AGENT: I'll provide a comprehensive analysis...
    """

    memory2 = reflect(conversation2)
    print("Test 2 - Detailed preference:")
    print(f"Memory extracted: {memory2}")
    print()

    # Test case 3: Risk tolerance
    conversation3 = """
    🧠 USER: I'm conservative and risk-averse when it comes to investing.
    🤖 AGENT: Based on your risk-averse profile...
    """

    memory3 = reflect(conversation3)
    print("Test 3 - Risk tolerance:")
    print(f"Memory extracted: {memory3}")
    print()

    # Test case 4: Stock interests
    conversation4 = """
    🧠 USER: What's your analysis of Tesla stock?
    🤖 AGENT: Tesla has several interesting factors...
    """

    memory4 = reflect(conversation4)
    print("Test 4 - Stock interest:")
    print(f"Memory extracted: {memory4}")
    print()

if __name__ == "__main__":
    print("🧪 Testing deterministic memory extraction...")
    test_reflection()