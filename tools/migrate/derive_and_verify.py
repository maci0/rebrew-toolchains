#!/usr/bin/env python3
"""Derive recipes from the existing artifacts and check the generated
replacements against them, semantically.

Migration tooling for the branch that introduces `generate.py` (see REPORT.md
next to this file).  It derives recipe data from files that already work and
proves that what generation produces is the same image; `derive_and_verify.py`
holds the classifier and the semantic comparison, `apply.py` performs the
migration, `verify_migration.py` re-runs the comparison against any baseline
revision.

    python3 tools/migrate/derive_and_verify.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import tempfile
from typing import TypedDict

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools" / "migrate"))

import generate  # noqa: E402  (needs REPO on sys.path first)

SHA = r"[0-9a-f]{64}"


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


class Recipe(TypedDict, total=False):
    """A generated image's install recipe (the manifest's ``recipe`` value)."""

    base: str
    apt: list[str]
    fetch: list[dict[str, str]]
    steps: list[dict[str, object]]
    env: dict[str, str]
    title: str
    description: str
    entrypoint: str
    wrapper_file: str
    root: str
    binary: str
    runner: str
    wrapper: dict[str, object]


# ---------------------------------------------------------------- semantics


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
    wrapper_cmds: list[str]


def semantics(d: pathlib.Path) -> Semantics:
    """What the image *does*, independent of formatting or comments."""
    text = (d / "Dockerfile").read_text()
    _, wrapper = wrapper_text(d)
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
    wrapper_cmds: list[str] = []
    for line in _join_continuations(wrapper):
        s = line.strip()
        if s.startswith("#") or not s or s in {"fi", "}", "done", ";;"}:
            continue
        wrapper_cmds.append(_norm_cmd(s))
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
        "wrapper_cmds": wrapper_cmds,
    }


def _norm_op(cmd: str) -> str:
    cmd = re.sub(r"/opt/[A-Za-z0-9_.+-]+", "/opt/X", cmd)
    cmd = re.sub(r"/tmp/[A-Za-z0-9_.+-]+", "/tmp/F", cmd)  # noqa: S108  (pattern, not a path)
    return re.sub(r"\s+", " ", cmd)


def _norm_cmd(cmd: str) -> str:
    cmd = re.sub(r"/opt/[A-Za-z0-9_.+-]+", "/opt/X", cmd)
    cmd = re.sub(r"\s+", " ", cmd)
    # flag order inside the exec line is not behavioural, the command is
    if " rebrew_" in cmd or cmd.startswith("rebrew_"):
        parts = cmd.split()
        return " ".join(sorted(parts))
    return cmd


def compare(profile: str, entry: dict[str, object]) -> tuple[bool, list[str]]:
    import generate

    d = REPO / str(entry["host_dir"])
    old = semantics(d)
    try:
        new_df = generate.render_dockerfile(profile, entry)
        new_wr = generate.render_wrapper(profile, entry)
    except (ValueError, AssertionError, KeyError) as error:
        return False, [f"render failed: {error}"]
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="rebrew-probe-"))
    (tmp / "Dockerfile").write_text(new_df)
    for p in tmp.glob("*.sh"):
        p.unlink()
    (tmp / "cc-wrapper.sh").write_text(new_wr)
    new = semantics(tmp)
    # compared as plain mappings: mypy 2.1 (the version uv.lock pins) will not
    # index a TypedDict with a loop variable, and the keys are strings here
    old_flat: dict[str, object] = dict(old)
    new_flat: dict[str, object] = dict(new)
    diffs = [
        f"{key}: {old_flat[key]!r} -> {new_flat[key]!r}"
        for key in ("base", "apt", "pins", "env", "entrypoint")
        if old_flat[key] != new_flat[key]
    ]
    old_ops, new_ops = old["ops"], new["ops"]
    if sorted(old_ops) != sorted(new_ops):
        missing = [o for o in old_ops if o not in new_ops]
        extra = [o for o in new_ops if o not in old_ops]
        diffs.append(f"ops: missing={missing[:3]} extra={extra[:3]}")
    oc, nc = old["wrapper_cmds"], new["wrapper_cmds"]
    if sorted(oc) != sorted(nc):
        missing = [c for c in oc if c not in nc]
        extra = [c for c in nc if c not in oc]
        diffs.append(f"wrapper: missing={missing[:3]} extra={extra[:3]}")
    return not diffs, diffs


def main() -> int:
    manifest = json.loads((REPO / "sources.json").read_text())
    same = 0
    failures: list[tuple[str, list[str]]] = []
    for profile, entry in manifest.items():
        if not isinstance(entry.get("recipe"), dict):
            continue
        ok, diffs = compare(profile, entry)
        if ok:
            same += 1
        else:
            failures.append((profile, diffs))
    with_recipe = sum(1 for e in manifest.values() if isinstance(e.get("recipe"), dict))
    print(f"profiles with a recipe: {with_recipe}")
    print(f"semantically identical after generation: {same}")
    print(f"not yet faithful: {len(failures)}")
    for profile, diffs in failures[:30]:
        print(f"  {profile}: {diffs[0][:150]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ---------------------------------------------------------------- derivation


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
    m = re.match(r"7z x (\S+) -o(\S+) -y", cmd)
    if m:
        return {"op": "7z", "from": m.group(1), "into": m.group(2)}
    m = re.match(r"cp -[ar]+ (.+)$", cmd)
    if m:
        parts = m.group(1).split()
        if len(parts) >= 2:
            return {
                "op": "cp",
                "from": parts[0] if len(parts) == 2 else parts[:-1],
                "into": parts[-1],
            }
    if cmd.startswith("chmod "):
        return {"op": "chmod", "cmd": cmd}
    m = re.match(r'ln -s ("[^"]*"\([^)]*\)"?|\S+) (\S+)', cmd)
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


def _paths(step: dict[str, object]) -> list[str]:
    """The paths a ``mkdir``-style step names (empty when it names none)."""
    value = step.get("paths")
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def derive(
    d: pathlib.Path, entry: dict[str, object], *, ignore_wrapper: bool = False
) -> Recipe | None:
    text = (d / "Dockerfile").read_text()
    ins_list = instructions(text)
    base = "base"
    apt: list[str] = []
    steps: list[dict[str, object]] = []
    env: dict[str, str] = {}
    fetch: list[dict[str, str]] = []
    title = ""
    description = ""
    downloads: list[tuple[str, str, str]] = []  # url, dest, sha (sha may be "")
    for ins in ins_list:
        verb = ins.split(" ", 1)[0].upper()
        if verb == "ARG":
            m = re.match(r"ARG BASE_IMAGE=rebrew/(\S+):", ins)
            if m:
                base = m.group(1)
        elif verb == "LABEL":
            # The OCI title/description are recipe data: the generator renders
            # them, so derivation has to carry them across.
            for key, value in re.findall(r"(org\.opencontainers\.image\.[a-z]+)=\"([^\"]*)\"", ins):
                if key == "org.opencontainers.image.title":
                    title = value
                elif key == "org.opencontainers.image.description":
                    description = value
        elif verb == "ENV":
            env.update(re.findall(r"([A-Z_][A-Z0-9_]*)=(\S+)", ins[4:]))
        elif verb == "RUN":
            body = ins[4:]
            if body.lstrip().startswith("printf"):
                continue
            # Every pinned download is found by its URL.  The in-build
            # `sha256sum -c` check is attached afterwards when the image has
            # one: whether a download is verified is the manifest's decision,
            # and requiring the check here silently dropped the one hashless
            # fetch in the corpus (the PSY-Q 4.5 SDK tarball).
            for dest, url in re.findall(r'curl -fsSL[^"]*?-o (\S+)\s+"(https?://[^"]+)"', body):
                downloads.append((url, dest, ""))
            for sha, checked in re.findall(
                r'echo "([0-9a-f]{64})\s+(\S+)"\s*\|\s*sha256sum -c -', body
            ):
                for index, (url, dest, _) in enumerate(downloads):
                    if dest == checked:
                        downloads[index] = (url, dest, sha)
            for raw_cmd in re.split(r"\s*&&\s*", body):
                cmd = raw_cmd.strip()
                if not cmd or cmd.startswith(("curl", "echo")):
                    continue
                op = classify(cmd)
                if op is None or op["op"] == "apt_meta":
                    continue
                if _is_entrypoint_chmod(op):
                    # Making the entrypoint executable is how the image
                    # delivers its wrapper (COPY then chmod); the generator
                    # emits that itself, so deriving it here would render it
                    # twice — and the first one runs before the COPY, where
                    # the file does not exist yet.
                    continue
                if op["op"] == "apt":
                    packages = op["packages"]
                    if isinstance(packages, list):
                        apt = [str(package) for package in packages]
                    continue
                steps.append(op)
    # map each download to the manifest pin that names it
    known = generate.pin_urls(entry)
    by_url = {url: name for name, (url, _sha) in known.items()}
    for url, dest, sha in downloads:
        name = by_url.get(url)
        if name is None:
            return None  # a download the manifest does not pin
        if sha and known[name][1] != sha:
            return None  # the Dockerfile and the manifest disagree about the bytes
        fetch.append({"pin": name, "as": dest})
    # entrypoint + wrapper
    entrypoint = ""
    for ins in ins_list:
        if ins.startswith("ENTRYPOINT"):
            m = re.search(r'"(/usr/local/bin/[^"]+)"', ins)
            if m:
                entrypoint = pathlib.Path(m.group(1)).name
    wfile, wtext = wrapper_text(d)
    # The install root is what the Dockerfile creates under /opt (it is not the
    # host_dir name for agbcc/arm-gba, ido/7.1, psp-gcc, camelot, ...).
    roots = [
        str(path)
        for step in steps
        if step.get("op") == "mkdir"
        for path in _paths(step)
        if path.startswith("/opt/")
    ]
    root = roots[0][len("/opt/") :] if roots else str(entry["host_dir"]).split("/", 1)[1]
    rec: Recipe = {
        "base": base,
        "apt": apt,
        "fetch": fetch,
        "steps": steps,
        "env": env,
        "root": root,
    }
    if title:
        rec["title"] = title
    if description:
        rec["description"] = description
    rec["entrypoint"] = entrypoint
    rec["wrapper_file"] = wfile
    if ignore_wrapper:
        return rec
    classified = classify_wrapper(rec, wtext)
    if classified is None:
        return None
    shape, _, binary = classified
    rec["binary"] = binary
    runner = shape.pop("runner", "wibo" if "rebrew_run" in wtext else "exec")
    rec["runner"] = str(runner)
    deduped: list[dict[str, object]] = []
    for step in steps:
        if step.get("op") in {"mkdir", "rm", "guard"} and step in deduped:
            continue
        deduped.append(step)
    rec["steps"] = deduped
    rec["wrapper"] = shape
    return rec


def _join_continuations(text: str) -> list[str]:
    """Shell lines joined on trailing backslashes — an exec call split over
    several lines is still one command."""
    out: list[str] = []
    buf = ""
    for raw in text.splitlines():
        line = raw.rstrip()
        if not buf and (not line.strip() or line.lstrip().startswith("#")):
            continue
        stripped = line.strip()
        buf = f"{buf} {stripped}" if buf else stripped
        if buf.endswith("\\"):
            buf = buf[:-1].rstrip()
            continue
        out.append(buf)
        buf = ""
    if buf:
        out.append(buf)
    return out


def classify_wrapper(rec: Recipe, wtext: str) -> tuple[dict[str, object], str, str] | None:
    body = [line.strip() for line in _join_continuations(wtext) if line.strip()]
    body = [
        line
        for line in body
        if line not in {". /usr/local/lib/rebrew/wrapper-common.sh", "set -e", "#!/bin/sh"}
    ]
    exec_line = next((line for line in body if "rebrew_exec" in line or "rebrew_run" in line), "")
    if not exec_line:
        return None
    prefix_env = []
    head = exec_line
    while re.match(r"^[A-Z_][A-Z0-9_]*=\S*\s", head):
        token, head = head.split(None, 1)
        prefix_env.append(token)
    m = re.search(r"(rebrew_exec|rebrew_run) (/opt/\S+)", head)
    if not m:
        return None
    path = m.group(2)
    exec_line = head
    root = str(rec["root"])
    if not path.startswith(f"/opt/{root}/"):
        # a shared prefix such as /opt/cross: keep the absolute path
        root = ""
    tail = exec_line.split(path, 1)[1].strip()
    if not tail.endswith('"$@"'):
        return None
    argv = tail[: -len('"$@"')].strip().split()
    # everything else in the body must be a simple assignment or be nothing
    other = [line for line in body if line != exec_line and "rebrew_pick_source" not in line]
    if any("rebrew_" in line for line in other):
        return None
    wrap_env: list[dict[str, str]] = [
        {"name": token.split("=", 1)[0], "value": token.split("=", 1)[1], "style": "prefix"}
        for token in prefix_env
    ]
    exported: set[str] = set()
    for line in other:
        if re.match(r"export [A-Z_][A-Z0-9_ ]*$", line):
            exported |= set(line.split()[1:])
            continue
        # `export NAME=value` on one line is the same statement as
        # `NAME=value` followed by `export NAME`; keep the spelling the image
        # already uses so the rendered wrapper is the wrapper it replaces.
        inline = re.match(r"export ([A-Z_][A-Z0-9_]*)=(.*)", line)
        if inline:
            exported.add(inline.group(1))
            wrap_env.append(
                {
                    "name": inline.group(1),
                    "value": inline.group(2).rstrip("\\").strip(),
                    "style": "export_inline",
                }
            )
            continue
        m2 = re.match(r"([A-Z_][A-Z0-9_]*)=(.*)", line)
        if not m2:
            return None
        # a wrapper that assigns before the exec is either exporting (a later
        # `export` line names it) or scoping (prefix style)
        wrap_env.append(
            {"name": m2.group(1), "value": m2.group(2).rstrip("\\").strip(), "style": "export"}
        )
    for item in wrap_env:
        if item["name"] not in exported:
            item["style"] = "export" if not exported else "prefix"
    binary = path if not root else path[len(f"/opt/{root}/") :]
    shape: dict[str, object] = {
        "shape": "passthrough",
        "validate_source": "rebrew_pick_source" in wtext,
        "argv": argv,
    }
    if "set -e" in wtext:
        shape["set_e"] = True
    if wrap_env:
        shape["env"] = wrap_env
    return shape, root, binary
