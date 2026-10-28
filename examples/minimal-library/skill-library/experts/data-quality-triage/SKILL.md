---
name: data-quality-triage
description: "Triages an unfamiliar tabular dataset before any modelling: column types, missingness, duplicate keys, constant and leakage-prone columns, and the correct split unit. Use at the start of a tabular task; not for cleaning, feature engineering, or model selection."
metadata:
  version: "0.1.0"
  scope: "example expert for ml-workflow-router"
---

# Data quality triage

## What this is for

Answer "can I trust this table enough to model it?" quickly, and write down what
you found. It produces a short triage, not a cleaned dataset.

## Inputs

- The data path, and whether it may be read (do not assume write access).
- The intended prediction target and the unit one row represents.
- Known grouping or time structure, if the user has it.

## Steps

1. **Shape and keys.** Row count, column count, candidate primary key. Test key
   uniqueness. Report duplicates; do not drop them yet.
2. **Types.** Per column: declared type, inferred type, count of unparseable
   values. Flag numbers stored as text and dates in mixed formats.
3. **Missingness.** Per column: count and share. Distinguish empty string from
   null from a sentinel like `-1` or `"N/A"`. Report whether missingness is
   plausibly related to the target — that changes what imputation means.
4. **Degenerate columns.** Constant columns, all-unique identifiers, columns with
   one dominant value.
5. **Leakage screen.** Any column that could only be known after the target event
   (post-outcome measurements, IDs that encode the label, aggregate over the whole
   dataset including test rows). Name the suspicion explicitly; do not silently
   delete the column.
6. **Split unit.** State the unit that must not be split across train and test:
   row, patient, session, device, location, or time. Where a group/time column
   exists, use it.
7. **Target sanity.** Class balance or target distribution, plus the trivial
   baseline (majority class / mean) that any model must beat.

## Output

A triage block the user can paste into a report:

- rows, columns, key uniqueness, duplicate count
- missingness table (top offenders only)
- columns flagged: constant, identifier, leakage-suspect
- the split unit and why
- trivial baseline value
- open questions that only the user can answer

## Checks before finishing

- Every claim above is computed, not assumed from column names.
- No data was modified. If a file was written, it is a new path.
- Any leakage suspicion is stated as a question for the user, not as a deletion.

## What it does not do

Does not impute, scale, encode, deduplicate, or train. Does not certify that the
label is correct or that the dataset is licensed for the intended use. Does not
substitute for domain review.
