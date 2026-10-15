#!/usr/bin/env python3
"""Behavior checks in a caller-specified scratch workspace; no project mutations."""
import argparse
from datetime import date
import json
from pathlib import Path
import unittest
import uuid

from wiki_health import Inspector, digest


class HealthTests(unittest.TestCase):
    workspace: Path

    def setUp(self):
        self.project = (self.workspace / f"case-{uuid.uuid4().hex}").resolve()
        assert self.project.is_relative_to(self.workspace)
        self.docs = self.project / "docs"
        self.docs.mkdir(parents=True)
        self.write("index.md", "# Docs\n\n[Design](design/main.md)\n")
        self.page("design/main.md", "doc-design")

    def write(self, path, content):
        target = (self.docs / path).resolve()
        assert target.is_relative_to(self.project)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def page(self, path, page_id, extra="", lifecycle="active", body="A substantive design description."):
        return self.write(path, f"---\nid: {page_id}\ntype: design\nlifecycle: {lifecycle}\n"
                          f"created: 2026-10-13\nupdated: 2026-10-13\n{extra}---\n# Design\n\n{body}\n")

    def ledger(self, name, collection, items):
        return self.write(f".wiki/{name}.json", json.dumps(
            {"schema": f"project-docs-wiki.{name}.v1", collection: items}))

    def source(self):
        raw = self.write("raw/documents/input.md", "Original source evidence.\n")
        live = self.project / "src" / "input.md"
        live.parent.mkdir()
        live.write_bytes(raw.read_bytes())
        self.sources = [{"id": "src-input", "raw_path": "raw/documents/input.md",
                         "sha256": digest(raw), "live_path": "src/input.md",
                         "authority": "primary", "state": "active", "refresh_due": None}]
        self.ledger("sources", "sources", self.sources)
        self.ledger("state", "processed", [{"source_id": "src-input", "page_id": "doc-design",
                                            "sha256": digest(raw)}])
        self.page("design/main.md", "doc-design", 'sources: ["src-input"]\n')
        return raw, live

    def inspect(self):
        return Inspector(self.docs, date(2026, 10, 13)).run()

    def codes(self, report):
        return {finding["code"] for finding in report["findings"]}

    def test_valid_records_are_read_only(self):
        self.source()
        before = {p.relative_to(self.project).as_posix(): digest(p)
                  for p in self.project.rglob("*") if p.is_file()}
        report = self.inspect()
        self.assertEqual(report["errors"], 0)
        self.assertEqual(report["warnings"], 0)
        after = {p.relative_to(self.project).as_posix(): digest(p)
                 for p in self.project.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_duplicate_document_identity(self):
        self.page("design/duplicate.md", "doc-design")
        self.assertIn("DUPLICATE_ID", self.codes(self.inspect()))

    def test_missing_link_and_code_example_boundary(self):
        self.page("design/main.md", "doc-design", body="[Missing](absent.md)")
        self.assertIn("BROKEN_LINK", self.codes(self.inspect()))
        self.page("design/main.md", "doc-design", body="Explanation.\n```markdown\n[Example](absent.md)\n```")
        self.assertNotIn("BROKEN_LINK", self.codes(self.inspect()))

    def test_index_reachability(self):
        self.write("index.md", "# Docs\n\nNo entries yet.\n")
        self.assertIn("UNINDEXED_PAGE", self.codes(self.inspect()))

    def test_raw_capture_tampering(self):
        raw, _ = self.source()
        raw.write_text("Rewritten evidence.\n", encoding="utf-8")
        self.assertIn("CAPTURE_CHANGED", self.codes(self.inspect()))

    def test_source_change_propagates_only_declared_dependency(self):
        _, live = self.source()
        self.page("design/dependent.md", "doc-dependent",
                  'relations: [{"type":"depends_on","target":"doc-design","basis":"EXTRACTED"}]\n')
        self.page("design/speculation.md", "doc-speculation",
                  'relations: [{"type":"depends_on","target":"doc-design","basis":"INFERRED"}]\n')
        live.write_text("Changed current source.\n", encoding="utf-8")
        report = self.inspect()
        affected = {f["file"] for f in report["findings"] if f["code"] == "DEPENDENCY_REVIEW"}
        self.assertEqual(affected, {"design/dependent.md"})
        self.assertIn("LIVE_SOURCE_CHANGED", self.codes(report))
        self.assertIn("REVIEW_REQUIRED", self.codes(report))

    def test_archived_source_history_does_not_become_live_review(self):
        _, live = self.source()
        old = self.docs / "design/main.md"
        self.page("legacy/design/main.md", "doc-design", 'sources: ["src-input"]\n', lifecycle="archived")
        old.unlink()
        self.write("index.md", "# Docs\n\n[History](legacy/design/main.md)\n")
        live.write_text("Changed current source.\n", encoding="utf-8")
        report = self.inspect()
        self.assertNotIn("REVIEW_REQUIRED", self.codes(report))
        self.assertNotIn("DEPENDENCY_REVIEW", self.codes(report))

    def test_processing_hash_does_not_silently_advance(self):
        self.source()
        state = self.ledger("state", "processed", [{"source_id": "src-input", "page_id": "doc-design",
                                                    "sha256": "0" * 64}])
        before = state.read_bytes()
        self.assertIn("PROCESSING_VERSION_MISMATCH", self.codes(self.inspect()))
        self.assertEqual(state.read_bytes(), before)

    def test_summary_alone_cannot_confirm_a_claim(self):
        self.source()
        self.sources[0]["authority"] = "synthesis"
        self.ledger("sources", "sources", self.sources)
        self.ledger("claims", "claims", [{"id": "claim-a", "page_id": "doc-design",
                                           "basis": "INFERRED", "assessment": "confirmed",
                                           "source_ids": ["src-input"], "verified_at": "2026-10-13",
                                           "verification": "Reviewed summary"}])
        self.assertIn("UNSUPPORTED_CONFIRMATION", self.codes(self.inspect()))

    def test_remote_review_deadline_uses_explicit_date(self):
        self.source()
        self.sources[0].pop("live_path")
        self.sources[0]["refresh_due"] = "2026-10-13"
        self.ledger("sources", "sources", self.sources)
        self.assertIn("SOURCE_REVIEW_DUE", self.codes(self.inspect()))
        earlier = Inspector(self.docs, date(2026, 10, 12)).run()
        self.assertNotIn("SOURCE_REVIEW_DUE", self.codes(earlier))

    def test_complex_existing_yaml_is_not_overwritten(self):
        page = self.page("design/main.md", "doc-design", "sources:\n  - old-source\n")
        before = page.read_bytes()
        report = self.inspect()
        self.assertIn("METADATA_LIST_UNSUPPORTED", self.codes(report))
        self.assertEqual(report["errors"], 0)
        self.assertEqual(page.read_bytes(), before)

    def test_duplicate_wikilink_names_are_not_guessed(self):
        self.page("design/main.md", "doc-design", body="Related [[note]] is ambiguous.")
        self.page("knowledge/a/note.md", "doc-note-a")
        self.page("knowledge/b/note.md", "doc-note-b")
        self.assertIn("AMBIGUOUS_WIKILINK", self.codes(self.inspect()))

    def test_relative_links_survive_repaired_move(self):
        old = self.docs / "design/main.md"
        content = old.read_text(encoding="utf-8")
        self.write("knowledge/main.md", content)
        old.unlink()
        self.write("index.md", "# Docs\n\n[Design](knowledge/main.md)\n")
        report = self.inspect()
        self.assertEqual(report["errors"], 0)
        self.assertEqual(report["warnings"], 0)

    def test_malformed_reference_types_produce_reports(self):
        self.page("design/main.md", "doc-design", 'relations: [{"target":[]},{"type":[],"target":"doc-design","basis":"EXTRACTED"}]\n')
        self.ledger("state", "processed", [{"source_id": [], "page_id": []}])
        self.ledger("claims", "claims", [{"id": "claim-b", "page_id": [], "basis": [],
                                           "assessment": [], "source_ids": []}])
        codes = self.codes(self.inspect())
        self.assertIn("BROKEN_RELATION", codes)
        self.assertIn("BROKEN_PROCESSING_REFERENCE", codes)
        self.assertIn("INVALID_CLAIM_STATE", codes)

    def test_source_paths_stay_in_the_declared_roots(self):
        self.source()
        self.sources[0]["live_path"] = "../outside.md"
        self.ledger("sources", "sources", self.sources)
        self.assertIn("INVALID_LIVE_PATH", self.codes(self.inspect()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    HealthTests.workspace = args.workspace.resolve()
    HealthTests.workspace.mkdir(parents=True, exist_ok=True)
    result = unittest.main(argv=[__file__], verbosity=2, exit=False)
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
