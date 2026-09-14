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
from collections.abc import Mapping
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

_OCI_LABELS = ("source", "licenses", "title", "description")

#: The shared run helpers a wrapper may dispatch through.  A wine image uses
#: ``rebrew_run``, a DOSBox image ``rebrew_dosbox_compile`` /
#: ``rebrew_dosbox_run``, a DOS-binary image ``rebrew_dosemu_run`` (dosemu2),
#: a native-binary image ``rebrew_exec``.
_RUN_HELPERS = (
    "rebrew_run",
    "rebrew_dosbox_compile",
    "rebrew_dosbox_run",
    "rebrew_dosemu_run",
    "rebrew_exec",
)


def _toolchain_dirs() -> list[Path]:
    """Every ``<family>/<version>-<arch>`` directory (``base/`` excluded)."""
    return sorted(path.parent for path in _REPO.glob("*/*/Dockerfile"))


def _manifest() -> dict[str, dict[str, str]]:
    text = (_REPO / "sources.json").read_text(encoding="utf-8")
    data: dict[str, dict[str, str]] = json.loads(text)
    return data


def _pins(entry: Mapping[str, object]) -> list[tuple[str, str, str]]:
    """Every pinned download as ``(name, url, sha256)``.

    The primary pin plus each secondary pin (``<name>_url`` /
    ``<name>_sha256``: a parser, a helper, an SDK, binutils) and each
    ``extra_pins`` entry.  Secondary pins once slipped past this file — the
    PSY-Q 4.5 SDK download lived here with no hash at all — so they are swept
    too.
    """
    pins = [("primary", str(entry.get("url", "")), str(entry.get("sha256", "")))]
    for key, value in entry.items():
        if key.endswith("_url"):
            name = key[: -len("_url")]
            pins.append((name, str(value), str(entry.get(f"{name}_sha256", ""))))
    extra = entry.get("extra_pins")
    if isinstance(extra, list):
        for index, pin in enumerate(extra):
            if isinstance(pin, dict):
                pins.append((f"extra{index}", str(pin.get("url", "")), str(pin.get("sha256", ""))))
    return pins


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
            for name, url, sha in _pins(entry):
                self.assertTrue(url.startswith("https://"), f"{profile}: {name} url")
                self.assertEqual(len(sha), 64, f"{profile}: {name} has no sha256")
            # A branch tarball moves, so its pin must name the commit it came
            # from.  A release asset is content-addressed by its sha256 alone
            # and has no commit to record (Open Watcom's `Last-CI-build`
            # snapshot is republished continuously).
            if "refs/heads/" in entry["url"]:
                self.assertTrue(entry["commit"], f"{profile}: branch pin without a commit")

    def test_every_pin_appears_in_its_dockerfile(self) -> None:
        for profile, entry in _manifest().items():
            text = (_REPO / entry["host_dir"] / "Dockerfile").read_text(encoding="utf-8")
            for name, url, sha in _pins(entry):
                self.assertIn(url, text, f"{profile}: {name} url not in its Dockerfile")
                self.assertIn(sha, text, f"{profile}: {name} sha256 not in its Dockerfile")

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

    def test_every_toolchain_directory_is_manifested(self) -> None:
        """Any directory carrying image inputs must be a manifest host_dir.

        The reverse sweep above only looks at directories holding a
        Dockerfile; a directory with just a wrapper file (what a template
        escaping bug leaves behind) would otherwise slip through.
        """
        known = {str(e["host_dir"]) for e in _manifest().values()}
        for path in sorted(_REPO.glob("*/*")):
            if not path.is_dir():
                continue
            has_inputs = (path / "Dockerfile").exists() or next(path.glob("*.sh"), None)
            self.assertTrue(
                has_inputs is None or str(path.relative_to(_REPO)) in known,
                f"{path.relative_to(_REPO)}: image inputs but no manifest entry",
            )

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
