"""
Multi-Agent Finance Workflow
Supervisor-powered financial analysis pipeline.
Run: python main.py
"""

import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from langchain_core.messages import HumanMessage, SystemMessage
from graph import graph

AGENT_LABELS = {
    "Supervisor": "🧭 Supervisor",
    "Researcher": "🔍 Researcher",
    "Analyst":    "📊 Analyst",
    "Compliance": "⚖️  Compliance",
    "Reporter":   "📝 Reporter",
}

SYSTEM_PROMPT = SystemMessage(content="""You are operating as a senior AI Finance Team at a major U.S. bank.
The team consists of a Researcher, Quantitative Analyst, Compliance Officer, and Executive Reporter.
Produce professional, data-driven analysis with specific numbers, regulatory citations, and clear recommendations.
Sound like a real banking professional. Every report must be executive-ready.""")

DEMO_PROMPTS = [
    "Analyze JPMorgan Chase (JPM) stock performance and assess the current outlook for large-cap bank stocks.",
    "What are the current AML compliance requirements for high-value wire transfers over $10,000, and are there any recent regulatory updates?",
    "Research Apple (AAPL) financials and determine if an institutional loan of $500M secured against AAPL equity would be appropriate.",
]


def run_query(prompt: str, verbose: bool = True) -> str:
    """Run a single query through the full multi-agent pipeline with live progress."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"PROMPT: {prompt}")
        print("="*60 + "\n")

    final_report = ""
    completed = []
    order = ["Researcher", "Analyst", "Compliance", "Reporter"]

    for event in graph.stream(
        {"messages": [SYSTEM_PROMPT, HumanMessage(content=prompt)], "next": ""},
        stream_mode="updates",
    ):
        for node_name, node_output in event.items():
            label = AGENT_LABELS.get(node_name, node_name)

            if node_name == "Supervisor":
                next_agent = node_output.get("next", "")
                if next_agent and next_agent != "FINISH":
                    step = order.index(next_agent) + 1 if next_agent in order else "?"
                    print(f"  {label} → routing to {next_agent} (step {step}/4)...")
                elif next_agent == "FINISH":
                    print(f"  {label} → workflow complete\n")

            elif node_name in AGENT_LABELS:
                print(f"  {label} working", end="", flush=True)
                messages = node_output.get("messages", [])
                if messages:
                    # Show token count as a rough progress indicator
                    last_msg = messages[-1]
                    content = getattr(last_msg, "content", "")
                    words = len(content.split()) if content else 0
                    print(f" ... done ({words} words)", flush=True)
                    completed.append(node_name)
                    if node_name == "Reporter":
                        final_report = content

                    # Mini progress bar
                    filled = len(completed)
                    bar = "█" * filled + "░" * (4 - filled)
                    pct = int(filled / 4 * 100)
                    print(f"  [{bar}] {pct}% — {filled}/4 agents complete\n")

    if verbose:
        print("=" * 60)
        print("FINAL EXECUTIVE REPORT")
        print("=" * 60)
        print(final_report)

    return final_report


def main():
    print("🏦 Multi-Agent Finance Workflow")
    print("Supervisor-powered | 4 Specialized Agents | Live Data Tools\n")

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        run_query(prompt)
        return

    print("Select a demo prompt or enter your own:")
    print()
    for i, p in enumerate(DEMO_PROMPTS, 1):
        print(f"  [{i}] {p}")
    print(f"  [0] Enter custom prompt")
    print()

    choice = input("Choice (1-3, or 0 for custom): ").strip()

    if choice == "0":
        prompt = input("Enter your financial analysis prompt: ").strip()
        if not prompt:
            prompt = DEMO_PROMPTS[0]
    else:
        try:
            idx = int(choice) - 1
            prompt = DEMO_PROMPTS[idx] if 0 <= idx < len(DEMO_PROMPTS) else DEMO_PROMPTS[0]
        except (ValueError, IndexError):
            prompt = DEMO_PROMPTS[0]

    run_query(prompt)


if __name__ == "__main__":
    main()
