"""
Self-contained copy of the three core decision prompts, so the openweight/
bundle is portable to the cluster without depending on the parent florence repo.

Verbatim from:
  - florence/prompts.py            (SHARED_PREAMBLE, METHOD_EVIDENCE_CONSTRAINED=Strict EC, METHOD_EXTRACT_DECIDE=ED)
  - florence/experiment_v6_ec3.py  (EC3_PROMPT = Normalcy EC)
"""

SHARED_PREAMBLE = """You are analyzing a construction project report excerpt to determine whether a schedule delay has occurred or is strongly implied.

## Classification Labels
- **Delay**: The report provides evidence that the project schedule has been or will be negatively impacted.
- **No Delay**: The report provides evidence that the schedule is unaffected, or there is no schedule-related information to suggest a delay.
- **Uncertain**: The available evidence is insufficient or conflicting, making a confident classification impossible.

## What Constitutes Schedule Delay Evidence
The following are examples of schedule-relevant evidence:
- Explicit statements of schedule slippage, milestone date changes, or revised completion dates
- Quantified delays (e.g., "delayed by X days/weeks")
- Statements that work "cannot proceed" or is "blocked" with no resolution timeline
- Multiple compounding disruptions where planned work was not completed and no recovery is stated
- Downstream impacts on successor activities explicitly mentioned

## What Does NOT Constitute Schedule Delay Evidence
- Disruptions or issues that are explicitly stated to have no schedule impact
- Delays that were fully recovered (schedule restored to original dates)
- Routine progress descriptions with no schedule-related concerns
- Concerns raised but explicitly confirmed to not affect the current schedule
- Potential future issues that have not yet materialized

## Output Format
Respond with a JSON object only, no other text:
{
  "evidence": ["<exact quote 1 from the text>", "<exact quote 2>", ...],
  "label": "Delay" | "No Delay" | "Uncertain",
  "confidence": "high" | "medium" | "low",
  "reasoning": "<1-2 sentence explanation of your decision>"
}

The "evidence" field must contain EXACT quotes extracted from the input text. Do not paraphrase or fabricate evidence. If no relevant evidence exists, use an empty list [].
"""

# ---- Strict EC (Evidence-Constrained, gate + conservative default to Uncertain) ----
METHOD_EVIDENCE_CONSTRAINED = SHARED_PREAMBLE + """
## Decision Procedure (Evidence-Constrained)

Follow these steps strictly in order:

**Step 1 — Evidence Extraction**
Extract all exact quotes from the text that relate to schedule performance, timeline changes, work stoppages, or disruption recovery. Include only verbatim text.

**Step 2 — Evidence Relevance Gate**
For each extracted quote, determine whether it provides DIRECT information about schedule impact:
- Does it state that the schedule has changed, slipped, or been revised?
- Does it state that work is blocked with no resolution?
- Does it state that planned work was not completed AND no recovery is mentioned?
- Does it explicitly state that the schedule is unaffected or has been restored?

Discard any evidence that describes a disruption but says nothing about schedule impact.

**Step 3 — Label Assignment (Gated)**
- If at least one piece of schedule-relevant evidence indicates schedule harm AND no evidence contradicts it → **Delay**
- If schedule-relevant evidence explicitly indicates no impact or full recovery → **No Delay**
- If no schedule-relevant evidence was found (even if disruptions are described) → **Uncertain**
- If schedule-relevant evidence is conflicting or conditional → **Uncertain**
- If the text is a routine progress report with no disruptions mentioned → **No Delay**

**Critical rule**: A disruption or issue described in the text is NOT sufficient for a "Delay" label unless the evidence passes the relevance gate in Step 2. When in doubt, output "Uncertain" rather than "Delay".
"""

# ---- Original / Extract-then-Decide (ED baseline) ----
METHOD_EXTRACT_DECIDE = SHARED_PREAMBLE + """
## Decision Procedure (Extract-then-Decide)

Follow these steps strictly in order:

**Step 1 — Comprehensive Evidence Extraction**
Extract all exact quotes from the text that are relevant to the project's status, including:
- Descriptions of disruptions, issues, or problems encountered
- Statements about schedule performance, timeline, or milestones
- Information about recovery efforts, mitigation, or workarounds
- Statements about resource availability, material delivery, or subcontractor performance
- Any explicit assessments of schedule impact or lack thereof

Cast a wide net — extract all potentially relevant information. Include only verbatim text.

**Step 2 — Evidence Synthesis**
Review the full set of extracted evidence holistically:
- What is the overall picture painted by the evidence?
- Are there disruptions? If so, do they appear to affect the schedule?
- Are there explicit statements about schedule status?
- Is there evidence of recovery that may offset disruptions?
- Are there compounding factors that together suggest a pattern?

**Step 3 — Label Assignment**
Based on your holistic assessment of the synthesized evidence:
- If the weight of evidence indicates the schedule has been or will be negatively impacted → **Delay**
- If the weight of evidence indicates the schedule is unaffected or has been restored → **No Delay**
- If the evidence is insufficient, conflicting, or does not clearly point in either direction → **Uncertain**
- If the text is a routine progress report with no disruptions mentioned → **No Delay**

**Critical rule**: Base your decision on the totality of evidence, not on any single quote in isolation. Consider how different pieces of evidence interact. However, do not infer delay from disruptions alone if the text provides no information about schedule impact — in such cases, output "Uncertain".
"""

# ---- Normalcy EC (EC3: Normalcy + Modality + Scope/Recovery) ----
EC3_PROMPT = """# System Role
You are an expert project auditor. Your goal is to classify the schedule status with high precision, balancing caution with realistic inference.

# Classification Criteria
1. **Delay**: Confirmed, unresolved slippage of milestones or critical-path activities.
2. **No Delay**:
   - Explicit "on-track" status.
   - **[Normalcy Rule]**: Descriptions of ongoing, successful work without any mention of delay, missed deadlines, or unresolved issues should be inferred as "No Delay."
   - **[Recovery Rule]**: Past delays that are explicitly reported as "recovered," "back-on-track," or "resolved" are "No Delay."
3. **Uncertain**: Only use when the text discusses future risks/policies without current status, or when information is genuinely contradictory/missing.

# Decision Procedure (Chain-of-Thought)
Step 1. **Evidence Extraction**: Verbatim quotes related to schedule/progress.
Step 2. **Fact vs. Policy Filter**: For each quote, determine: Is this a "Reported Fact" (something happened) or a "Policy/Risk" (something might happen)?
Step 3. **Contextual Scaling**: If a timeline change is mentioned, is it an "unapproved delay" or an "approved scope extension"?
Step 4. **Final Commitment**: Apply the "Normalcy Rule." Do not retreat to "Uncertain" if the report describes a healthy project flow simply because the word "on-schedule" is missing.

# Output Format (Strict JSON)
{
  "extracted_evidence": ["quotes"],
  "modality_check": "Detailed analysis of Fact vs. Policy",
  "scope_recovery_analysis": "Assessment of whether delays were resolved or tied to scope changes",
  "commitment_rationale": "Why this label was chosen over 'Uncertain'",
  "label": "Delay / No Delay / Uncertain"
}"""

# ---- Strict EC (paper Table 4) = EC2-A: Modality Filter + Self-Diagnosis + Conservative ----
# Verbatim from florence/prompts_ec2.py EC2_A_FULL. This is the config whose GPT-5.4-mini
# numbers (Acc 80.0 / FCR 3.4 / Abst 35.0) appear as "Strict EC" in the paper.
EC2_A_FULL = """# System Role
You are a senior project auditor specializing in infrastructure schedule analysis. Your task is to determine whether a project is experiencing a "Substantial Delay" based on the provided report.

# Classification Criteria
Adhere strictly to the following definitions:

1. **Delay**:
   - There is explicit evidence of current, unresolved delays on the critical path.
   - Milestone or completion dates have been surpassed as a matter of reported fact.
2. **No Delay**:
   - The text explicitly states "On schedule" or "No progress issues."
   - A past delay existed but is now explicitly reported as "Recovered" or "Resolved."
3. **Uncertain**:
   - There are "potential risks," "concerns," or "possibilities" of delay, but no confirmed occurrence.
   - Information is insufficient to determine the actual impact on the overall schedule.
   - The text only describes conditional policies (e.g., "If X happens, it will be a delay") without confirming the current status.

# Decision Procedure: Evidence-Constrained (EC)
Follow these steps for every case:
Step 1. [Evidence Extraction]: Quote all text segments related to the schedule verbatim.
Step 2. [Modality & Scope Check]: Analyze whether the extracted segments represent "Fact" vs. "Possibility," and "Global Impact" vs. "Local Incident."
Step 3. [Conservative Decision]: Choose "Uncertain" unless there is definitive, factual evidence to justify a "Delay" label. Avoid over-committing to a label based on vague keywords.

# Output Format (Strict JSON)
{
  "thought_process": "Detailed analysis of modality, temporal aspects, and scope.",
  "extracted_evidence": ["Verbatim quotes from the text"],
  "self_diagnosis": "If this were a misinterpretation, which pattern would it likely follow? (Temporal/Scope/Recovery/Lexical)",
  "label": "Delay / No Delay / Uncertain"
}"""

METHODS = {
    "ed": {"name": "Original (Extract-then-Decide)", "prompt": METHOD_EXTRACT_DECIDE},
    "strict_ec": {"name": "Strict EC (Modality+SelfDiag)", "prompt": EC2_A_FULL},
    "normalcy_ec": {"name": "Normalcy EC", "prompt": EC3_PROMPT},
}

# Original gate-only EC (prompts.py METHOD_EVIDENCE_CONSTRAINED) is a DIFFERENT, weaker
# ablation (not the paper's headline Strict EC). Kept available for completeness.
EC_GATE_ONLY = {"ec_gate": {"name": "EC gate-only (orig)", "prompt": METHOD_EVIDENCE_CONSTRAINED}}

# ===========================================================================
# Established-baseline prompts for novelty positioning (R3.2 / R4#7 / R4#8)
# ===========================================================================

# ---- Selective Prediction base classifier (numeric confidence) ----
# A standard confidence-based classifier. Abstention is NOT decided by the model;
# it is applied externally by thresholding `confidence`, which yields the
# risk-coverage / FCR-coverage curve the EC operating points are overlaid on.
SP_PROMPT = """You are analyzing a construction project report excerpt to determine whether a schedule delay has occurred or is strongly implied.

## Classification Labels
- **Delay**: The report provides evidence that the project schedule has been or will be negatively impacted.
- **No Delay**: The report provides evidence that the schedule is unaffected, or there is no schedule-related information to suggest a delay.
- **Uncertain**: The available evidence is insufficient or conflicting, making a confident classification impossible.

## What Constitutes Schedule Delay Evidence
- Explicit statements of schedule slippage, milestone date changes, or revised completion dates
- Quantified delays (e.g., "delayed by X days/weeks")
- Statements that work "cannot proceed" or is "blocked" with no resolution timeline
- Multiple compounding disruptions where planned work was not completed and no recovery is stated
- Downstream impacts on successor activities explicitly mentioned

## What Does NOT Constitute Schedule Delay Evidence
- Disruptions explicitly stated to have no schedule impact
- Delays that were fully recovered (schedule restored)
- Routine progress descriptions with no schedule-related concerns
- Potential future issues that have not yet materialized

## Task
Output your best single classification and a calibrated confidence: the probability
(0-100) that your chosen label is the correct one. Be well-calibrated — use high
values only when the evidence is explicit and unambiguous, and low values when the
text is ambiguous, conflicting, or lacks schedule information.

## Output Format
Respond with a JSON object only, no other text:
{
  "label": "Delay" | "No Delay" | "Uncertain",
  "confidence": <integer 0-100>,
  "reasoning": "<1-2 sentence explanation>"
}
"""

# ---- Self-consistency base prompt ----
# Classic self-consistency: sample the same reasoning prompt k times at a non-zero
# temperature and take the majority vote over the extracted label. We reuse the
# Extract-then-Decide reasoning prompt as the base sampler.
SC_BASE_PROMPT = METHOD_EXTRACT_DECIDE

# Baseline method registry (single-pass). SC is handled separately (multi-sample).
BASELINE_SINGLE = {
    "sp": {"name": "Selective Prediction (confidence)", "prompt": SP_PROMPT},
}

# ---- LP: logit/logprob-based uncertainty (constrained single-token label) ----
# Established uncertainty-aware baseline: the model emits exactly one label token;
# the token's probability (from logprobs) is the confidence used for the
# risk-coverage sweep. Single-token labels keep the confidence clean.
LP_PROMPT = """You are classifying a construction project report excerpt for schedule status.

Labels (output EXACTLY one of these tokens, nothing else, no reasoning, no punctuation):
- `Delay`     — evidence the schedule has been or will be negatively impacted
- `NoDelay`   — schedule unaffected/restored, or no schedule-relevant evidence
- `Uncertain` — evidence insufficient or conflicting

Output only the single token (Delay, NoDelay, or Uncertain)."""

LP_LABEL_TOKENS = {"delay": "Delay", "nodelay": "No Delay", "no": "No Delay", "uncertain": "Uncertain"}

# ---- RAG: retrieval-augmented in-context classification ----
# Established retrieval baseline: retrieve the top-k most similar OTHER cases
# (leave-one-out) as few-shot exemplars, then classify with the ED reasoning prompt.
EMBED_MODEL_DEFAULT = "nomic-embed-text"
RAG_K = 3
RAG_BASE_PROMPT = METHOD_EXTRACT_DECIDE  # same task framing; exemplars prepended at runtime
