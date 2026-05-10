"""
Run all test prompts through the graph and save results to eval/results/.
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from graph import graph
from eval.test_prompts import TEST_PROMPTS

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def extract_agent_outputs(messages):
    outputs = {}
    for msg in messages:
        name = getattr(msg, "name", None)
        if name in ("Researcher", "Analyst", "Compliance", "Reporter"):
            outputs[name] = getattr(msg, "content", "")
    return outputs


def run_eval(prompt_entry):
    print(f"\nRunning prompt {prompt_entry['id']}: {prompt_entry['prompt'][:60]}...")
    start = time.time()

    result = graph.invoke(
        {
            "messages": [HumanMessage(content=prompt_entry["prompt"])],
            "next": "",
            "completed": [],
        },
        config={"recursion_limit": 20},
    )

    latency = round(time.time() - start, 2)
    agent_outputs = extract_agent_outputs(result["messages"])

    record = {
        "id": prompt_entry["id"],
        "category": prompt_entry["category"],
        "prompt": prompt_entry["prompt"],
        "timestamp": datetime.utcnow().isoformat(),
        "latency_seconds": latency,
        "completed_agents": result.get("completed", []),
        "agent_outputs": agent_outputs,
    }

    out_path = os.path.join(RESULTS_DIR, f"run_{prompt_entry['id']}.json")
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)

    print(f"  Done in {latency}s → saved to {out_path}")
    return record


if __name__ == "__main__":
    print(f"Running {len(TEST_PROMPTS)} eval prompts...")
    for prompt_entry in TEST_PROMPTS:
        run_eval(prompt_entry)
    print("\nAll evals complete. Results saved to eval/results/")
