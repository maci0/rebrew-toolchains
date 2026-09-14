#!/usr/bin/env python3
"""Prove the generated images are the images that were already here.

Carries its own Dockerfile and wrapper parsers: it must read a file the way
Docker and a shell do, and it must not share that reading with a renderer whose
mistakes it is supposed to catch.

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
import collections
import json
import pathlib
import re
import sys
import tempfile
from typing import TypedDict

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools" / "migrate"))

import gitrev  # noqa: E402

import generate  # noqa: E402

#: Differences this migration *intends*: every entry is checked to be exactly
#: the pin it names, and anything else still fails the run.  The clang images
#: fetched ncurses' libtinfo5 over plaintext http; the same bytes are served
#: over https (sha256 unchanged), so the pin was upgraded while migrating.
ACKNOWLEDGED = dict.fromkeys(
    ("clang-3.9.1", "clang-8.0.0", "clang-9.0.0"), "pin upgraded from http to https (same sha256)"
)


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


# ---------------------------------------------------------------- the parsers
#
# These read a Dockerfile and its wrapper the way Docker and a shell do: line
# continuations joined, comments dropped before that (a comment inside a
# continued `RUN` swallows the rest of the command if you keep it), the
# install steps and the entrypoint's delivery separated.  They were in
# `derive_and_verify.py`, which existed to re-derive recipes from a baseline;
# that tooling is gone and this proof is what needed them.


def instructions(text: str) -> list[str]:
    """The Dockerfile's instructions, joined across line continuations.

    Comments are dropped wherever they appear, including *inside* a multi-line
    instruction, which is what Docker itself does before joining.  Treating one
    as part of the command swallowed everything after it on that command:
    msvc-6.0-sp6 copies `MSPDB60.DLL` next to `CL.EXE` after a comment, and the
    copy — which its wrapper needs — vanished from the derived recipe while the
    comparison, using this same parser, called the result equal.
    """
    out, buf = [], ""
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        buf = f"{buf} {line.strip()}" if buf else line.strip()
        if buf.endswith("\\"):
            buf = buf[:-1].rstrip()
            continue
        out.append(re.sub(r"\s+", " ", buf))
        buf = ""
    if buf:
        out.append(re.sub(r"\s+", " ", buf))
    return out


def wrapper_text(d: pathlib.Path) -> tuple[str, str]:
    sibs = sorted(p for p in d.glob("*.sh") if p.is_file())
    if sibs:
        return sibs[0].name, sibs[0].read_text()
    lines: list[str] = []
    for ins in instructions((d / "Dockerfile").read_text()):
        if ins.startswith("RUN printf "):
            for quoted in re.findall(r"'((?:[^']|'\\'')*)'", ins):
                chunk = quoted.replace("'\\''", "'")
                if not chunk.startswith("%s"):
                    lines.append(chunk)
    return "", "\n".join(lines) + "\n"


class Semantics(TypedDict):
    """The instruction-by-instruction meaning of one Dockerfile + wrapper."""

    base: str
    apt: list[str]
    pins: list[str]
    ops: list[str]
    env: dict[str, str]
    labels: dict[str, str]
    copies: list[str]
    delivery: list[str]
    entrypoint: str


def semantics(d: pathlib.Path) -> Semantics:
    """What the image *does*, independent of formatting or comments."""
    text = (d / "Dockerfile").read_text()
    base = "base"
    apt: list[str] = []
    pins: list[str] = []
    ops: list[str] = []
    env: dict[str, str] = {}
    labels: dict[str, str] = {}
    copies: list[str] = []
    delivery: list[str] = []
    entrypoint = ""
    for ins in instructions(text):
        verb = ins.split(" ", 1)[0].upper()
        if verb == "ARG":
            m = re.match(r"ARG BASE_IMAGE=rebrew/(\S+):", ins)
            if m:
                base = m.group(1)
        elif verb == "ENTRYPOINT":
            m = re.search(r'"(/usr/local/bin/[^"]+)"', ins)
            if m:
                entrypoint = pathlib.Path(m.group(1)).name
        elif verb == "LABEL":
            # Labels are documentation, and documentation nobody compares is
            # documentation that rots; a wrong title/description is a defect
            # like any other.
            labels.update(re.findall(r"(org\.opencontainers\.image\.[a-z]+)=\"([^\"]*)\"", ins))
        elif verb == "COPY":
            # A wrapper that is COPYed from the wrong file, or not COPYed at
            # all, changes the image — the wrapper's *text* is read from the
            # directory, so without this the file could be missing from the
            # image and still compare equal.
            m = re.match(r"COPY\s+(?:--from=\S+\s+)?(\S+)\s+(\S+)", ins)
            if m:
                copies.append(f"{m.group(1)} -> {m.group(2)}")
        elif verb == "ENV":
            env.update(re.findall(r"([A-Z_][A-Z0-9_]*)=(\S+)", ins[4:]))
        elif verb == "RUN":
            body = ins[4:]
            # A printf'd inline wrapper and its trailing `chmod` share one RUN;
            # only the printf itself is wrapper text, the rest is image setup.
            if body.startswith("printf"):
                body = body.split("> /usr/local/bin/", 1)[-1]
                body = body[body.find("&&") + 2 :] if "&&" in body else ""
            if "curl" in body:
                pins += re.findall(r'"(https?://[^"]+)"', body)
            m = re.search(r"apt-get install -y --no-install-recommends ([^&|;]+)", body)
            if m:
                apt += sorted(m.group(1).split())
            for raw_cmd in re.split(r"\s*&&\s*", body):
                cmd = raw_cmd.strip()
                if not cmd or cmd.startswith(("curl ", "echo ", "printf ", "rm ")):
                    continue
                if cmd.startswith("apt-get"):
                    continue
                op = classify(cmd)
                if op is not None and op.get("op") not in {"script", "apt_meta"}:
                    if _is_entrypoint_chmod(op):
                        # counted, not deduped: the entrypoint must be made
                        # executable exactly once, after the COPY that puts it
                        # there.  Deduping this is what hid 53 images whose
                        # install step chmod'd a file that did not exist yet.
                        delivery.append(_norm_op(cmd))
                        continue
                    ops.append(json.dumps(op, sort_keys=True))
                else:
                    ops.append(_norm_op(cmd))
    # repeated idempotent operations are not a difference
    seen: list[str] = []
    for text_op in ops:
        idempotent = any(word in text_op for word in ("mkdir", "rm ", "ls ", "chmod"))
        if text_op in seen and idempotent:
            continue
        seen.append(text_op)
    return {
        "base": base,
        "apt": apt,
        "pins": pins,
        "ops": seen,
        "env": env,
        "labels": labels,
        "copies": copies,
        "delivery": delivery,
        "entrypoint": entrypoint,
    }


def _norm_op(cmd: str) -> str:
    cmd = re.sub(r"/opt/[A-Za-z0-9_.+-]+", "/opt/X", cmd)
    cmd = re.sub(r"/tmp/[A-Za-z0-9_.+-]+", "/tmp/F", cmd)  # noqa: S108  (pattern, not a path)
    return re.sub(r"\s+", " ", cmd)


def classify(cmd: str) -> dict[str, object] | None:
    """One shell command -> one schema op (None = handled elsewhere)."""
    if cmd.startswith(("curl ", "echo ", "printf ")):
        return None
    m = re.match(r"mkdir -p (.+)", cmd)
    if m:
        return {"op": "mkdir", "paths": m.group(1).split()}
    m = re.match(r"tar x(\w)f (\S+) (.+)$", cmd)
    if m and re.search(r"(^| )-C ", m.group(3)):
        flags = m.group(3)
        into = re.search(r"-C (\S+)", flags)
        strip = re.search(r"--strip-components=(\d+)", flags)
        wild = "--wildcards" in flags
        into_dir = into.group(1) if into else ""
        members = [tok for tok in flags.split() if not tok.startswith("-") and tok != into_dir]
        if into:
            op = {
                "op": "tar",
                "compression": {"z": "gz", "J": "xz", "j": "bz2"}.get(m.group(1), "gz"),
                "from": m.group(2),
                "into": into.group(1),
            }
            if strip:
                op["strip"] = int(strip.group(1))
            if members:
                op["members"] = members
            if wild:
                op["wildcards"] = True
            return op
    m = re.match(r"unzip -q (\S+) -d (\S+)", cmd)
    if m:
        return {"op": "unzip", "from": m.group(1), "into": m.group(2)}
    m = re.match(r"cp (-[ar]+) (.+)$", cmd)
    if m:
        parts = m.group(2).split()
        if len(parts) >= 2:
            # `-a` preserves owners and times, `-r` does not: not the same
            # command, so the flag is carried rather than re-chosen.
            return {
                "op": "cp",
                "flags": m.group(1),
                "from": parts[0] if len(parts) == 2 else parts[:-1],
                "into": parts[-1],
            }
    if cmd.startswith("chmod "):
        return {"op": "chmod", "cmd": cmd}
    # The source may be a quoted command substitution containing spaces and a
    # pipeline — `ln -s "$(ldconfig -p | awk '/x/{print $NF; exit}')" /opt/…/y`
    # — so the name is the last token and everything before it is the source.
    # Matching on the first token instead read that command as `ln -s "$(ldconfig
    # -p`, and because the comparison reused this classifier it agreed with
    # itself and called the truncated render equal.
    m = re.match(r"ln -s (.+) (\S+)$", cmd)
    if m:
        return {"op": "link", "target": m.group(1), "name": m.group(2)}
    if cmd.startswith(("ls ", "find ")):
        return {"op": "guard", "cmd": cmd}
    if cmd.startswith("rm "):
        return {"op": "rm", "cmd": cmd}
    if re.match(r"^/opt/\S+ --version", cmd) or cmd.endswith("--version"):
        return {"op": "check_run", "cmd": cmd}
    m = re.match(r"apt-get install -y --no-install-recommends (.+)", cmd)
    if m:
        return {"op": "apt", "packages": m.group(1).split()}
    if cmd.startswith("apt-get"):
        return {"op": "apt_meta", "cmd": cmd}
    return {"op": "script", "run": cmd}


def _is_entrypoint_chmod(op: dict[str, object]) -> bool:
    """True for the `chmod +x /usr/local/bin/<entrypoint>` delivery step."""
    cmd = " ".join(str(part) for part in (op.get("cmd"), op.get("path")) if part)
    return "chmod" in cmd and "/usr/local/bin/" in cmd


#: Clauses that are the same command written by a different mechanism, or that
#: another stage already compares: the download, its in-build hash check, the
#: entrypoint's delivery, and the apt bookkeeping.
_DROPPED_CLAUSES = (
    re.compile(r"^curl -fsSL"),
    re.compile(r'^echo "[0-9a-f]{64} '),
    re.compile(r"^chmod \+x /usr/local/bin/"),
    re.compile(r"^rm -rf /var/lib/apt/lists"),
    re.compile(r"^apt-get (update|install)"),
)


def _canonical_tar(clause: str) -> str:
    """GNU tar reads long options anywhere before the members, so where
    `--strip-components=1` sits relative to `-C` is not part of the command."""
    tokens = clause.split(" ")
    if tokens[0] != "tar":
        return clause
    flags = [token for token in tokens[1:] if token.startswith("--")]
    rest = [token for token in tokens[1:] if not token.startswith("--")]
    return " ".join(["tar", *flags, *rest])


def install_clauses(text: str) -> list[str]:
    """The clauses an image runs to install its toolchain, as written.

    A second, independent comparison to the classified one: this reads the
    clauses as text, so it cannot agree with a renderer by mis-reading a
    command the same way twice.  The classified stage missed a truncated
    `ln -s "$(ldconfig -p | awk …)"` for exactly that reason.
    """
    out: list[str] = []
    for ins in instructions(text):
        # the inline-wrapper RUN of a pre-migration file is wrapper text, and
        # the wrapper is compared as a wrapper
        if not ins.startswith("RUN ") or ins.startswith("RUN printf"):
            continue
        for part in ins[4:].split("&&"):
            clause = re.sub(r"\s+", " ", part).strip()
            if clause and not any(pattern.match(clause) for pattern in _DROPPED_CLAUSES):
                out.append(_canonical_tar(clause))
    return sorted(out)


def wrapper_lines(directory: pathlib.Path) -> list[str]:
    """The wrapper, exactly as written — commands *and* prose.

    Compared as text for the same reason the install clauses are: the
    classified wrapper comparison sorts the tokens of a `rebrew_…` call, which
    would hide a swapped argument, and an argument is the whole point of a
    compiler wrapper.  Comments are kept too (minus the generator's own
    header): the wrapper's prose says how the compiler has to be driven, and a
    generated file that drops a paragraph is a documentation regression, not a
    formatting difference.
    """
    _, text = wrapper_text(directory)
    out: list[str] = []
    buf = ""
    for raw in text.splitlines():
        stripped = re.sub(r"\s+", " ", raw.strip())
        if not stripped or stripped == "#":
            continue
        if stripped.startswith("#!"):
            continue
        if stripped.startswith("#"):
            # prose is its own entry; a comment inside a continued command does
            # not continue it
            if buf:
                out.append(buf)
                buf = ""
            if stripped.startswith((generate.MARKER, "# Entrypoint —", "# shellcheck source=")):
                continue
            out.append(stripped)
            continue
        buf = f"{buf} {stripped}" if buf else stripped
        if buf.endswith("\\"):
            buf = buf[:-1].rstrip()
            continue
        out.append(buf)
        buf = ""
    if buf:
        out.append(buf)
    return out


def _differences(label: str, old: list[str], new: list[str]) -> list[str]:
    """What changed between two line lists, counting duplicates.

    Membership was the wrong test: `line not in new` finds nothing when a line
    was *duplicated*, and `old == new` had already failed — so a wrapper that
    sourced the shared helper twice was reported as no difference at all.
    """
    if old == new:
        return []
    lost = collections.Counter(old) - collections.Counter(new)
    gained = collections.Counter(new) - collections.Counter(old)
    problems = [f"{label} lost: {line}" for line in list(lost.elements())[:4]]
    problems += [f"{label} gained: {line}" for line in list(gained.elements())[:4]]
    return problems or [f"{label}: the same lines in a different order"]


def wrapper_diff(old_dir: pathlib.Path, new_dir: pathlib.Path) -> list[str]:
    return _differences("wrapper line", wrapper_lines(old_dir), wrapper_lines(new_dir))


def clause_diff(old_dir: pathlib.Path, new_dir: pathlib.Path) -> list[str]:
    """Raw install clauses that changed, beyond the ones already accounted for."""
    old = install_clauses((old_dir / "Dockerfile").read_text(encoding="utf-8"))
    new = install_clauses((new_dir / "Dockerfile").read_text(encoding="utf-8"))
    return _differences("clause", sorted(old), sorted(new))


def diff(old_dir: pathlib.Path, new_dir: pathlib.Path) -> list[str]:
    old, new = semantics(old_dir), semantics(new_dir)
    # "copies" is deliberately absent: the old files printf'd the wrapper
    # inline and the generated ones COPY it from a sibling file, so the
    # delivery differs while the wrapper *text* — compared line by line in
    # wrapper_diff() — is identical.  copy_sources() checks the new COPY has a
    # file to copy, which is the failure this would otherwise hide.
    keys = (
        "base",
        "apt",
        "pins",
        "env",
        "labels",
        "delivery",
        "entrypoint",
        "user",
        "workdir",
    )
    out = [
        f"{key}: {old.get(key)!r} -> {new.get(key)!r}"
        for key in keys
        if (key in old or key in new) and old.get(key) != new.get(key)
    ]
    for label, o, n in (("ops", old["ops"], new["ops"]),):
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
    base = gitrev.checkout(args.baseline, tmp / "tree")
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
            problems = (
                diff(old_dir, new_dir)
                + clause_diff(old_dir, new_dir)
                + wrapper_diff(old_dir, new_dir)
                + copy_sources(new_dir)
            )
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
        gitrev.discard(base, tmp)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
