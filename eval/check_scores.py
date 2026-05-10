"""
Runs the scorer and fails with exit code 1 if pipeline avg score drops below threshold.
Used by GitHub Actions to block merges on quality regressions.
"""

import os
import sys
import json
from glob import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.scorer import score_run, print_summary

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
PASS_THRESHOLD = 3.0  # pipeline avg must be >= this to pass CI


if __name__ == "__main__":
    result_files = sorted(glob(os.path.join(RESULTS_DIR, "run_0*.json")))
    result_files = [f for f in result_files if "_scored" not in f]

    if not result_files:
        print("No result files found. Run eval/run_evals.py first.")
        sys.exit(1)

    scored_runs = [score_run(f) for f in result_files]
    print_summary(scored_runs)

    pipeline_avg = round(
        sum(r["overall_score"] for r in scored_runs) / len(scored_runs), 2
    )

    print(f"\nThreshold: {PASS_THRESHOLD}/5")
    print(f"Pipeline avg: {pipeline_avg}/5")

    if pipeline_avg < PASS_THRESHOLD:
        print(f"\n❌ FAILED — pipeline avg {pipeline_avg} is below threshold {PASS_THRESHOLD}")
        sys.exit(1)
    else:
        print(f"\n✅ PASSED — pipeline avg {pipeline_avg} meets threshold {PASS_THRESHOLD}")
        sys.exit(0)
