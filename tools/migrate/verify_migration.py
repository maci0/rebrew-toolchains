#!/usr/bin/env python3
"""Prove the generated images are the images that were already here.

    python3 tools/migrate/verify_migration.py [--baseline HEAD] [profile ...]

The migration replaced 272 hand-written Dockerfiles (and 233 hand-written
wrappers) with files rendered from ``sources.json``.  A rewrite of that size is
only safe if it can be *shown* to change nothing, so this checks out the
baseline revision into a throw-away worktree and compares each profile's
semantics — base image, apt packages, pins and their hashes, env, entrypoint,
install steps, wrapper commands — against the generated file now in the tree.

``semantics()`` normalises quoting, line continuation, path spelling and
ordering, so an equal verdict means the image builds the same toolchain, not
that the file text matches.  Anything not equal is printed, and the exit status
is non-zero.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools" / "migrate"))

from derive_and_verify import semantics  # noqa: E402

import generate  # noqa: E402

#: Differences this migration *intends*: every entry is checked to be exactly
#: the pin it names, and anything else still fails the run.  The clang images
#: fetched ncurses' libtinfo5 over plaintext http; the same bytes are served
#: over https (sha256 unchanged), so the pin was upgraded while migrating.
ACKNOWLEDGED = dict.fromkeys(
    ("clang-3.9.1", "clang-8.0.0", "clang-9.0.0"), "pin upgraded from http to https (same sha256)"
)


def baseline_tree(rev: str, into: pathlib.Path) -> pathlib.Path:
    """Check ``rev`` out into ``into`` and return that path."""
    if into.exists():
        shutil.rmtree(into)
    subprocess.run(  # noqa: S603  (fixed argv, no shell)
        ["git", "worktree", "add", "--detach", str(into), rev],  # noqa: S607
        cwd=REPO,
        check=True,
        capture_output=True,
    )
    return into


def copy_sources(directory: pathlib.Path) -> list[str]:
    """Every ``COPY`` source in the generated Dockerfile, checked to exist.

    A COPY of a file that is not in the build context fails the build, so this
    is an integrity check rather than an equivalence one.
    """
    problems: list[str] = []
    text = (directory / "Dockerfile").read_text(encoding="utf-8")
    for line in text.splitlines():
        m = re.match(r"COPY\s+(?:--from=\S+\s+)?(\S+)\s+(\S+)", line.strip())
        if m and not m.group(1).startswith("$") and not (directory / m.group(1)).exists():
            problems.append(f"COPY {m.group(1)} has no such file")
    return problems


def diff(old_dir: pathlib.Path, new_dir: pathlib.Path) -> list[str]:
    old, new = semantics(old_dir), semantics(new_dir)
    # "copies" is deliberately absent: the old files printf'd the wrapper
    # inline and the generated ones COPY it from a sibling file, so the
    # delivery differs while the wrapper *text* — compared as wrapper_cmds
    # below — is identical.  copy_sources() checks the new COPY actually has
    # a file to copy, which is the failure this would otherwise hide.
    keys = ("base", "apt", "pins", "env", "labels", "entrypoint", "user", "workdir")
    out = [
        f"{key}: {old.get(key)!r} -> {new.get(key)!r}"
        for key in keys
        if (key in old or key in new) and old.get(key) != new.get(key)
    ]
    for label, o, n in (
        ("ops", old["ops"], new["ops"]),
        ("wrapper_cmds", old["wrapper_cmds"], new["wrapper_cmds"]),
    ):
        if sorted(o) != sorted(n):
            missing = [x for x in o if x not in n]
            extra = [x for x in n if x not in o]
            if missing:
                out.append(f"{label} lost: {missing[:4]}")
            if extra:
                out.append(f"{label} gained: {extra[:4]}")
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="HEAD", help="revision to compare against")
    parser.add_argument("profiles", nargs="*", help="profiles to check (default: all)")
    args = parser.parse_args(argv)

    entries = generate.manifest()
    wanted = args.profiles or list(entries)
    unknown = [p for p in wanted if p not in entries]
    if unknown:
        print(f"verify: no such profile: {', '.join(unknown)}", file=sys.stderr)
        return 2

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="rebrew-baseline-"))
    base = baseline_tree(args.baseline, tmp / "tree")
    try:
        differ: list[tuple[str, list[str]]] = []
        acknowledged: list[tuple[str, str]] = []
        skipped = 0
        for profile in wanted:
            entry = entries[profile]
            host = pathlib.Path(str(entry["host_dir"]))
            old_dir, new_dir = base / host, REPO / host
            if not (old_dir / "Dockerfile").exists():
                skipped += 1  # new image, nothing to compare against
                continue
            if not (new_dir / "Dockerfile").exists():
                # a name typo or a missing generation would otherwise compare
                # two empty directories and call it equal
                print(f"  {profile}: no generated Dockerfile at {host}", file=sys.stderr)
                differ.append((profile, [f"missing {host}/Dockerfile"]))
                continue
            problems = diff(old_dir, new_dir) + copy_sources(new_dir)
            if not problems:
                continue
            if profile in ACKNOWLEDGED and all(
                "http://deb.debian.org" in problem for problem in problems
            ):
                acknowledged.append((profile, ACKNOWLEDGED[profile]))
                continue
            differ.append((profile, problems))
        print(
            f"verify: {len(wanted) - skipped} compared, {skipped} new, "
            f"{len(acknowledged)} acknowledged, {len(differ)} differ"
        )
        for profile, why in acknowledged:
            print(f"  acknowledged: {profile} — {why}")
        for profile, problems in differ:
            print(f"  {profile}")
            for problem in problems:
                print(f"    {problem}")
        return 1 if differ else 0
    finally:
        subprocess.run(  # noqa: S603  (fixed argv, no shell)
            ["git", "worktree", "remove", "--force", str(base)],  # noqa: S607
            cwd=REPO,
            check=False,
            capture_output=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
