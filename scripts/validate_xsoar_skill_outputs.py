"""Validate generated public XSOAR skill reference indexes."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    command_index_path = root / "references" / "commands" / "index.json"
    if not command_index_path.exists():
        errors.append("missing references/commands/index.json")
    else:
        command_index = json.loads(command_index_path.read_text(encoding="utf-8"))
        for command in command_index.get("commands", []):
            path = command.get("path")
            if not path:
                errors.append("command index entry missing path")
                continue
            if str(command.get("source_url", "")).startswith("local:"):
                errors.append(f"local source URL in command index: {path}")
            if not (root / "references" / "commands" / path).exists():
                errors.append(f"missing command reference: {path}")

    structure_index_path = root / "references" / "structures" / "index.json"
    if not structure_index_path.exists():
        errors.append("missing references/structures/index.json")
    else:
        structure_index = json.loads(structure_index_path.read_text(encoding="utf-8"))
        for item in structure_index.get("artifact_types", []):
            path = item.get("path")
            if not path:
                errors.append("structure index entry missing path")
                continue
            if not (root / "references" / "structures" / path).exists():
                errors.append(f"missing structure reference: {path}")

    return errors


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0] if argv else ".").resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("XSOAR skill references are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
