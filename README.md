# XSOAR Development Skill

Public-safe Codex skill for Cortex XSOAR / Demisto content development.

The skill focuses on XSOAR artifact shape, command lookup, runtime import
behavior, playbook and pack metadata conventions, and review guardrails that
prevent generic Python cleanup from breaking XSOAR content.

## What Is Included

- A generic `SKILL.md` for XSOAR scripts, automations, playbooks, dashboards,
  lists, layouts, incident fields, and content packs.
- Public command and script references derived from `xsoar.pan.dev`.
- Synthetic structure references that describe common artifact shapes without
  exposing any team-specific repository or playbook names.
- A safety audit script that blocks known private markers before publication.

## Optional Private Overlay

If your team has private rules, keep them outside Git under `references/local/`.
The public skill documents the overlay convention, but `.gitignore` prevents
those files from being committed.

Suggested local-only overlay files:

- `references/local/private-workflow.md`
- `references/local/private-command-overrides.json`
- `references/local/private-structure-examples/`

## Validation

Run the public safety gate before publishing or sharing:

```powershell
python .\scripts\audit_public_safety.py --root . --fail-on-high
```

For full review output:

```powershell
python .\scripts\audit_public_safety.py --root . --json
```

High-confidence findings must be fixed before sharing. Weak-signal findings
may be public documentation examples, but should still be reviewed.
