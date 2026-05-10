"""
LLM-as-judge scorer. Reads saved eval results and grades each agent's output 1-5.
"""

import os
import sys
import json
from glob import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

SCORING_CRITERIA = {
    "Researcher": """You are grading a Researcher agent's output from a bank finance AI system.
Score 1-5 based on:
- Did it include specific numbers, prices, or data? (not just vague statements)
- Did it cite sources or mention where data came from?
- Did it actually attempt to answer the question asked?
- Did it use available tools (market data, web search)?

1 = No data, no sources, didn't try
2 = Minimal data, mostly vague
3 = Some data but missing sources or depth
4 = Good data with some sources
5 = Specific data, clear sources, thorough""",

    "Analyst": """You are grading an Analyst agent's output from a bank finance AI system.
Score 1-5 based on:
- Did it perform actual quantitative analysis (ratios, percentages, comparisons)?
- Did it go beyond just restating what the Researcher found?
- Did it identify trends, risks, or opportunities with specific numbers?
- Did it add analytical value?

1 = Just restated Researcher data, no analysis
2 = Minimal analysis, mostly repetition
3 = Some analysis but thin on numbers
4 = Good analysis with specific metrics
5 = Deep quantitative analysis, clear insights""",

    "Compliance": """You are grading a Compliance agent's output from a bank finance AI system.
Score 1-5 based on:
- Did it cite specific regulations (AML, BSA, Basel III, CFPB, etc.)?
- Did it actually review the findings for compliance issues?
- Did it flag any risks or approve items with reasoning?
- Did it add compliance value beyond a generic response?

1 = Didn't do anything, just asked a question
2 = Very generic, no specific regulations cited
3 = Some regulations mentioned but shallow
4 = Specific regulations cited with analysis
5 = Thorough compliance review with specific citations and clear findings""",

    "Reporter": """You are grading a Reporter agent's output from a bank finance AI system.
Score 1-5 based on:
- Does the report contain all 5 required sections: Executive Summary, Market & Research Findings, Quantitative Analysis, Compliance & Risk Assessment, Strategic Recommendations?
- Is it written in a professional banking tone?
- Does it include specific numbers and citations from the other agents?
- Is it executive-ready quality?

1 = Missing most sections, unprofessional
2 = Has some sections but incomplete
3 = Has all sections but thin content
4 = All sections with good content
5 = All sections, specific numbers, professional tone, executive-ready""",
}


class AgentScore(BaseModel):
    score: int
    reasoning: str


scorer_llm = llm.with_structured_output(AgentScore)


def score_output(agent_name: str, prompt: str, output: str) -> AgentScore:
    criteria = SCORING_CRITERIA[agent_name]
    message = f"""{criteria}

Original question asked: {prompt}

{agent_name} output to grade:
{output}

Provide your score (1-5) and brief reasoning."""

    return scorer_llm.invoke(message)


def score_run(result_file: str) -> dict:
    with open(result_file) as f:
        run = json.load(f)

    print(f"\nScoring run {run['id']} — {run['category']}")
    print(f"Prompt: {run['prompt'][:70]}...")

    scores = {}
    for agent_name, output in run["agent_outputs"].items():
        if not output or output.strip() == "":
            scores[agent_name] = {"score": 0, "reasoning": "No output"}
            continue
        result = score_output(agent_name, run["prompt"], output)
        scores[agent_name] = {"score": result.score, "reasoning": result.reasoning}
        print(f"  {agent_name}: {result.score}/5 — {result.reasoning[:80]}...")

    overall = round(sum(s["score"] for s in scores.values()) / len(scores), 2)
    print(f"  Overall: {overall}/5")

    scored_run = {**run, "scores": scores, "overall_score": overall}
    out_path = result_file.replace(".json", "_scored.json")
    with open(out_path, "w") as f:
        json.dump(scored_run, f, indent=2)

    return scored_run


def print_summary(scored_runs: list):
    print("\n" + "="*60)
    print("EVAL SCORECARD SUMMARY")
    print("="*60)

    agent_totals = {a: [] for a in SCORING_CRITERIA}

    for run in scored_runs:
        print(f"\nRun {run['id']} ({run['category']}): {run['overall_score']}/5")
        for agent, s in run["scores"].items():
            print(f"  {agent}: {s['score']}/5")
            agent_totals[agent].append(s["score"])

    print("\n" + "-"*60)
    print("AGENT AVERAGES ACROSS ALL RUNS")
    print("-"*60)
    for agent, scores in agent_totals.items():
        if scores:
            avg = round(sum(scores) / len(scores), 2)
            bar = "█" * int(avg) + "░" * (5 - int(avg))
            print(f"  {agent:<12} {avg}/5  {bar}")

    all_scores = [r["overall_score"] for r in scored_runs]
    print(f"\n  Pipeline avg: {round(sum(all_scores)/len(all_scores), 2)}/5")


if __name__ == "__main__":
    result_files = sorted(glob(os.path.join(RESULTS_DIR, "run_0*.json")))
    result_files = [f for f in result_files if "_scored" not in f]

    if not result_files:
        print("No result files found. Run eval/run_evals.py first.")
        sys.exit(1)

    print(f"Scoring {len(result_files)} runs...")
    scored_runs = [score_run(f) for f in result_files]
    print_summary(scored_runs)
