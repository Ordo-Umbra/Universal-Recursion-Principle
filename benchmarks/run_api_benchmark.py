"""
run_api_benchmark.py

Run the S Compass benchmark corpus through the REST API and produce a
structured Markdown report.

Usage::

    python -m benchmarks.run_api_benchmark          # write report to stdout
    python -m benchmarks.run_api_benchmark -o REPORT.md  # write to file

The script:

1. Boots the Flask app via ``create_app()``.
2. Creates one session per regime group + one for edge cases.
3. Submits every scenario through ``POST /v1/step``.
4. Collects scores, regimes, policy actions, and coherence graphs.
5. Retrieves session summaries and rolling-window stats via the GET endpoints.
6. Compares computed regimes against human-labelled expected regimes.
7. Emits a Markdown report with per-scenario detail, confusion matrix,
   accuracy metrics, and aggregate statistics.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from io import StringIO
from typing import Any, Dict, List, TextIO, Tuple

from s_compass.api import create_app

from .corpus import (
    ALL_SCENARIOS,
    COLLAPSE,
    CORPUS_STATS,
    CREATIVE_GROUNDED,
    EDGE_CASES,
    HALLUCINATION_RISK,
    RIGID,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REGIMES = ["creative-grounded", "hallucination-risk", "rigid", "collapse"]

SESSION_GROUPS: List[Tuple[str, str, List[Dict[str, Any]]]] = [
    ("bench_creative", "Creative-Grounded", CREATIVE_GROUNDED),
    ("bench_hallucination", "Hallucination-Risk", HALLUCINATION_RISK),
    ("bench_rigid", "Rigid", RIGID),
    ("bench_collapse", "Collapse", COLLAPSE),
    ("bench_edge", "Edge Cases", EDGE_CASES),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _post_json(client, url: str, body: dict) -> dict:
    """POST JSON via the Flask test client and return parsed response."""
    resp = client.post(url, data=json.dumps(body), content_type="application/json")
    return {"status": resp.status_code, "data": resp.get_json()}


def _get_json(client, url: str) -> dict:
    resp = client.get(url)
    return {"status": resp.status_code, "data": resp.get_json()}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_benchmark() -> Dict[str, Any]:
    """Execute the full benchmark and return structured results."""
    app = create_app()
    app.config["TESTING"] = True
    results: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "corpus_size": CORPUS_STATS["total"],
        "scenarios": [],
        "sessions": {},
        "policy_evaluate_checks": [],
    }

    with app.test_client() as client:
        # -- Run each session group -----------------------------------------
        for session_id, group_name, scenarios in SESSION_GROUPS:
            # Start session
            start_resp = _post_json(client, "/v1/session/start", {
                "session_id": session_id,
                "metadata": {"group": group_name, "benchmark": True},
            })
            assert start_resp["status"] == 201, f"Failed to start {session_id}"

            for scenario in scenarios:
                # Build step payload (strip benchmark-only keys)
                step_body = {
                    "session_id": session_id,
                    "prompt": scenario["prompt"],
                    "output": scenario["output"],
                    "retrieved_context": scenario.get("retrieved_context", []),
                    "model": scenario.get("model", {}),
                }

                step_resp = _post_json(client, "/v1/step", step_body)
                assert step_resp["status"] == 200, (
                    f"Step failed for {scenario['label']}: {step_resp}"
                )

                data = step_resp["data"]
                results["scenarios"].append({
                    "label": scenario["label"],
                    "description": scenario["description"],
                    "expected_regime": scenario["expected_regime"],
                    "computed_regime": data["regime"],
                    "match": data["regime"] == scenario["expected_regime"],
                    "scores": data["scores"],
                    "policy": data["policy"],
                    "prompt_preview": scenario["prompt"][:80],
                    "output_preview": scenario["output"]["text"][:120],
                })

            # -- Collect session summary and rolling-window stats -----------
            summary_resp = _get_json(client, f"/v1/session/{session_id}")
            window_resp = _get_json(client, f"/v1/session/{session_id}/window?window=20")
            results["sessions"][session_id] = {
                "group_name": group_name,
                "summary": summary_resp["data"],
                "window": window_resp["data"],
            }

        # -- List all sessions (exercises GET /v1/sessions) -----------------
        list_resp = _get_json(client, "/v1/sessions")
        results["all_sessions"] = list_resp["data"]["sessions"]

        # -- Standalone policy evaluate checks (exercises POST /v1/policy/evaluate)
        policy_test_vectors = [
            {"c": 0.7, "i": 0.6, "kappa": 0.8, "expected_regime": "creative-grounded"},
            {"c": 0.8, "i": 0.2, "kappa": 0.3, "expected_regime": "hallucination-risk"},
            {"c": 0.2, "i": 0.8, "kappa": 0.9, "expected_regime": "rigid"},
            {"c": 0.1, "i": 0.1, "kappa": 0.2, "expected_regime": "collapse"},
            {"c": 0.5, "i": 0.5, "kappa": 0.5, "expected_regime": "creative-grounded"},
        ]
        for vec in policy_test_vectors:
            pol_resp = _post_json(client, "/v1/policy/evaluate", {
                "scores": {"c": vec["c"], "i": vec["i"], "kappa": vec["kappa"]},
            })
            results["policy_evaluate_checks"].append({
                "input": {"c": vec["c"], "i": vec["i"], "kappa": vec["kappa"]},
                "expected_regime": vec["expected_regime"],
                "computed_regime": pol_resp["data"]["regime"],
                "match": pol_resp["data"]["regime"] == vec["expected_regime"],
                "policy_action": pol_resp["data"]["policy"]["action"],
                "s_score": pol_resp["data"]["scores"]["s"],
            })

    return results


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _confusion_matrix(scenarios: List[Dict]) -> Dict[str, Dict[str, int]]:
    """Build a confusion matrix: matrix[expected][computed] = count."""
    matrix: Dict[str, Dict[str, int]] = {r: {r2: 0 for r2 in REGIMES} for r in REGIMES}
    for s in scenarios:
        exp = s["expected_regime"]
        comp = s["computed_regime"]
        if exp in matrix and comp in matrix[exp]:
            matrix[exp][comp] += 1
    return matrix


def _per_regime_accuracy(scenarios: List[Dict]) -> Dict[str, Dict[str, Any]]:
    """Precision, recall, and F1 per regime."""
    tp: Dict[str, int] = defaultdict(int)
    fp: Dict[str, int] = defaultdict(int)
    fn: Dict[str, int] = defaultdict(int)
    for s in scenarios:
        exp, comp = s["expected_regime"], s["computed_regime"]
        if exp == comp:
            tp[exp] += 1
        else:
            fn[exp] += 1
            fp[comp] += 1

    stats = {}
    for r in REGIMES:
        p = tp[r] / (tp[r] + fp[r]) if (tp[r] + fp[r]) > 0 else 0.0
        rec = tp[r] / (tp[r] + fn[r]) if (tp[r] + fn[r]) > 0 else 0.0
        f1 = 2 * p * rec / (p + rec) if (p + rec) > 0 else 0.0
        stats[r] = {
            "true_positives": tp[r],
            "false_positives": fp[r],
            "false_negatives": fn[r],
            "precision": round(p, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
        }
    return stats


def generate_report(results: Dict[str, Any], out: TextIO = sys.stdout) -> None:
    """Write a Markdown report from benchmark results."""
    scenarios = results["scenarios"]
    total = len(scenarios)
    correct = sum(1 for s in scenarios if s["match"])
    accuracy = correct / total if total > 0 else 0.0

    w = out.write

    w("# S Compass API Benchmark Report\n\n")
    w(f"**Generated:** {results['timestamp']}\n\n")
    w(f"**Corpus size:** {results['corpus_size']} scenarios\n\n")
    w(f"**Overall regime accuracy:** {correct}/{total} "
      f"({accuracy:.1%})\n\n")

    # -- Per-regime accuracy ------------------------------------------------
    w("## Per-Regime Accuracy\n\n")
    regime_stats = _per_regime_accuracy(scenarios)
    w("| Regime | Precision | Recall | F1 | TP | FP | FN |\n")
    w("|--------|-----------|--------|----|----|----|----|\n")
    for r in REGIMES:
        s = regime_stats[r]
        w(f"| {r} | {s['precision']:.2f} | {s['recall']:.2f} | "
          f"{s['f1']:.2f} | {s['true_positives']} | "
          f"{s['false_positives']} | {s['false_negatives']} |\n")
    w("\n")

    # -- Confusion matrix ---------------------------------------------------
    w("## Confusion Matrix\n\n")
    w("_Rows = expected, Columns = computed_\n\n")
    header = "| | " + " | ".join(REGIMES) + " |\n"
    w(header)
    w("|" + "---|" * (len(REGIMES) + 1) + "\n")
    matrix = _confusion_matrix(scenarios)
    for exp in REGIMES:
        row = f"| **{exp}** |"
        for comp in REGIMES:
            val = matrix[exp][comp]
            marker = f" **{val}** " if exp == comp else f" {val} "
            row += marker + "|"
        w(row + "\n")
    w("\n")

    # -- Detailed scenario results ------------------------------------------
    w("## Scenario Details\n\n")
    for session_id, group_name, _ in SESSION_GROUPS:
        group_scenarios = [s for s in scenarios
                          if s["label"].startswith(session_id.replace("bench_", ""))]
        # Fallback: match by expected regime group
        if not group_scenarios:
            group_scenarios = [s for s in scenarios
                               if s["label"].startswith(group_name.lower().split("-")[0])
                               or s["label"].startswith(group_name.lower().replace("-", "_"))]
        # More robust: match from SESSION_GROUPS corpus
        pass  # we'll just iterate all scenarios by group

    # Group by label prefix
    current_group = ""
    for s in scenarios:
        group = s["label"].rsplit("-", 1)[0].rsplit("-", 1)[0]
        if group != current_group:
            current_group = group
            w(f"\n### {group.replace('-', ' ').title()}\n\n")

        match_icon = "✅" if s["match"] else "❌"
        w(f"#### {match_icon} `{s['label']}`\n\n")
        w(f"_{s['description']}_\n\n")
        w(f"- **Prompt:** {s['prompt_preview']}\n")
        w(f"- **Output preview:** {s['output_preview']}...\n")
        w(f"- **Expected regime:** `{s['expected_regime']}`\n")
        w(f"- **Computed regime:** `{s['computed_regime']}`\n")
        w(f"- **Scores:** C={s['scores']['c']:.4f}, "
          f"I={s['scores']['i']:.4f}, "
          f"κ={s['scores']['kappa']:.4f}, "
          f"S={s['scores']['s']:.4f}\n")
        w(f"- **Policy:** `{s['policy']['action']}` — {s['policy']['reason']}\n\n")

    # -- Session summaries --------------------------------------------------
    w("## Session Summaries\n\n")
    for session_id, info in results["sessions"].items():
        summary = info["summary"]
        w(f"### {info['group_name']} (`{session_id}`)\n\n")
        w(f"- **Steps:** {summary.get('step_count', 0)}\n")
        w(f"- **Regime counts:** {summary.get('regime_counts', {})}\n")
        avg = summary.get("avg_scores", {})
        if avg:
            w(f"- **Avg scores:** C={avg.get('c', 0):.4f}, "
              f"I={avg.get('i', 0):.4f}, "
              f"κ={avg.get('kappa', 0):.4f}, "
              f"S={avg.get('s', 0):.4f}\n")

        window = info.get("window", {})
        if window and window.get("stats"):
            w(f"- **Rolling window ({window.get('window', 'N/A')}):**\n")
            for field_name in ("c", "i", "kappa", "s"):
                st = window["stats"].get(field_name, {})
                if st:
                    w(f"  - {field_name}: "
                      f"mean={st.get('mean', 0):.4f}, "
                      f"std={st.get('std', 0):.4f}, "
                      f"range=[{st.get('min', 0):.4f}, {st.get('max', 0):.4f}]\n")
        w("\n")

    # -- Standalone policy evaluate -----------------------------------------
    w("## Standalone Policy Evaluation\n\n")
    w("These test the `POST /v1/policy/evaluate` endpoint with known score vectors.\n\n")
    w("| C | I | κ | S | Expected | Computed | Match | Action |\n")
    w("|---|---|---|---|----------|----------|-------|--------|\n")
    for p in results["policy_evaluate_checks"]:
        match_icon = "✅" if p["match"] else "❌"
        w(f"| {p['input']['c']} | {p['input']['i']} | {p['input']['kappa']} "
          f"| {p['s_score']} | {p['expected_regime']} | {p['computed_regime']} "
          f"| {match_icon} | {p['policy_action']} |\n")
    w("\n")

    # -- Sessions list ------------------------------------------------------
    w("## Active Sessions\n\n")
    w(f"Sessions returned by `GET /v1/sessions`: "
      f"{', '.join(results.get('all_sessions', []))}\n\n")

    # -- Key observations ---------------------------------------------------
    w("## Key Observations\n\n")

    mismatches = [s for s in scenarios if not s["match"]]
    if mismatches:
        w(f"**{len(mismatches)} regime mismatches** detected:\n\n")
        for m in mismatches:
            w(f"- `{m['label']}`: expected `{m['expected_regime']}`, "
              f"got `{m['computed_regime']}` "
              f"(C={m['scores']['c']:.4f}, I={m['scores']['i']:.4f}, "
              f"κ={m['scores']['kappa']:.4f})\n")
        w("\n")
    else:
        w("All scenarios matched their expected regime labels. ✅\n\n")

    # Score distributions by expected regime
    w("### Score Distributions by Expected Regime\n\n")
    w("| Regime | Avg C | Avg I | Avg κ | Avg S |\n")
    w("|--------|-------|-------|-------|-------|\n")
    for r in REGIMES:
        group = [s for s in scenarios if s["expected_regime"] == r]
        if group:
            avg_c = sum(s["scores"]["c"] for s in group) / len(group)
            avg_i = sum(s["scores"]["i"] for s in group) / len(group)
            avg_k = sum(s["scores"]["kappa"] for s in group) / len(group)
            avg_s = sum(s["scores"]["s"] for s in group) / len(group)
            w(f"| {r} | {avg_c:.4f} | {avg_i:.4f} | {avg_k:.4f} | {avg_s:.4f} |\n")
    w("\n")

    w("---\n\n")
    w("*Report generated by `benchmarks/run_api_benchmark.py` against the "
      "S Compass REST API.*\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="S Compass API benchmark")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--json", dest="json_output",
        help="Also write raw JSON results to this path",
    )
    args = parser.parse_args()

    results = run_benchmark()

    # Write Markdown report
    if args.output:
        with open(args.output, "w") as f:
            generate_report(results, f)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        generate_report(results, sys.stdout)

    # Optionally write raw JSON
    if args.json_output:
        with open(args.json_output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"JSON results written to {args.json_output}", file=sys.stderr)


if __name__ == "__main__":
    main()
