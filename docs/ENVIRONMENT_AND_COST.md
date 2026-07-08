# Execution Environment and Computational Cost

Supporting documentation for

"Navigating the Certainty Gap: The Hydraulic Effect of Evidence-Constrained LLMs in Professional Decision-Making"

Standalone record of the compute environments, software, models, evaluation protocol, and cost for the open-weight + proprietary multi-model experiments added for the resubmission. Intended as the source for the paper's *Implementation Details* / reproducibility appendix and as an internal cost record. 

---

## 1. Scope

Each model was evaluated on the **40-case construction benchmark** (`dataset_v2.json`) under up to seven decision/baseline configurations × the appropriate number of inferences. **12 models reported** across 5 vendors (6 open-weight + 6 proprietary), plus 1 model run-but-excluded (gemini-2.5-pro). Prompts and scoring are byte-identical to the paper's configs (Strict EC = EC2_A_FULL).

---

## 2. Compute environments

| Environment | Hardware | Role |
|---|---|---|
| **Local Mac** | Mac Studio (Mac16,9), Apple M4 Max (T6041), 16 cores (12P+4E), 128 GB unified; macOS 15.7.7 (24G720), Darwin 24.6.0 arm64 | Ollama host for deepseek-r1-70b & initial gemma3; OpenAI sync runs + all batch orchestration; RAG embeddings; figures/analysis |
| **ozlab cluster** (SLURM, controller `summer`) | 4 GPU worker nodes (see measured table below); Ubuntu 24.04.4 LTS, kernel 6.17, NVIDIA driver 595.71.05 / CUDA 13.2 (x86_64), driver 580.142 / CUDA 13.0 (oz05 ARM) | Open-weight inference, one model per node, in parallel |
| **OpenAI API** | — | gpt-5.4-mini (sync), gpt-5.5 (Batch) |
| **Anthropic API** | — | Claude Opus 4.8 + Sonnet 4.6 (Batch) |
| **Google Gemini API** | — | Gemini-3.5-flash + 3.1-pro (+ 2.5-pro, excluded) (Batch) |

**Measured cluster worker specs (probed 2026-06-20):**

| Node | GPU | VRAM | Arch | CPU cores | RAM (installed) | OS / kernel | Driver / CUDA | Model run |
|---|---|---|---|---|---|---|---|---|
| oz04 | RTX 5090 | 32 GB (32607 MiB) | Blackwell x86_64 | 24 | 128 GiB | Ubuntu 24.04.4, 6.17.0-29 | 595.71.05 / 13.2 | qwen3-32b |
| oz02 | RTX 5070 Ti | 16 GB (16303 MiB) | Blackwell x86_64 | 24 | 48 GiB | Ubuntu 24.04.4, 6.17.0-35 | 595.71.05 / 13.2 | gemma3-27b |
| oz06 | RTX 5080 | 16 GB (16303 MiB) | Blackwell x86_64 | 16 | 32 GiB | Ubuntu 24.04.4, 6.17.0-35 | 595.71.05 / 13.2 | magistral-24b |
| oz05 | GB10 (Grace-Blackwell) | 128 GB unified | Blackwell **aarch64** | 20 | 128 GiB | Ubuntu 24.04.4, 6.17.0-1018-nvidia | 580.142 / 13.0 | gpt-oss-120B + llama4-scout |

(RAM = installed capacity; `free -h` shows slightly less — 125/46/30/121 GiB respectively — due to kernel/reserved memory.)

---

## 3. Software / runtimes

| Component | Version |
|---|---|
| Python (orchestration/analysis, Mac venv) | CPython **3.14.6** (`/Volumes/TMP4TB/florence/venv`) |
| Python (cluster system) | 3.12.3 (Ubuntu 24.04) |
| Ollama | client **0.30.10** (Mac, confirmed); cluster ran a per-job Ollama install of the same release (x86_64 on oz02/04/06; aarch64 on oz05) |
| openai SDK | **2.43.0** |
| anthropic SDK | **0.111.0** |
| google-genai SDK | **2.9.0** (google-auth 2.49.2) |
| HTTP / data deps | httpx 0.28.1, pydantic 2.12.5, requests 2.33.1, certifi 2026.2.25, python-dotenv 1.2.2, tqdm 4.67.3 |
| Figures / numerics | matplotlib **3.10.8**, numpy 2.4.4, scipy 1.17.1, pandas 3.0.2 |
| Embeddings (open-weight RAG) | `nomic-embed-text` (Ollama, 768-d) |
| Embeddings (API RAG) | OpenAI `text-embedding-3-small` (1536-d) — shared across all API runs so retrieved neighbours are identical |

Note: the metric/scoring code (`analyze_open.py`) uses the Python standard library only; `matplotlib`/`numpy`/`scipy` are used solely for the figures (`make_figures.py`).

Harness (portable, self-contained): `openweight/{run_open_models.py, prompts_core.py, dataset_v2.json, analyze_open.py}` + provider runners `run_openai_batch.py`, `run_claude_batch.py`, `run_gemini_batch.py`. Decoding: temperature = 0 for single-pass configs; SC samples at temperature 0.7 (open) / default + k=5 (reasoning models vary intrinsically). All structured output requested as JSON; robust balanced-brace JSON extraction.

---

## 4. Models

### Open-weight (local/cluster, fully reproducible)

| slug | Ollama tag | Quant | Arch | Reasoning |
|---|---|---|---|---|
| gemma3_27b | `gemma3:27b` | Q4_K_M | dense | instruct |
| qwen3_32b | `qwen3:32b` | Q4_K_M | dense | thinking-toggle |
| magistral_24b | `magistral` (24B) | Q4_K_M | dense | reasoning |
| llama4_scout | `llama4:scout` | Q4_K_M | MoE 109B/17B | instruct |
| gpt_oss_120b | `gpt-oss:120b` | MXFP4 | MoE 117B/5B | reasoning-effort |
| deepseek_r1_70b | `deepseek-r1:70b` | Q4_K_M | dense (R1 distill) | RL-reasoning |

Per-model Ollama digests recorded in `openweight/results_cluster/show-*.txt`.

### Proprietary API (resolved model IDs)

| slug | Resolved model ID | Vendor | Reasoning setting | Charge |
|---|---|---|---|---|
| gpt_5_4_mini | gpt-5.4-mini-2026-03-17 | OpenAI | reasoning_effort=high | sync (standard) |
| gpt_5_5 | gpt-5.5-2026-04-23 | OpenAI | reasoning_effort=high | **Batch** |
| claude_opus_4_8 | claude-opus-4-8 | Anthropic | default | **Batch** |
| claude_sonnet_4_6 | claude-sonnet-4-6 | Anthropic | default | **Batch** |
| gemini_3_5_flash | gemini-3.5-flash | Google | default (thinking) | **Batch** |
| gemini_3_1_pro | gemini-3.1-pro-preview | Google | default (thinking) | **Batch** |
| ~~gemini_2_5_pro~~ | gemini-2.5-pro | Google | default | **Batch** — **EXCLUDED** (pathological outlier: degenerate ED) |

LP (logit/logprob uncertainty) is reported for open-weight instruct models only; Claude/Gemini expose no token logprobs and reasoning models yield degenerate logits → LP N/A there.

---

## 5. Evaluation protocol (per model)

Configs: **ED** (Extract-then-Decide), **Strict EC** (= EC2-A: Modality Filter + Self-Diagnosis + Conservative, paper Table 4), **Normalcy EC** (EC3); baselines **SP** (selective prediction + risk-coverage sweep), **SC** (self-consistency k=5 majority vote), **RAG** (retrieval-augmented in-context, kNN k=3, leave-one-out), **LP** (open-weight instruct only), **CAL** (calibration ECE/Brier from SP/LP). Inference counts: core 3×40 + SP 40 + SC 5×40 + RAG 40 ≈ 400/model (LP +40 where applicable). gpt-5.5 + all Claude/Gemini submitted via each provider's **Batch API (50% discount)**.

---

## 6. Cost

### API spend (actual tokens × current list price; Batch = 50% off)

| Model | Input tok | Output tok | Rate in/out ($/1M) | Cost |
|---|---|---|---|---|
| gpt-5.4-mini (sync) | 323,401 | 164,544 | 0.75 / 4.50 | $0.98 |
| gpt-5.5 (batch) | 323,401 | 155,061 | 2.50 / 15.00 | $3.13 |
| Claude Opus 4.8 (batch) | 542,847 | 103,152 | 2.50 / 12.50 | $2.65 |
| Claude Sonnet 4.6 (batch) | 359,128 | 97,341 | 1.50 / 7.50 | $1.27 |
| Gemini-3.5-flash (batch) | 330,459 | 282,273 | 0.75 / 4.50 | $1.52 |
| Gemini-3.1-pro (batch) | 330,459 | 297,776 | 1.00 / 6.00 | $2.12 |
| **Reported subtotal (6)** | | | | **$11.67** |
| gemini-2.5-pro (batch, excluded) | 346,100 | 248,710 | 0.625 / 5.00 | $1.46 |
| **Total API spend** | | | | **$13.13** |

Token note: SC sampling tokens are estimated as 5× the ED-suite tokens (k=5, same prompt); single-pass suites are exact from recorded `usage`. Output tokens for Gemini/Claude/GPT reasoning models include thinking tokens. Embeddings (`text-embedding-3-small`, ~80k tok) ≈ $0.002, negligible.

**Pricing source (verified 2026-06-20, not from memory):** OpenAI `developers.openai.com/api/docs/pricing`; Gemini `ai.google.dev/gemini-api/docs/pricing`; Claude per the claude-api reference. Batch = 50% off on all three.

### Budget adherence
- Claude (Opus 4.8 + Sonnet 4.6): **$3.92** — cap $10 ✓
- Gemini (3 models run): **$5.10** ($3.64 for the 2 kept + $1.46 excluded) — cap ¥5000 (≈$32) ✓
- OpenAI: **$4.12**
- Batch saved ~50% on 6 of 7 API models (e.g., gpt-5.5 $3.13 vs $6.22 standard).

### Open-weight compute
The open-weight experiments incurred no API costs and were performed using local and institutional GPU resources.

---

## 7. Reproducibility notes 

- **Open-weight tier carries the reproducibility claim**: open weights + pinned Ollama quant + digests (`show-*.txt`) + temperature 0 + released harness/scripts/dataset → re-runnable by reviewers.
- **Proprietary tier complements, does not replace it**: API models are not weight-reproducible. We log resolved model IDs (§4), run config, and dates here for traceability.
- **Caveats to state in Limitations**: (a) `gemini-3.1-pro-preview` is a preview model and may be deprecated (reproducibility risk) — kept alongside the GA `gemini-3.5-flash`; (b) SC token counts in the cost table are estimated (5× ED); (c) reasoning-model outputs are stochastic even at temperature 0; (d) gemini-2.5-pro excluded as a pathological outlier (archived under `openweight/results_api/_excluded/`).
- **Artifacts**: `openweight/CROSS_MODEL_ANALYSIS.md` (open), `openweight/CROSS_MODEL_ANALYSIS_API.md` (proprietary), raw results in `openweight/results_cluster/` and `openweight/results_api/`.
