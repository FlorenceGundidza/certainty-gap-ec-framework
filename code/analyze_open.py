"""
Compute core metrics (Accuracy, False Confirmation Rate, Abstention) for
open-weight runs, using the SAME definitions as the original paper analysis
(analysis_v6_ec3.py: metrics()).

  Accuracy        = correct / total
  FCR             = false_confirmations / (# cases with gold != Delay)
  Abstention      = # Uncertain predictions / total
  (also reports false_denials)

Usage:
    python analyze_open.py <slug> [<slug> ...]
    python analyze_open.py --all          # every *__all.json in results/
"""

import json
import sys
from pathlib import Path

OUTDIR = Path(__file__).resolve().parent / "results"
METHOD_ORDER = ["ed", "strict_ec", "normalcy_ec"]
METHOD_NAME = {"ed": "Original (ED)", "strict_ec": "Strict EC", "normalcy_ec": "Normalcy EC"}


def normalize_label(label) -> str:
    if not label:
        return "PARSE_ERROR"
    l = str(label).strip().lower()
    if "uncertain" in l or "abstain" in l:
        return "Uncertain"
    if "no delay" in l or "no_delay" in l or "nodelay" in l or "no impact" in l:
        return "No Delay"
    if "delay" in l:
        return "Delay"
    return str(label)


def metrics(results):
    m = {"total": 0, "correct": 0, "committed": 0, "unc": 0, "fc": 0, "fd": 0, "nd": 0, "dt": 0,
         "parse_err": 0, "per_case": {}}
    for r in results:
        gold = r["gold_label"]
        if gold == "Delay":
            m["dt"] += 1
        else:
            m["nd"] += 1
    for r in results:
        m["total"] += 1
        gold = r["gold_label"]
        if "response" not in r or r.get("response", {}).get("parse_error"):
            m["parse_err"] += 1
        pred = normalize_label(r.get("response", {}).get("label") if "response" in r else None)
        m["per_case"][r["case_id"]] = {"gold": gold, "pred": pred}
        if pred == "Uncertain":
            m["unc"] += 1
            if gold == "Uncertain":
                m["correct"] += 1
            continue
        m["committed"] += 1
        if pred == gold:
            m["correct"] += 1
        if gold != "Delay" and pred == "Delay":
            m["fc"] += 1
        if gold == "Delay" and pred == "No Delay":
            m["fd"] += 1
    return m


def _is_correct(pred, gold):
    return pred == gold or (pred == "Uncertain" and gold == "Uncertain")


def committed_point(results):
    """Committed-basis operating point of a single-pass method (for SP overlay)."""
    total = len(results)
    committed = [r for r in results if normalize_label(r.get("response", {}).get("label")) != "Uncertain"]
    cov = len(committed) / total if total else 0.0
    nd_c = sum(1 for r in committed if r["gold_label"] != "Delay")
    fc = sum(1 for r in committed if r["gold_label"] != "Delay"
             and normalize_label(r["response"].get("label")) == "Delay")
    err = sum(1 for r in committed if not _is_correct(normalize_label(r["response"].get("label")), r["gold_label"]))
    return {
        "coverage": cov,
        "fcr_committed": (fc / nd_c) if nd_c else 0.0,
        "risk": (err / len(committed)) if committed else 0.0,
    }


def sp_curve(sp_results):
    """Risk-coverage and FCR-coverage curve by sweeping the confidence threshold."""
    rows = []
    for r in sp_results:
        resp = r.get("response", {})
        try:
            conf = float(resp.get("confidence"))
        except (TypeError, ValueError):
            continue
        pred = normalize_label(resp.get("label"))
        gold = r["gold_label"]
        rows.append({"conf": conf, "gold": gold,
                     "correct": _is_correct(pred, gold),
                     "fc": (gold != "Delay" and pred == "Delay")})
    total = len(rows)
    curve = []
    for tau in [0.0] + sorted({x["conf"] for x in rows}):
        committed = [x for x in rows if x["conf"] >= tau]
        nd_c = sum(1 for x in committed if x["gold"] != "Delay")
        curve.append({
            "tau": tau,
            "coverage": len(committed) / total if total else 0.0,
            "risk": sum(1 for x in committed if not x["correct"]) / len(committed) if committed else 0.0,
            "fcr_committed": sum(1 for x in committed if x["fc"]) / nd_c if nd_c else 0.0,
        })
    return curve, total


def sp_fcr_at_coverage(curve, target_cov):
    """SP frontier FCR at the coverage closest to target_cov (for EC comparison)."""
    if not curve:
        return None
    best = min(curve, key=lambda p: abs(p["coverage"] - target_cov))
    return best


def report(slug):
    path = OUTDIR / f"{slug}__all.json"
    if not path.exists():
        print(f"  (missing: {path.name})")
        return
    data = json.load(open(path))
    print(f"\n### {slug}")

    # ---- Core EC configurations (+ SC as a method row if present) ----
    print(f"| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |")
    print(f"|---|---|---|---|---|---|")
    rows = list(METHOD_ORDER)
    if "sc" in data:
        rows += ["sc"]            # SC-vote (majority, no abstention) as a method row
    if "lp" in data:
        rows += ["lp"]            # logprob-confidence label (argmax, no abstention)
    if "rag" in data:
        rows += ["rag"]           # retrieval-augmented ICL
    name = dict(METHOD_NAME, sc="Self-Consistency (vote)",
                lp="Logprob Uncertainty (argmax)", rag="Retrieval-Augmented ICL")
    for mk in rows:
        if mk not in data:
            continue
        m = metrics(data[mk])
        acc = f"{m['correct']}/{m['total']} ({m['correct']/m['total']*100:.1f}%)"
        fcr = f"{m['fc']}/{m['nd']} ({m['fc']/m['nd']*100:.1f}%)" if m['nd'] else "-"
        ab = f"{m['unc']}/{m['total']} ({m['unc']/m['total']*100:.1f}%)"
        print(f"| {name[mk]} | {acc} | {fcr} | {ab} | {m['fd']} | {m['parse_err']} |")

    # ---- SC-abstain (abstain when agreement below threshold) ----
    if "sc" in data:
        print("\n**Self-Consistency with abstention** (abstain if agreement < τ):")
        print("| τ_agree | Accuracy | FCR | Abstention |")
        print("|---|---|---|---|")
        for tau in (0.6, 0.8, 1.0):
            res2 = []
            for r in data["sc"]:
                rr = dict(r)
                if r.get("sc_agreement", 0) < tau:
                    rr["response"] = {"label": "Uncertain"}
                res2.append(rr)
            m = metrics(res2)
            print(f"| {tau:.1f} | {m['correct']/m['total']*100:.1f}% | "
                  f"{m['fc']}/{m['nd']} ({m['fc']/m['nd']*100:.1f}%) | {m['unc']/m['total']*100:.1f}% |")

    # ---- Selective Prediction risk-coverage curve + EC overlay (R4#8) ----
    if "sp" in data:
        curve, total = sp_curve(data["sp"])
        print("\n**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):")
        print("| τ_conf | Coverage | Risk(err) | FCR(committed) |")
        print("|---|---|---|---|")
        shown = curve[:: max(1, len(curve) // 8)]
        for p in shown:
            print(f"| {p['tau']:.0f} | {p['coverage']*100:.1f}% | {p['risk']*100:.1f}% | {p['fcr_committed']*100:.1f}% |")
        print("\n**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):")
        print("| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |")
        print("|---|---|---|---|---|")
        for mk in ("ed", "strict_ec", "normalcy_ec"):
            if mk not in data:
                continue
            pt = committed_point(data[mk])
            sp_pt = sp_fcr_at_coverage(curve, pt["coverage"])
            better = "yes" if (sp_pt and pt["fcr_committed"] < sp_pt["fcr_committed"] - 1e-9) else \
                     ("tie" if sp_pt and abs(pt["fcr_committed"] - sp_pt["fcr_committed"]) < 1e-9 else "no")
            sp_str = f"{sp_pt['fcr_committed']*100:.1f}% @ {sp_pt['coverage']*100:.1f}%" if sp_pt else "-"
            print(f"| {METHOD_NAME[mk]} | {pt['coverage']*100:.1f}% | {pt['fcr_committed']*100:.1f}% | {sp_str} | {better} |")

    # ---- LP: logprob-confidence risk-coverage curve + EC overlay ----
    if "lp" in data:
        curve, total = sp_curve(data["lp"])   # same machinery; uses response.confidence
        print("\n**Logprob Uncertainty (LP) — FCR/Risk vs Coverage curve** (logprob-confidence threshold sweep):")
        print("| τ_conf | Coverage | Risk(err) | FCR(committed) |")
        print("|---|---|---|---|")
        for p in curve[:: max(1, len(curve) // 8)]:
            print(f"| {p['tau']:.0f} | {p['coverage']*100:.1f}% | {p['risk']*100:.1f}% | {p['fcr_committed']*100:.1f}% |")
        print("\n**EC vs LP frontier:**")
        print("| Config | Coverage | FCR(committed) | LP FCR @ matched coverage | EC better? |")
        print("|---|---|---|---|---|")
        for mk in ("ed", "strict_ec", "normalcy_ec"):
            if mk not in data:
                continue
            pt = committed_point(data[mk])
            lp_pt = sp_fcr_at_coverage(curve, pt["coverage"])
            better = "yes" if (lp_pt and pt["fcr_committed"] < lp_pt["fcr_committed"] - 1e-9) else \
                     ("tie" if lp_pt and abs(pt["fcr_committed"] - lp_pt["fcr_committed"]) < 1e-9 else "no")
            lp_str = f"{lp_pt['fcr_committed']*100:.1f}% @ {lp_pt['coverage']*100:.1f}%" if lp_pt else "-"
            print(f"| {METHOD_NAME[mk]} | {pt['coverage']*100:.1f}% | {pt['fcr_committed']*100:.1f}% | {lp_str} | {better} |")

    # ---- Calibration analysis (CAL): ECE / Brier for confidence-bearing methods ----
    cal_targets = [(k, name.get(k, k)) for k in ("sp", "lp") if k in data]
    if cal_targets:
        print("\n**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):")
        print("| Confidence source | ECE | Brier | n |")
        print("|---|---|---|---|")
        for k, label in cal_targets:
            ece, brier, n = calibration(data[k])
            print(f"| {label} | {ece*100:.1f}% | {brier:.3f} | {n} |")


def calibration(results, bins=10):
    """Expected Calibration Error and Brier score over confidence-bearing predictions."""
    rows = []
    for r in results:
        resp = r.get("response", {})
        try:
            conf = float(resp.get("confidence")) / 100.0
        except (TypeError, ValueError):
            continue
        pred = normalize_label(resp.get("label"))
        correct = 1.0 if _is_correct(pred, r["gold_label"]) else 0.0
        rows.append((conf, correct))
    n = len(rows)
    if n == 0:
        return 0.0, 0.0, 0
    brier = sum((c - y) ** 2 for c, y in rows) / n
    ece = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        grp = [(c, y) for c, y in rows if (c > lo or (b == 0 and c == 0)) and c <= hi]
        if not grp:
            continue
        conf_avg = sum(c for c, _ in grp) / len(grp)
        acc_avg = sum(y for _, y in grp) / len(grp)
        ece += abs(acc_avg - conf_avg) * len(grp) / n
    return ece, brier, n


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args == ["--all"]:
        slugs = sorted({p.name[:-len('__all.json')] for p in OUTDIR.glob("*__all.json")})
    else:
        slugs = args
    for s in slugs:
        report(s)
