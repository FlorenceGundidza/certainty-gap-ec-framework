# Real-document experiment (R3.1/R4#2,3) — natural un-curated paragraphs

## (B) Behavioral shift on 110 natural paragraphs (label-free): %Delay / %NoDelay / %Abstain

| model | ED D/ND/Abs | Strict D/ND/Abs | Normalcy D/ND/Abs | Strict−ED abstain |
|---|---|---|---|---|
| gpt_5_4_mini | 12/61/27 | 5/2/94 | 11/35/54 | +66pt |
| gpt_5_5 | 12/86/2 | 6/0/94 | 10/26/64 | +92pt |
| claude_opus_4_8 | 8/80/12 | 8/1/91 | 10/14/76 | +79pt |
| claude_sonnet_4_6 | 10/84/6 | 5/3/93 | 11/19/70 | +86pt |
| gemini_3_5_flash | 12/81/7 | 7/1/92 | 11/15/75 | +85pt |
| gemini_3_1_pro | 11/83/2 | 6/3/91 | 9/18/73 | +89pt |

## (A) On 68 document-confirmed DELAY paragraphs: false-denial rate (missed real delays)

Tests over-conservatism on real docs — does EC abstain/deny on genuine delays?

| model | ED FD% | Strict FD% | Normalcy FD% | Strict detect% (Delay) | Strict abstain% |
|---|---|---|---|---|---|
| gpt_5_4_mini | 53 | 3 | 26 | 7 | 90 |
| gpt_5_5 | 82 | 0 | 22 | 9 | 91 |
| claude_opus_4_8 | 76 | 0 | 10 | 12 | 88 |
| claude_sonnet_4_6 | 82 | 1 | 15 | 7 | 91 |
| gemini_3_5_flash | 79 | 1 | 15 | 7 | 91 |
| gemini_3_1_pro | 76 | 3 | 15 | 10 | 87 |

## (A') On 4 document-confirmed NO-DELAY paragraphs: false-confirmation count (n=4, indicative only)

| model | ED | Strict | Normalcy |
|---|---|---|---|
| gpt_5_4_mini | 1/4 | 0/4 | 1/4 |
| gpt_5_5 | 0/4 | 0/4 | 0/4 |
| claude_opus_4_8 | 0/4 | 1/4 | 1/4 |
| claude_sonnet_4_6 | 1/4 | 0/4 | 1/4 |
| gemini_3_5_flash | 0/4 | 0/4 | 0/4 |
| gemini_3_1_pro | 0/4 | 0/4 | 0/4 |

---

## Interpretation (honest)

**Primary finding (B) — the Hydraulic Effect reproduces on naturally-occurring text.**
Across all six models, on 110 un-curated schedule-relevant paragraphs sampled from 55 real
reports, Strict EC raises abstention far above ED (+66 to +92 pt) and Normalcy EC sits in
between. The *direction and ordering* of the commitment knob (Strict > Normalcy > ED in
abstention) is identical to the curated benchmark — so the mechanism is not an artifact of
hand-picked cases; it operates on natural document text.

**Scope limitation (honest) — granularity matters.**
The *magnitude* is extreme: Strict EC abstains on ~90% of isolated paragraphs (detect% on
even document-confirmed-delay paragraphs is only 7–12%). This is consistent with EC's design
— it abstains on evidentiary insufficiency — and most isolated paragraphs genuinely do not
contain self-contained evidence to license a project-level delay verdict (a paragraph may
mention "schedule" only in passing). Correspondingly, ED *over-commits*: it labels 76–82% of
these paragraphs "No Delay" (the (A) "false-denial" column) without sufficient evidence —
exactly the over-commitment EC is designed to suppress. The practical implication, which we
state as a limitation, is that **Strict EC is calibrated for evidence-sufficient inputs
(case- or document-level), and over-abstains at isolated-fragment granularity.** The 40-case
benchmark is itself drawn from these same reports at the appropriate (evidence-sufficient)
granularity, bridging the two settings.

**Label caveat.** The document-level outcome (the report's overall delayed/on-time status) is
a *weak proxy* for a paragraph-level gold label — a paragraph from a delayed project need not
itself describe the delay. The (A)/(A') tables are therefore indicative only; the label-free
behavioral comparison (B) is the sound primary lens. (Only 4 paragraphs carry a confirmed
No-Delay document label, so (A') is not statistically meaningful.)

**Takeaway for R3.1/R4#2,3.** The behavioral phenomenon generalizes to naturally-occurring
documents (addressing the "small/curated cases only" concern), while the experiment also
surfaces an honest scope boundary — EC's conservatism is granularity-dependent — which we add
to Limitations and flag for future work (apply EC at document level / with sufficient-context
retrieval).
