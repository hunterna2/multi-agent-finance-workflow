# Multi-Agent Financial Analysis Workflow

**Live demo:** https://aca-multi-agent-finance.mangostone-87dfdce5.eastus.azurecontainerapps.io

A production-grade **Supervisor-powered multi-agent system** built with LangGraph + Azure OpenAI. Give it one natural-language prompt and it automatically orchestrates a team of four specialized AI agents — Researcher, Analyst, Compliance Officer, and Executive Reporter — to deliver a professional banking executive report with real market data.

---

## What This Demonstrates

- **Multi-agent orchestration** with a Supervisor using Pydantic structured output to intelligently route tasks
- **LangGraph state management** with shared message history, completed-agent tracking, and cycle prevention
- **MLOps eval layer** — LLM-as-judge scoring, automated CI/CD quality gates, and run history tracking
- **LangSmith observability** — every agent call traced with latency, token counts, and full input/output logs
- **Real external tool integration** — live stock data (yfinance), web search (Tavily), and a live RAG knowledge base
- **Production deployment** on Azure Container Apps with scale-to-zero cost optimization

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
        └──────────────────── all route back to Supervisor ──▶ FINISH

     ↕ every node traced automatically in LangSmith
```

---

## MLOps Eval Layer

This project includes a full evaluation pipeline for measuring and tracking agent quality over time.

### Eval Scorecard (baseline run)

| Agent | Avg Score | Notes |
|---|---|---|
| Reporter | 4.8 / 5 | Consistently executive-ready |
| Researcher | 3.4 / 5 | Good, occasional tool failures |
| Compliance | 3.2 / 5 | Strong on regulatory questions |
| Analyst | 2.8 / 5 | Weakest — improvement target |
| **Pipeline avg** | **3.55 / 5** | Above 3.0 CI threshold ✅ |

### How it works

```
eval/test_prompts.py     ← 5 fixed financial questions (benchmark)
eval/run_evals.py        ← runs all 5 through the full agent pipeline
eval/scorer.py           ← LLM-as-judge grades each agent 1-5
run_logs/run_history.json ← persistent score history over time
.github/workflows/eval.yml ← CI/CD runs evals on every push, fails if avg < 3.0
```

### Running evals locally

```bash
python eval/run_evals.py    # run the 5 test prompts
python eval/scorer.py       # grade each agent + log to run_history.json
python run_logs/run_logger.py  # print score history table
```

### CI/CD quality gate

Every push to `main` automatically:
1. Runs all 5 test prompts through the full pipeline
2. Scores each agent with an LLM judge
3. Fails the build if pipeline average drops below **3.0/5**

---

## Observability — LangSmith

All runs are traced automatically to LangSmith with:
- Full agent execution tree with latency per node
- Token counts and cost per LLM call
- Tool call inputs and outputs
- Supervisor routing decisions

Configured via 3 env vars in `agents.py`:
```python
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<key>
LANGCHAIN_PROJECT=multi-agent-finance
```

---

## Agents & Tools

| Agent | Role | Tools |
|---|---|---|
| **Researcher** | Gathers market data, SEC news, internal KB | `get_market_data`, `search_web`, `query_rag_chatbot` |
| **Analyst** | Quantitative analysis, trends, risk flags | `get_market_data`, `search_web` |
| **Compliance** | AML/BSA, capital requirements, regulatory review | `query_rag_chatbot`, `search_web` |
| **Reporter** | Synthesizes everything into an executive report | *(none)* |

---

## Project Structure

```
multi-agent-finance-workflow/
├── app.py                      # Streamlit UI — agent pipeline + Metrics tab
├── graph.py                    # LangGraph Supervisor + StateGraph + routing
├── agents.py                   # 4 ReAct agents with system prompts + LangSmith config
├── tools.py                    # yfinance, Tavily, RAG chatbot tools
├── eval/
│   ├── test_prompts.py         # 5 fixed benchmark questions
│   ├── run_evals.py            # runs benchmark through the pipeline
│   ├── scorer.py               # LLM-as-judge scoring (1-5 per agent)
│   ├── check_scores.py         # CI gate — fails if avg < 3.0
│   └── results/                # saved JSON outputs per run
├── run_logs/
│   ├── run_logger.py           # persistent score history
│   └── run_history.json        # timestamped score log
├── .github/workflows/eval.yml  # GitHub Actions CI/CD pipeline
├── Dockerfile                  # Azure Container Apps deployment
└── requirements.txt
```

---

## Running Locally

```bash
git clone <repo-url>
cd multi-agent-finance-workflow
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
streamlit run app.py
```

### Required env vars

```env
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<langsmith-key>
LANGCHAIN_PROJECT=multi-agent-finance
TAVILY_API_KEY=<key>   # optional — enables live web search
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Azure OpenAI GPT-4o |
| Agent framework | LangGraph + LangChain |
| Observability | LangSmith |
| Market data | yfinance |
| Web search | Tavily |
| RAG knowledge base | Azure Container Apps |
| UI | Streamlit |
| CI/CD | GitHub Actions |
| Hosting | Azure Container Apps (scale-to-zero) |
| Eval | LLM-as-judge (GPT-4o) |
