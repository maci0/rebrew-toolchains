"""Contract tests for the toolchain image matrix.

Every toolchain image is built from ``<family>/<version>-<arch>/Dockerfile``
and pinned by a ``sources.json`` entry.  These tests pin the uniformity that
matters: a complete manifest whose pin agrees with the Dockerfile, the OCI
labels every image carries, an absolute entrypoint wrapper, the non-root
runtime user, an install root under ``/opt``, and a wrapper that goes through
the shared ``base/wrapper-common.sh`` helpers instead of calling wine or
DOSBox directly (the drift this guards against: older images ran
``exec wine`` and skipped ``REBREW_RUNNER``).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

_OCI_LABELS = ("source", "licenses", "title", "description")

#: The shared run helpers a wrapper may dispatch through.  A wine image uses
#: ``rebrew_run``, a DOSBox image ``rebrew_dosbox_compile`` /
#: ``rebrew_dosbox_run``, a native-binary image ``rebrew_exec``.
_RUN_HELPERS = ("rebrew_run", "rebrew_dosbox_compile", "rebrew_dosbox_run", "rebrew_exec")


def _toolchain_dirs() -> list[Path]:
    """Every ``<family>/<version>-<arch>`` directory (``base/`` excluded)."""
    return sorted(path.parent for path in _REPO.glob("*/*/Dockerfile"))


def _manifest() -> dict[str, dict[str, str]]:
    text = (_REPO / "sources.json").read_text(encoding="utf-8")
    data: dict[str, dict[str, str]] = json.loads(text)
    return data


class TestManifest(unittest.TestCase):
    def test_every_entry_is_complete(self) -> None:
        for profile, entry in _manifest().items():
            for key in ("family", "host_dir", "url", "sha256", "commit", "layout"):
                self.assertIn(key, entry, f"{profile}: missing {key}")
            self.assertTrue(entry["family"], profile)
            self.assertTrue(entry["host_dir"], profile)
            self.assertTrue(entry["url"].startswith("https://"), profile)
            self.assertEqual(len(entry["sha256"]), 64, f"{profile}: bad sha256")
            self.assertTrue(entry["layout"], profile)
            # A branch tarball moves, so its pin must name the commit it came
            # from.  A release asset is content-addressed by its sha256 alone
            # and has no commit to record (Open Watcom's `Last-CI-build`
            # snapshot is republished continuously).
            if "refs/heads/" in entry["url"]:
                self.assertTrue(entry["commit"], f"{profile}: branch pin without a commit")

    def test_every_pin_appears_in_its_dockerfile(self) -> None:
        for profile, entry in _manifest().items():
            text = (_REPO / entry["host_dir"] / "Dockerfile").read_text(encoding="utf-8")
            self.assertIn(entry["url"], text, f"{profile}: url not in its Dockerfile")
            self.assertIn(entry["sha256"], text, f"{profile}: sha256 not in its Dockerfile")

    def test_every_dockerfile_has_a_manifest_entry(self) -> None:
        """Reverse sweep: a Dockerfile whose download pins nothing is a gap."""
        dirs = {str(d.relative_to(_REPO)) for d in _toolchain_dirs()}
        self.assertEqual(dirs, {e["host_dir"] for e in _manifest().values()})


class TestImageContract(unittest.TestCase):
    def test_carries_the_oci_labels(self) -> None:
        for d in _toolchain_dirs():
            text = (d / "Dockerfile").read_text(encoding="utf-8")
            for key in _OCI_LABELS:
                self.assertIn(f"org.opencontainers.image.{key}", text, f"{d}: {key}")

    def test_entrypoint_is_an_absolute_wrapper(self) -> None:
        for d in _toolchain_dirs():
            text = (d / "Dockerfile").read_text(encoding="utf-8")
            self.assertRegex(
                text,
                r'(?m)^ENTRYPOINT \["/usr/local/bin/[^"]+"\]$',
                f"{d}: ENTRYPOINT must be an absolute /usr/local/bin wrapper",
            )

    def test_installs_as_root_and_runs_as_the_unprivileged_user(self) -> None:
        for d in _toolchain_dirs():
            text = (d / "Dockerfile").read_text(encoding="utf-8")
            self.assertRegex(text, r"(?m)^USER root$", f"{d}: install steps need root")
            self.assertRegex(text, r"(?m)^USER rebrew$", f"{d}: must drop the runtime user")

    def test_install_root_is_under_opt(self) -> None:
        for d in _toolchain_dirs():
            self.assertIn("mkdir -p /opt/", (d / "Dockerfile").read_text(encoding="utf-8"), d)

    def test_wrapper_goes_through_the_shared_helpers(self) -> None:
        """Inline wrappers and sibling ``*.sh`` wrappers are both allowed, but
        every one of them must source ``wrapper-common.sh`` and dispatch
        through a shared run helper."""
        for d in _toolchain_dirs():
            parts = [(d / "Dockerfile").read_text(encoding="utf-8")]
            parts += [p.read_text(encoding="utf-8") for p in sorted(d.glob("*.sh"))]
            blob = "\n".join(parts)
            self.assertIn("wrapper-common.sh", blob, f"{d}: wrapper does not source the helpers")
            self.assertTrue(
                any(helper in blob for helper in _RUN_HELPERS),
                f"{d}: wrapper uses none of {_RUN_HELPERS}",
            )


if __name__ == "__main__":
    unittest.main()
