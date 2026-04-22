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

## Optional Private Overlay

If your team has private rules, keep them outside Git under `references/local/`.
The public skill documents the overlay convention, but `.gitignore` prevents
those files from being committed.

Suggested local-only overlay files:

- `references/local/private-workflow.md`
- `references/local/private-command-overrides.json`
- `references/local/private-structure-examples/`

## Publication Hygiene

Before sharing changes, review the repository for private team overlays, local
paths, credentials, generated exports, and organization-specific examples. Keep
private rules under `references/local/`, which is ignored by Git.
