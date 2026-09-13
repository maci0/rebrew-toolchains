"""The generated docs must match the manifest, and name every upstream.

``docs/TOOLCHAINS.md`` and ``docs/PROVENANCE.md`` are derived from
``sources.json`` plus each toolchain Dockerfile (see ``catalog.py``).  Without
these tests the committed copies would silently rot as toolchains are added
or re-pinned — and a new download source could arrive with no provenance or
licence recorded, which is the documentation failure the generator exists to
prevent.  The same file also keeps the prose docs honest: every relative link
between them must resolve.
"""

from __future__ import annotations

import re
import unittest

import catalog  # repo root is on sys.path under `python -m unittest discover`

_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class TestCatalog(unittest.TestCase):
    def test_committed_catalog_is_current(self) -> None:
        expected = catalog.render(catalog.manifest())
        actual = catalog.DOC.read_text(encoding="utf-8")
        self.assertEqual(actual, expected, "run `make docs` to regenerate the catalog")

    def test_committed_provenance_is_current(self) -> None:
        expected = catalog.provenance(catalog.manifest())
        actual = catalog.PROVENANCE.read_text(encoding="utf-8")
        self.assertEqual(actual, expected, "run `make docs` to regenerate provenance")

    def test_every_pinned_url_has_documented_provenance(self) -> None:
        """A new upstream must be described (and licence-classed) in SOURCES."""
        for profile, entry in catalog.manifest().items():
            for url in catalog.urls_of(entry):
                self.assertTrue(
                    catalog.source_of(url),
                    f"{profile} pins {url} — add its upstream to catalog.SOURCES",
                )

    def test_equivalence_rows_match_real_aliases(self) -> None:
        """Every "verified alias" row must be registered, and resolve."""
        manifest = catalog.manifest()
        for community, profile, status, _evidence in catalog.EQUIVALENCES:
            self.assertIn(profile, manifest, f"{community}: unknown profile {profile}")
            if status != "verified alias":
                continue
            aliases = manifest[profile].get("aliases", [])
            if not isinstance(aliases, list):
                self.fail(f"{community}: {profile} has no alias list")
            self.assertIn(community, [str(a) for a in aliases], community)

    def test_catalog_covers_every_manifest_entry(self) -> None:
        rendered = catalog.render(catalog.manifest())
        for profile, entry in catalog.manifest().items():
            self.assertIn(f"rebrew/{entry['family']}:", rendered, profile)
            self.assertIn(str(entry["host_dir"]).split("/")[-1], rendered, profile)

    def test_every_family_has_a_description(self) -> None:
        for entry in catalog.manifest().values():
            self.assertIn(entry["family"], catalog.FAMILIES, entry["host_dir"])


class TestDocLinks(unittest.TestCase):
    """Relative markdown links in the prose docs must point at real files."""

    def test_relative_links_resolve(self) -> None:
        docs = [catalog.REPO / "README.md", *sorted((catalog.REPO / "docs").glob("*.md"))]
        checked = 0
        for doc in docs:
            for target in _LINK.findall(doc.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                path = target.split("#", 1)[0]
                if not path:
                    continue
                checked += 1
                self.assertTrue(
                    (doc.parent / path).exists(),
                    f"{doc.relative_to(catalog.REPO)} links to missing {target}",
                )
        self.assertGreater(checked, 0, "no relative links found — did the docs move?")


if __name__ == "__main__":
    unittest.main()
