# XSOAR File Structures

This reference is built from synthetic examples and public XSOAR conventions.
Use it as a starting point before editing XSOAR artifacts.

## How To Use

1. Classify the file by path and top-level fields.
2. Open the matching JSON file under `references/structures/`.
3. Preserve observed defaults and wrapper behavior unless the task explicitly
   changes package shape.
4. Read private overlay files under `references/local/` only when they exist.

## Packaged Script Metadata

Common package shape:

```text
<PackName>/
  Scripts/
    <ScriptName>/
      <ScriptName>.py
      <ScriptName>.yml
      README.md
```

Do:

- Keep Python code in the sibling `.py` file when using package-shaped content.
- Preserve `type`, `subtype`, `dockerimage`, `enabled`, `runas`, `runonce`,
  `args`, `outputs`, and `tests` fields when present.

Do not:

- Do not inline code into `script` unless producing an exported/draft automation.

## Exported Or Draft Automation

Exported or draft automations may be single YAML files:

```yaml
commonfields:
  id: ExampleAutomation
name: ExampleAutomation
script: |-
  register_module_line('ExampleAutomation', 'start', __line__())
  CONSTANT_PACK_VERSION = '1.0.0'
  demisto.debug('pack id = ExamplePack, pack version = 1.0.0')
  """
  Example module docstring.
  """
type: python
subtype: python3
```

Do:

- Preserve embedded script indentation and XSOAR wrapper lines.
- Keep guarded main patterns when present.

Do not:

- Do not add `from __future__` imports or generic CLI/file-system entrypoints.

## Python Runtime Script

Do:

- Preserve expected `demistomock` and `CommonServerPython` imports for packaged
  content.
- Use XSOAR guard patterns for code that must also execute as embedded YAML.

Do not:

- Do not treat missing local XSOAR runtime modules as proof that imports should
  be deleted.

## Playbook YAML

Do:

- Preserve task IDs, task UUIDs, `nexttasks`, `scriptarguments`, conditions,
  view coordinates, quiet settings, inputs, and outputs.

Do not:

- Do not regenerate task IDs unless deliberately rebuilding the playbook.

## Other Artifact Types

Incident fields, incident types, lists, layouts, dashboards, classifiers,
mappers, and pack metadata each have their own key conventions. Load the
matching JSON reference before editing keys or removing fields.
