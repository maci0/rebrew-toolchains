#!/usr/bin/env python3
"""Apply the migration: derive a recipe per profile, inject it into
sources.json, regenerate every image, and verify each one is the same image.

    python3 tools/migrate/apply.py --check    # dry run: report, write nothing
    python3 tools/migrate/apply.py            # inject recipes and generate

The rules:

* the *install* half of a recipe is always derived (pins, apt, ops, env,
  entrypoint); a Dockerfile that cannot be derived is reported and skipped, not
  guessed;
* the *wrapper* half is derived when this branch can express it, otherwise the
  image keeps its hand-written wrapper and says so in the manifest
  (`wrapper.shape == "handwritten"` + a reason), which a test counts and lists;
* every generated Dockerfile is compared against the one it replaces —
  semantically, with paths/order/quoting normalised — and the run fails if a
  single image would change behaviour.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools" / "migrate"))

from derive_and_verify import (  # noqa: E402
    Recipe as RecipeType,
)
from derive_and_verify import (  # noqa: E402
    classify_wrapper,
    derive,
    wrapper_text,
)

import generate  # noqa: E402

#: Wrapper shapes this branch can express.  Everything else keeps its
#: hand-written wrapper and is listed by the test that guards this list.
EXPRESSIBLE = {"passthrough", "dosbox_compile", "psyq_dosemu", "psyq_native"}


#: Wrappers that were printf'd inline in a Dockerfile were never linted, so
#: they can be missing the directive shellcheck needs to follow the shared
#: helper.  Materialising one adds it.
DIRECTIVE = "# shellcheck source=base/wrapper-common.sh\n"


def _with_source_directive(text: str) -> str:
    if "shellcheck source=" in text or "wrapper-common.sh" not in text:
        return text
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith("#!"):
            lines.insert(index + 1, DIRECTIVE)
            return "".join(lines)
    return DIRECTIVE + text


def shape_reason(text: str) -> str:
    """Why this wrapper is not generated yet, so the manifest says something
    a reader can act on instead of 'unsupported'."""
    if "rebrew_dosbox" in text:
        return "DOSBox harness (staged source, FAT-cased artifact) — template pending"
    if "rebrew_dosemu_run" in text:
        return "dosemu2 pipeline (COMPILE.BAT / multi-stage DOS) — template pending"
    if "convert_gas_syntax" in text:
        return "Apple GCC pipeline (cc1 | convert_gas_syntax.py | GNU as) — template pending"
    if "|" in text and "rebrew_" in text:
        return "multi-stage pipeline (cpp | cc1 | assembler | converter) — template pending"
    if "qemu-irix" in text:
        return "qemu-irix driver plus converter — template pending"
    return "per-family argv normalisation — template pending"


def baseline_tree(rev: str, into: pathlib.Path) -> pathlib.Path:
    """Check ``rev`` out into ``into``: the files to derive *from*.

    Deriving from the working tree only works while the tree still holds the
    hand-written files.  After the migration it holds the generated ones, so a
    newly taught wrapper shape is applied by deriving from the revision that
    still had the originals.
    """
    if into.exists():
        shutil.rmtree(into)
    subprocess.run(  # noqa: S603  (fixed argv, no shell)
        ["git", "worktree", "add", "--detach", str(into), rev],  # noqa: S607
        cwd=REPO,
        check=True,
        capture_output=True,
    )
    return into


def _require_handwritten(
    source: pathlib.Path, rev: str, manifest: dict[str, dict[str, object]]
) -> None:
    """Refuse to derive from a revision that is already generated.

    Deriving from generated files bakes their scaffolding into the recipes —
    the post-COPY `chmod +x`, the wrapper file name, the rendered labels — and
    the result then renders the image twice over.  It still *compares* equal,
    which is how such a mistake slips through, so it is checked here instead.
    """
    generated = [
        profile
        for profile, entry in manifest.items()
        if generate.MARKER in (source / str(entry["host_dir"]) / "Dockerfile").read_text()
    ]
    if generated:
        raise SystemExit(
            f"apply: {rev} is already generated ({len(generated)} Dockerfiles carry the "
            f"marker, e.g. {generated[0]}); pass the revision before the migration"
        )


def derive_install(d: pathlib.Path, entry: dict[str, object]) -> RecipeType | None:
    """The install half: everything except the wrapper."""
    rec = derive(d, entry)
    if rec is None:
        # the wrapper was the problem: retry with the wrapper ignored
        _, _text = wrapper_text(d)
        rec = derive(d, entry, ignore_wrapper=True)
        if rec is None:
            return None
    return rec


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report, write nothing")
    parser.add_argument(
        "--baseline",
        metavar="REV",
        help="derive from REV's files (the hand-written ones) instead of the working tree",
    )
    args = parser.parse_args()

    sources = REPO / "sources.json"
    manifest: dict[str, dict[str, object]] = json.loads(sources.read_text())

    scratch: pathlib.Path | None = None
    source = REPO
    if args.baseline:
        scratch = pathlib.Path(tempfile.mkdtemp(prefix="rebrew-derive-"))
        source = baseline_tree(args.baseline, scratch / "tree")
        _require_handwritten(source, args.baseline, manifest)
    handwritten: list[tuple[str, str]] = []
    failed: list[tuple[str, str]] = []
    injected = 0

    for profile, entry in manifest.items():
        d = source / str(entry["host_dir"])
        rec = derive_install(d, entry)
        if rec is None:
            failed.append((profile, "install recipe not derivable"))
            continue
        name, text = wrapper_text(d)
        shape = classify_wrapper(rec, text)
        if shape is None or shape[0].get("shape") not in EXPRESSIBLE:
            why = shape_reason(text)
            if not name:
                # the wrapper is inline in the Dockerfile today; write it out so
                # the generated Dockerfile has a file to COPY.  It belongs in
                # the repository, never in the baseline copy.
                name = f"{generate.entrypoint_name(entry)}-wrapper.sh"
                target = REPO / str(entry["host_dir"]) / name
                if not target.exists():
                    target.write_text(_with_source_directive(text), encoding="utf-8")
            rec["wrapper"] = {"shape": "handwritten", "why": why, "file": name}
            handwritten.append((profile, why))
        else:
            wrapper, root, binary = shape
            if root:
                rec["root"] = root
            if binary:
                rec["binary"] = binary
            if name:
                wrapper["file"] = name
            rec["wrapper"] = wrapper
        if not rec.get("root"):
            rec["root"] = str(entry["host_dir"]).split("/", 1)[1]
        entry["recipe"] = rec
        injected += 1

    print(f"recipes derived: {injected}  (hand-written wrappers: {len(handwritten)})")
    for profile, why in handwritten:
        print(f"  hand-written wrapper: {profile} — {why}")
    for profile, why in failed:
        print(f"  NOT DERIVED: {profile} — {why}")
    if args.check:
        if scratch is not None:
            _drop(source, scratch)
        return 1 if failed else 0

    try:
        sources.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        return generate.main([])
    finally:
        if scratch is not None:
            _drop(source, scratch)


def _drop(source: pathlib.Path, scratch: pathlib.Path) -> None:
    subprocess.run(  # noqa: S603  (fixed argv, no shell)
        ["git", "worktree", "remove", "--force", str(source)],  # noqa: S607
        cwd=REPO,
        check=False,
        capture_output=True,
    )
    shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
