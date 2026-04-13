from graph import graph
from langchain_core.messages import HumanMessage, SystemMessage

print("🚀 Multi-Agent Finance Team is ready!\n")

prompt = input("Enter your finance prompt (or press Enter for demo): ") or "Analyze Q1 loan trends and check for compliance risks"

print("🔄 Running full workflow...\n")

# Strong system instruction for the entire team (especially the Reporter)
system_instruction = SystemMessage(content="""You are a senior AI Finance Team at a major U.S. bank.
Always produce a professional, detailed executive report with these exact sections:

**Market & Research Summary**
**Quantitative Analysis**
**Compliance & Risk Assessment**
**Final Recommendations**

Use bullet points. Be specific, confident, and sound like a real banking professional.""")

result = graph.invoke({
    "messages": [system_instruction, HumanMessage(content=prompt)]
})

print("\n=== FINAL EXECUTIVE REPORT ===\n")
print(result["messages"][-1].content)