# Human-evaluation re-analysis — R3.3 / R4#4 / R4#5
> Recomputed from the retained responses (`v2_results/responses_canonical.csv`, 9 evaluators × 22 substantive cases). No new data collection.

## Headline numbers
- **Overall inter-evaluator agreement: Fleiss κ = 0.28** (9 raters, 22 cases) — "fair" range, consistent with the paper's reported ~0.35 (difference = case subset / attention-check handling).
- **Agreement is structured by case difficulty, not random noise:**

  | Case group | Fleiss κ | N | Interpretation |
  |---|---|---|---|
  | positive_control (clear) | **+0.44** | 4 | evaluators agree on unambiguous cases |
  | other | +0.26 | 10 | mixed |
  | revision_target (the ambiguous target cases) | **+0.13** | 5 | low agreement *by design* |
  | attention_check | +0.15 | 2 | — |

  Agreement is **highest on clear control cases and lowest on the deliberately-ambiguous target cases**. Low κ therefore reflects **genuine task ambiguity** — the property the benchmark is built to probe — rather than unreliable annotation. Human evaluators disagreeing on these cases *is* the Certainty-Gap phenomenon, not a measurement artifact.
- **The aggregate verdict is robust despite n=9 and low κ:** leave-one-evaluator-out flips the per-case **majority** label in only **3/198 (1.5%)** of (case × dropped-evaluator) combinations → **98.5% of majority labels are unchanged** when any single evaluator is removed. The panel's *collective* judgement is stable even though individual agreement is "fair".
- **Per-case uncertainty is already quantified:** Wilson 95% CIs are reported for every case (`v2_stats` in `results.json`); with n=9 these are wide (e.g., case-1 accuracy 0.67, CI [0.35, 0.88]), and we scope every human-study claim accordingly.

## How this answers the reviews
- **R4#5 (κ=0.35 only "fair"):** Expected and informative. We now report κ *by case difficulty*; the gradient (control 0.44 → ambiguous 0.13) shows the low overall value is driven by the ambiguous targets, supporting — not undermining — the premise that these cases are genuinely hard. Humans' own accuracy on them is low and variable (per-case rates range 0%–89%), i.e., the task is hard for people too.
- **R4#4 (only 9 evaluators / statistical power):** We (i) report Wilson CIs on every estimate and frame the study as a small **expert panel / exploratory** validation, not a powered population study; (ii) demonstrate the majority verdict's robustness (98.5% leave-one-out stability); (iii) flag a larger panel as future work.
- **R3.3 (validation rigor):** add the per-category κ table, the leave-one-out sensitivity, and explicit scoping language; retain the attention-check filtering already applied (`ac_report`, all 9 retained).

## Deferred (needs your decision)
- Recruiting **additional evaluators** to raise power / tighten CIs — requires running another panel. Not done here.

Script: numbers reproducible from `responses_canonical.csv` (Fleiss κ + leave-one-out in the re-analysis snippet).
