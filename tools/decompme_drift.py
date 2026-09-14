#!/usr/bin/env python3
"""Where this catalogue stands against decomp.me's.

    python3 tools/decompme_drift.py [--values <local values.yaml>] [--quiet]

decomp.me is the compatibility target: a compiler id its front end accepts is
an id a user may arrive with, and `build.sh <alias>` is how they get an image
for it.  Its corpus is public: `decompme/compilers` keeps one image spec per id in
`values.yaml`, so the difference between the two catalogues can be computed
rather than guessed.

It reports which of their ids resolve to an image here, how many of those pin
at least one byte-identical URL (the two projects independently choosing the
same upstream artifact), and which ids do not resolve.  Every gap
has to be declared in ``GAPS`` with a reason: an undeclared one fails the run,
so a corpus change on their side shows up as a failing check rather than as a
silently missing image.

Needs network for their file (``--values`` reads a local copy instead).
The YAML is read with a regex on its two shapes (`file:` and a `- ` list under
`files:`) rather than with PyYAML, which this repo does not depend on.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
VALUES = "https://raw.githubusercontent.com/decompme/compilers/main/values.yaml"

#: decomp.me ids this repo does not provide, each with the reason.  An id that
#: is neither provided nor listed here fails the run.
GAPS = {
    "wibo_dlls": (
        "not a compiler: decomp.me's wibo runtime DLLs; the base image installs wibo itself"
    ),
    "psp-gcc-1.7.1": "the release asset ships a 0-byte as and ld (see GAPS in catalog.py)",
}


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310  (fixed https url)
        body: bytes = response.read()
    return body.decode("utf-8")


def entries(values_yaml: str) -> dict[str, set[str]]:
    """decomp.me's ids and the URLs each one pins.

    Their file reuses URLs through YAML anchors (`- &decomp_dev <url>` at the
    top, `*decomp_dev` in a spec), so the anchors are resolved first: without
    that the shared-pin count silently undercounts by about a third.
    """
    anchors = dict(re.findall(r"- &(\w+) (https?://\S+)", values_yaml))
    out: dict[str, set[str]] = {}
    current = ""
    in_files = False
    for line in values_yaml.splitlines():
        m = re.match(r"\s*- id: (\S+)", line)
        if m:
            current = m.group(1)
            out.setdefault(current, set())
            in_files = False
            continue
        if re.match(r"\s*files:", line):
            in_files = True
            continue
        m = re.match(r"\s*file: (https?://\S+)", line)
        if m and current:
            out[current].add(m.group(1))
            continue
        m = re.match(r"\s*file: \*(\w+)", line)
        if m and current and m.group(1) in anchors:
            out[current].add(anchors[m.group(1)])
            continue
        m = re.match(r"\s*- (https?://\S+)", line)
        if m and current and in_files:
            out[current].add(m.group(1))
            continue
        m = re.match(r"\s*- \*(\w+)", line)
        if m and current and in_files and m.group(1) in anchors:
            out[current].add(anchors[m.group(1)])
    return out


def ours() -> tuple[dict[str, str], set[str]]:
    """What resolves here (`id -> profile`) and every URL the manifest pins."""
    manifest = json.loads((REPO / "sources.json").read_text(encoding="utf-8"))
    resolves: dict[str, str] = {}
    urls: set[str] = set()
    for profile, entry in manifest.items():
        resolves[profile] = profile
        for alias in entry.get("aliases") or []:
            resolves[alias] = profile
        urls.add(entry["url"])
        for key in ("parser", "helper", "sdk", "binutils"):
            if entry.get(f"{key}_url"):
                urls.add(entry[f"{key}_url"])
        for pin in entry.get("extra_pins") or []:
            if pin.get("url"):
                urls.add(pin["url"])
    return resolves, urls


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--values", help="read a local values.yaml instead of fetching")
    args = parser.parse_args(argv)

    theirs = entries(
        pathlib.Path(args.values).read_text(encoding="utf-8") if args.values else fetch(VALUES)
    )
    resolves, urls = ours()

    covered = sorted(i for i in theirs if i in resolves)
    shared = [i for i in covered if theirs[i] & urls]
    missing = sorted(i for i in theirs if i not in resolves)
    undeclared = [i for i in missing if i not in GAPS]

    print(f"decomp.me ids with an image spec: {len(theirs)}")
    print(f"  resolve to an image here:       {len(covered)}")
    print(f"  pin a byte-identical URL:       {len(shared)}")
    print(f"  not provided here:              {len(missing)}")
    for name in missing:
        print(f"    {name}: {GAPS.get(name, 'UNDECLARED GAP')}")
    if undeclared:
        print(
            f"\n{len(undeclared)} decomp.me id(s) neither provided nor declared in GAPS: "
            f"{', '.join(undeclared)}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
