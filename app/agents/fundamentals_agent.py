# Call yfinance_tools → get_fundamentals()
# Call yfinance_tools → get_revenue_growth_yoy()
# Call yfinance_tools → get_net_margin_trend()
# Package numbers into a prompt
# LLM → analyze + return structured JSON
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate 

from core.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from tools.yfinance_tools import (               
    get_fundamentals,
    get_revenue_growth_yoy,
    get_net_margin_trend,
)

llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    model=OPENROUTER_MODEL,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

prompt = PromptTemplate(
    input_variables=["data"],
    template="""
You are a stock fundamentals analysis assistant.

Analyze the following raw fundamentals data and return a JSON object with:
- valuation_status (undervalued / fair / overvalued)
- revenue_growth_comment
- profitability_comment
- key_strengths (list, 2-5 bullets)
- risk_factors (list, 2-5 bullets)
- fundamentals_score (1-10)

Data to analyze (already numeric and clean):
{data}

STRICT RULES:
- Return JSON ONLY
- No prose, no markdown, no backticks
"""
)

def run_fundamentals_agent(stock: str) -> dict:
    raw = get_fundamentals(stock)
    raw["revenue_growth_yoy"] = get_revenue_growth_yoy(stock)
    raw["net_margin_trend"] = get_net_margin_trend(stock)

    formatted = prompt.format(data=raw)
    response = llm.invoke(formatted)

    try:
        return json.loads(response.content)
    except Exception:
        import re
        match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("LLM did not return JSON")
