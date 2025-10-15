"""
LangChain Tools Definition
Contains all tool definitions for the agent
"""

from langchain_core.tools import tool
from tavily import TavilyClient
import os
import re

# Initialize Tavily client
tavily_client = None

def get_tavily_client():
    """Lazy initialization of Tavily client"""
    global tavily_client
    if tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        tavily_client = TavilyClient(api_key=api_key)
    return tavily_client


@tool
def search_tool(query: str) -> str:
    """
    Search the internet for current information using Tavily API.
    Use this when you need to find recent information, facts, or answer questions requiring web search.
    
    Args:
        query: The search query string
        
    Returns:
        Search results as a formatted string
    """
    try:
        client = get_tavily_client()
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )
        
        results = []
        for idx, result in enumerate(response.get('results', []), 1):
            results.append(f"{idx}. {result.get('title', 'No title')}")
            results.append(f"   {result.get('content', 'No content')[:200]}...")
            results.append(f"   URL: {result.get('url', 'No URL')}\n")
        
        return "\n".join(results) if results else "No results found."
    
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def math_tool(expression: str) -> str:
    """
    Evaluate mathematical expressions safely.
    Supports basic arithmetic operations: +, -, *, /, **, parentheses.
    
    Args:
        expression: Mathematical expression as a string (e.g., "2 + 2", "10 * 5 + 3")
        
    Returns:
        The result of the calculation
    """
    try:
        # Remove any potentially dangerous characters
        safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        
        if not safe_expr.strip():
            return "Error: Invalid expression"
        
        # Evaluate the expression safely
        result = eval(safe_expr, {"__builtins__": {}}, {})
        
        return f"Result: {result}"
    
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Math error: {str(e)}"


@tool
def custom_ticker_info(ticker_symbol: str) -> str:
    """
    Get mock stock ticker information for demonstration purposes.
    Returns simulated stock data for educational purposes.
    
    Args:
        ticker_symbol: Stock ticker symbol (e.g., "AAPL", "GOOGL")
        
    Returns:
        Mock stock information
    """
    # Mock data for demonstration
    mock_data = {
        "AAPL": {"price": 178.50, "change": "+2.3%", "volume": "52M"},
        "GOOGL": {"price": 142.30, "change": "-0.8%", "volume": "28M"},
        "MSFT": {"price": 385.20, "change": "+1.5%", "volume": "35M"},
        "TSLA": {"price": 242.80, "change": "+3.2%", "volume": "98M"},
        "AMZN": {"price": 178.25, "change": "+1.1%", "volume": "45M"},
        "META": {"price": 512.80, "change": "+2.8%", "volume": "31M"},
    }
    
    ticker = ticker_symbol.upper().strip()
    
    if ticker in mock_data:
        data = mock_data[ticker]
        return f"""Ticker: {ticker}
Price: ${data['price']}
Change: {data['change']}
Volume: {data['volume']}
(Note: This is mock data for demonstration purposes)"""
    else:
        available = ", ".join(mock_data.keys())
        return f"Mock data not available for {ticker}. Available tickers: {available}"


# Tool registry for easy access
TOOLS = [search_tool, math_tool, custom_ticker_info]