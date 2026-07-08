# R4#9 Cost-sensitive evaluation + R4#11 Computational cost

Default cost matrix (high-stakes): false confirmation=5.0, false denial=3.0, abstention=1.0, other-commit-error=2.0, correct=0.

## R4#9 — expected cost per method (lower is better; default matrix)

| model | ED | Strict EC | Normalcy | SC | RAG | best (default) | Strict-EC optimal when FC≥ |
|---|---|---|---|---|---|---|---|
| gemma3_27b | 0.90 | 0.30 | 0.55 | 0.90 | 0.53 | strict_ec | 1 |
| qwen3_32b | 0.68 | 0.33 | 0.57 | 0.42 | 0.35 | strict_ec | 3 |
| magistral_24b | 0.45 | 0.33 | 0.80 | 0.42 | 0.20 | rag | — |
| llama4_scout | 0.40 | 0.28 | 0.50 | 0.40 | 0.30 | strict_ec | 1 |
| gpt_oss_120b | 0.60 | 0.40 | 0.53 | 0.42 | 0.50 | strict_ec | 4 |
| deepseek_r1_70b | 0.42 | 0.42 | 0.53 | 0.38 | 0.17 | rag | — |
| gpt_5_4_mini | 0.53 | 0.33 | 0.72 | 0.62 | 0.45 | strict_ec | 2 |
| gpt_5_5 | 0.82 | 0.28 | 0.57 | 0.82 | 0.65 | strict_ec | 1 |
| claude_opus_4_8 | 0.60 | 0.35 | 0.60 | 0.57 | 0.65 | strict_ec | 2 |
| claude_sonnet_4_6 | 0.60 | 0.35 | 0.57 | 0.60 | 0.47 | strict_ec | 2 |
| gemini_3_5_flash | 0.57 | 0.33 | 0.57 | 0.70 | 0.57 | strict_ec | 2 |
| gemini_3_1_pro | 0.68 | 0.33 | 0.57 | 0.70 | 0.60 | strict_ec | 2 |

## R4#11 — computational cost (avg output tokens/case; EC overhead vs ED single-pass)

| model | ED out | Strict out | Normalcy out | SP out | EC/ED overhead | SC calls/case |
|---|---|---|---|---|---|---|
| gemma3_27b | 143 | 234 | 269 | 67 | 1.64x | 5 (k) |
| qwen3_32b | 147 | 643 | 278 | 74 | 4.38x | 5 (k) |
| magistral_24b | 121 | 192 | 211 | 59 | 1.59x | 5 (k) |
| llama4_scout | 146 | 219 | 251 | 67 | 1.50x | 5 (k) |
| gpt_oss_120b | 122 | 241 | 276 | 53 | 1.97x | 5 (k) |
| deepseek_r1_70b | 408 | 465 | 521 | 395 | 1.14x | 5 (k) |
| gpt_5_4_mini | 400 | 657 | 519 | 190 | 1.64x | 5 (k) |
| gpt_5_5 | 395 | 507 | 444 | 192 | 1.28x | 5 (k) |
| claude_opus_4_8 | 199 | 563 | 530 | 99 | 2.84x | 5 (k) |
| claude_sonnet_4_6 | 178 | 557 | 543 | 94 | 3.14x | 5 (k) |
| gemini_3_5_flash | 731 | 887 | 702 | 490 | 1.21x | 5 (k) |
| gemini_3_1_pro | 732 | 971 | 803 | 618 | 1.33x | 5 (k) |

Notes: EC configs emit a structured evidence+modality trace (more output tokens than ED); SC multiplies *calls* by k=5; SP/LP are single-pass and cheapest. Input tokens are dominated by the case excerpt and are comparable across configs.
