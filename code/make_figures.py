"""Generate the 3 paper figures from raw results. Output PNG+PDF to paper1_IEEEAccess/figures/."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import analyze_open as A
import analyze_costsens as CS

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(os.path.dirname(HERE), "paper1_IEEEAccess", "figures"); os.makedirs(FIG, exist_ok=True)
OPEN = [("gemma3_27b", "Gemma-3-27B"), ("qwen3_32b", "Qwen3-32B"), ("magistral_24b", "Magistral-24B"),
        ("llama4_scout", "Llama-4-Scout"), ("gpt_oss_120b", "gpt-oss-120B"), ("deepseek_r1_70b", "DeepSeek-R1-70B")]
PROP = [("gpt_5_4_mini", "gpt-5.4-mini"), ("gpt_5_5", "gpt-5.5"), ("claude_opus_4_8", "Claude Opus 4.8"),
        ("claude_sonnet_4_6", "Claude Sonnet 4.6"), ("gemini_3_5_flash", "Gemini-3.5-flash"), ("gemini_3_1_pro", "Gemini-3.1-pro")]
ALL = [("results_cluster", s, l) for s, l in OPEN] + [("results_api", s, l) for s, l in PROP]

def m(base, slug, cfg):
    d = json.load(open(os.path.join(HERE, base, f"{slug}__{cfg}.json")))
    mm = A.metrics(d)
    return (mm["fc"] / mm["nd"] * 100 if mm["nd"] else 0, mm["unc"] / 40 * 100)

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), bbox_inches="tight", dpi=200)
    print("wrote", name)

# ---- Fig 1: cross-model FCR, ED vs Strict EC ----
labels = [l for _, _, l in ALL]
ed_fcr = [m(b, s, "ed")[0] for b, s, _ in ALL]
st_fcr = [m(b, s, "strict_ec")[0] for b, s, _ in ALL]
fig, ax = plt.subplots(figsize=(11, 4.2))
x = range(len(labels)); w = 0.4
ax.bar([i - w/2 for i in x], ed_fcr, w, label="ED (baseline)", color="#c0504d")
ax.bar([i + w/2 for i in x], st_fcr, w, label="Strict EC", color="#4f81bd")
ax.axhline(3.4, ls="--", c="gray", lw=1); ax.text(len(labels)-0.5, 3.7, "3.4% (1/29)", fontsize=8, color="gray")
ax.axvline(5.5, ls=":", c="k", lw=0.8); ax.text(2.5, max(ed_fcr)*0.97, "open-weight", ha="center", fontsize=9)
ax.text(8.5, max(ed_fcr)*0.97, "proprietary API", ha="center", fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
ax.set_ylabel("False-Confirmation Rate (%)"); ax.set_title("Strict EC drives FCR to ≤3.4% across 12 models / 5 vendors")
ax.legend(); save(fig, "fig1_crossmodel_fcr"); plt.close(fig)

# ---- Fig 2: Hydraulic Effect scatter (abstention vs FCR; ED->Strict, ED->Normalcy) ----
fig, ax = plt.subplots(figsize=(7.5, 5.5))
xs_all, ys_all = [], []
for b, s, l in ALL:
    ef, ea = m(b, s, "ed"); sf, sa = m(b, s, "strict_ec"); nf, na = m(b, s, "normalcy_ec")
    ax.annotate("", xy=(sa, sf), xytext=(ea, ef), arrowprops=dict(arrowstyle="->", color="#4f81bd", alpha=0.55, lw=1.2))
    ax.annotate("", xy=(na, nf), xytext=(ea, ef), arrowprops=dict(arrowstyle="->", color="#e08a1e", alpha=0.55, lw=1.2))
    ax.plot(ea, ef, "o", color="k", ms=5, zorder=5)
    ax.plot(sa, sf, "s", color="#4f81bd", ms=5, zorder=5)
    ax.plot(na, nf, "^", color="#e08a1e", ms=5, zorder=5)
    xs_all += [ea, sa, na]; ys_all += [ef, sf, nf]
ax.plot([], [], "ks", color="k", marker="o", ms=5, label="ED (baseline)")
ax.plot([], [], "s", color="#4f81bd", ms=5, label="Strict EC (↑abstain, ↓FCR)")
ax.plot([], [], "^", color="#e08a1e", ms=5, label="Normalcy EC (↓abstain)")
ax.set_xlim(-2, max(xs_all) + 4); ax.set_ylim(-1, max(ys_all) + 2)
ax.set_xlabel("Abstention (%)"); ax.set_ylabel("False-Confirmation Rate (%)")
ax.set_title("The Hydraulic Effect: conserved commitment–abstention trade-off (12 models)")
ax.legend(fontsize=8, loc="upper right"); ax.grid(alpha=0.3); save(fig, "fig2_hydraulic_effect"); plt.close(fig)

# ---- Fig 3: cost-sensitivity (expected cost vs false-confirmation cost), gpt-5.5 ----
base, slug = "results_api", "gpt_5_5"
ocs = {c: CS.outcomes(json.load(open(os.path.join(HERE, base, f"{slug}__{c}.json")))) for c in ["ed", "strict_ec", "normalcy_ec", "sc", "rag"]}
xs = [i * 0.5 for i in range(1, 25)]  # FC cost 0.5..12
fig, ax = plt.subplots(figsize=(7, 4.5))
styles = {"ed": ("ED", "#c0504d", "-"), "strict_ec": ("Strict EC", "#4f81bd", "-"),
          "normalcy_ec": ("Normalcy EC", "#e08a1e", "--"), "sc": ("Self-Consistency", "#7f7f7f", ":"), "rag": ("RAG (supervised)", "#2ca02c", "-.")}
for c, (lab, col, ls) in styles.items():
    ax.plot(xs, [CS.exp_cost(ocs[c], fc) for fc in xs], ls, color=col, label=lab, lw=1.8)
ax.set_xlabel("Cost of a false confirmation (abstention=1, false denial=3)")
ax.set_ylabel("Expected decision cost (lower better)")
ax.set_title("Cost-sensitive operating point (gpt-5.5): Strict EC wins as FC cost rises")
ax.legend(fontsize=8); ax.grid(alpha=0.3); save(fig, "fig3_cost_sensitivity"); plt.close(fig)

# ---- Fig 4: real-document granularity — Strict EC abstention & delay-detection, paragraph vs document ----
def realdoc_stat(outdir, slug):
    rows = json.load(open(os.path.join(HERE, outdir, f"{slug}__strict_ec.json")))
    n = len(rows)
    ab = sum(1 for r in rows if A.normalize_label(r.get("response", {}).get("label")) == "Uncertain") / n * 100
    dels = [r for r in rows if r.get("doc_outcome") == "Delay"]
    det = sum(1 for r in dels if A.normalize_label(r.get("response", {}).get("label")) == "Delay") / len(dels) * 100 if dels else 0
    return ab, det
RD = [("gpt_5_4_mini", "gpt-5.4-mini"), ("gpt_5_5", "gpt-5.5"), ("claude_opus_4_8", "Opus 4.8"),
      ("claude_sonnet_4_6", "Sonnet 4.6"), ("gemini_3_5_flash", "G-3.5-flash"), ("gemini_3_1_pro", "G-3.1-pro")]
if all(os.path.exists(os.path.join(HERE, "results_realdoc_doc", f"{s}__strict_ec.json")) for s, _ in RD):
    par = [realdoc_stat("results_realdoc", s) for s, _ in RD]
    doc = [realdoc_stat("results_realdoc_doc", s) for s, _ in RD]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
    xx = range(len(RD)); w = 0.38
    a1.bar([i - w/2 for i in xx], [p[0] for p in par], w, label="isolated paragraph", color="#c0504d")
    a1.bar([i + w/2 for i in xx], [d[0] for d in doc], w, label="document-level", color="#4f81bd")
    a1.set_ylabel("Strict EC abstention (%)"); a1.set_title("(a) Abstention is granularity-driven")
    a1.set_xticks(list(xx)); a1.set_xticklabels([l for _, l in RD], rotation=35, ha="right", fontsize=8); a1.legend(fontsize=8)
    a2.bar([i - w/2 for i in xx], [p[1] for p in par], w, label="isolated paragraph", color="#c0504d")
    a2.bar([i + w/2 for i in xx], [d[1] for d in doc], w, label="document-level", color="#4f81bd")
    a2.set_ylabel("Detection of real delays (%)"); a2.set_title("(b) EC detects delays when evidence suffices")
    a2.set_xticks(list(xx)); a2.set_xticklabels([l for _, l in RD], rotation=35, ha="right", fontsize=8); a2.legend(fontsize=8)
    fig.suptitle("Real documents: Strict EC's conservatism is evidence-calibrated, not reckless", fontsize=12)
    save(fig, "fig4_realdoc_granularity"); plt.close(fig)
print("figures dir:", FIG)
