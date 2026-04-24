# XSOAR High-Risk Overrides

These rules override generic Python cleanup and ambiguous public documentation
when working on Cortex XSOAR/Demisto content. Use them together with the
structured command and artifact references, not as a replacement for lookup.

## Lookup Order

1. Classify the artifact with `references/structures/index.json`.
2. Read the relevant structure reference.
3. Search `references/commands/**/*.json` for every XSOAR command/API before
   using or changing it.
4. Apply these overrides if they conflict with generic Python advice.
5. Apply private overlay rules from `references/local/` only when those files
   exist locally.

## XSOAR Lists

Do not assume every tenant exposes helper methods such as `demisto.getList(...)`
in automation runtime. When uncertainty exists, prefer explicit command lookup
and tenant verification before changing list access.

Common direct command shape:

```python
demisto.executeCommand("getList", {"listName": list_name})
```

For list writes, make missing-list behavior explicit and handle empty or
malformed content safely. Treat missing lists, "item not found" responses, empty
list content, and malformed JSON as recoverable states.

## Debug Output For Draft Automations

For manually tested automations, log concrete command inputs that affect result
shape, such as query, date window, pagination, list name, and dry-run state.
Also log pagination stop reasons, malformed response handling, and summary
counts.

## Faithful Forks Before Redesign

When a user asks for a derived XSOAR automation, treat the working reference
automation as the behavioral contract before redesigning helpers or fallback
logic.

Preserve helper defaults, `demisto.executeCommand(...)` envelopes, fallback
flow, output semantics, and integration routing unless the user explicitly asks
for different behavior.

Before changing logic in a broken draft automation, compare the working and
draft command envelopes first. Check the exact command names and the concrete
args sent to XSOAR, not only the surrounding Python logic.

If a draft automation is meant to be a live fork of an existing one, a
faithful fork is the default. A behavioral redesign is a separate decision, not
an implicit cleanup step.

## Incident Search Date Windows

For direct incident search command calls, prefer concrete ISO UTC timestamps.
Compute relative windows in Python first.

```python
demisto.executeCommand("getIncidents", {
    "query": query,
    "fromdate": from_date_iso,
    "todate": to_date_iso,
    "size": page_size,
    "page": page,
})
```

Do not pass relative values such as `now`, `24 hours ago`, or `6 months ago`
directly to native commands unless the target runtime has been verified to
accept them.

Do not blindly rename script argument names. A script may expose arguments named
`fromDate` and `toDate` while converting them internally before calling a native
command with lowercase keys.

## XSOAR Runtime Imports

Packaged content commonly imports XSOAR runtime modules:

```python
import demistomock as demisto
from CommonServerPython import *
```

Do not remove those imports just because local Python reports
`No module named 'demistomock'`. For packaged content, they are part of the
XSOAR content-development pattern. If local unit tests need to import a module,
add or use local test stubs rather than deleting valid XSOAR imports.

## Embedded Exported Automations

Single-file exported automations can contain wrapper lines before the script
body:

```python
register_module_line('<AutomationName>', 'start', __line__())
CONSTANT_PACK_VERSION = '<version>'
demisto.debug('pack id = <PackName>, pack version = <version>')
```

Preserve wrapper lines when present. Do not add `from __future__` imports above
them. Do not convert embedded YAML automations into package-shaped metadata
unless the task explicitly asks for a package conversion.

## Deprecation And Field Deletion

Treat deprecation reports as audit input, not an automatic deletion plan. Before
removing incident fields, search for canonical field names across active
layouts, automations, playbooks, and mappers. Dynamic writes can be the only
live reference to a field.

## Documentation Lookup Rule

Before using an unfamiliar command/API or changing argument casing, search the
split JSON catalog:

```powershell
$skillRoot = '<path-to-xsoar-development-skill>'
rg -n -i '"name": "command-name"|"argument-name"' "$skillRoot\references\commands"
```

If the catalog has no match, use official online docs or verified tenant
evidence before guessing. Tenant-specific commands may not exist in public
documentation.
