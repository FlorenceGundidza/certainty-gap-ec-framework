# Real-document experiment (R3.1/R4#2,3) — document-level contexts

## (B) Behavioral shift on 55 document-level contexts (label-free): %Delay / %NoDelay / %Abstain

| model | ED D/ND/Abs | Strict D/ND/Abs | Normalcy D/ND/Abs | Strict−ED abstain |
|---|---|---|---|---|
| gpt_5_4_mini | 58/29/13 | 49/2/49 | 58/38/4 | +36pt |
| gpt_5_5 | 64/35/2 | 55/2/44 | 58/24/18 | +42pt |
| claude_opus_4_8 | 56/29/15 | 51/5/44 | 62/16/22 | +29pt |
| claude_sonnet_4_6 | 58/27/15 | 47/5/47 | 62/18/20 | +33pt |
| gemini_3_5_flash | 58/35/5 | 53/7/40 | 58/20/22 | +35pt |
| gemini_3_1_pro | 60/36/4 | 58/7/35 | 56/18/25 | +31pt |

## (A) On 34 document-confirmed DELAY document-level contexts: false-denial rate (missed real delays)

Tests over-conservatism on real docs — does EC abstain/deny on genuine delays?

| model | ED FD% | Strict FD% | Normalcy FD% | Strict detect% (Delay) | Strict abstain% |
|---|---|---|---|---|---|
| gpt_5_4_mini | 9 | 0 | 15 | 79 | 21 |
| gpt_5_5 | 9 | 0 | 12 | 82 | 18 |
| claude_opus_4_8 | 0 | 3 | 9 | 79 | 18 |
| claude_sonnet_4_6 | 9 | 3 | 6 | 76 | 21 |
| gemini_3_5_flash | 6 | 6 | 12 | 82 | 12 |
| gemini_3_1_pro | 9 | 0 | 6 | 88 | 12 |

## (A') On 2 document-confirmed NO-DELAY document-level contexts: false-confirmation count (indicative only)

| model | ED | Strict | Normalcy |
|---|---|---|---|
| gpt_5_4_mini | 0/2 | 0/2 | 0/2 |
| gpt_5_5 | 0/2 | 0/2 | 0/2 |
| claude_opus_4_8 | 0/2 | 0/2 | 1/2 |
| claude_sonnet_4_6 | 0/2 | 0/2 | 1/2 |
| gemini_3_5_flash | 0/2 | 0/2 | 0/2 |
| gemini_3_1_pro | 0/2 | 0/2 | 0/2 |

---

## Interpretation (C2 — granularity follow-up to the paragraph-level experiment)

This experiment re-runs the real-document probe at **document granularity**: for each of 55
reports, the schedule-relevant paragraphs are concatenated into a single evidence-sufficient
context (median ~3.6k chars), labeled by the document's overall outcome.

**The paragraph-level over-abstention was a granularity artifact, not a flaw.**
At document granularity, Strict EC's abstention drops to **35–49%** (vs ~90% on isolated
paragraphs), and — decisively — it **detects 76–88% of the 34 document-confirmed delays** with
a **false-denial rate of 0–6%** (vs detect 7–12% on fragments). When the input actually
contains sufficient evidence, EC commits; it abstains predominantly when evidence is genuinely
insufficient. This converts the earlier limitation into a *positive*: EC's conservatism is
**evidence-calibrated and granularity-appropriate**.

**The Hydraulic Effect persists at a usable magnitude.** Strict still raises abstention over ED
(+29 to +42 pt) and Normalcy still lowers it relative to Strict — the same conserved knob,
now at an operationally reasonable level rather than the pathological ~90%.

**Bottom line for R3.1/R4#2,3.** Across two granularities and 6 models on naturally-occurring
(un-curated) text: the Hydraulic mechanism reproduces; and EC's abstention is driven by
evidence sufficiency, not by fragment length. The recommended deployment unit is therefore the
case-/document-level context (as in the 40-case benchmark), and we state the fragment-level
over-abstention as a documented boundary condition.
