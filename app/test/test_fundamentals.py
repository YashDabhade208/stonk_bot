import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamentals_agent import run_fundamentals_agent

if __name__ == "__main__":
    stock = input("Enter stock symbol (e.g., AAPL, TSLA, NVDA): ").strip().upper()
    print("\nRunning fundamentals agent...\n")
    result = run_fundamentals_agent(stock)
    print(result)
