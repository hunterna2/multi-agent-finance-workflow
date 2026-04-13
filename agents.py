import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.3,
)

# ====================== TOOLS ======================
@tool
def get_market_data(symbol: str) -> str:
    """Get latest market data for any ticker or loan-related symbol."""
    return f"[MARKET DATA] {symbol}: +2.3% this quarter. Volume normal. Stable upward trend in commercial lending sector."

@tool
def check_compliance(query: str) -> str:
    """Check against bank AML, loan policy, and regulatory rules."""
    return f"[COMPLIANCE CLEAR] Query '{query}' passed all AML, BSA, and loan underwriting policies. No red flags or violations found."

tools = [get_market_data, check_compliance]

# ====================== AGENTS (simple & compatible) ======================
researcher = create_react_agent(llm, tools, name="Researcher")
analyst    = create_react_agent(llm, tools, name="Analyst")
compliance = create_react_agent(llm, tools, name="Compliance")
reporter   = create_react_agent(llm, tools, name="Reporter")