# Design notes

Deliberate trade-offs behind a single-entry router. Written to be falsifiable, not
to sell the approach.

## Problem

An agent with N ML expert skills faces a selection problem on every turn, pays
context for all N descriptions, and tends to route by surface keywords. Adding
more experts makes selection worse, not better, past a point.

## Decision

One always-on entry. Experts are ordinary directories read on demand.

Consequences, accepted:

| Consequence | Why accepted |
|---|---|
| Experts are not callable slash commands | Selection cost and context cost drop a lot; the loss is discoverability |
| The router must know where experts live | A small config file is cheaper than N registrations |
| A missing expert fails at read time, not at call time | Failure is explicit and names the file |
| Router drift can mis-route | The routing table is a small, reviewable artifact |

## What was rejected

- **Register all experts globally.** Rejected: reintroduces the N-description
  problem and invites keyword routing.
- **One mega-skill containing all expert content.** Rejected: unmaintainable,
  unbounded context, and it silently takes ownership of upstream content and
  licences.
- **Auto-choosing by embedding similarity over task text.** Rejected for now:
  cheap to add, but it hides the decision and gives no place to record
  prerequisites or environment splits.

## Non-obvious invariants

1. **Status is data, not prose.** A machine-readable status file makes "did you
   actually run this?" answerable, and makes lying about capability harder.
2. **Interpreter paths are explicit.** PATH `python` on a multi-environment
   machine is a coin flip; an absolute interpreter is reproducible.
3. **Failures stay in the record.** A failed capability (`blocked`) is more useful
   than a deleted one, because it stops the next attempt from repeating the same
   dead end.
4. **Numbers from third parties are claims.** Benchmark tables and VRAM formulas
   copied between skills drift into contradictions; the router requires
   measurement instead.

## Known weaknesses

- Routing quality depends on the routing table being maintained.
- The router cannot verify that an expert's advice is *correct*, only that it was
  read and bounded.
- Environment splitting multiplies setup cost; it is only worth it when
  dependency graphs genuinely conflict.
- Preview: no installer, no schema migration story yet.

## Roadmap (not promises)

- [ ] Machine-checkable routing table schema.
- [ ] `--check` mode that validates config paths and prints capability status.
- [ ] Optional probe that reports which experts are stale versus upstream.
- [ ] Worked example library layout (structure only, no third-party content).
