---
name: xsoar-development
description: Use when working with Cortex XSOAR or Demisto content, including scripts, automations, playbooks, dashboards, content packs, exported YAML, pack metadata, demisto.executeCommand calls, native command syntax, CommonServerPython, demistomock, incident fields, layouts, and XSOAR package structure. This skill prevents generic Python fixes that break XSOAR runtime and packaging behavior.
---

# XSOAR Development

## First Principle

Treat Cortex XSOAR runtime, packaging, and export semantics as the source of
truth. Generic Python cleanup is allowed only after checking whether the pattern
is required by XSOAR, the content pack format, or a private team overlay.

## Mandatory Workflow

1. Classify the artifact before changing it.
   - Start with `references/structures/index.json`.
   - Read `references/xsoar-file-structures.md` for the concise human summary.
   - Load the exact structure JSON that matches the artifact, for example
     `packaged-script-yml.json`, `exported-automation-yml.json`,
     `python-runtime-script.json`, `playbook-yml.json`,
     `incident-field-json.json`, `list-json.json`, `layout-json.json`, or
     `dashboard-json.json`.
2. Before using, adding, or changing any XSOAR command/API call, search
   `references/commands/**/*.json` and then read the matching JSON file. Do not
   load the whole catalog into context.

   ```powershell
   $skillRoot = '<path-to-xsoar-development-skill>'
   rg -n -i '"name": "getIncidents"|"fromdate"|"todate"' "$skillRoot\references\commands"
   rg -n -i '"name": "return_results"|"CommandResults"' "$skillRoot\references\commands"
   rg -n -i 'executeCommand|command-name|argument-name' "$skillRoot\references\commands"
   ```

   If `rg` is unavailable, use:

   ```powershell
   Get-ChildItem "$skillRoot\references\commands" -Recurse -Filter *.json |
     Select-String -Pattern 'getIncidents|fromdate|todate'
   ```
3. Apply high-risk override rules before generic Python advice.
   - Always read `references/high-risk-overrides.md` before editing command
     calls, wrapper metadata, list access, runtime imports, or date filtering.
   - If a private overlay exists under `references/local/`, read it after the
     public references and before making team-specific changes.
4. Preserve the artifact shape you classified.
   - Packaged scripts usually use `Scripts/<Name>/<Name>.py`,
     `Scripts/<Name>/<Name>.yml`, and `README.md`; the metadata file commonly
     has `script: ''`.
   - Exported or draft automations are usually one YAML file with embedded
     `script: |-` and wrapper/runtime prologue lines such as
     `register_module_line(...)`, `CONSTANT_PACK_VERSION`, and
     `demisto.debug('pack id = ...')`.
   - Playbooks, incident fields, incident types, lists, layouts, classifiers,
     mappers, dashboards, and pack metadata have their own key conventions.
     Load the matching structure JSON before editing keys.
5. Verify narrowly with the local tool that matches the changed artifact. If a
   repository defines its own packaging or review workflow, follow the private
   overlay or repository documentation.

## Non-Negotiable Guardrails

- Do not remove expected XSOAR imports such as `demistomock` or
  `CommonServerPython` from packaged `.py` files just because normal local
  Python cannot import them.
- Do not add `from __future__` imports to automation code that may be wrapped
  or embedded into exported YAML.
- Preserve exported automation prologues inside `script: |-`, including
  `register_module_line('<Name>', 'start', __line__())`,
  `CONSTANT_PACK_VERSION = '<version>'`, pack/version `demisto.debug(...)`,
  and the module docstring that follows.
- For direct `demisto.executeCommand("getIncidents", args)` calls, prefer
  concrete ISO UTC timestamps for date windows. Avoid passing relative strings
  such as `now`, `24 hours ago`, or `6 months ago` directly to native commands.
- Distinguish script-facing argument names such as `fromDate` and `toDate` from
  native direct command argument keys such as `fromdate` and `todate`.
- Do not add generic standalone Python scaffolding, CLI entrypoints,
  filesystem assumptions, shebangs, duplicate headers, or logging rewrites to
  XSOAR automations unless the artifact is explicitly a local helper script.

## Reference Map

- `references/commands/index.json`: compact index of public command/API
  records, aliases, kinds, source URLs, and file paths.
- `references/commands/<kind>/<name>.json`: one search-friendly JSON record per
  public command/API record. Load only the specific matching file.
- `references/docs/*.json`: public prose support docs such as pack format,
  integration conventions, and context/output guidance.
- `references/structures/index.json`: artifact classifier index and paths to
  synthetic file-structure references.
- `references/xsoar-file-structures.md`: concise guide to required, default,
  optional, wrapper, and path conventions.
- `references/high-risk-overrides.md`: mandatory rules for known XSOAR failure
  modes.
- `references/local/`: optional private overlay location. These files are
  intentionally ignored by Git.

## Safety Gate

Before publishing or sharing the skill, run:

```powershell
python .\scripts\audit_public_safety.py --root . --fail-on-high
```
