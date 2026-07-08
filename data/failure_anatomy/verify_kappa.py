"""
Standalone, API-FREE verification of the failure-taxonomy agreement (R4#12).
Recomputes Fleiss' kappa, majority/unanimous concordance, and agreement with the
original single-model diagnosis directly from the saved raw labels — NO model calls,
fully deterministic. Run: python verify_kappa.py

Inputs (same directory):
  reannotation_3judges.json        raw per-case labels from the 3 independent judges
  results_v5_anatomy/all_diagnoses.json   original single-model (gpt-5.4-mini) diagnosis
"""
import json, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CATS = ["Temporal & Modality Confusion", "Scope & Granularity Mismatch", "Recovery Neglect",
        "Lexical Overheating", "Scope-Change Conflation", "Excessive Conservatism (Over-Abstention)"]
JUDGES = ["gpt-5.4-mini", "claude-sonnet-4-6", "gemini-3.5-flash"]


def norm(s):
    if not s:
        return None
    s = re.sub(r"^\s*\d+[\.\)]\s*", "", str(s)).strip().lower()
    for c in CATS:
        if s == c.lower() or s in c.lower() or c.lower().split(" (")[0] in s:
            return c
    return None


def fleiss_kappa(rows):
    N = len(rows); n = sum(rows[0].values())
    assert all(sum(r.values()) == n for r in rows), "ragged ratings: each item needs the same #raters"
    P_i = [(sum(v * v for v in r.values()) - n) / (n * (n - 1)) for r in rows]
    P_bar = sum(P_i) / N
    p_j = {c: sum(r.get(c, 0) for r in rows) / (N * n) for c in CATS}
    P_e = sum(v * v for v in p_j.values())
    return (P_bar - P_e) / (1 - P_e), P_bar, P_e


def main():
    data = json.load(open(os.path.join(HERE, "reannotation_3judges.json")))
    valid = [o for o in data if all(o["labels"].get(j) for j in JUDGES)]
    rows = [Counter(o["labels"][j] for j in JUDGES) for o in valid]
    kappa, P_bar, P_e = fleiss_kappa([dict(r) for r in rows])
    unanimous = sum(1 for o in valid if len(set(o["labels"][j] for j in JUDGES)) == 1)
    majority = sum(1 for o in valid if max(Counter(o["labels"][j] for j in JUDGES).values()) >= 2)

    orig_path = os.path.join(HERE, "results_v5_anatomy", "all_diagnoses.json")
    vs_orig = None
    if os.path.exists(orig_path):
        orig = {d["case_id"]: norm(d.get("diagnosis", {}).get("primary_failure_category"))
                for d in json.load(open(orig_path))}
        vs_orig = sum(1 for o in valid
                      if orig.get(o["case_id"]) == Counter(o["labels"][j] for j in JUDGES).most_common(1)[0][0])

    N = len(valid)
    print("== R4#12 failure-taxonomy agreement (recomputed from raw labels, no API) ==")
    print(f"cases with 3 valid labels : {N}/{len(data)}")
    print(f"Fleiss' kappa             : {kappa:.3f}   (P_bar={P_bar:.3f}, P_e={P_e:.3f})")
    print(f"unanimous (3/3)           : {unanimous}/{N} ({unanimous/N*100:.0f}%)")
    print(f"majority (>=2/3)          : {majority}/{N} ({majority/N*100:.0f}%)")
    if vs_orig is not None:
        print(f"judge-majority == original: {vs_orig}/{N} ({vs_orig/N*100:.0f}%)")
    print(f"\nReported in FAILURE_REANNOTATION.md: kappa=0.612, majority 96%, unanimous 61%, vs-orig 57%")


if __name__ == "__main__":
    main()
