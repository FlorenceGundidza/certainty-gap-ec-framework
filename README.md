# Evidence-Constrained LLM Decision-Making — Reproducibility Package

Code, data, and raw model outputs accompanying the paper **"Navigating the Certainty Gap: The Hydraulic Effect of Evidence-Constrained LLMs in Professional Decision-Making"**.

## Overview

This repository contains the complete reproducibility package for the experiments reported in the paper, including:

- the 40-case construction-delay ambiguity benchmark,
- Evidence-Constrained prompting implementations,
- evaluation and analysis scripts,
- raw outputs from all twelve evaluated models (six proprietary and six open-weight),
- anonymized human evaluation data,
- figure generation scripts,
- supporting documentation.

The repository is organized so that the principal experiments, figures, and quantitative analyses reported in the paper can be independently reproduced from the released code, benchmark, and raw outputs.

## What this reproduces  
- The empirical analyses supporting the observed **Hydraulic Effect** under the evaluated benchmark conditions, including the reduction of the False Confirmation Rate (FCR) to ≤3.4% using Strict EC while increasing abstention across the twelve evaluated models.
- All **baselines**: Selective Prediction (risk–coverage), Self-Consistency (k=5),
  Retrieval-Augmented ICL (+leave-one-category-out), Log-Probability uncertainty,
  Calibration (ECE/Brier).
- The **cost-sensitive**, **computational-cost**, **cross-model**,
  **real-document**, failure-taxonomy re-annotation, and human-evaluation
  re-analyses.

## Repository Layout 
```
code/
  run_open_models.py        harness (Ollama / OpenAI-compatible); suites core|sp|sc|lp|rag|strict|rag_loco
  prompts_core.py           Prompt implementations (ED, Strict EC=EC2_A_FULL, Normalcy EC, SP, SC, RAG, LP)
  run_openai_batch.py       OpenAI Batch runner          run_claude_batch.py    Anthropic Batch runner
  run_gemini_batch.py       Gemini Batch runner          real_doc_run.py        real-document runner
  analyze_open.py           metrics (Acc, FCR, abstention, SP/LP risk–coverage, ECE/Brier, EC-vs-SP)
  analyze_costsens.py       cost-sensitive + compute     analyze_realdoc.py     real-document analysis
  annotate_failures.py      independent 3-judge failure re-annotation (Fleiss κ)
  requirements.txt
data/
  dataset_v2.json           40-case curated ambiguity benchmark
  dataset_realdoc.json      110 un-curated natural paragraphs from 55 real reports (+weak doc-level labels)
  failure_cases_all.json    23 failure cases
  human_eval/               anonymized evaluator responses (9 raters) + re-analysis
results/
  results_cluster/          raw outputs, 6 open-weight models (+ show-*.txt digests)
  results_api/              raw outputs, 6 proprietary models
  results_realdoc/          raw outputs, real-document experiment
docs/
  CROSS_MODEL_ANALYSIS.md  CROSS_MODEL_ANALYSIS_API.md  COST_SENSITIVE_AND_COMPUTE.md
  REALDOC_ANALYSIS.md  ENVIRONMENT_AND_COST.md
LICENSE (Apache-2.0, code)   LICENSE-DATA (CC BY 4.0, data)   SOURCE_REPORTS.md ```

## Reproducing the Open-Weight Experiments)
```bash
python -m venv venv && source venv/bin/activate && pip install -r code/requirements.txt
ollama pull gemma3:27b            # full model list + digests in docs/CROSS_MODEL_ANALYSIS.md
python code/run_open_models.py gemma3:27b --suite core,sp,sc,lp,rag,strict
python code/analyze_open.py
```

## Reproduce — proprietary / real-document
Set `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY`; run the `run_*_batch.py`
adapters (Batch API, 50% cost) or `real_doc_run.py`. Outputs are non-deterministic;
resolved model IDs + run config are in `docs/ENVIRONMENT_AND_COST.md`.

## Notes
- **Strict EC = EC2_A_FULL** (Modality Filter + Self-Diagnosis + Conservative), matching paper Table 4.
- Decoding: temperature 0 for single-pass configs; SC at temperature 0.7 / k=5.
- The open-weight tier carries the exact-reproducibility claim; proprietary outputs are released as JSON.
- **Licenses:** code under **Apache-2.0** (`LICENSE`); data under **CC BY 4.0** (`LICENSE-DATA`).
- The 55 source PDF reports are **not** redistributed (third-party IFI documents); see `SOURCE_REPORTS.md`.

## Citation

If you use this repository, please cite the accompanying paper:

Florence Gundidza, Masato Kikuchi, and Tadachika Ozono.

**Navigating the Certainty Gap: The Hydraulic Effect of Evidence-Constrained LLMs in Professional Decision-Making.**

*Under review at IEEE Access.*

The DOI and BibTeX entry will be added after publication.

