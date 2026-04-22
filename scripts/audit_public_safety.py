"""Audit the public XSOAR skill repo for private or in-house references.

The scanner intentionally reports pattern names, paths, and line numbers rather
than echoing matched content. That keeps review output safe enough to share.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


SKIP_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
}

SKIP_REL_PREFIXES = (
    "references/local/",
    "references\\local\\",
)

_PRIVATE_CODE = "M" + "DR"
_PRIVATE_PREFIX = _PRIVATE_CODE + "F_"
_PRIVATE_INTERACTIVE = _PRIVATE_CODE + "Interactive"
_PRIVATE_REPO = "XSoar-" + _PRIVATE_CODE
_DOT_CODEX = "." + "codex"
_DOT_AGENTS = "." + "agents"
_MIRROR_NAME = "Tres" + "orit"
_PACK_A = "S2Primary" + "AlertIngestion"
_PACK_B = "Playbook" + "Scheduler"
_WORKFLOW_FILE = "WORK" + r"FLOW\.md"
_PRIVATE_TOOL_A = "xsoar" + "_batch"
_PRIVATE_TOOL_B = "stage" + "-ready"
_PRIVATE_TOOL_C = "audit" + "-deprecated"
_LOCAL_SOURCE = "local:" + "xsoar-development"

HIGH_CONFIDENCE_PATTERNS = {
    "private_playbook_markers": re.compile(
        rf"\b{_PRIVATE_CODE}\b|{_PRIVATE_PREFIX}|{_PRIVATE_INTERACTIVE}|{_PRIVATE_REPO}",
        re.IGNORECASE,
    ),
    "personal_home_path": re.compile(r"C:[\\/]+Users[\\/]+darka", re.IGNORECASE),
    "codex_or_agent_home": re.compile(rf"{re.escape(_DOT_CODEX)}|{re.escape(_DOT_AGENTS)}", re.IGNORECASE),
    "local_trash_repo_path": re.compile(r"D:[\\/]+Downloads[\\/]+Trash", re.IGNORECASE),
    "local_mirror_path": re.compile(r"T:[\\/]+Desarrollo", re.IGNORECASE),
    "private_mirror_name": re.compile(_MIRROR_NAME, re.IGNORECASE),
    "internal_pack_names": re.compile(rf"{_PACK_A}|{_PACK_B}", re.IGNORECASE),
    "local_workflow_files": re.compile(
        rf"(?<!-){_WORKFLOW_FILE}|{_PRIVATE_TOOL_A}|{_PRIVATE_TOOL_B}|{_PRIVATE_TOOL_C}",
        re.IGNORECASE,
    ),
    "local_source_url": re.compile(rf"source_url[\"']?\s*:\s*[\"']{re.escape(_LOCAL_SOURCE)}", re.IGNORECASE),
}

WEAK_SIGNAL_PATTERNS = {
    "email_address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "private_looking_host": re.compile(
        r"\b(?:[a-z0-9-]+\.)+(?:local|lan|corp|internal|intranet|onmicrosoft\.com)\b",
        re.IGNORECASE,
    ),
    "credential_terms": re.compile(
        r"password|passwd|secret|token|apikey|api_key|credential|client_secret|private_key|bearer",
        re.IGNORECASE,
    ),
    "workflow_context_terms": re.compile(
        r"tenant|client|customer|production|scheduler|fallback|unified notification",
        re.IGNORECASE,
    ),
    "windows_absolute_path": re.compile(r"\b[A-Z]:[\\/][^\s\"'<>`]+", re.IGNORECASE),
}


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        rel_text = str(rel)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if rel_text.startswith(SKIP_REL_PREFIXES):
            continue
        yield path


def scan_patterns(root: Path, patterns: dict[str, re.Pattern[str]]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in iter_files(root):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        for line_no, line in enumerate(lines, start=1):
            for name, pattern in patterns.items():
                count = len(pattern.findall(line))
                if count:
                    findings.append(
                        {
                            "file": rel,
                            "line": line_no,
                            "pattern": name,
                            "count": count,
                        }
                    )
    return findings


def summarize(findings: list[dict[str, object]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for finding in findings:
        pattern = str(finding["pattern"])
        summary[pattern] = summary.get(pattern, 0) + int(finding["count"])
    return dict(sorted(summary.items()))


def scan_root(root: Path) -> dict[str, object]:
    high = scan_patterns(root, HIGH_CONFIDENCE_PATTERNS)
    weak = scan_patterns(root, WEAK_SIGNAL_PATTERNS)
    return {
        "root": str(root),
        "high_confidence_count": len(high),
        "weak_signal_count": len(weak),
        "high_confidence_summary": summarize(high),
        "weak_signal_summary": summarize(weak),
        "high_confidence_findings": high,
        "weak_signal_findings": weak,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit public XSOAR skill content for private markers.")
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument("--json", action="store_true", help="Print full JSON report.")
    parser.add_argument("--fail-on-high", action="store_true", help="Exit non-zero if high-confidence findings exist.")
    args = parser.parse_args(argv)

    report = scan_root(Path(args.root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps({k: report[k] for k in ("high_confidence_count", "weak_signal_count", "high_confidence_summary", "weak_signal_summary")}, indent=2, sort_keys=True))

    if args.fail_on_high and report["high_confidence_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
