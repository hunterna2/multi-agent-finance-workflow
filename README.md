# Multi-Agent Financial Analysis Workflow

**Live demo:** https://aca-multi-agent-finance.mangostone-87dfdce5.eastus.azurecontainerapps.io

A production-grade **Supervisor-powered multi-agent system** built with LangGraph + Azure OpenAI. Give it one natural-language prompt and it automatically orchestrates a team of four specialized AI agents — Researcher, Analyst, Compliance Officer, and Executive Reporter — to deliver a professional banking executive report with real market data.

---

## What This Demonstrates

- **Multi-agent orchestration** with a Supervisor using Pydantic structured output (`with_structured_output`) to intelligently route tasks
- **LangGraph state management** with shared message history, completed-agent tracking, and cycle prevention
- **Real external tool integration**: live stock data (yfinance), web search (Tavily), and a live RAG knowledge base
- **Production deployment** on Azure Container Apps with managed identity, ACR, and secret management
- **Streaming UI** built in Streamlit showing live agent progress as the pipeline executes

---

## Architecture

```
User Prompt
     │
     ▼
 ┌─────────────┐
 │  Supervisor  │  ← GPT-4o with structured output (RouteDecision)
 │  (router)    │    Tracks completed agents, never loops
 └──────┬──────┘
        │ routes to next agent
        ▼
 ┌────────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
 │ Researcher │───▶│ Analyst  │───▶│ Compliance │───▶│ Reporter │
 └────────────┘    └──────────┘    └────────────┘    └──────────┘
  RAG + yfinance   yfinance        RAG + Search      Final report
  + Web Search     + Search        (regulatory)      (no tools)
        │
        └──────────────────────── all route back to Supervisor ──▶ FINISH
```

Each agent runs a **ReAct loop** (`create_react_agent`) — it can call tools multiple times before handing off. The Supervisor sees the full conversation history and always advances to the next uncompleted agent.

---

## Agents & Tools

| Agent | Role | Tools |
|-------|------|-------|
| **Researcher** | Gathers market data, SEC news, internal KB | `get_market_data`, `search_web`, `query_rag_chatbot` |
| **Analyst** | Quantitative analysis, trends, risk flags | `get_market_data`, `search_web` |
| **Compliance** | AML/BSA, capital requirements, regulatory review | `query_rag_chatbot`, `search_web` |
| **Reporter** | Synthesizes everything into an executive report | *(none)* |

| Tool | Source | Notes |
|------|--------|-------|
| `get_market_data` | yfinance | Live price, volume, 52-week range — no API key needed |
| `search_web` | Tavily API | SEC filings, earnings, regulatory news |
| `query_rag_chatbot` | Azure Container Apps RAG | Internal bank knowledge base with citations |

---

## Project Structure

```
multi-agent-finance-workflow/
├── app.py            # Streamlit UI — streaming agent progress, live report
├── graph.py          # LangGraph Supervisor + StateGraph + routing logic
├── agents.py         # 4 create_react_agent instances with system prompts
├── tools.py          # yfinance, Tavily, and RAG chatbot tools
├── main.py           # CLI entry point for local testing
├── Dockerfile        # Container image for Azure deployment
├── requirements.txt  # Pinned dependencies
└── .env.example      # Environment variable template
```

---

## Running Locally

### 1. Clone & set up environment

```bash
git clone <repo-url>
cd multi-agent-finance-workflow
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure `.env`

```bash
cp .env.example .env
```

```env
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Optional — enables live web search
TAVILY_API_KEY=<your-key>   # Free tier at https://tavily.com
```

### 3. Run

```bash
# Streamlit UI
streamlit run app.py

# CLI
python main.py "Analyze JPM stock and check for compliance risks"
```

---

## Example Prompts

```
Analyze JPMorgan Chase (JPM) stock performance and assess the outlook for large-cap bank stocks.
```
```
What are the AML compliance requirements for wire transfers over $10,000? Any recent FinCEN updates?
```
```
Should we issue a $500M institutional loan secured against Apple (AAPL) equity? Assess the risk.
```
```
Compare Bank of America (BAC) and Goldman Sachs (GS) latest earnings — trading revenue and loan loss provisions.
```
```
Assess the risk profile of a $2B commercial real estate portfolio given current interest rate conditions.
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Azure OpenAI GPT-4o |
| Agent framework | LangGraph + LangChain |
| Market data | yfinance |
| Web search | Tavily |
| RAG knowledge base | Azure Container Apps (Project 1) |
| UI | Streamlit |
| Hosting | Azure Container Apps |
| Container registry | Azure Container Registry |
| Structured output | Pydantic v2 |
