"""Analyze the real-document experiment (R3.1/R4#2,3). Run from openweight/."""
import json, os
from pathlib import Path
import run_open_models as R

OUT = Path(os.environ.get("REALDOC_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_realdoc")))
MODELS = ["gpt_5_4_mini", "gpt_5_5", "claude_opus_4_8", "claude_sonnet_4_6", "gemini_3_5_flash", "gemini_3_1_pro"]
CFG = ["ed", "strict_ec", "normalcy_ec"]


def norm(x):
    return R._norm(x.get("response", {}).get("label"))


def rates(rows):
    n = len(rows)
    d = sum(1 for r in rows if norm(r) == "Delay")
    nd = sum(1 for r in rows if norm(r) == "No Delay")
    un = sum(1 for r in rows if norm(r) == "Uncertain")
    pe = sum(1 for r in rows if norm(r) in ("PARSE_ERROR", "ERROR"))
    return n, d, nd, un, pe


import json as _j
_ref = _j.load(open(OUT / f"{MODELS[0]}__ed.json"))
N_ALL = len(_ref)
N_DEL = sum(1 for r in _ref if r.get("doc_outcome") == "Delay")
N_ND = sum(1 for r in _ref if r.get("doc_outcome") == "No Delay")
GRAN = "document-level contexts" if str(OUT).rstrip("/").endswith("_doc") else "natural paragraphs"
print(f"# Real-document experiment (R3.1/R4#2,3) — {GRAN}\n")
print(f"## (B) Behavioral shift on {N_ALL} {GRAN} (label-free): %Delay / %NoDelay / %Abstain\n")
print("| model | ED D/ND/Abs | Strict D/ND/Abs | Normalcy D/ND/Abs | Strict−ED abstain |")
print("|---|---|---|---|---|")
for s in MODELS:
    try:
        cells = {}
        for c in CFG:
            n, d, nd, un, pe = rates(json.load(open(OUT / f"{s}__{c}.json")))
            cells[c] = (d/n*100, nd/n*100, un/n*100, pe)
        e, st, no = cells["ed"], cells["strict_ec"], cells["normalcy_ec"]
        print(f"| {s} | {e[0]:.0f}/{e[1]:.0f}/{e[2]:.0f} | {st[0]:.0f}/{st[1]:.0f}/{st[2]:.0f} | "
              f"{no[0]:.0f}/{no[1]:.0f}/{no[2]:.0f} | {st[2]-e[2]:+.0f}pt |")
    except FileNotFoundError:
        print(f"| {s} | (missing) | | | |")

print(f"\n## (A) On {N_DEL} document-confirmed DELAY {GRAN}: false-denial rate (missed real delays)\n")
print("Tests over-conservatism on real docs — does EC abstain/deny on genuine delays?\n")
print("| model | ED FD% | Strict FD% | Normalcy FD% | Strict detect% (Delay) | Strict abstain% |")
print("|---|---|---|---|---|---|")
for s in MODELS:
    try:
        row = []
        det = ab = None
        for c in CFG:
            rows = [r for r in json.load(open(OUT / f"{s}__{c}.json")) if r.get("doc_outcome") == "Delay"]
            n = len(rows)
            fd = sum(1 for r in rows if norm(r) == "No Delay") / n * 100
            row.append(fd)
            if c == "strict_ec":
                det = sum(1 for r in rows if norm(r) == "Delay") / n * 100
                ab = sum(1 for r in rows if norm(r) == "Uncertain") / n * 100
        print(f"| {s} | {row[0]:.0f} | {row[1]:.0f} | {row[2]:.0f} | {det:.0f} | {ab:.0f} |")
    except FileNotFoundError:
        print(f"| {s} | (missing) | | | | |")

# tiny FCR check on the 4 on_time paragraphs
print(f"\n## (A') On {N_ND} document-confirmed NO-DELAY {GRAN}: false-confirmation count (indicative only)\n")
print("| model | ED | Strict | Normalcy |")
print("|---|---|---|---|")
for s in MODELS:
    try:
        cells = []
        for c in CFG:
            rows = [r for r in json.load(open(OUT / f"{s}__{c}.json")) if r.get("doc_outcome") == "No Delay"]
            cells.append(sum(1 for r in rows if norm(r) == "Delay"))
        print(f"| {s} | {cells[0]}/{N_ND} | {cells[1]}/{N_ND} | {cells[2]}/{N_ND} |")
    except FileNotFoundError:
        print(f"| {s} | (missing) | | |")
