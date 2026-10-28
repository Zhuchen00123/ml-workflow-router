#!/usr/bin/env python3
"""Static check for a ml-workflow-router configuration.

Validates that the router's config resolves, that interpreters exist, that every
expert directory has a parseable SKILL.md, and that the status/routing files agree
with the library on disk.

Runs nothing from any expert. With --probe it executes each interpreter with a
single `-c` version print (no network, no imports of project code).

Usage:
    python scripts/check.py [--config PATH] [--probe] [--json] [--quiet]

Exit codes: 0 = no problems, 1 = problems found, 2 = config could not be located.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REQUIRED_KEYS = ("schema_version", "project_root", "expert_library",
                 "status_file", "routing_file", "interpreters")
PLACEHOLDER_MARKS = ("<", ">")


def find_config(explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_file() else None
    env = os.environ.get("ML_WORKFLOW_CONFIG")
    if env:
        p = Path(env).expanduser()
        if p.is_file():
            return p
    here = Path(__file__).resolve().parent
    for candidate in (Path.cwd() / "config.json",
                      here.parent / "config.json",
                      here.parent / "skills" / "ml-workflow-router" / "config.json"):
        if candidate.is_file():
            return candidate
    return None


def read_frontmatter(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fields: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def resolve(value: str, base: Path) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else (base / p)


def looks_like_placeholder(value: str) -> bool:
    return all(mark in value for mark in PLACEHOLDER_MARKS)


def check(config_path: Path, probe: bool) -> tuple[dict, list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []
    base = config_path.parent
    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"config is not readable JSON: {exc}"], warnings

    for key in REQUIRED_KEYS:
        if key not in cfg:
            problems.append(f"config missing required key: {key}")
    if problems:
        return cfg, problems, warnings

    for key in ("project_root", "expert_library", "status_file", "routing_file"):
        value = cfg.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"config field {key} is empty")
        elif looks_like_placeholder(value):
            problems.append(f'{key} still contains a placeholder: {value}')
    interpreters = cfg.get("interpreters") or {}
    if not isinstance(interpreters, dict):
        problems.append("interpreters must be an object")
        interpreters = {}
    for name, value in interpreters.items():
        if not isinstance(value, str):
            problems.append(f"interpreter {name} is not a string")
        elif value.strip() and looks_like_placeholder(value):
            problems.append(f"interpreter {name} still contains a placeholder")

    report: dict = {"config": str(config_path), "project_root": None,
                    "interpreters": {}, "experts": {}, "status": {},
                    "routing": {}}

    if cfg.get("project_root") and not looks_like_placeholder(cfg["project_root"]):
        report["project_root"] = str(resolve(cfg["project_root"], base))

    for name, value in interpreters.items():
        if not isinstance(value, str) or not value.strip() or looks_like_placeholder(value):
            continue
        exe = resolve(value, base)
        entry = {"path": str(exe), "exists": exe.is_file()}
        if not entry["exists"]:
            warnings.append(f"interpreter {name} not found at {exe} (reported unavailable, not guessed)")
        elif probe:
            try:
                out = subprocess.run([str(exe), "-c", "import sys;print(sys.version.split()[0])"],
                                     capture_output=True, text=True, timeout=30)
                entry["probe"] = (out.stdout.strip() or out.stderr.strip()[:200]) or f"exit {out.returncode}"
                entry["probe_ok"] = out.returncode == 0
            except (OSError, subprocess.SubprocessError) as exc:
                entry["probe"] = f"failed: {exc}"
                entry["probe_ok"] = False
        report["interpreters"][name] = entry

    library = resolve(cfg["expert_library"], base) if isinstance(cfg["expert_library"], str) else None
    present: dict[str, dict] = {}
    if library is None or not library.is_dir():
        problems.append(f"expert_library not found: {library}")
    else:
        for folder in sorted(p for p in library.iterdir() if p.is_dir()):
            skill = folder / "SKILL.md"
            if not skill.is_file():
                warnings.append(f"expert {folder.name} has no SKILL.md (not loadable)")
                present[folder.name] = {"skill_md": False}
                continue
            front = read_frontmatter(skill)
            if front is None:
                problems.append(f"expert {folder.name}: SKILL.md frontmatter is missing or unparseable")
                present[folder.name] = {"skill_md": True, "frontmatter": False}
                continue
            name_field = front.get("name", "")
            if name_field != folder.name:
                problems.append(f"expert {folder.name}: frontmatter name is {name_field!r}, expected the directory name")
            present[folder.name] = {
                "skill_md": True,
                "frontmatter": True,
                "name_matches_dir": name_field == folder.name,
                "has_local_notes": (folder / "LOCAL-NOTES.md").is_file(),
                "has_references": (folder / "references").is_dir(),
            }
        report["experts"] = {"library": str(library), "count": len(present), "detail": present}
        if not present:
            problems.append(f"expert_library has no expert directories: {library}")

    routing_path = resolve(cfg["routing_file"], base) if isinstance(cfg["routing_file"], str) else None
    if routing_path and routing_path.is_file():
        try:
            routing = json.loads(routing_path.read_text(encoding="utf-8"))
            referenced = set()
            for route in routing.get("routes", []) or []:
                for key in ("primary", "helpers"):
                    for item in route.get(key) or []:
                        if isinstance(item, str):
                            referenced.add(item)
            missing = sorted(referenced - set(present))
            unreferenced = sorted(set(present) - referenced)
            report["routing"] = {"file": str(routing_path), "referenced": len(referenced),
                                 "missing_experts": missing, "unreferenced_experts": unreferenced}
            for item in missing:
                problems.append(f"routing references a missing expert: {item}")
            for item in unreferenced:
                warnings.append(f"expert {item} exists but no route references it")
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"routing_file is not readable JSON: {exc}")
    else:
        warnings.append(f"routing_file not found: {routing_path}")

    status_path = resolve(cfg["status_file"], base) if isinstance(cfg["status_file"], str) else None
    if status_path and status_path.is_file():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            caps = status.get("capabilities") or {}
            tally: dict[str, int] = {}
            for value in caps.values():
                key = value if isinstance(value, str) else "unknown"
                tally[key] = tally.get(key, 0) + 1
            blockers = status.get("known_blockers") or {}
            report["status"] = {"file": str(status_path), "capabilities": len(caps),
                                "tally": tally, "blockers": sorted(blockers)}
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"status_file is not readable JSON: {exc}")
    else:
        warnings.append(f"status_file not found: {status_path} (router cannot check capability state)")

    return report, problems, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a ml-workflow-router config.")
    ap.add_argument("--config", help="path to config.json")
    ap.add_argument("--probe", action="store_true", help="run each interpreter once for its version")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--quiet", action="store_true", help="only print problems")
    args = ap.parse_args()

    config_path = find_config(args.config)
    if config_path is None:
        print("No config found. Pass --config, set ML_WORKFLOW_CONFIG, or create config.json "
              "from config.example.json.", file=sys.stderr)
        return 2

    report, problems, warnings = check(config_path, args.probe)
    ok = not problems

    if args.json:
        print(json.dumps({"ok": ok, "problems": problems, "warnings": warnings, "report": report},
                         ensure_ascii=False, indent=2))
        return 0 if ok else 1

    if not args.quiet:
        print(f"config: {config_path}")
        if report.get("project_root"):
            print(f"project_root: {report['project_root']}")
        for name, entry in (report.get("interpreters") or {}).items():
            state = "ok" if entry.get("exists") else "MISSING"
            extra = f" | probe: {entry['probe']}" if "probe" in entry else ""
            print(f"  interpreter {name}: {state}{extra}")
        experts = report.get("experts") or {}
        if experts:
            print(f"experts: {experts.get('count', 0)} in {experts.get('library')}")
            notes = sum(1 for v in experts.get("detail", {}).values() if v.get("has_local_notes"))
            print(f"  with LOCAL-NOTES.md: {notes}")
        routing = report.get("routing") or {}
        if routing:
            print(f"routing: {routing.get('referenced', 0)} expert names referenced, "
                  f"{len(routing.get('missing_experts') or [])} missing")
        status = report.get("status") or {}
        if status:
            tally = ", ".join(f"{k}={v}" for k, v in sorted(status.get("tally", {}).items()))
            print(f"capabilities: {status.get('capabilities', 0)} ({tally or 'none'})")
            if status.get("blockers"):
                print(f"known blockers: {', '.join(status['blockers'])}")

    if warnings and not args.quiet:
        print(f"\n{len(warnings)} warning(s):")
        for item in warnings:
            print(f"  - {item}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for item in problems:
            print(f"  - {item}")
        return 1
    if not args.quiet:
        print("\nOK: config resolves and the library is internally consistent.")
        print("Note: consistency is not capability. Only tests can mark something verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
