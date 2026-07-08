# Open-weight cross-model results 
Strict EC corresponds to the EC2_A_FULL configuration used throughout the paper. Log-probability (LP) uncertainty was evaluated only for instruct-style models (Gemma 3, Magistral, and Llama 4 Scout). LP results are not reported for reasoning models (Qwen 3, GPT-OSS-120B, and DeepSeek-R1-70B) because these models do not provide reliable answer-token probability distributions suitable for LP-based uncertainty estimation. All open-weight experiments were performed using Ollama with temperature set to 0.

### gemma3_27b
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 31/40 (77.5%) | 6/29 (20.7%) | 2/40 (5.0%) | 1 | 0 |
| Strict EC | 35/40 (87.5%) | 1/29 (3.4%) | 9/40 (22.5%) | 1 | 0 |
| Normalcy EC | 34/40 (85.0%) | 3/29 (10.3%) | 3/40 (7.5%) | 1 | 0 |
| Self-Consistency (vote) | 31/40 (77.5%) | 6/29 (20.7%) | 2/40 (5.0%) | 1 | 0 |
| Logprob Uncertainty (argmax) | 31/40 (77.5%) | 7/29 (24.1%) | 0/40 (0.0%) | 0 | 0 |
| Retrieval-Augmented ICL | 34/40 (85.0%) | 3/29 (10.3%) | 5/40 (12.5%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 77.5% | 6/29 (20.7%) | 5.0% |
| 0.8 | 77.5% | 6/29 (20.7%) | 5.0% |
| 1.0 | 77.5% | 6/29 (20.7%) | 5.0% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 22.5% | 20.7% |
| 30 | 100.0% | 22.5% | 20.7% |
| 40 | 95.0% | 18.4% | 22.2% |
| 65 | 92.5% | 18.9% | 23.1% |
| 70 | 87.5% | 14.3% | 16.7% |
| 75 | 85.0% | 11.8% | 13.0% |
| 85 | 75.0% | 6.7% | 9.5% |
| 90 | 65.0% | 3.8% | 5.6% |
| 95 | 40.0% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 95.0% | 22.2% | 22.2% @ 95.0% | tie |
| Strict EC | 77.5% | 5.0% | 9.5% @ 75.0% | yes |
| Normalcy EC | 92.5% | 11.5% | 23.1% @ 92.5% | yes |

**Logprob Uncertainty (LP) — FCR/Risk vs Coverage curve** (logprob-confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 18.4% | 25.9% |
| 52 | 100.0% | 18.4% | 25.9% |
| 78 | 97.4% | 18.9% | 26.9% |
| 100 | 94.7% | 19.4% | 28.0% |
| 100 | 92.1% | 20.0% | 29.2% |

**EC vs LP frontier:**
| Config | Coverage | FCR(committed) | LP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 95.0% | 22.2% | 28.0% @ 94.7% | yes |
| Strict EC | 77.5% | 5.0% | 29.2% @ 92.1% | yes |
| Normalcy EC | 92.5% | 11.5% | 29.2% @ 92.1% | yes |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 13.5% | 0.121 | 40 |
| Logprob Uncertainty (argmax) | 20.2% | 0.191 | 38 |

### qwen3_32b
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 31/40 (77.5%) | 3/29 (10.3%) | 2/40 (5.0%) | 1 | 0 |
| Strict EC | 32/40 (80.0%) | 0/29 (0.0%) | 10/40 (25.0%) | 1 | 1 |
| Normalcy EC | 32/40 (80.0%) | 2/29 (6.9%) | 1/40 (2.5%) | 1 | 0 |
| Self-Consistency (vote) | 35/40 (87.5%) | 2/29 (6.9%) | 4/40 (10.0%) | 1 | 0 |
| Retrieval-Augmented ICL | 33/40 (82.5%) | 0/29 (0.0%) | 4/40 (10.0%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 87.5% | 2/29 (6.9%) | 10.0% |
| 0.8 | 87.5% | 2/29 (6.9%) | 15.0% |
| 1.0 | 87.5% | 2/29 (6.9%) | 17.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 17.5% | 6.9% |
| 45 | 100.0% | 17.5% | 6.9% |
| 60 | 97.5% | 17.9% | 7.1% |
| 85 | 95.0% | 18.4% | 7.4% |
| 90 | 90.0% | 16.7% | 7.7% |
| 95 | 70.0% | 3.6% | 0.0% |
| 98 | 5.0% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 95.0% | 11.1% | 7.4% @ 95.0% | no |
| Strict EC | 75.0% | 0.0% | 0.0% @ 70.0% | tie |
| Normalcy EC | 97.5% | 7.1% | 7.1% @ 97.5% | tie |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 15.5% | 0.156 | 40 |

### magistral_24b
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 36/40 (90.0%) | 3/29 (10.3%) | 5/40 (12.5%) | 1 | 0 |
| Strict EC | 35/40 (87.5%) | 1/29 (3.4%) | 6/40 (15.0%) | 1 | 0 |
| Normalcy EC | 32/40 (80.0%) | 5/29 (17.2%) | 1/40 (2.5%) | 1 | 0 |
| Self-Consistency (vote) | 35/40 (87.5%) | 2/29 (6.9%) | 4/40 (10.0%) | 1 | 0 |
| Logprob Uncertainty (argmax) | 29/40 (72.5%) | 1/29 (3.4%) | 0/40 (0.0%) | 0 | 0 |
| Retrieval-Augmented ICL | 36/40 (90.0%) | 0/29 (0.0%) | 7/40 (17.5%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 87.5% | 2/29 (6.9%) | 12.5% |
| 0.8 | 92.5% | 2/29 (6.9%) | 17.5% |
| 1.0 | 92.5% | 2/29 (6.9%) | 17.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 12.5% | 10.3% |
| 30 | 100.0% | 12.5% | 10.3% |
| 70 | 95.0% | 13.2% | 11.1% |
| 75 | 92.5% | 13.5% | 11.5% |
| 80 | 87.5% | 11.4% | 8.3% |
| 85 | 72.5% | 13.8% | 10.5% |
| 90 | 50.0% | 0.0% | 0.0% |
| 95 | 30.0% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 87.5% | 12.5% | 8.3% @ 87.5% | no |
| Strict EC | 85.0% | 4.3% | 8.3% @ 87.5% | yes |
| Normalcy EC | 97.5% | 17.9% | 10.3% @ 100.0% | no |

**Logprob Uncertainty (LP) — FCR/Risk vs Coverage curve** (logprob-confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 3.3% | 4.8% |
| 82 | 100.0% | 3.3% | 4.8% |
| 91 | 96.7% | 3.4% | 5.0% |
| 93 | 93.3% | 3.6% | 5.3% |
| 96 | 90.0% | 3.7% | 5.6% |
| 98 | 86.7% | 3.8% | 5.9% |
| 99 | 83.3% | 4.0% | 6.2% |
| 100 | 80.0% | 4.2% | 6.2% |
| 100 | 76.7% | 4.3% | 6.7% |
| 100 | 73.3% | 4.5% | 7.1% |
| 100 | 66.7% | 5.0% | 8.3% |
| 100 | 50.0% | 6.7% | 11.1% |

**EC vs LP frontier:**
| Config | Coverage | FCR(committed) | LP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 87.5% | 12.5% | 5.9% @ 86.7% | no |
| Strict EC | 85.0% | 4.3% | 6.2% @ 83.3% | yes |
| Normalcy EC | 97.5% | 17.9% | 5.0% @ 96.7% | no |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 12.1% | 0.126 | 40 |
| Logprob Uncertainty (argmax) | 3.2% | 0.035 | 30 |

### llama4_scout
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 34/40 (85.0%) | 1/29 (3.4%) | 3/40 (7.5%) | 1 | 0 |
| Strict EC | 35/40 (87.5%) | 1/29 (3.4%) | 10/40 (25.0%) | 1 | 0 |
| Normalcy EC | 32/40 (80.0%) | 1/29 (3.4%) | 1/40 (2.5%) | 1 | 0 |
| Self-Consistency (vote) | 34/40 (85.0%) | 1/29 (3.4%) | 3/40 (7.5%) | 1 | 0 |
| Logprob Uncertainty (argmax) | 30/40 (75.0%) | 5/29 (17.2%) | 0/40 (0.0%) | 0 | 0 |
| Retrieval-Augmented ICL | 34/40 (85.0%) | 0/29 (0.0%) | 5/40 (12.5%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 85.0% | 1/29 (3.4%) | 7.5% |
| 0.8 | 85.0% | 1/29 (3.4%) | 7.5% |
| 1.0 | 85.0% | 1/29 (3.4%) | 7.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 15.0% | 10.3% |
| 0 | 100.0% | 15.0% | 10.3% |
| 20 | 97.5% | 12.8% | 10.7% |
| 40 | 92.5% | 13.5% | 11.5% |
| 60 | 90.0% | 13.9% | 12.0% |
| 70 | 85.0% | 11.8% | 8.7% |
| 80 | 80.0% | 6.2% | 0.0% |
| 90 | 55.0% | 0.0% | 0.0% |
| 95 | 40.0% | 0.0% | 0.0% |
| 100 | 27.5% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 92.5% | 3.8% | 11.5% @ 92.5% | yes |
| Strict EC | 75.0% | 5.3% | 0.0% @ 80.0% | no |
| Normalcy EC | 97.5% | 3.6% | 10.7% @ 97.5% | yes |

**Logprob Uncertainty (LP) — FCR/Risk vs Coverage curve** (logprob-confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 18.9% | 19.2% |
| 57 | 100.0% | 18.9% | 19.2% |
| 64 | 97.3% | 16.7% | 20.0% |
| 96 | 94.6% | 14.3% | 16.7% |
| 100 | 91.9% | 11.8% | 13.0% |

**EC vs LP frontier:**
| Config | Coverage | FCR(committed) | LP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 92.5% | 3.8% | 13.0% @ 91.9% | yes |
| Strict EC | 75.0% | 5.3% | 13.0% @ 91.9% | yes |
| Normalcy EC | 97.5% | 3.6% | 20.0% @ 97.3% | yes |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 11.6% | 0.120 | 40 |
| Logprob Uncertainty (argmax) | 16.7% | 0.153 | 37 |

### gpt_oss_120b
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 32/40 (80.0%) | 3/29 (10.3%) | 5/40 (12.5%) | 1 | 0 |
| Strict EC | 31/40 (77.5%) | 1/29 (3.4%) | 12/40 (30.0%) | 1 | 0 |
| Normalcy EC | 34/40 (85.0%) | 3/29 (10.3%) | 5/40 (12.5%) | 1 | 0 |
| Self-Consistency (vote) | 35/40 (87.5%) | 2/29 (6.9%) | 4/40 (10.0%) | 1 | 0 |
| Retrieval-Augmented ICL | 35/40 (87.5%) | 3/29 (10.3%) | 4/40 (10.0%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 87.5% | 2/29 (6.9%) | 10.0% |
| 0.8 | 85.0% | 2/29 (6.9%) | 12.5% |
| 1.0 | 85.0% | 2/29 (6.9%) | 12.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 22.5% | 13.8% |
| 65 | 100.0% | 22.5% | 13.8% |
| 70 | 97.5% | 20.5% | 14.3% |
| 71 | 92.5% | 16.2% | 11.5% |
| 78 | 90.0% | 13.9% | 8.0% |
| 80 | 87.5% | 14.3% | 8.3% |
| 82 | 82.5% | 9.1% | 8.7% |
| 85 | 80.0% | 6.2% | 9.1% |
| 90 | 72.5% | 6.9% | 10.5% |
| 92 | 70.0% | 3.6% | 5.6% |
| 93 | 52.5% | 0.0% | 0.0% |
| 95 | 50.0% | 0.0% | 0.0% |
| 96 | 15.0% | 0.0% | 0.0% |
| 97 | 5.0% | 0.0% | 0.0% |
| 98 | 2.5% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 87.5% | 12.5% | 8.3% @ 87.5% | no |
| Strict EC | 70.0% | 5.9% | 5.6% @ 70.0% | no |
| Normalcy EC | 87.5% | 12.5% | 8.3% @ 87.5% | no |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 14.9% | 0.143 | 40 |

### deepseek_r1_70b
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 35/40 (87.5%) | 2/29 (6.9%) | 4/40 (10.0%) | 1 | 0 |
| Strict EC | 32/40 (80.0%) | 2/29 (6.9%) | 10/40 (25.0%) | 0 | 0 |
| Normalcy EC | 33/40 (82.5%) | 2/29 (6.9%) | 2/40 (5.0%) | 1 | 0 |
| Self-Consistency (vote) | 36/40 (90.0%) | 2/29 (6.9%) | 5/40 (12.5%) | 1 | 0 |
| Retrieval-Augmented ICL | 37/40 (92.5%) | 0/29 (0.0%) | 6/40 (15.0%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 90.0% | 2/29 (6.9%) | 12.5% |
| 0.8 | 90.0% | 2/29 (6.9%) | 12.5% |
| 1.0 | 92.5% | 1/29 (3.4%) | 15.0% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 15.0% | 6.9% |
| 20 | 100.0% | 15.0% | 6.9% |
| 50 | 97.5% | 15.4% | 7.1% |
| 60 | 95.0% | 15.8% | 7.4% |
| 80 | 87.5% | 14.3% | 8.3% |
| 90 | 82.5% | 9.1% | 4.5% |
| 95 | 42.5% | 0.0% | 0.0% |
| 100 | 37.5% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 90.0% | 8.0% | 8.3% @ 87.5% | yes |
| Strict EC | 75.0% | 10.0% | 4.5% @ 82.5% | no |
| Normalcy EC | 95.0% | 7.4% | 7.4% @ 95.0% | tie |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 11.5% | 0.135 | 40 |
