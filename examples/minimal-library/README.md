# Example expert library

A three-expert library you can check, route through, and copy. Self-contained and
written for this repo — it contains no third-party skill content.

```text
examples/minimal-library/
├── config.json                     relative paths, resolves from this directory
├── environment/
│   ├── runtime-status.json         capability states (all unverified, by design)
│   └── task-routing.json           task → expert routes
└── skill-library/experts/
    ├── data-quality-triage/        audit before modelling
    ├── tabular-baseline/           first defensible baseline
    └── figure-export/              reproducible result figure
```

## Try it in one command

From the repository root:

```bash
python scripts/check.py --config examples/minimal-library/config.json
```

Expected: config resolves, 3 experts found, 3 routing references all present, and
`gpu_training` listed as a known blocker. Exit code 0.

Two things worth noticing:

1. `interpreters.core` is empty and the checker reports it as unset rather than
   substituting a PATH `python`. That is the behaviour you want on a machine with
   several environments.
2. The status file marks everything `unverified` and records one `blocked`
   capability. Nothing in this example claims a capability works.

Add `--json` for machine-readable output, or `--probe` after filling in a real
interpreter path to have it print the interpreter's version.

## How these experts demonstrate the contract

| Contract element | Where to see it |
|---|---|
| Frontmatter `name` must equal the directory name | checked by `scripts/check.py` |
| `LOCAL-NOTES.md` is read before `SKILL.md` | each expert has one |
| Experts state what they do **not** do | last section of every `SKILL.md` |
| Checks require executed evidence, not narrative | "Checks before finishing" |
| Failure is recorded, not deleted | `runtime-status.json` → `known_blockers` |

## Point a router install at this library

Copy `skills/ml-workflow-router/` into a discovery root, then either copy this
`config.json` next to its `SKILL.md` or set:

```bash
export ML_WORKFLOW_CONFIG=/absolute/path/to/examples/minimal-library/config.json
```

The router will then route only among these three experts. When you want the
larger routing table, build your own library using the names in
[`references/routing.md`](../../skills/ml-workflow-router/references/routing.md).

## Copying it as a starting point

```bash
cp -r examples/minimal-library ~/my-ml-project
```

Then edit `config.json` (absolute paths are fine there), add experts under
`skill-library/experts/`, and grow `task-routing.json`. Keep the habit of
recording what failed: a blocker entry is cheaper than rediscovering the same dead
end.
