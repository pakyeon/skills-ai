#!/usr/bin/env python3
"""Read-only structural checks for the project-docs-wiki schema (stdlib only)."""
from __future__ import annotations

import argparse
from collections import deque
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote

LIFECYCLES = {"draft", "active", "superseded", "merged", "archived"}
BASES = {"EXTRACTED", "CALCULATED", "INFERRED", "AMBIGUOUS", "UNVERIFIED"}
ASSESSMENTS = {"confirmed", "provisional", "disputed", "unsupported", "superseded"}
RELATIONS = {"depends_on", "implements", "supports", "contradicts", "supersedes", "derived_from", "related_to"}
ADMIN = {"index.md", "_index.md", "schema.md", "log.md"}
LIST_FIELDS = {"aliases", "sources", "claims", "relations"}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def strip_code(text: str) -> str:
    lines, fence = [], None
    for line in text.splitlines():
        mark = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if mark:
            token, tail = mark.groups()
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


class Inspector:
    def __init__(self, docs: Path, as_of: date):
        self.docs = docs.resolve()
        self.project = self.docs.parent
        self.as_of = as_of
        self.findings: list[dict] = []
        self.pages: dict[Path, dict] = {}
        self.ids: dict[str, Path] = {}
        self.links: dict[Path, set[Path]] = {}
        self.changed_sources: set[str] = set()
        self.direct_impacts: set[str] = set()

    def report(self, level: str, code: str, file: str | Path, detail: str):
        if isinstance(file, Path):
            file = file.relative_to(self.docs).as_posix()
        self.findings.append({"level": level, "code": code, "file": file, "detail": detail})

    def bounded(self, base: Path, value: str) -> Path:
        if not isinstance(value, str) or not value or Path(value).is_absolute():
            raise ValueError("Expected a relative path")
        candidate = (base / value).resolve()
        if not candidate.is_relative_to(base):
            raise ValueError("Path leaves its declared root")
        return candidate

    def metadata(self, path: Path, text: str) -> tuple[dict, str]:
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
        if not match:
            return {}, text
        values = {}
        for line in match.group(1).splitlines():
            found = re.match(r"^([a-z_]+):\s*(.*?)\s*$", line)
            if not found:
                continue
            key, value = found.groups()
            if key in LIST_FIELDS:
                try:
                    parsed = json.loads(value)
                    if not isinstance(parsed, list):
                        raise ValueError("not a list")
                    values[key] = parsed
                except (ValueError, json.JSONDecodeError):
                    self.report("warning", "METADATA_LIST_UNSUPPORTED", path,
                                f"{key}: review existing YAML or use a one-line JSON list")
                continue
            if value.startswith('"'):
                try:
                    value = json.loads(value)
                except ValueError:
                    continue
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1].replace("''", "'")
            else:
                value = value.split(" #", 1)[0].strip()
            if isinstance(value, str):
                values[key] = value
        return values, text[match.end():]

    def discover(self):
        for directory, dirs, files in os.walk(self.docs, followlinks=False):
            dirs[:] = sorted(name for name in dirs
                             if not name.startswith(".") and name != "raw"
                             and not (Path(directory) / name).is_symlink()
                             and not (hasattr(Path(directory) / name, "is_junction")
                                      and (Path(directory) / name).is_junction()))
            for name in sorted(files):
                path = Path(directory) / name
                if path.suffix.lower() != ".md":
                    continue
                if path.is_symlink() or not path.resolve().is_relative_to(self.docs):
                    self.report("warning", "UNINSPECTED_LINKED_FILE", path, "Inspect linked file separately")
                    continue
                try:
                    text = path.read_text(encoding="utf-8-sig")
                except (OSError, UnicodeError) as error:
                    self.report("error", "PAGE_UNREADABLE", path, type(error).__name__)
                    continue
                meta, body = self.metadata(path, text)
                archived = path.relative_to(self.docs).parts[0] == "legacy"
                self.pages[path] = {"meta": meta, "body": body, "archived": archived}
                self.links[path] = set()
                page_id = meta.get("id")
                if page_id:
                    if page_id in self.ids:
                        self.report("error", "DUPLICATE_ID", path, page_id)
                    else:
                        self.ids[page_id] = path
                    if meta.get("lifecycle") not in LIFECYCLES:
                        self.report("error", "INVALID_LIFECYCLE", path, "Use a declared lifecycle")
                    if not meta.get("type"):
                        self.report("warning", "MISSING_TYPE", path, "Declare the document's role")
                elif path.name not in ADMIN and not archived:
                    self.report("warning", "LEGACY_METADATA", path, "Assign an ID when substantively updating")
                prose = re.sub(r"^\s*#+[^\n]*$", "", strip_code(body), flags=re.M).strip()
                if not prose:
                    self.report("warning", "EMPTY_PAGE", path, "No substantive body")

    def add_link(self, path: Path, target: str, wiki: bool = False):
        target = unquote(target.strip().strip("<>"))
        if not target or target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return
        target = target.split("#", 1)[0].split("?", 1)[0]
        if not target:
            return
        if wiki:
            target = target.split("|", 1)[0].strip()
            candidate_paths = set()
            if target in self.ids:
                candidate_paths.add(self.ids[target])
            for base in (path.parent, self.docs):
                for suffix in ("", ".md"):
                    candidate = (base / (target + suffix)).resolve()
                    if candidate in self.pages:
                        candidate_paths.add(candidate)
            if not candidate_paths and "/" not in target and "\\" not in target:
                candidate_paths = {item for item in self.pages if item.stem == target}
            if len(candidate_paths) != 1:
                self.report("error", "AMBIGUOUS_WIKILINK" if candidate_paths else "BROKEN_LINK",
                            path, target)
                return
            candidate = next(iter(candidate_paths))
        else:
            candidate = (path.parent / target).resolve()
            if not candidate.is_relative_to(self.project):
                self.report("warning", "EXTERNAL_FILE_LINK", path, "Outside project; not inspected")
                return
            if not candidate.is_file():
                self.report("error", "BROKEN_LINK", path, target)
                return
        if candidate in self.pages:
            self.links[path].add(candidate)

    def check_links(self):
        for path, page in self.pages.items():
            prose = strip_code(page["body"])
            for target in re.findall(r"\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", prose):
                self.add_link(path, target)
            for target in re.findall(r"\[\[([^\]]+)\]\]", prose):
                self.add_link(path, target, wiki=True)
            for target in re.findall(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", prose, re.M):
                self.add_link(path, target)
            for relation in page["meta"].get("relations", []):
                if (not isinstance(relation, dict) or not isinstance(relation.get("target"), str)
                        or relation["target"] not in self.ids
                        or not isinstance(relation.get("type"), str) or relation["type"] not in RELATIONS):
                    self.report("error", "BROKEN_RELATION", path, "Relation must resolve to a document ID")
                else:
                    self.links[path].add(self.ids[relation["target"]])
        roots = [path for path in self.pages if path.name in {"index.md", "_index.md"}
                 and not self.pages[path]["archived"]]
        visited, queue = set(roots), deque(roots)
        while queue:
            for target in self.links[queue.popleft()]:
                if target not in visited:
                    visited.add(target)
                    queue.append(target)
        for path, page in self.pages.items():
            if path.name not in ADMIN and not page["archived"] and path not in visited:
                self.report("warning", "UNINDEXED_PAGE", path, "Not reachable from a live index")

    def ledger(self, name: str, collection: str) -> list[dict]:
        path = self.docs / ".wiki" / f"{name}.json"
        if not path.exists():
            return []
        if not path.resolve().is_relative_to(self.docs):
            self.report("error", "LEDGER_OUTSIDE_ROOT", f".wiki/{name}.json", "Not inspected")
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            expected = f"project-docs-wiki.{name}.v1"
            if not isinstance(data, dict) or data.get("schema") != expected:
                raise ValueError("schema")
            items = data.get(collection)
            if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
                raise ValueError("collection")
            return items
        except (OSError, UnicodeError, ValueError) as error:
            self.report("error", "INVALID_LEDGER", f".wiki/{name}.json", type(error).__name__)
            return []

    def by_id(self, items: list[dict], name: str) -> dict[str, dict]:
        result = {}
        for item in items:
            key = item.get("id")
            if not isinstance(key, str) or not key or key in result:
                self.report("error", "INVALID_LEDGER_ID", f".wiki/{name}.json", "Missing or duplicate ID")
                continue
            result[key] = item
        return result

    def check_records(self):
        sources = self.by_id(self.ledger("sources", "sources"), "sources")
        claims = self.by_id(self.ledger("claims", "claims"), "claims")
        processed = self.ledger("state", "processed")
        for source_id, source in sources.items():
            expected = source.get("sha256")
            raw = source.get("raw_path")
            if raw:
                try:
                    raw_path = self.bounded(self.docs, raw)
                    if raw_path.relative_to(self.docs).parts[0] != "raw":
                        raise ValueError("Capture must be under raw/")
                    if not raw_path.is_file():
                        self.report("error", "CAPTURE_MISSING", ".wiki/sources.json", source_id)
                    elif not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                        self.report("error", "INVALID_SOURCE_HASH", ".wiki/sources.json", source_id)
                    elif digest(raw_path) != expected:
                        self.report("error", "CAPTURE_CHANGED", ".wiki/sources.json", source_id)
                except (OSError, ValueError):
                    self.report("error", "INVALID_SOURCE_PATH", ".wiki/sources.json", source_id)
            if source.get("state", "active") != "active":
                self.changed_sources.add(source_id)
                continue
            if source.get("live_path"):
                try:
                    live = self.bounded(self.project, source["live_path"])
                    if not live.is_file():
                        self.report("warning", "LIVE_SOURCE_MISSING", ".wiki/sources.json", source_id)
                        self.changed_sources.add(source_id)
                    elif expected and digest(live) != expected:
                        self.report("warning", "LIVE_SOURCE_CHANGED", ".wiki/sources.json", source_id)
                        self.changed_sources.add(source_id)
                except (OSError, ValueError):
                    self.report("error", "INVALID_LIVE_PATH", ".wiki/sources.json", source_id)
            due = source.get("refresh_due")
            if due:
                try:
                    if date.fromisoformat(due) <= self.as_of:
                        self.report("warning", "SOURCE_REVIEW_DUE", ".wiki/sources.json", source_id)
                        self.changed_sources.add(source_id)
                except (ValueError, TypeError):
                    self.report("error", "INVALID_REVIEW_DATE", ".wiki/sources.json", source_id)
        done = set()
        for record in processed:
            source_id, page_id = record.get("source_id"), record.get("page_id")
            if (not isinstance(source_id, str) or not isinstance(page_id, str)
                    or source_id not in sources or page_id not in self.ids):
                self.report("error", "BROKEN_PROCESSING_REFERENCE", ".wiki/state.json", "Unknown source or page")
                continue
            pair = (source_id, page_id)
            if pair in done:
                self.report("error", "DUPLICATE_PROCESSING_REFERENCE", ".wiki/state.json", page_id)
            done.add(pair)
            if not sources[source_id].get("sha256") or record.get("sha256") != sources[source_id]["sha256"]:
                self.report("warning", "PROCESSING_VERSION_MISMATCH", ".wiki/state.json", page_id)
                if self.active(page_id):
                    self.direct_impacts.add(page_id)
            if source_id in self.changed_sources and self.active(page_id):
                self.direct_impacts.add(page_id)
        for path, page in self.pages.items():
            page_id = page["meta"].get("id")
            for source_id in page["meta"].get("sources", []):
                if not isinstance(source_id, str) or source_id not in sources:
                    self.report("error", "BROKEN_SOURCE_REFERENCE", path, "Unknown source ID")
                elif self.active(page_id):
                    if source_id in self.changed_sources:
                        self.direct_impacts.add(page_id)
                    if (source_id, page_id) not in done:
                        self.report("warning", "PROCESSING_BASELINE_MISSING", path, source_id)
            for claim_id in page["meta"].get("claims", []):
                if not isinstance(claim_id, str) or claim_id not in claims:
                    self.report("error", "BROKEN_CLAIM_REFERENCE", path, "Unknown claim ID")
        for claim_id, claim in claims.items():
            page_id = claim.get("page_id")
            if not isinstance(page_id, str) or page_id not in self.ids:
                self.report("error", "BROKEN_CLAIM_PAGE", ".wiki/claims.json", claim_id)
            if (not isinstance(claim.get("basis"), str) or claim["basis"] not in BASES
                    or not isinstance(claim.get("assessment"), str) or claim["assessment"] not in ASSESSMENTS):
                self.report("error", "INVALID_CLAIM_STATE", ".wiki/claims.json", claim_id)
            source_ids = claim.get("source_ids", [])
            if not isinstance(source_ids, list) or any(not isinstance(s, str) or s not in sources for s in source_ids):
                self.report("error", "BROKEN_CLAIM_SOURCE", ".wiki/claims.json", claim_id)
                continue
            if claim.get("assessment") == "confirmed":
                try:
                    date.fromisoformat(claim.get("verified_at", ""))
                    verified = bool(claim.get("verification"))
                except (ValueError, TypeError):
                    verified = False
                grounded = any(isinstance(sources[s].get("authority"), str)
                               and sources[s]["authority"] not in {"unknown", "synthetic", "synthesis"}
                               for s in source_ids)
                if (not verified or not grounded or not isinstance(claim.get("basis"), str)
                        or claim["basis"] in {"AMBIGUOUS", "UNVERIFIED"}):
                    self.report("error", "UNSUPPORTED_CONFIRMATION", ".wiki/claims.json", claim_id)
                if self.active(page_id) and any(s in self.changed_sources for s in source_ids):
                    self.direct_impacts.add(page_id)

    def active(self, page_id: str | None) -> bool:
        if not isinstance(page_id, str):
            return False
        path = self.ids.get(page_id)
        return bool(path and not self.pages[path]["archived"]
                    and self.pages[path]["meta"].get("lifecycle") in {"draft", "active"})

    def check_impacts(self):
        impacted = set(self.direct_impacts)
        again = True
        while again:
            again = False
            for page_id, path in self.ids.items():
                if not self.active(page_id) or page_id in impacted:
                    continue
                relations = self.pages[path]["meta"].get("relations", [])
                if any(isinstance(r, dict) and r.get("basis") == "EXTRACTED"
                       and isinstance(r.get("type"), str)
                       and r["type"] in {"depends_on", "implements", "derived_from"}
                       and isinstance(r.get("target"), str)
                       and r["target"] in impacted for r in relations):
                    impacted.add(page_id)
                    again = True
        for page_id in sorted(impacted):
            self.report("warning", "REVIEW_REQUIRED" if page_id in self.direct_impacts else "DEPENDENCY_REVIEW",
                        self.ids[page_id], "Input or declared dependency changed; review meaning before updating")

    def run(self) -> dict:
        self.discover()
        self.check_links()
        self.check_records()
        self.check_impacts()
        return {"as_of": self.as_of.isoformat(), "pages": len(self.pages),
                "errors": sum(f["level"] == "error" for f in self.findings),
                "warnings": sum(f["level"] == "warning" for f in self.findings),
                "findings": self.findings,
                "scope": "Local structure and recorded hashes; no semantic, remote, or approval verification"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", required=True, type=Path)
    parser.add_argument("--as-of", required=True, type=date.fromisoformat)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.docs.is_dir():
        print("Docs directory does not exist", file=sys.stderr)
        return 1
    try:
        report = Inspector(args.docs, args.as_of).run()
    except (OSError, UnicodeError) as error:
        print(f"Inspection could not finish: {type(error).__name__}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['pages']} pages; {report['errors']} errors; {report['warnings']} warnings")
        for finding in report["findings"]:
            print(f"{finding['level']}: {finding['code']} | {finding['file']} | {finding['detail']}")
    return 2 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
