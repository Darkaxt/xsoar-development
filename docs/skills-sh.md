# Publishing and installing from skills.sh

`xsoar-development` is published for skills.sh as a single GitHub-hosted Agent Skill. There is no separate registry submission step: users install from the public repository with the `skills` CLI, and skills.sh can discover the package through install telemetry.

## Install

List the skill:

```powershell
npx skills add Darkaxt/xsoar-development --list
```

Install the skill:

```powershell
npx skills add Darkaxt/xsoar-development --skill xsoar-development
```

Update installed skills:

```powershell
npx skills update
```

## Compatibility

This skill is public Cortex XSOAR / Demisto content-development guidance. It is useful for agents that support Agent Skills and can read local reference files on demand.

The skill does not require XSOAR credentials by itself. It guides edits to scripts, automations, playbooks, dashboards, content packs, exported YAML, `demisto.executeCommand` usage, native command syntax, XSOAR runtime imports, and package structure.

## Public and private content

This repository includes public-safe references derived from upstream Cortex XSOAR documentation and synthetic artifact-structure examples. Private team rules, local workflow notes, generated exports, credentials, and organization-specific examples must stay out of Git.

Keep private overlays under:

```text
references/local/
```

That directory is ignored except for `.gitkeep`. If a team needs private workflow rules, the agent should read the public skill first, then any local overlay present on that machine.

## Safety notes

- Preserve XSOAR artifact shape before applying generic Python cleanup.
- Look up command and API contracts in `references/commands/**/*.json` before changing command calls.
- Do not remove XSOAR runtime imports such as `demistomock` or `CommonServerPython` just because local Python cannot import them.
- Do not commit generated exports, ready-package outputs, review reports, credentials, or private overlays.
- Command and documentation records include upstream source references. Check upstream documentation and terms before redistributing vendor material beyond this metadata.

## Maintainer validation

Before advertising a release, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate_skills_sh.ps1
```

The validator checks root skill metadata, skills CLI discovery from GitHub and the local checkout, and targeted public-hygiene paths. It intentionally does not scan the full generated `references/commands/**` catalog on every run.
