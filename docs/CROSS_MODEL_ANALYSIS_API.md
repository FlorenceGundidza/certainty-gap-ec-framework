# API (proprietary) cross-model results 
Strict EC = EC2_A_FULL. Suites: core(ED/Strict/Normalcy)+SP+SC(k=5)+RAG; LP excluded (Claude/Gemini expose no logprobs). RAG embeddings: OpenAI text-embedding-3-small. gpt-5.5 + all Claude/Gemini via Batch API (50%).
NOTE: gemini-2.5-pro was run but EXCLUDED as a pathological outlier (degenerate ED = all 'No Delay'); archived under results_api/_excluded/.


### gpt_5_4_mini
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 34/40 (85.0%) | 3/29 (10.3%) | 5/40 (12.5%) | 1 | 0 |
| Strict EC | 31/40 (77.5%) | 1/29 (3.4%) | 15/40 (37.5%) | 0 | 0 |
| Normalcy EC | 32/40 (80.0%) | 4/29 (13.8%) | 1/40 (2.5%) | 1 | 0 |
| Self-Consistency (vote) | 33/40 (82.5%) | 4/29 (13.8%) | 3/40 (7.5%) | 0 | 0 |
| Retrieval-Augmented ICL | 34/40 (85.0%) | 2/29 (6.9%) | 5/40 (12.5%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 82.5% | 4/29 (13.8%) | 7.5% |
| 0.8 | 82.5% | 3/29 (10.3%) | 12.5% |
| 1.0 | 82.5% | 3/29 (10.3%) | 12.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 17.5% | 13.8% |
| 72 | 97.5% | 15.4% | 10.7% |
| 78 | 92.5% | 16.2% | 11.5% |
| 86 | 87.5% | 14.3% | 12.5% |
| 89 | 82.5% | 12.1% | 13.0% |
| 91 | 72.5% | 10.3% | 10.5% |
| 93 | 67.5% | 3.7% | 5.9% |
| 96 | 57.5% | 4.3% | 7.1% |
| 98 | 42.5% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 87.5% | 12.5% | 12.5% @ 87.5% | tie |
| Strict EC | 62.5% | 6.2% | 6.2% @ 65.0% | tie |
| Normalcy EC | 97.5% | 14.3% | 10.7% @ 97.5% | no |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 10.7% | 0.136 | 40 |

### gpt_5_5
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 31/40 (77.5%) | 5/29 (17.2%) | 0/40 (0.0%) | 0 | 0 |
| Strict EC | 33/40 (82.5%) | 1/29 (3.4%) | 13/40 (32.5%) | 0 | 0 |
| Normalcy EC | 35/40 (87.5%) | 4/29 (13.8%) | 4/40 (10.0%) | 1 | 0 |
| Self-Consistency (vote) | 31/40 (77.5%) | 5/29 (17.2%) | 0/40 (0.0%) | 0 | 0 |
| Retrieval-Augmented ICL | 32/40 (80.0%) | 3/29 (10.3%) | 1/40 (2.5%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 77.5% | 5/29 (17.2%) | 0.0% |
| 0.8 | 75.0% | 5/29 (17.2%) | 2.5% |
| 1.0 | 75.0% | 5/29 (17.2%) | 2.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 25.0% | 20.7% |
| 82 | 95.0% | 23.7% | 17.9% |
| 86 | 87.5% | 17.1% | 12.0% |
| 90 | 77.5% | 12.9% | 9.5% |
| 93 | 62.5% | 12.0% | 13.3% |
| 95 | 55.0% | 9.1% | 16.7% |
| 97 | 42.5% | 0.0% | 0.0% |
| 99 | 25.0% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 100.0% | 17.2% | 20.7% @ 100.0% | yes |
| Strict EC | 67.5% | 6.2% | 13.3% @ 62.5% | yes |
| Normalcy EC | 90.0% | 16.0% | 15.4% @ 90.0% | no |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 18.4% | 0.196 | 40 |

### claude_opus_4_8
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 32/40 (80.0%) | 3/29 (10.3%) | 2/40 (5.0%) | 0 | 0 |
| Strict EC | 32/40 (80.0%) | 1/29 (3.4%) | 13/40 (32.5%) | 1 | 0 |
| Normalcy EC | 34/40 (85.0%) | 4/29 (13.8%) | 5/40 (12.5%) | 1 | 0 |
| Self-Consistency (vote) | 33/40 (82.5%) | 3/29 (10.3%) | 1/40 (2.5%) | 0 | 0 |
| Retrieval-Augmented ICL | 32/40 (80.0%) | 3/29 (10.3%) | 1/40 (2.5%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 82.5% | 3/29 (10.3%) | 2.5% |
| 0.8 | 82.5% | 3/29 (10.3%) | 2.5% |
| 1.0 | 82.5% | 3/29 (10.3%) | 2.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 25.0% | 17.2% |
| 60 | 97.5% | 23.1% | 14.3% |
| 68 | 87.5% | 17.1% | 12.5% |
| 72 | 75.0% | 13.3% | 10.5% |
| 80 | 57.5% | 8.7% | 15.4% |
| 90 | 40.0% | 0.0% | 0.0% |
| 93 | 30.0% | 0.0% | 0.0% |
| 96 | 25.0% | 0.0% | 0.0% |
| 98 | 15.0% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 95.0% | 11.1% | 15.4% @ 92.5% | yes |
| Strict EC | 67.5% | 6.2% | 13.3% @ 62.5% | yes |
| Normalcy EC | 87.5% | 16.7% | 12.5% @ 87.5% | no |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 9.9% | 0.143 | 40 |

### claude_sonnet_4_6
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 33/40 (82.5%) | 3/29 (10.3%) | 2/40 (5.0%) | 1 | 0 |
| Strict EC | 32/40 (80.0%) | 1/29 (3.4%) | 13/40 (32.5%) | 1 | 0 |
| Normalcy EC | 35/40 (87.5%) | 4/29 (13.8%) | 4/40 (10.0%) | 1 | 0 |
| Self-Consistency (vote) | 33/40 (82.5%) | 3/29 (10.3%) | 2/40 (5.0%) | 1 | 0 |
| Retrieval-Augmented ICL | 34/40 (85.0%) | 2/29 (6.9%) | 3/40 (7.5%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 82.5% | 3/29 (10.3%) | 5.0% |
| 0.8 | 82.5% | 3/29 (10.3%) | 5.0% |
| 1.0 | 85.0% | 2/29 (6.9%) | 7.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 22.5% | 13.8% |
| 52 | 100.0% | 22.5% | 13.8% |
| 55 | 97.5% | 20.5% | 14.3% |
| 62 | 90.0% | 16.7% | 16.0% |
| 72 | 82.5% | 15.2% | 13.6% |
| 78 | 65.0% | 3.8% | 6.2% |
| 82 | 60.0% | 4.2% | 7.1% |
| 85 | 57.5% | 4.3% | 7.1% |
| 88 | 52.5% | 4.8% | 8.3% |
| 90 | 47.5% | 5.3% | 10.0% |
| 92 | 40.0% | 0.0% | 0.0% |
| 95 | 32.5% | 0.0% | 0.0% |
| 97 | 25.0% | 0.0% | 0.0% |
| 99 | 15.0% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 95.0% | 11.1% | 14.3% @ 97.5% | yes |
| Strict EC | 67.5% | 5.9% | 6.2% @ 65.0% | yes |
| Normalcy EC | 90.0% | 16.0% | 16.0% @ 90.0% | tie |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 8.7% | 0.128 | 40 |

### gemini_3_5_flash
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 33/40 (82.5%) | 3/29 (10.3%) | 1/40 (2.5%) | 0 | 1 |
| Strict EC | 33/40 (82.5%) | 1/29 (3.4%) | 12/40 (30.0%) | 1 | 0 |
| Normalcy EC | 35/40 (87.5%) | 4/29 (13.8%) | 4/40 (10.0%) | 1 | 0 |
| Self-Consistency (vote) | 32/40 (80.0%) | 4/29 (13.8%) | 0/40 (0.0%) | 0 | 0 |
| Retrieval-Augmented ICL | 32/40 (80.0%) | 2/29 (6.9%) | 2/40 (5.0%) | 1 | 1 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 80.0% | 4/29 (13.8%) | 0.0% |
| 0.8 | 77.5% | 4/29 (13.8%) | 2.5% |
| 1.0 | 82.5% | 3/29 (10.3%) | 7.5% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 17.5% | 10.3% |
| 80 | 100.0% | 17.5% | 10.3% |
| 90 | 97.5% | 17.9% | 10.7% |
| 95 | 95.0% | 15.8% | 11.1% |
| 98 | 50.0% | 0.0% | 0.0% |
| 100 | 32.5% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 97.5% | 10.7% | 10.7% @ 97.5% | tie |
| Strict EC | 70.0% | 5.9% | 0.0% @ 50.0% | no |
| Normalcy EC | 90.0% | 16.0% | 11.1% @ 95.0% | no |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 15.2% | 0.157 | 40 |

### gemini_3_1_pro
| Method | Accuracy | FCR | Abstention | FalseDenial | ParseErr |
|---|---|---|---|---|---|
| Original (ED) | 31/40 (77.5%) | 3/29 (10.3%) | 1/40 (2.5%) | 0 | 3 |
| Strict EC | 33/40 (82.5%) | 1/29 (3.4%) | 12/40 (30.0%) | 1 | 0 |
| Normalcy EC | 35/40 (87.5%) | 4/29 (13.8%) | 4/40 (10.0%) | 1 | 0 |
| Self-Consistency (vote) | 32/40 (80.0%) | 4/29 (13.8%) | 0/40 (0.0%) | 0 | 0 |
| Retrieval-Augmented ICL | 33/40 (82.5%) | 3/29 (10.3%) | 2/40 (5.0%) | 1 | 0 |

**Self-Consistency with abstention** (abstain if agreement < τ):
| τ_agree | Accuracy | FCR | Abstention |
|---|---|---|---|
| 0.6 | 82.5% | 3/29 (10.3%) | 2.5% |
| 0.8 | 80.0% | 3/29 (10.3%) | 15.0% |
| 1.0 | 60.0% | 2/29 (6.9%) | 40.0% |

**Selective Prediction — FCR/Risk vs Coverage curve** (confidence threshold sweep):
| τ_conf | Coverage | Risk(err) | FCR(committed) |
|---|---|---|---|
| 0 | 100.0% | 20.5% | 17.2% |
| 85 | 100.0% | 20.5% | 17.2% |
| 95 | 92.3% | 13.9% | 7.7% |
| 98 | 56.4% | 0.0% | 0.0% |
| 100 | 53.8% | 0.0% | 0.0% |

**EC vs SP frontier** (does EC beat the standard selective-prediction frontier at equal coverage?):
| Config | Coverage | FCR(committed) | SP FCR @ matched coverage | EC better? |
|---|---|---|---|---|
| Original (ED) | 97.5% | 10.7% | 17.2% @ 100.0% | yes |
| Strict EC | 70.0% | 5.9% | 0.0% @ 56.4% | no |
| Normalcy EC | 90.0% | 16.0% | 7.7% @ 92.3% | no |

**Calibration (CAL)** — confidence quality (ECE, Brier; lower is better):
| Confidence source | ECE | Brier | n |
|---|---|---|---|
| sp | 17.5% | 0.172 | 39 |
