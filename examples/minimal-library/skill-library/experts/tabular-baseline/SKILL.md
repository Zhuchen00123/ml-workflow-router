---
name: tabular-baseline
description: "Builds a first honest tabular baseline: a declared split, preprocessing fitted inside training folds, one cross-validated score, one holdout score, and a saved pipeline. Use when a tabular dataset needs a trustworthy reference result; not for deep architectures or hyperparameter research."
metadata:
  version: "0.1.0"
  scope: "example expert for ml-workflow-router"
---

# Tabular baseline

## What this is for

Produce the number that every later model must beat, with a split you can defend
and a pipeline you can reproduce.

## Preconditions

- A triage exists (see `data-quality-triage`) naming the split unit and the
  trivial baseline.
- The target column and the metric are agreed. If the metric is unstated, propose
  one and say why, based on class balance and the cost of each error type.

## Steps

1. **Split first.** Use the unit from triage (group/time/stratified). Hold the
   final test set out before any model sees the data. Record the exact rule and
   seed.
2. **Pipeline.** Put imputation, scaling, encoding, and the estimator in one
   pipeline object, so preprocessing is fitted per fold. Never fit a scaler on the
   full dataset before splitting.
3. **Validate.** Cross-validate on training data only. Report mean and spread
   across folds, not a single lucky fold.
4. **Fit and score holdout once.** Compare against the trivial baseline. If the
   model does not beat it, say so plainly — that is a result.
5. **Save.** Persist the fitted pipeline plus the split definition and versions.
6. **Diagnose lightly.** Overall score, per-class or per-group score, and a short
   list of the top feature importances if the estimator has them.

## Output

- split rule, row counts per split, and the seed
- cross-validated score (mean ± spread) and holdout score
- trivial baseline for comparison
- path to the saved pipeline and the command to refit it
- one paragraph on what the result does not prove

## Checks before finishing

- Preprocessing was fitted inside folds: the code path shows it, not just the claim.
- Holdout was scored once. If you re-tuned after seeing it, label the score as
  contaminated.
- Metric direction and class balance are stated next to the number.
- Numbers come from the executed run, not from a previous session's memory.

## What it does not do

Does not tune extensively, does not select features for you, does not claim
causality, and does not establish that the score generalises to a different
population or time period. Does not replace the triage's leakage judgement.
