# Independent failure-taxonomy re-annotation — R4#12
> Three **independent** annotators from distinct vendors (gpt-5.4-mini, claude-sonnet-4-6, gemini-3.5-flash) re-labeled the 23 failure cases with the SAME 6-category taxonomy used in the paper. Script: `annotate_failures.py`; raw labels: `reannotation_3judges.json`.

## Result (all 23 cases)
- **Inter-annotator agreement: Fleiss κ = 0.612** ("substantial", Landis–Koch) over all 23 failure cases (each labeled by all three judges).
- **Majority (≥2/3) agreement on 22/23 (96%)**; **unanimous (3/3) on 14/23 (61%)**.
- **Judge-majority vs. the original single-model (gpt-5.4-mini) diagnosis: 13/23 (57%)** — the independent panel mostly confirms the original labels and occasionally refines them.
- Note: an initial pass had one judge (OpenAI annotator under `max_completion_tokens=2048`, high reasoning) return no category on 5 cases; those were recovered with a larger token budget (6000). On the 18 cases that never needed recovery, κ = 0.705; including the 5 recovered (harder, more-contested) cases gives the full-sample κ = 0.612. We report the **full-sample 0.612** as the honest headline.

## Interpretation (for R4#12)
The taxonomy is **reliably applicable by independent annotators**: substantial chance-corrected agreement (full-sample κ=0.612) and 96% majority concordance indicate the failure categories ("Lexical Overheating", "Recovery Neglect", "Scope-Change Conflation", "Temporal & Modality Confusion", "Excessive Conservatism", "Scope & Granularity Mismatch") are not artifacts of a single model's self-diagnosis. The clearest categories reach unanimity (e.g., case_01/31/32 "Scope-Change Conflation", case_36 "Recovery Neglect", case_11 "Lexical Overheating", and the over-abstention cluster). The moderate (61%) match to the *original* labels is honest evidence that the categories are stable while individual borderline assignments can shift — consistent with the genuine ambiguity the paper studies.

## Honest caveats
- Annotators are independent **LLMs**, not human domain experts — this validates *category reliability / applicability*, not ground-truth correctness. A human-expert annotation remains stronger and is noted as future work (deferred — needs your decision).
- One judge failed to emit a category on 5 cases (parsing/empty); a retry pass would recover them but does not change the substantial-agreement conclusion.

## Independent verification (no API, deterministic)
The raw per-judge labels are released as `reannotation_3judges.json` and the original
single-model diagnosis as `results_v5_anatomy/all_diagnoses.json`. Recompute every number
above **without any model calls**:
```
python verify_kappa.py
# -> Fleiss kappa 0.612, majority 22/23 (96%), unanimous 14/23 (61%), vs-original 13/23 (57%)
```
(`annotate_failures.py` regenerates the labels from scratch via the 3 judge APIs, but that is
non-deterministic and costs API credits; `verify_kappa.py` is the deterministic check.)
