#!/usr/bin/env python3
"""Check a revision out into a throw-away worktree, and clean it up again.

Both migration tools derive or compare against a revision that is *not* the
working tree — `apply.py` against the last revision that held the hand-written
files, `verify_migration.py` against the revision those files are compared
with.  They had their own copies of this, already divergent (one explained a
missing revision, the other did not), and `apply.py` created the worktree
*before* validating the revision, so a rejected argument leaked a checkout into
`.git/worktrees` and `/tmp`.  It is one function now, and the caller is
expected to hold it in a `try`/`finally`.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]


def checkout(rev: str, into: pathlib.Path) -> pathlib.Path:
    """Check ``rev`` out into ``into`` and return it.

    A shallow clone does not have the revision at all, and `git worktree add`
    answers that with a bare exit 128, so the revision is checked first.
    """
    known = subprocess.run(  # noqa: S603  (fixed argv, no shell)
        ["git", "cat-file", "-e", f"{rev}^{{commit}}"],  # noqa: S607
        cwd=REPO,
        check=False,
        capture_output=True,
    )
    if known.returncode:
        raise SystemExit(
            f"{rev} is not in this clone — a shallow checkout hides it, so fetch "
            f"the full history or pass another revision"
        )
    if into.exists():
        shutil.rmtree(into)
    subprocess.run(  # noqa: S603  (fixed argv, no shell)
        ["git", "worktree", "add", "--detach", str(into), rev],  # noqa: S607
        cwd=REPO,
        check=True,
        capture_output=True,
    )
    return into


def discard(tree: pathlib.Path, scratch: pathlib.Path) -> None:
    """Remove the worktree and the temporary directory that held it."""
    subprocess.run(  # noqa: S603  (fixed argv, no shell)
        ["git", "worktree", "remove", "--force", str(tree)],  # noqa: S607
        cwd=REPO,
        check=False,
        capture_output=True,
    )
    shutil.rmtree(scratch, ignore_errors=True)
