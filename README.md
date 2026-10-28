# ml-workflow-router

A single routing skill for machine-learning work. It decides **which expert
instructions to load, in what order, and what counts as done** — instead of
registering dozens of experts into the agent's skill catalogue.

> **Status: preview (v0.1.1-preview).** The routing design, safety contract, and
> config format are settled; the packaging still moves. No expert content is
> bundled — see [NOTICE.md](NOTICE.md).

## Why one entry instead of N experts

Registering 24 expert skills puts 24 descriptions in front of the model on every
turn and makes "which one applies" a constant background decision. Registering
only the router keeps a single always-on entry and pays for expert instructions
only when a step actually needs them.

The cost is explicit and worth stating: **the experts are not callable skills.**
The router reads their files. If you want `/polars` to work as a slash command,
this design is not what you want.

## What it actually enforces

Most of the value is in the non-negotiables, not the routing table:

- Split by the real observational unit **before** touching features; fit learned
  preprocessing inside training folds only.
- One experiment, **one** primary trainer. No framework nesting.
- `torch.cuda.is_available()` is not evidence; require a real kernel, backward, sync.
- Package imports are not capabilities; a status file records what was executed.
- Untrusted data (cells, retrieved text, metadata) never authorizes new tool calls.
- No automatic downloads, logins, uploads, cloud credentials, third-party model
  mirrors, unpinned builds, or unexplained listening on `0.0.0.0`.
- Third-party benchmark/VRAM/venue numbers are claims, not measurements.

## Quick start

```bash
git clone https://github.com/Zhuchen00123/ml-workflow-router
cd ml-workflow-router

# Validate the bundled example library (no install, no network)
python scripts/check.py --config examples/minimal-library/config.json
```

Expected: 3 experts found, 3 routing references resolved, `gpu_training` shown as a
known blocker, exit code 0.

Then install the skill and point it at your own library:

1. Copy `skills/ml-workflow-router/` into a discovery root, e.g.
   `~/.dsh/skills/ml-workflow-router/` (global) or
   `<project>/.agents/skills/ml-workflow-router/` (project only).
2. Copy `config.example.json` to `config.json` beside `SKILL.md` — or set
   `ML_WORKFLOW_CONFIG` to your own path — and replace every `<...>` placeholder.
3. Provide an expert library matching the directory names in
   [`references/routing.md`](skills/ml-workflow-router/references/routing.md).
   Each expert directory needs a `SKILL.md`; `LOCAL-NOTES.md` is optional but read
   first when present.
4. Maintain a `runtime-status.json` and a `task-routing.json` so the router can
   check real capability state instead of assuming it. Both paths are config fields.
5. Run `python scripts/check.py` again against your config.

The router degrades honestly: unresolved paths are reported as gaps, never
silently replaced with a PATH `python`.

## The config checker

`scripts/check.py` validates a configuration **without** running anything from the
expert library:

| Check | Why it matters |
|---|---|
| Config parses; required keys present | Fails loudly instead of half-working |
| Unresolved `<...>` placeholders flagged | Catches the copy-template-and-forget case |
| Interpreter paths exist; empty means unavailable | No PATH fallback, ever |
| Every expert has parseable frontmatter with `name` == directory | Keeps routing names honest |
| Routing file references resolve to real experts | Catches renamed or deleted experts |
| Status file summarises capabilities and blockers | Makes "verified" auditable |

```bash
python scripts/check.py                       # find config automatically
python scripts/check.py --config path/to/config.json
python scripts/check.py --probe               # also print each interpreter's version
python scripts/check.py --json                # machine-readable
```

Exit codes: `0` clean, `1` problems, `2` config not found.

It reports consistency, not capability. A green run means the router will not
trip over missing files; it does not mean the libraries work.

## Example expert library

[`examples/minimal-library/`](examples/minimal-library/) is a complete, runnable
three-expert library — `data-quality-triage`, `tabular-baseline`, `figure-export`
— written for this repo, no third-party content:

```text
examples/minimal-library/
├── config.json                  relative paths, works right after cloning
├── environment/
│   ├── runtime-status.json      all unverified by design, plus one blocker
│   └── task-routing.json        task → expert routes
└── skill-library/experts/       three experts with SKILL.md + LOCAL-NOTES.md
```

It is meant to be copied as a project skeleton:

```bash
cp -r examples/minimal-library ~/my-ml-project
```

## Example config

```json
{
  "schema_version": 1,
  "project_root": "F:/work/ml",
  "expert_library": "F:/work/ml/skill-library/experts",
  "status_file": "F:/work/ml/environment/runtime-status.json",
  "routing_file": "F:/work/ml/environment/task-routing.json",
  "interpreters": {
    "core": "D:/Envs/ml-core/python.exe",
    "timeseries": "D:/Envs/ml-timeseries/python.exe",
    "data": "D:/Envs/ml-data/python.exe"
  }
}
```

Relative paths resolve against the config file's directory, so a repo-local
example works without editing.

Splitting interpreters is optional. It exists because some stacks genuinely
conflict — for example a time-series library pinning `numpy<2.5` against a main
environment on `numpy==2.5.3`. One environment with a silently downgraded
dependency is not a working configuration.

## Scope and non-goals

**Does:** route, sequence, enforce verification and safety defaults, choose an
interpreter, validate the wiring, and state limitations.

**Does not:** teach algorithms, bundle experts, install packages, download
models, run services, or guarantee any expert's upstream content is correct.

## Repository layout

```
skills/ml-workflow-router/
├── SKILL.md                    routing + workflow + safety + evidence rules
└── references/
    └── routing.md              task → expert table with authority boundaries
scripts/check.py                config/library validator (stdlib only)
examples/minimal-library/       runnable 3-expert example + its own config
config.example.json             template with placeholders
docs/design.md                  design notes and deliberate trade-offs
NOTICE.md                       third-party attribution (no content bundled)
```

## Verifying a claim about this skill

Nothing here asserts that any ML capability works on your machine. Status belongs
in your own `runtime-status.json`, backed by a test you ran. If this repo's text
and your test disagree, your test wins.

## Licence

MIT — see [LICENSE](LICENSE). Expert skills you point it at keep their own
licences; honour them.
