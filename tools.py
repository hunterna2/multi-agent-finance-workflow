import os
import requests
import yfinance as yf
from langchain_core.tools import tool
from tavily import TavilyClient

RAG_BASE_URL = "https://aca-backend-banking-demo.mangostone-87dfdce5.eastus.azurecontainerapps.io"


@tool
def query_rag_chatbot(question: str) -> str:
    """Query the live banking RAG chatbot for grounded answers about bank policies,
    loan products, compliance rules, and internal knowledge base content.
    Returns the answer with cited sources when available."""
    endpoints = ["/chat", "/api/chat", "/query", "/api/query", "/ask"]
    payload_keys = [
        {"question": question},
        {"query": question},
        {"message": question},
        {"input": question},
    ]
    for endpoint in endpoints:
        for payload in payload_keys:
            try:
                resp = requests.post(
                    f"{RAG_BASE_URL}{endpoint}",
                    json=payload,
                    timeout=15,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    answer = (
                        data.get("answer")
                        or data.get("response")
                        or data.get("message")
                        or data.get("content")
                        or data.get("result")
                        or str(data)
                    )
                    sources = data.get("sources") or data.get("citations") or data.get("references") or []
                    if sources:
                        src_text = "\n".join(f"  - {s}" for s in sources[:5])
                        return f"{answer}\n\nSources:\n{src_text}"
                    return str(answer)
            except Exception:
                continue
    # Try GET as last resort
    try:
        resp = requests.get(
            f"{RAG_BASE_URL}/chat",
            params={"question": question},
            timeout=10,
        )
        if resp.status_code == 200:
            return str(resp.json())
    except Exception:
        pass
    return (
        f"[RAG UNAVAILABLE] Could not reach banking knowledge base for: '{question}'. "
        "Proceeding with general knowledge."
    )


@tool
def get_market_data(symbol: str) -> str:
    """Fetch real-time or recent market data for a stock, ETF, or financial instrument
    using yfinance. Returns price, change, volume, and key financial metrics."""
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.fast_info
        hist = ticker.history(period="5d")

        if hist.empty:
            return f"[NO DATA] No market data found for symbol: {symbol}"

        latest_close = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else latest_close
        pct_change = ((latest_close - prev_close) / prev_close) * 100

        volume = hist["Volume"].iloc[-1]
        high_52w = getattr(info, "year_high", "N/A")
        low_52w = getattr(info, "year_low", "N/A")
        market_cap = getattr(info, "market_cap", None)
        mc_str = f"${market_cap:,.0f}" if market_cap else "N/A"

        return (
            f"[MARKET DATA] {symbol.upper()}\n"
            f"  Latest Close: ${latest_close:.2f}\n"
            f"  1-Day Change: {pct_change:+.2f}%\n"
            f"  Volume: {volume:,.0f}\n"
            f"  52-Week High: {high_52w}\n"
            f"  52-Week Low: {low_52w}\n"
            f"  Market Cap: {mc_str}"
        )
    except Exception as e:
        return f"[MARKET DATA ERROR] Failed to fetch data for {symbol}: {str(e)}"


@tool
def search_web(query: str) -> str:
    """Search the web for current financial news, SEC filings, regulatory updates,
    earnings reports, and market intelligence. Uses Tavily for high-quality financial results."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return (
            "[SEARCH UNAVAILABLE] TAVILY_API_KEY not set. "
            f"Would have searched for: '{query}'"
        )
    try:
        client = TavilyClient(api_key=api_key)
        result = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
        )
        answer = result.get("answer", "")
        results = result.get("results", [])

        output_parts = []
        if answer:
            output_parts.append(f"Summary: {answer}")
        for r in results[:4]:
            title = r.get("title", "")
            url = r.get("url", "")
            content = r.get("content", "")[:300]
            output_parts.append(f"\n[{title}] {url}\n{content}")

        return "\n".join(output_parts) if output_parts else f"No results found for: {query}"
    except Exception as e:
        return f"[SEARCH ERROR] {str(e)}"


# Tool bundles per agent role
researcher_tools = [query_rag_chatbot, get_market_data, search_web]
analyst_tools = [get_market_data, search_web]
compliance_tools = [query_rag_chatbot, search_web]
reporter_tools = []
