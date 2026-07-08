"""
R4#9 cost-sensitive evaluation + R4#11 computational-cost analysis.
Operates on existing results (results_cluster = open-weight, results_api = proprietary).
Outputs a markdown report. No new inference.
"""
import json, glob, os
from pathlib import Path
import analyze_open as A

OPEN = ["gemma3_27b", "qwen3_32b", "magistral_24b", "llama4_scout", "gpt_oss_120b", "deepseek_r1_70b"]
PROP = ["gpt_5_4_mini", "gpt_5_5", "claude_opus_4_8", "claude_sonnet_4_6", "gemini_3_5_flash", "gemini_3_1_pro"]
DIRS = {"results_cluster": OPEN, "results_api": PROP}
METHODS = ["ed", "strict_ec", "normalcy_ec", "sc", "rag"]

# default cost matrix (high-stakes: false confirmation is worst). correct = 0.
C = {"fc": 5.0, "fd": 3.0, "abstain": 1.0, "other": 2.0}


def outcomes(records):
    o = {"correct": 0, "fc": 0, "fd": 0, "abstain": 0, "other": 0, "n": 0}
    for r in records:
        g = r["gold_label"]; p = A.normalize_label(r.get("response", {}).get("label"))
        o["n"] += 1
        if p == "Uncertain":
            if g == "Uncertain":
                o["correct"] += 1
            else:
                o["abstain"] += 1
            continue
        if p == g:
            o["correct"] += 1
        elif g != "Delay" and p == "Delay":
            o["fc"] += 1
        elif g == "Delay" and p == "No Delay":
            o["fd"] += 1
        else:
            o["other"] += 1
    return o


def exp_cost(o, cfc):
    cm = dict(C); cm["fc"] = cfc
    tot = o["fc"]*cm["fc"] + o["fd"]*cm["fd"] + o["abstain"]*cm["abstain"] + o["other"]*cm["other"]
    return tot / o["n"]


def load(d, slug, suite):
    return json.load(open(f"{d}/{slug}__{suite}.json"))


print("# R4#9 Cost-sensitive evaluation + R4#11 Computational cost\n")
print(f"Default cost matrix (high-stakes): false confirmation={C['fc']}, false denial={C['fd']}, "
      f"abstention={C['abstain']}, other-commit-error={C['other']}, correct=0.\n")

# ---- R4#9 cost-sensitive: expected cost per method (default matrix) + FC-threshold where Strict wins ----
print("## R4#9 — expected cost per method (lower is better; default matrix)\n")
print("| model | ED | Strict EC | Normalcy | SC | RAG | best (default) | Strict-EC optimal when FC≥ |")
print("|---|---|---|---|---|---|---|---|")
for d, slugs in DIRS.items():
    for s in slugs:
        ocs = {m: outcomes(load(d, s, m)) for m in METHODS}
        costs = {m: exp_cost(ocs[m], C["fc"]) for m in METHODS}
        best = min(costs, key=costs.get)
        # smallest integer FC cost (sweep 1..12) at which strict_ec is the argmin
        thr = None
        for cfc in [1, 2, 3, 4, 5, 6, 8, 10, 12]:
            cc = {m: exp_cost(ocs[m], cfc) for m in METHODS}
            if min(cc, key=cc.get) == "strict_ec":
                thr = cfc; break
        row = " | ".join(f"{costs[m]:.2f}" for m in METHODS)
        print(f"| {s} | {row} | {best} | {thr if thr else '—'} |")

# ---- R4#11 computational cost: tokens per method + 4-stage overhead vs ED ----
print("\n## R4#11 — computational cost (avg output tokens/case; EC overhead vs ED single-pass)\n")
print("| model | ED out | Strict out | Normalcy out | SP out | EC/ED overhead | SC calls/case |")
print("|---|---|---|---|---|---|---|")
def avg_out(d, s, suite):
    recs = load(d, s, suite); v = [r.get("usage", {}).get("completion_tokens") for r in recs if r.get("usage")]
    v = [x for x in v if x]; return sum(v)/len(v) if v else float("nan")
for d, slugs in DIRS.items():
    for s in slugs:
        ed = avg_out(d, s, "ed"); st = avg_out(d, s, "strict_ec"); no = avg_out(d, s, "normalcy_ec"); sp = avg_out(d, s, "sp")
        ov = (st/ed) if ed and ed == ed else float("nan")
        print(f"| {s} | {ed:.0f} | {st:.0f} | {no:.0f} | {sp:.0f} | {ov:.2f}x | 5 (k) |")
print("\nNotes: EC configs emit a structured evidence+modality trace (more output tokens than ED); "
      "SC multiplies *calls* by k=5; SP/LP are single-pass and cheapest. Input tokens are dominated by the "
      "case excerpt and are comparable across configs.")
