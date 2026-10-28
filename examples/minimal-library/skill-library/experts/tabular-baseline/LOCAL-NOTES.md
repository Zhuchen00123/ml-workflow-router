# Local notes — tabular-baseline

- Example expert. Prefer the project's existing dataframe and estimator libraries;
  do not install anything to satisfy this file.
- The router points at more capable experts for deep learning, time series, and
  gradient boosting. This one stays deliberately small: a defensible baseline.
- One trainer per experiment. If a neural model is also wanted, run it as a
  separate experiment against this baseline, not nested inside it.
- Never write to the raw data. Artifacts go under a project output directory.
- If the interpreter or a required library is missing, report the gap. Do not
  fall back to a different interpreter silently.
