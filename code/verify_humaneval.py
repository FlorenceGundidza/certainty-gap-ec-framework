"""
Standalone, API-FREE verification of the human-evaluation stats (R3.3/R4#4,5).
Recomputes overall + per-category Fleiss' kappa and the leave-one-evaluator-out
majority stability directly from the released responses — deterministic, no model calls.
Run: python verify_humaneval.py   (expects v2_results/responses_canonical.csv)
"""
import csv, os
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "v2_results", "responses_canonical.csv")


def fleiss(items):
    cats = sorted({l for it in items for l in it})
    N = len(items); n = min(len(it) for it in items)
    items = [it[:n] for it in items]
    P = []
    for it in items:
        c = Counter(it); P.append((sum(v * v for v in c.values()) - n) / (n * (n - 1)))
    Pbar = sum(P) / N
    pj = {k: sum(Counter(it).get(k, 0) for it in items) / (N * n) for k in cats}
    Pe = sum(v * v for v in pj.values())
    return (Pbar - Pe) / (1 - Pe) if (1 - Pe) else float("nan"), N, n


def main():
    rows = list(csv.DictReader(open(CSV)))
    by_case = defaultdict(list); cat = {}; pc = defaultdict(dict); parts = set()
    for r in rows:
        by_case[r["case_id"]].append(r["canonical_code"]); cat[r["case_id"]] = r["case_category"]
        pc[r["case_id"]][r["participant_id"]] = r["canonical_code"]; parts.add(r["participant_id"])
    P = len(parts)
    full = [v for v in by_case.values() if len(v) == P]
    k, N, n = fleiss(full)
    print("== Human-eval agreement (recomputed from responses_canonical.csv, no API) ==")
    print(f"participants={P}  cases(full)={N}  raters/case={n}")
    print(f"Overall Fleiss kappa : {k:.3f}")
    percat = defaultdict(list)
    for cid, labs in by_case.items():
        if len(labs) == P: percat[cat[cid]].append(labs)
    print("Per-category Fleiss kappa:")
    for c, items in sorted(percat.items()):
        if len(items) >= 2:
            kk, NN, _ = fleiss(items); print(f"  {c:18} {kk:+.3f}  (N={NN})")
    flips = tot = 0
    for cid, dd in pc.items():
        if len(dd) < P: continue
        full_maj = Counter(dd.values()).most_common(1)[0][0]
        for drop in dd:
            sub = [v for p, v in dd.items() if p != drop]
            if Counter(sub).most_common(1)[0][0] != full_maj: flips += 1
            tot += 1
    print(f"Leave-one-evaluator-out: majority flips {flips}/{tot} = {flips/tot*100:.1f}%  "
          f"(stability {(1-flips/tot)*100:.1f}%)")
    print("\nReported in HUMAN_EVAL_REANALYSIS.md: overall 0.28; control 0.44 / other 0.26 / "
          "revision_target 0.13; LOO stability 98.5%")


if __name__ == "__main__":
    main()
