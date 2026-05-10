"""
Logs each pipeline run's metadata to a persistent JSON file.
Tracks prompt, scores, latency, token estimate, and timestamp over time.
"""

import os
import json
from datetime import datetime, UTC


LOG_FILE = os.path.join(os.path.dirname(__file__), "run_history.json")


def load_history() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def log_run(
    prompt: str,
    agent_outputs: dict,
    scores: dict,
    overall_score: float,
    latency_seconds: float,
    total_tokens: int = 0,
):
    history = load_history()

    record = {
        "id": len(history) + 1,
        "timestamp": datetime.now(UTC).isoformat(),
        "prompt": prompt[:200],
        "latency_seconds": latency_seconds,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(total_tokens * 0.00001, 4),
        "overall_score": overall_score,
        "agent_scores": {
            agent: s["score"] for agent, s in scores.items()
        },
        "completed_agents": list(agent_outputs.keys()),
    }

    history.append(record)

    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2)

    return record


def print_history():
    history = load_history()
    if not history:
        print("No runs logged yet.")
        return

    print(f"\n{'='*60}")
    print(f"RUN HISTORY ({len(history)} runs)")
    print(f"{'='*60}")

    for run in history[-10:]:
        ts = run["timestamp"][:16].replace("T", " ")
        scores = " | ".join(
            f"{a[:4]}: {s}" for a, s in run["agent_scores"].items()
        )
        print(
            f"#{run['id']:03d} {ts}  "
            f"overall: {run['overall_score']}/5  "
            f"latency: {run['latency_seconds']}s  "
            f"tokens: {run['total_tokens']}  "
            f"cost: ${run['estimated_cost_usd']}"
        )
        print(f"     {scores}")
        print(f"     prompt: {run['prompt'][:70]}...")

    scores_all = [r["overall_score"] for r in history]
    print(f"\n  Avg overall score: {round(sum(scores_all)/len(scores_all), 2)}/5")
    total_cost = sum(r["estimated_cost_usd"] for r in history)
    print(f"  Total estimated cost: ${round(total_cost, 4)}")


if __name__ == "__main__":
    print_history()
