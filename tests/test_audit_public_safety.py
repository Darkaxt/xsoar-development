import tempfile
import unittest
from pathlib import Path

from scripts.audit_public_safety import scan_root


class AuditPublicSafetyTests(unittest.TestCase):
    def test_high_confidence_marker_is_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = "M" + "DR"
            (root / "SKILL.md").write_text(f"Do not publish {marker} details\n", encoding="utf-8")

            report = scan_root(root)

            self.assertEqual(report["high_confidence_count"], 1)
            self.assertEqual(report["high_confidence_findings"][0]["pattern"], "private_playbook_markers")

    def test_local_source_url_is_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "references" / "commands" / "native"
            path.mkdir(parents=True)
            (path / "getList.json").write_text(
                '{"source_url":"local:' + 'xsoar-development/repo-command-usage"}',
                encoding="utf-8",
            )

            report = scan_root(root)

            self.assertEqual(report["high_confidence_count"], 1)
            self.assertEqual(report["high_confidence_findings"][0]["pattern"], "local_source_url")

    def test_weak_signals_do_not_fail_high_confidence_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference.json").write_text(
                '{"example": "analyst@example.com", "note": "token parameter"}',
                encoding="utf-8",
            )

            report = scan_root(root)

            self.assertEqual(report["high_confidence_count"], 0)
            self.assertGreaterEqual(report["weak_signal_count"], 1)

    def test_git_and_private_overlay_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git = root / ".git"
            git.mkdir()
            private_repo = "D:\\Downloads\\" + "Trash\\XSoar-" + "M" + "DR"
            (git / "config").write_text(private_repo + "\n", encoding="utf-8")
            local = root / "references" / "local"
            local.mkdir(parents=True)
            (local / "private-workflow.md").write_text("M" + "DR overlay\n", encoding="utf-8")

            report = scan_root(root)

            self.assertEqual(report["high_confidence_count"], 0)


if __name__ == "__main__":
    unittest.main()
