#!/usr/bin/env python3
"""Derive recipes from the existing artifacts and check the generated
replacements against them, semantically.

Migration tooling for the branch that introduces `generate.py` (see REPORT.md
next to this file).  It is not part of `make lint`/`make test` yet: it is
throwaway, it exists to derive the recipe data from files that already work and
to prove that what generation produces is the same image, and it is deleted
once the recipes are in the manifest.

    python3 tools/migrate/derive_and_verify.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, "/home/maci/Desktop/Projects/relumea/rebrew-toolchains")
REPO = pathlib.Path("/home/maci/Desktop/Projects/relumea/rebrew-toolchains")
SHA = r"[0-9a-f]{64}"
import generate


def instructions(text: str) -> list[str]:
    out, buf = [], ""
    for raw in text.splitlines():
        line = raw.rstrip()
        if not buf and (not line.strip() or line.lstrip().startswith("#")):
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
            for chunk in re.findall(r"'((?:[^']|'\\'')*)'", ins):
                chunk = chunk.replace("'\\''", "'")
                if not chunk.startswith("%s"):
                    lines.append(chunk)
    return "", "\n".join(lines) + "\n"


# ---------------------------------------------------------------- semantics

def semantics(d: pathlib.Path) -> dict[str, object]:
    """What the image *does*, independent of formatting or comments."""
    text = (d / "Dockerfile").read_text()
    name, wrapper = wrapper_text(d)
    sem: dict[str, object] = {
        "base": "base",
        "apt": [],
        "pins": [],
        "ops": [],
        "env": {},
        "entrypoint": "",
        "wrapper_cmds": [],
    }
    for ins in instructions(text):
        verb = ins.split(" ", 1)[0].upper()
        if verb == "ARG":
            m = re.match(r"ARG BASE_IMAGE=rebrew/(\S+):", ins)
            if m:
                sem["base"] = m.group(1)
        elif verb == "ENTRYPOINT":
            m = re.search(r'"(/usr/local/bin/[^"]+)"', ins)
            if m:
                sem["entrypoint"] = pathlib.Path(m.group(1)).name
        elif verb == "ENV":
            for k, v in re.findall(r"([A-Z_][A-Z0-9_]*)=(\S+)", ins[4:]):
                sem["env"][k] = v  # type: ignore[index]
        elif verb == "RUN":
            body = ins[4:]
            # A printf'd inline wrapper and its trailing `chmod` share one RUN;
            # only the printf itself is wrapper text, the rest is image setup.
            if body.startswith("printf"):
                body = body.split("> /usr/local/bin/", 1)[-1]
                body = body[body.find("&&") + 2 :] if "&&" in body else ""
            if "curl" in body:
                sem["pins"] += re.findall(r'"(https?://[^"]+)"', body)  # type: ignore[operator]
            m = re.search(r"apt-get install -y --no-install-recommends ([^&|;]+)", body)
            if m:
                sem["apt"] += sorted(m.group(1).split())  # type: ignore[operator]
            for cmd in re.split(r"\s*&&\s*", body):
                cmd = cmd.strip()
                if not cmd or cmd.startswith(("curl ", "echo ", "printf ", "rm ")):
                    continue
                if cmd.startswith("apt-get"):
                    continue
                sem["ops"].append(_norm_op(cmd))  # type: ignore[attr-defined]
    for line in wrapper.splitlines():
        s = line.strip()
        if s.startswith("#") or not s or s in {"fi", "}", "done", ";;"}:
            continue
        sem["wrapper_cmds"].append(_norm_cmd(s))  # type: ignore[attr-defined]
    return sem


def _norm_op(cmd: str) -> str:
    cmd = re.sub(r"/opt/[A-Za-z0-9_.+-]+", "/opt/X", cmd)
    cmd = re.sub(r"/tmp/[A-Za-z0-9_.+-]+", "/tmp/F", cmd)
    cmd = re.sub(r"\s+", " ", cmd)
    if cmd.startswith("tar "):
        head, *rest = cmd.split(" ")
        flags = sorted(r for r in rest if r.startswith("-"))
        args = [r for r in rest if not r.startswith("-")]
        return " ".join([head, *args, *flags])
    return cmd


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
    tmp = pathlib.Path("/tmp/_gen_probe")
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "Dockerfile").write_text(new_df)
    for p in tmp.glob("*.sh"):
        p.unlink()
    (tmp / "cc-wrapper.sh").write_text(new_wr)
    new = semantics(tmp)
    diffs = []
    for key in ("base", "apt", "pins", "env", "entrypoint"):
        if old[key] != new[key]:
            diffs.append(f"{key}: {old[key]!r} -> {new[key]!r}")
    old_ops, new_ops = list(old["ops"]), list(new["ops"])  # type: ignore[arg-type]
    if sorted(old_ops) != sorted(new_ops):
        missing = [o for o in old_ops if o not in new_ops]
        extra = [o for o in new_ops if o not in old_ops]
        diffs.append(f"ops: missing={missing[:3]} extra={extra[:3]}")
    oc, nc = list(old["wrapper_cmds"]), list(new["wrapper_cmds"])  # type: ignore[arg-type]
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
    print(f"profiles with a recipe: {sum(1 for e in manifest.values() if isinstance(e.get('recipe'), dict))}")
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
    if m and " -C " in f" {m.group(3)} ":
        flags = m.group(3)
        into = re.search(r"-C (\S+)", flags)
        strip = re.search(r"--strip-components=(\d+)", flags)
        if into:
            op: dict[str, object] = {
                "op": "tar",
                "compression": {"z": "gz", "J": "xz", "j": "bz2"}.get(m.group(1), "gz"),
                "from": m.group(2),
                "into": into.group(1),
            }
            if strip:
                op["strip"] = int(strip.group(1))
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
    m = re.match(r"ln -s (\S+) (\S+)", cmd)
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


def derive(d: pathlib.Path, entry: dict[str, object]) -> dict[str, object] | None:
    text = (d / "Dockerfile").read_text()
    ins_list = instructions(text)
    rec: dict[str, object] = {"base": "base", "apt": [], "fetch": [], "steps": [], "env": {}}
    pins: list[tuple[str, str, str]] = []          # url, sha, dest
    for ins in ins_list:
        verb = ins.split(" ", 1)[0].upper()
        if verb == "ARG":
            m = re.match(r"ARG BASE_IMAGE=rebrew/(\S+):", ins)
            if m:
                rec["base"] = m.group(1)
        elif verb == "ENV":
            for k, v in re.findall(r"([A-Z_][A-Z0-9_]*)=(\S+)", ins[4:]):
                rec["env"][k] = v  # type: ignore[index]
        elif verb == "RUN":
            body = ins[4:]
            if body.lstrip().startswith("printf"):
                continue
            for url, sha, dest in re.findall(
                rf'curl -fsSL[^"]*"(https?://[^"]+)"\s*&&\s*echo "({SHA})\s+([^"]+)"', body
            ):
                pins.append((url, sha, dest.strip()))
            for cmd in re.split(r"\s*&&\s*", body):
                cmd = cmd.strip()
                if not cmd or cmd.startswith(("curl", "echo")):
                    continue
                op = classify(cmd)
                if op is None:
                    continue
                if op["op"] in {"apt_meta"}:
                    continue
                if op["op"] == "apt":
                    rec["apt"] = op["packages"]  # type: ignore[assignment]
                    continue
                rec["steps"].append(op)  # type: ignore[attr-defined]
    # map each downloaded file to a manifest pin by URL
    known = generate.pin_urls(entry)
    for url, sha, dest in pins:
        name = next((k for k, (u, s) in known.items() if u == url), None)
        if name is None or known[name][1] != sha:
            return None
        rec["fetch"].append({"pin": name, "as": dest})  # type: ignore[attr-defined]
    # entrypoint + wrapper
    entrypoint = ""
    for ins in ins_list:
        if ins.startswith("ENTRYPOINT"):
            m = re.search(r'"(/usr/local/bin/[^"]+)"', ins)
            if m:
                entrypoint = pathlib.Path(m.group(1)).name
    rec["entrypoint"] = entrypoint
    wfile, wtext = wrapper_text(d)
    rec["wrapper_file"] = wfile
    # The install root is what the Dockerfile creates under /opt (it is not the
    # host_dir name for agbcc/arm-gba, ido/7.1, psp-gcc, camelot, ...).
    roots = [p for step in rec["steps"] if step.get("op") == "mkdir" for p in step["paths"] if p.startswith("/opt/")]  # type: ignore[attr-defined]
    root = roots[0][len("/opt/"):] if roots else str(entry["host_dir"]).split("/", 1)[1]
    rec["root"] = root
    classified = classify_wrapper(rec, entry, wtext)
    if classified is None:
        return None
    shape, path_root, binary = classified
    rec["binary"] = binary
    rec["runner"] = shape.pop("runner", "wibo" if "rebrew_run" in wtext else "exec")
    rec["wrapper"] = shape
    return rec


def classify_wrapper(rec: dict[str, object], entry: dict[str, object], wtext: str) -> dict[str, object] | None:
    body = [l.strip() for l in wtext.splitlines() if l.strip() and not l.strip().startswith("#")]
    body = [l for l in body if l not in {". /usr/local/lib/rebrew/wrapper-common.sh", "set -e", "#!/bin/sh"}]
    exec_line = next((l for l in body if "rebrew_exec" in l or "rebrew_run" in l), "")
    if not exec_line:
        return None
    m = re.search(r"(rebrew_exec|rebrew_run) (/opt/\S+)", exec_line)
    if not m:
        return None
    helper, path = m.group(1), m.group(2)
    root = str(rec["root"])
    if not path.startswith(f"/opt/{root}/"):
        # a shared prefix such as /opt/cross: keep the absolute path
        root = ""
    tail = exec_line.split(path, 1)[1].strip()
    if not tail.endswith('"$@"'):
        return None
    argv = tail[: -len('"$@"')].strip().split()
    # everything else in the body must be a simple assignment or be nothing
    other = [l for l in body if l != exec_line]
    if any("rebrew_" in l for l in other):
        return None
    wrap_env: list[dict[str, str]] = []
    exported: set[str] = set()
    for line in other:
        if re.match(r"export [A-Z_][A-Z0-9_ ]*$", line):
            exported |= set(line.split()[1:])
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
    if wrap_env:
        shape_env = wrap_env
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
