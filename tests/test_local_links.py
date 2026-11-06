"""Audit authored repository-local links without fetching URLs or running examples."""

from collections import Counter
import html
import os
from pathlib import Path
import re
import tomllib
import unittest
from urllib.parse import unquote, urlsplit


REPO = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", "target", "node_modules", "build", "__pycache__", ".pytest_cache"}
INLINE_LINK = re.compile(r"\[[^\]\n]*\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+['\"][^\n]*?['\"])?\s*\)")
REFERENCE_LINK = re.compile(r"^\s*\[([^\]\n]+)\]:\s*(<[^>]*>|\S+)", re.MULTILINE)


def prose_only(text):
    """Preserve line numbers, but do not mistake fenced examples for real links."""
    result = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            result.append("\n" if line.endswith("\n") else "")
        elif fence is None:
            result.append(line)
        else:
            result.append("\n" if line.endswith("\n") else "")
    return "".join(result)


def anchors(text):
    result = set()
    duplicates = Counter()
    prose = prose_only(text)
    for match in re.finditer(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", prose, re.MULTILINE):
        label = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", match[1])
        label = re.sub(r"<[^>]*>", "", label).replace("`", "")
        label = html.unescape(label).strip().lower()
        slug = re.sub(r"[^\w\s-]", "", label)
        slug = re.sub(r"\s", "-", slug)
        number = duplicates[slug]
        duplicates[slug] += 1
        result.add(slug if number == 0 else f"{slug}-{number}")
    result.update(re.findall(r"<(?:a|[^\s>]+)\s+[^>]*?(?:id|name)=[\"']([^\"']+)[\"']", prose))
    return result


def authored_documents():
    documents = {REPO / "README.md", REPO / "ROADMAP.md"}
    for relative in ("README", "practice", "src/shared"):
        directory = REPO / relative
        if not directory.is_dir():
            continue
        for parent, directories, files in os.walk(directory, followlinks=False):
            directories[:] = [name for name in directories if name not in EXCLUDED]
            documents.update(Path(parent) / name for name in files if name.endswith(".md"))
    return sorted(path for path in documents if path.is_file())


class LocalLinkTests(unittest.TestCase):
    def test_authored_markdown_targets_and_fragments_exist(self):
        failures = []
        checked = 0
        anchor_cache = {}
        for document in authored_documents():
            text = prose_only(document.read_text())
            # Backticked example links are not rendered Markdown links. Replacing
            # their text still leaves links with backticked labels recognizable.
            link_text = re.sub(r"`+[^`\n]*`+", lambda match: " " * len(match[0]), text)
            destinations = [(match[1], match.start()) for match in INLINE_LINK.finditer(link_text)]
            destinations += [(match[2], match.start()) for match in REFERENCE_LINK.finditer(link_text)
                             if not match[1].startswith("^")]
            for raw, offset in destinations:
                destination = raw.strip("<>")
                url = urlsplit(destination)
                if url.scheme or url.netloc:
                    continue
                relative = unquote(url.path)
                target = ((REPO / relative.lstrip("/")) if relative.startswith("/")
                          else document.parent / relative) if relative else document
                target = target.resolve()
                if not target.is_relative_to(REPO):
                    continue  # Deliberate external-checkout links are not this audit's scope.
                checked += 1
                location = f"{document.relative_to(REPO)}:{text.count(chr(10), 0, offset) + 1}"
                if not target.exists():
                    failures.append(f"{location}: {destination} (target missing)")
                elif url.fragment and target.suffix.lower() == ".md":
                    if target not in anchor_cache:
                        anchor_cache[target] = anchors(target.read_text())
                    if unquote(url.fragment) not in anchor_cache[target]:
                        failures.append(f"{location}: {destination} (anchor missing)")
        self.assertGreater(checked, 100, "The audit should inspect the real documentation corpus")
        self.assertFalse(failures, "Broken local links:\n" + "\n".join(failures))

    def test_heading_and_example_handling(self):
        text = "# Intro\n## API / Interfaces\n## Intro\n```md\n# Not a heading\n[x](missing.md)\n```\n"
        self.assertEqual(anchors(text), {"intro", "api--interfaces", "intro-1"})
        self.assertNotIn("missing.md", prose_only(text))

    def test_typescript_relative_import_targets_exist(self):
        failures = []
        checked = 0
        for source in (REPO / "practice/typescript").glob("*.spec.ts"):
            for match in re.finditer(r"\bfrom\s*['\"](\.[^'\"]+)['\"]", source.read_text()):
                checked += 1
                target = source.parent / match[1]
                candidates = (target, Path(str(target) + ".ts"), target / "index.ts")
                if not any(path.is_file() for path in candidates):
                    failures.append(f"{source.relative_to(REPO)}: {match[1]}")
        self.assertEqual(checked, 16)
        self.assertFalse(failures, "Broken relative imports:\n" + "\n".join(failures))

    def test_python_development_config_has_no_missing_package_targets(self):
        manifest = tomllib.loads((REPO / "pyproject.toml").read_text())
        self.assertFalse(manifest["tool"]["uv"]["package"])
        self.assertNotIn("scripts", manifest["project"])
        for relative in manifest["tool"]["pytest"]["ini_options"]["testpaths"]:
            self.assertTrue((REPO / relative).is_dir(), relative)
        lock = tomllib.loads((REPO / "uv.lock").read_text())
        project = next(package for package in lock["package"]
                       if package["name"] == manifest["project"]["name"])
        self.assertEqual(project["source"], {"virtual": "."})
