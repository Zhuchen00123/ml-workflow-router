# Local notes — data-quality-triage

- This is an example expert shipped with the router. It contains no upstream code.
- No package requirements: the triage can be done with whatever dataframe tool the
  project already uses. If nothing is installed, report that instead of installing.
- Read-only on the user's data. Any intermediate file goes to a new path.
- The leakage screen is a set of questions, not a verdict. Domain knowledge decides.
- If the table is too large to load, say so and propose a sampling or streaming
  read; do not silently truncate and present the truncated result as complete.
