#!/usr/bin/env python3
"""check_pins.py — verify every pinned download still exists.

`make lint`/`make test` prove the manifest and the images agree; none of them
can notice that an upstream *deleted* an asset (PPAs republish and prune old
builds, GitHub release tags get retagged, `files.decomp.dev` rotates dated
bundles).  This is the check that notices: it asks each pinned URL for its
headers and fails on anything that is no longer there.

It covers the manifest's pins *and* the shared base images' pins.  It did not,
and the dosemu2 PPA pruned the build `base-dosemu` had pinned while four
weekly runs looked elsewhere: the image could not be built by anything, which
the smoke job found before this check did.

Deliberately not part of `make test`: it needs the network, and a transient
outage must not look like a broken manifest.  Run it by hand (`make pins`) or
on the weekly schedule in .github/workflows/pins.yml.

Usage:  python3 tests/check_pins.py [profile ...]
Exit:   0 all pinned URLs resolve, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TIMEOUT_SECONDS = 20
#: Some hosts (Launchpad, codeload) reject HEAD; fall back to a ranged GET.
_FALLBACK_STATUS = (403, 405, 501)


def _request(url: str, method: str) -> tuple[int, str]:
    """Return (status, reason); status 0 means the request could not be made."""
    # S310: the URLs are our own manifest's, all https; the rule exists to stop
    # `file:`/custom schemes reaching urlopen.
    request = urllib.request.Request(url, method=method)  # noqa: S310
    if method == "GET":
        request.add_header("Range", "bytes=0-0")
    request.add_header("User-Agent", "rebrew-toolchains-pin-check")
    try:
        with urllib.request.urlopen(  # noqa: S310  (same manifest-sourced URLs)
            request, timeout=TIMEOUT_SECONDS
        ) as response:
            return int(response.status), str(response.reason)
    except urllib.error.HTTPError as error:
        return int(error.code), str(error.reason)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return 0, str(error)


#: 404/410 mean the asset is gone; anything else is worth one more try, since a
#: single flaky URL backs several profiles and would otherwise fail them all.
_GONE = (404, 410)
_ATTEMPTS = 3


def check(url: str) -> str | None:
    """None when the URL resolves, else a one-line reason."""
    problem = "not attempted"
    for attempt in range(_ATTEMPTS):
        status, reason = _request(url, "HEAD")
        if status in _FALLBACK_STATUS:
            status, reason = _request(url, "GET")
        if 200 <= status < 400:
            return None
        if status in _GONE:
            return f"HTTP {status} {reason}"
        problem = f"unreachable: {reason}" if status == 0 else f"HTTP {status} {reason}"
        if attempt + 1 < _ATTEMPTS:
            time.sleep(2 * (attempt + 1))
    return problem


def base_pins() -> list[tuple[str, str]]:
    """Every URL the shared base images download, labelled by their directory.

    These images are not in the manifest — they are built first, by `build.sh`,
    and everything else inherits them — so a pruned pin there breaks the whole
    matrix and no manifest check can see it.
    """
    pins: list[tuple[str, str]] = []
    for dockerfile in sorted(REPO.glob("base*/Dockerfile")):
        text = re.sub(r"\\\s*\n\s*", " ", dockerfile.read_text(encoding="utf-8"))
        pins.extend(
            (dockerfile.parent.name, url)
            for url in re.findall(r'curl[^"]*"(https?://[^"]+)"', text)
        )
    return pins


def main(argv: list[str]) -> int:
    sys.path.insert(0, str(REPO))
    import catalog

    manifest = catalog.manifest()
    wanted = set(argv)
    checked = 0
    failures: list[tuple[str, str, str]] = []
    for profile, entry in manifest.items():
        if wanted and profile not in wanted:
            continue
        for url in catalog.urls_of(entry):
            checked += 1
            problem = check(url)
            if problem is None:
                print(f"ok   {profile:28s} {url}")
            else:
                print(f"FAIL {profile:28s} {url} ({problem})")
                failures.append((profile, url, problem))
    for label, url in base_pins():
        if wanted and label not in wanted:
            continue
        checked += 1
        problem = check(url)
        if problem is None:
            print(f"ok   {label:28s} {url}")
        else:
            print(f"FAIL {label:28s} {url} ({problem})")
            failures.append((label, url, problem))
    failing_urls = {url for _label, url, _problem in failures}
    print(
        f"\n{checked} pinned URL(s) checked, {len(failures)} failing "
        f"({len(failing_urls)} distinct failing URLs)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
