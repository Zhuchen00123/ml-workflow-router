# Task → expert routing reference

Supplement to `SKILL.md`. Each row states the primary expert, what helps it, and
where its authority ends. Expert **names** are directory names in your
`expert_library`; nothing here bundles their content.

## Data preparation

| Task | Primary | Helpers / conditions | Authority ends at |
|---|---|---|---|
| First contact with CSV/TSV/JSON: types, missingness, outlier clues | `exploratory-data-analysis` | figures via `matplotlib` | It reports structure; it must not delete outliers, impute, or overwrite raw data. Format coverage is bounded. |
| Cleaning, dedup, column transforms, joins, group-by, CSV↔Parquet | `polars` | EDA decides what to check | Deterministic transforms only. Record row counts and key aggregates before/after. |
| Excel numeric tables | `polars` / project pandas + openpyxl | — | Macros, formulas, styling, recalculation are not ordinary ETL. |
| SQL extract into a dataframe | `polars` + project SQL driver | read-only credentials, explicit query scope | Not a database-security task. |
| Read-only remote dataset exploration | `huggingface-datasets` | explicit user approval for remote access | Viewer GET endpoints only. Never upload agent sessions, prompts, or local files. |
| Label definition, sample selection, deduplication policy | project code + EDA | user defines label semantics and licence | No skill here certifies semantic correctness of labels. |
| Scaling, imputation, encoding, feature selection | `scikit-learn` | `polars` for deterministic transforms | Learned transforms fit inside training folds via a Pipeline. |
| Data too large for memory | `polars` first; `dask` when measured necessary | `get-available-resources` | Measure the bottleneck before introducing a cluster engine. |

## Modelling

| Task | Primary | Helpers | Notes |
|---|---|---|---|
| Tabular classification/regression | `scikit-learn` | EDA, `polars`, `matplotlib` | Build a reproducible baseline before reaching for a neural net. |
| Clustering, usual anomaly detection, PCA | `scikit-learn` | EDA, `matplotlib` | Cluster metrics and thresholds must follow the task definition. |
| Nonlinear embedding / projection | `umap-learn` | `scikit-learn`, `matplotlib` | Islands, gaps and axes are not proven classes or physical distances. |
| Custom MLP/CNN/RNN, own training loop | `pytorch-lightning` | `tensorboard`, resource check | Lightning manages training engineering; it does not validate architecture choices. |
| Vision with pretrained backbones | `transformers` or `pytorch-lightning` | `torchvision` | Pick by the actual model ecosystem. Segmentation/detection need task-specific metrics. |
| NLP/audio/multimodal pretrained models | `transformers` | project data pipeline | Handles processors/tokenizers/Trainer; not every deep model belongs here. |
| LoRA-style fine-tuning | `transformers` + `peft-fine-tuning` | resource check | PEFT rewrites parameters; do not stack Lightning on top without reason. QLoRA readiness ≠ LoRA readiness. |
| Time-series classification/forecasting/anomaly | `aeon` | `statsmodels` for ARIMA/SARIMAX | Split and backtest by time; never shuffle before predicting the future. |
| Graph algorithms, paths, centrality, communities | `networkx` | `matplotlib` | Not a graph neural network. |
| Node/edge/graph prediction (GCN, GAT, GraphSAGE) | `torch-geometric` | PyTorch, optionally Lightning | Split edges/nodes to avoid leakage. Optional compiled extensions are separate installs. |
| Single-agent RL with Gymnasium | `stable-baselines3` | `tensorboard` | Verify reward/termination/truncation and evaluate on independent seeds. Not LLM RLHF/GRPO. |
| Diffusion image generation | `stable-diffusion-image-generation` | HF libraries per task | Generation quality and safety behaviour are not implied by the pipeline running. |
| 3DGS diagnosis / experiment planning | `3dgs-training-debugger` / `3dgs-experiment-planner` | a specific 3DGS implementation | Documentation only. Renderer, COLMAP, dataset and custom CUDA builds are separate, separately verified installs. |

## Evaluation, explanation, operations

| Task | Primary | Conditions |
|---|---|---|
| Splitting, CV, metrics, hyperparameter search | `scikit-learn` | Stratify/group/time split by the real observational unit; tune on validation only. |
| Effect sizes, confidence intervals, assumption checks | `statistical-analysis` | Declare the experimental unit and multiple comparisons. Do not treat correlated batches as independent replicates. |
| Coefficient inference, GLM, mixed models | `statsmodels` | A successful fit is not causal identification. |
| Training curves, gradient/throughput clues | `tensorboard` | Local logs; compare runs only at matched data/metric/budget. |
| Feature attribution | `shap` | Explain a fixed, already-validated model; choose the background set deliberately; check additivity. Attribution ≠ causality. |
| Figures for reports/papers | `matplotlib` | Figures come from real results; state units, intervals, sample sizes. |
| Experiment tracking, model registry | `mlflow` | Use local artifacts and aliases. Stages are deprecated. No cloud deployment or 0.0.0.0 listener without an explicit request. |
| Inference/export/deployment, drift monitoring | project code (optionally `mlflow`) | Needs its own input contract, numerical parity, latency/memory, and permission tests. Not covered by any single expert here. |

## Cross-cutting rules

1. **One experiment, one primary trainer.** sklearn / Lightning / HF Trainer / SB3.
2. **EDA investigates, Polars transforms, sklearn learns.** Keep the three roles separate.
3. **Define validation before fitting learned preprocessing.**
4. **Not every request needs training.** ETL, statistics, graph algorithms, and
   inference on an existing model can be delivered directly.
5. **Logging, statistics, and explanation are three different things.**
6. **Missing expert ≠ install a new framework.** Use project code for the narrow
   case and add an expert only for a real, recurring gap.
7. **Every status claim needs a test.** An import is not a capability.
