import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReferenceIntegrityTests(unittest.TestCase):
    def test_command_index_paths_exist(self):
        index = json.loads((ROOT / "references" / "commands" / "index.json").read_text(encoding="utf-8"))

        missing = [
            command["path"]
            for command in index["commands"]
            if not (ROOT / "references" / "commands" / command["path"]).exists()
        ]

        self.assertEqual(missing, [])

    def test_command_index_excludes_local_source_urls(self):
        index = json.loads((ROOT / "references" / "commands" / "index.json").read_text(encoding="utf-8"))

        local = [
            command
            for command in index["commands"]
            if str(command.get("source_url", "")).startswith("local:")
        ]

        self.assertEqual(local, [])

    def test_structure_index_paths_exist(self):
        index = json.loads((ROOT / "references" / "structures" / "index.json").read_text(encoding="utf-8"))

        missing = [
            item["path"]
            for item in index["artifact_types"]
            if not (ROOT / "references" / "structures" / item["path"]).exists()
        ]

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
