import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools import researcher_tools, analyst_tools, compliance_tools, reporter_tools

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.3,
    max_retries=6,
)

RESEARCHER_PROMPT = """You are the Research Specialist on a senior bank finance team.
Your job is to gather real data: pull market prices, search for SEC filings and news,
and query the bank's internal knowledge base for relevant policies and products.
Be thorough and cite sources. Hand off a structured research brief."""

ANALYST_PROMPT = """You are the Quantitative Analyst on a senior bank finance team.
Your job is to analyze the data gathered by the researcher: identify trends,
calculate key metrics, compare against benchmarks, and flag risks or opportunities.
Use market data tools when you need current prices or financials.
Produce a concise quantitative analysis with specific numbers."""

COMPLIANCE_PROMPT = """You are the Compliance Officer on a senior bank finance team.
Your job is to review all findings for regulatory and policy compliance:
AML/BSA rules, loan underwriting standards, capital requirements, and CFPB guidelines.
Query the bank's RAG knowledge base to verify against internal policies.
Search for any recent regulatory changes. Flag violations clearly, approve clean items."""

REPORTER_PROMPT = """You are the Executive Report Writer on a senior bank finance team.
Your job is to synthesize all research, analysis, and compliance findings into a
polished, executive-ready report. Structure it with these exact sections:

**Executive Summary**
**Market & Research Findings**
**Quantitative Analysis**
**Compliance & Risk Assessment**
**Strategic Recommendations**

Write in a confident, professional banking tone. Be specific with numbers and citations.
This report goes to the C-suite."""

researcher = create_react_agent(
    llm,
    researcher_tools,
    name="Researcher",
    prompt=RESEARCHER_PROMPT,
)

analyst = create_react_agent(
    llm,
    analyst_tools,
    name="Analyst",
    prompt=ANALYST_PROMPT,
)

compliance = create_react_agent(
    llm,
    compliance_tools,
    name="Compliance",
    prompt=COMPLIANCE_PROMPT,
)

reporter = create_react_agent(
    llm,
    reporter_tools,
    name="Reporter",
    prompt=REPORTER_PROMPT,
)
