"""Every image is rendered from the manifest, and the exceptions are declared.

``generate.py`` renders each toolchain's Dockerfile — and its wrapper, unless
that wrapper is declared hand-written — from ``sources.json``.  These tests are
the gate that keeps the two in step: a hand-edited Dockerfile fails here
instead of drifting until the next rebuild produces a different image than the
one in the tree, and a wrapper that generation cannot express yet has to say so
in the manifest with a reason, so the exception list cannot grow quietly.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import generate  # repo root is on sys.path under `python -m unittest discover`

_REPO = Path(__file__).resolve().parents[1]

#: The wrappers that are still hand-written, each declaring a reason in the
#: manifest (``wrapper.shape == "handwritten"``).  This list is the point: a
#: new exception is a deliberate edit here, in the same change that adds it,
#: and the reasons behind the clusters are the queue of shapes still to
#: implement (DOSBox harness, dosemu2 pipeline, compiler pipeline, per-family
#: argv normalisation).
_HANDWRITTEN = (
    "borland-2.0",
    "borland-2.0-decompme",
    "borland-3.1",
    "borland-3.1-decompme",
    "delphi-1.0",
    "gcc-2.7.2-sn0001",
    "gcc-2.7.2-sn0001-cxx",
    "gcc-2.7.2-sn0004",
    "gcc-2.7.2-sn0006",
    "gcc-2.7.2-sn0006-cxx",
    "gcc-2.7.2-snew",
    "gcc-2.8.1-sn",
    "gcc-2.8.1-sn-cxx",
    "gcc-2.8.1-snew-cxx",
    "gcc-3.1-1041",
    "gcc-4.0.0-5026",
    "gcc-4.0.1-5363",
    "gcc-4.0.1-5370",
    "icc-5.0.1-010525z",
    "ido-4.1",
    "msc-5.1",
    "msc-6.0",
    "msvc-1.0",
    "msvc-1.5",
    "msvc-1.52",
    "msvc-6.0",
    "msvc-6.0-win9x",
    "msvc-8.0-portable",
    "psp-gcc-1.3.1",
    "psyq-2.6.3-221",
    "psyq-3.3",
    "psyq-3.5",
    "psyq-3.6",
    "psyq-4.0",
    "psyq-4.1",
    "psyq-4.3",
    "psyq-4.4",
    "psyq-4.6",
    "saturn-cygnus-2.7-96Q3",
)

_REQUIRED_RECIPE_KEYS = ("base", "fetch", "steps", "root", "entrypoint", "wrapper")


class TestGeneration(unittest.TestCase):
    def test_generated_files_are_current(self) -> None:
        """A Dockerfile or wrapper that differs from its rendering is stale."""
        rendered = generate.render_all(generate.manifest())
        stale = sorted(
            str(path.relative_to(_REPO))
            for path, text in rendered.items()
            if not path.exists() or path.read_text(encoding="utf-8") != text
        )
        self.assertEqual(stale, [], "run `make generate` to re-render these")

    def test_every_dockerfile_is_generated(self) -> None:
        entries = generate.manifest()
        for profile, entry in entries.items():
            text = (_REPO / entry["host_dir"] / "Dockerfile").read_text(encoding="utf-8")
            self.assertTrue(text.startswith(generate.MARKER), f"{profile}: hand-written Dockerfile")

    def test_handwritten_wrappers_are_the_declared_ones(self) -> None:
        entries = generate.manifest()
        declared = {p for p, e in entries.items() if generate.handwritten_wrapper(e)}
        self.assertEqual(sorted(declared), list(_HANDWRITTEN))
        for profile in declared:
            why = generate.handwritten_wrapper(entries[profile])
            self.assertTrue(why and why != "no reason given", f"{profile}: no reason given")

    def test_generated_wrappers_are_marked_and_handwritten_ones_are_not(self) -> None:
        for profile, entry in generate.manifest().items():
            wrapper = _REPO / entry["host_dir"] / generate.wrapper_filename(entry)
            text = wrapper.read_text(encoding="utf-8")
            if generate.handwritten_wrapper(entry):
                self.assertNotIn(generate.MARKER, text, f"{profile}: generated but declared")
            else:
                self.assertIn(generate.MARKER, text, f"{profile}: not generated, not declared")

    def test_every_profile_has_a_complete_recipe(self) -> None:
        for profile, entry in generate.manifest().items():
            recipe = generate.recipe(entry)
            for key in _REQUIRED_RECIPE_KEYS:
                self.assertIn(key, recipe, f"{profile}: recipe is missing {key}")
            self.assertTrue(recipe["base"] in generate.BASES, f"{profile}: unknown base")


if __name__ == "__main__":
    unittest.main()
