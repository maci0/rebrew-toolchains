#!/usr/bin/env python3
"""generate.py — render every image's Dockerfile and wrapper from sources.json.

The manifest owns everything about a toolchain: its pins, its install recipe,
its entrypoint and its runtime.  This module turns that data into the two files
`docker build` consumes, so the repository has one source of truth instead of
272 hand-maintained copies of the same eight procedures.

    make generate          # rewrite the generated files
    python3 generate.py --check   # fail if a generated file is stale (CI)

Generated files start with a marker line; `--check` re-renders in memory and
compares, so a hand edit cannot survive CI (the same contract the generated
catalog has).

The recipe schema, per profile under `"recipe"`:

    shape       pe | native | cc1 | dosbox | dosemu2 | qemu-irix | pipeline
                (drives the wrapper default and the catalog's runtime column)
    base        base | base-noble | base-dosemu      (the shared base image)
    runner      wine | wibo            (pe only; the default PE loader)
    apt         extra apt packages to install
    fetch       downloads, in order; each references a pin from the manifest:
                {"pin": "primary"|"parser"|"helper"|"sdk"|"binutils"|"extra0..",
                 "as": "/tmp/x.tar.gz"}
    steps       install operations, in order:
                {"op": "tar", "from": ..., "into": ..., "strip": 1,
                 "compression": "gz"|"xz"|"bz2"}
                {"op": "unzip", "from": ..., "into": ..., "subpath": "a/b"}
                {"op": "7z", "from": ..., "into": ...}
                {"op": "cp", "from": "src"|[sources], "into": ...}
                {"op": "mkdir", "paths": [...]}
                {"op": "chmod", "paths": [...]} | {"op": "chmod", "recursive": "/dir"}
                {"op": "link", "target": ..., "name": ...}
                {"op": "guard", "check": "/opt/.../cl.exe"}
                {"op": "check_run", "cmd": "/opt/.../gcc --version"}
                {"op": "script", "run": "..."}      # last resort, discouraged
    env         environment variables for the image
    root        the image's install directory under /opt (defaults to the
                `<version>-<platform>` directory name); unused when `binary` is
                absolute
    binary      path of the compiler, relative to /opt/<root> — or absolute
                when the wrapper reaches a shared prefix (`/opt/cross/bin/gcc`)
    wrapper     {"shape": "passthrough"|"normalising", "validate_source": bool,
                 "set_e": bool,
                 "env": [{"name": ..., "value": ..., "style": "prefix"|"export"}],
                 ...shape parameters}
    handwritten a reason, for the few images whose pipeline is not expressible
                (their Dockerfile and wrapper are left alone)

Anything the schema cannot express must say so via `handwritten`, which a test
counts and lists — silent special cases are what this file exists to prevent.
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent
MARKER = "# Generated from sources.json by generate.py — do not edit; run `make generate`."
CURL = "curl -fsSL --retry 3 --retry-all-errors"
PIN_KEYS = ("parser", "helper", "sdk", "binutils")
BASES = ("base", "base-noble", "base-dosemu")
RUNTIME = {
    "pe": "wine, wibo via `REBREW_RUNNER=wibo`",
    "native": "native",
    "cc1": "native",
    "dosbox": "DOSBox",
    "dosemu2": "dosemu2 (needs `--device /dev/kvm`)",
    "qemu-irix": "native",
    "pipeline": "native",
}


def manifest() -> dict[str, dict[str, object]]:
    text = (REPO / "sources.json").read_text(encoding="utf-8")
    data: dict[str, dict[str, object]] = json.loads(text)
    return data


def _text(entry: dict[str, object], key: str) -> str:
    value = entry.get(key, "")
    return value if isinstance(value, str) else ""


def recipe(entry: dict[str, object]) -> dict[str, object]:
    value = entry.get("recipe", {})
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def pin_urls(entry: dict[str, object]) -> dict[str, tuple[str, str]]:
    """Every pinned download, keyed by the name a recipe refers to."""
    pins = {"primary": (_text(entry, "url"), _text(entry, "sha256"))}
    for key in PIN_KEYS:
        url = _text(entry, f"{key}_url")
        if url:
            pins[key] = (url, _text(entry, f"{key}_sha256"))
    for index, pin in enumerate(_list(entry.get("extra_pins"))):
        if isinstance(pin, dict):
            pins[f"extra{index}"] = (_text(pin, "url"), _text(pin, "sha256"))
    return pins


def _title(entry: dict[str, object]) -> tuple[str, str]:
    rec = recipe(entry)
    if _text(rec, "title"):
        return _text(rec, "title"), _text(rec, "description")
    family = _text(entry, "family")
    version = _text(entry, "host_dir").split("/", 1)[1]
    label = _text(rec, "label") or _text(entry, "family")
    kind = f" ({label})" if label and label != family else ""
    return f"rebrew {family} {version}{kind}", f"{family} {version} toolchain image"


def _require(condition: object, message: str) -> None:
    """Validation that survives `python -O`; `assert` does not."""
    if not condition:
        raise ValueError(message)


def render_dockerfile(profile: str, entry: dict[str, object]) -> str:
    rec = recipe(entry)
    base = _text(rec, "base") or "base"
    _require(base in BASES, f"{profile}: unknown base {base}")
    lines = [MARKER, f"# profile: {profile}", ""]

    if _text(rec, "handwritten"):
        raise ValueError(f"{profile} is marked handwritten and must not be generated")

    lines += [f"ARG BASE_IMAGE=rebrew/{base}:1.0", "", "FROM ${BASE_IMAGE}", "", "USER root", ""]
    title, description = _title(entry)
    lines += [
        'LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \\',
        '      org.opencontainers.image.licenses="MIT" \\',
        f'      org.opencontainers.image.title="{title}" \\',
        f'      org.opencontainers.image.description="{description}"',
        "",
    ]

    apt = [str(p) for p in _list(rec.get("apt"))]
    if apt:
        lines += [
            "RUN apt-get update \\",
            f"    && apt-get install -y --no-install-recommends {' '.join(apt)} \\",
            "    && rm -rf /var/lib/apt/lists/*",
            "",
        ]

    env = rec.get("env")
    if isinstance(env, dict) and env:
        pairs = " \\\n    ".join(f"{k}={v}" for k, v in env.items())
        lines += [f"ENV {pairs}", ""]

    pins = pin_urls(entry)
    fetches = [f for f in _list(rec.get("fetch")) if isinstance(f, dict)]
    steps = [s for s in _list(rec.get("steps")) if isinstance(s, dict)]
    # Downloads run before the install steps, so a download that lands in a
    # directory of its own needs that `mkdir` to happen first — the images did
    # it in the RUN that also downloaded (`mkdir -p /opt/x /tmp/y && curl …`).
    # That step is rendered here and not repeated in the steps RUN below.
    needed = {
        str(pathlib.PurePosixPath(str(f["as"])).parent): index
        for index, f in enumerate(fetches)
        if str(pathlib.PurePosixPath(str(f["as"])).parent) != "/tmp"  # noqa: S108
    }
    early: dict[int, str] = {}
    rest: list[dict[str, object]] = []
    for step in steps:
        paths = [str(p) for p in _list(step.get("paths"))]
        targets = [needed[p] for p in paths if p in needed]
        if step.get("op") == "mkdir" and targets and min(targets) not in early:
            early[min(targets)] = "mkdir -p " + " ".join(paths)
            continue
        rest.append(step)

    for index, fetch in enumerate(fetches):
        name = str(fetch.get("pin", "primary"))
        url, sha = pins.get(name, ("", ""))
        _require(url, f"{profile}: fetch names unknown pin {name}")
        # Every download is verified in-build; a pin with no hash is a manifest
        # gap, not a licence to fetch blind (the image contract test enforces
        # the same rule for the manifest itself).
        _require(sha, f"{profile}: pin {name} has no sha256 in sources.json")
        dest = str(fetch["as"])
        mkdir = f"{early[index]} && " if index in early else ""
        lines += [
            f"RUN {mkdir}{CURL} -o {dest} \\",
            f'        "{url}" \\',
            f'    && echo "{sha}  {dest}" | sha256sum -c -',
            "",
        ]

    steps = rest
    if steps:
        body = _render_steps(profile, steps)
        # One RUN, chained with && and carried by backslashes: a recipe step
        # that is not chained would silently become its own instruction.
        lines += [f"RUN {body[0]} \\"]
        lines += [f"    && {c} \\" for c in body[1:-1]]
        lines.append(f"    && {body[-1]}")
        lines.append("")

    wrapper_file = wrapper_filename(entry)
    lines += [f"COPY {wrapper_file} /usr/local/bin/{entrypoint_name(entry)}"]
    lines += [
        f"RUN chmod +x /usr/local/bin/{entrypoint_name(entry)}",
        "",
        f'ENTRYPOINT ["/usr/local/bin/{entrypoint_name(entry)}"]',
        "",
        "USER rebrew",
        "",
    ]
    return "\n".join(lines)


def install_root(entry: dict[str, object]) -> str:
    """The image's /opt directory — not always the host_dir's tail (agbcc/arm-gba
    installs to /opt/agbcc-agbcc_arm, psp-gcc to /opt/psp-gcc-1.3.1)."""
    rec = recipe(entry)
    return _text(rec, "root") or _text(entry, "host_dir").split("/", 1)[1]


def binary_path(entry: dict[str, object]) -> str:
    binary = _text(recipe(entry), "binary")
    if binary.startswith("/"):
        return binary
    return f"/opt/{install_root(entry)}/{binary}"


def entrypoint_name(entry: dict[str, object]) -> str:
    rec = recipe(entry)
    name = _text(rec, "entrypoint")
    if name:
        return name
    wrapper = rec.get("wrapper")
    if isinstance(wrapper, dict) and _text(wrapper, "name"):
        return _text(wrapper, "name")
    return {"pe": "cl", "native": "cc", "cc1": "cc"}.get(_text(rec, "shape"), "cc")


def wrapper_filename(entry: dict[str, object]) -> str:
    rec = recipe(entry)
    wrapper = rec.get("wrapper")
    name = _text(wrapper, "file") if isinstance(wrapper, dict) else ""
    if not name and _text(rec, "wrapper_file"):
        name = _text(rec, "wrapper_file")
    return name or f"{entrypoint_name(entry)}-wrapper.sh"


def _render_steps(profile: str, steps: list[dict[str, object]]) -> list[str]:
    """Emit the recipe's operations, in order and verbatim.

    The generator never invents commands: `mkdir`, cleanup `rm` and the `ls`
    guards are explicit ops in the recipe, so a generated image is exactly the
    image the recipe describes.  The invariants that matter (every download is
    cleaned up, the compiler binary is guarded) are checked by `validate()`
    rather than silently added here.
    """
    out: list[str] = []
    for step in steps:
        op = _text(step, "op")
        if op == "tar":
            strip = f" --strip-components={step['strip']}" if step.get("strip") else ""
            flag = {"gz": "z", "xz": "J", "bz2": "j"}[_text(step, "compression") or "gz"]
            members = " ".join(str(m) for m in _list(step.get("members")))
            wild = " --wildcards" if step.get("wildcards") else ""
            # Options come before the members: GNU tar reads everything after
            # the first member name as a member, so `tar xzf a.tar b/c --strip-
            # components=1` fails with exit 2 on the option.
            middle = f" {members}" if members else ""
            out.append(f"tar x{flag}f {step['from']}{strip}{wild} -C {step['into']}{middle}")
        elif op == "unzip":
            if step.get("subpath"):
                out.append(
                    f"unzip -q {step['from']} -d {step['into']}"
                    f" && cp -a {step['into']}/{step['subpath']}/. {step['into']}/"
                )
            else:
                out.append(f"unzip -q {step['from']} -d {step['into']}")
        elif op == "7z":
            out.append(f"7z x {step['from']} -o{step['into']} -y")
        elif op == "cp":
            raw = step.get("from")
            sources = raw if isinstance(raw, list) else [raw]
            out.append(f"cp -a {' '.join(str(s) for s in sources)} {step['into']}")
        elif op == "mkdir":
            out.append("mkdir -p " + " ".join(str(p) for p in _list(step.get("paths"))))
        elif op in {"chmod", "guard", "rm"}:
            out.append(str(step["cmd"]))
        elif op == "link":
            out.append(f"ln -s {step['target']} {step['name']}")
        elif op == "check_run":
            out.append(str(step["cmd"]))
        elif op == "script":
            out.append(str(step["run"]))
        else:
            raise ValueError(f"{profile}: unknown step op {op!r}")
    return out


def handwritten_wrapper(entry: dict[str, object]) -> str:
    """The reason this image's wrapper is not generated ("" when it is)."""
    wrapper = recipe(entry).get("wrapper")
    if isinstance(wrapper, dict) and _text(wrapper, "shape") == "handwritten":
        return _text(wrapper, "why") or "no reason given"
    return ""


def render_wrapper(profile: str, entry: dict[str, object]) -> str:
    rec = recipe(entry)
    wrapper = rec.get("wrapper")
    wrapper = wrapper if isinstance(wrapper, dict) else {}
    shape = _text(wrapper, "shape")
    if shape == "handwritten":
        raise ValueError(f"{profile}: wrapper is declared hand-written")
    if shape == "passthrough":
        return _wrapper_passthrough(profile, entry, wrapper)
    if shape == "normalising":
        return _wrapper_normalising(entry, wrapper)
    raise ValueError(f"{profile}: wrapper shape {shape!r} is not expressible; mark it handwritten")


def _head(entry: dict[str, object], what: str) -> list[str]:
    return [
        "#!/bin/sh",
        MARKER,
        f"# {what} — {_text(entry, 'host_dir')}",
        "#",
        "# shellcheck source=base/wrapper-common.sh",
        ". /usr/local/lib/rebrew/wrapper-common.sh",
        "",
    ]


def _wrapper_passthrough(profile: str, entry: dict[str, object], wrapper: dict[str, object]) -> str:
    rec = recipe(entry)
    runner = _text(rec, "runner") or ("wine" if _text(rec, "shape") == "pe" else "exec")
    helper = {"wibo": "rebrew_run", "wine": "rebrew_run", "exec": "rebrew_exec"}[runner]
    binary = _text(rec, "binary")
    _require(binary, f"{profile}: passthrough wrapper needs a binary")
    argv = " ".join(str(a) for a in _list(wrapper.get("argv")))

    lines = _head(entry, "Entrypoint")
    if wrapper.get("set_e"):
        lines.append("set -e")
    if wrapper.get("validate_source"):
        lines.append('rebrew_pick_source "$@"')

    # Wrapper-scoped environment, in the style the image already uses: an
    # `export`ed assignment (visible to everything the wrapper runs) or a
    # command-scoped prefix.  Image-level env belongs in the Dockerfile and is
    # not repeated here.
    exported: list[str] = []
    prefixed: list[str] = []
    for item in _list(wrapper.get("env")):
        if not isinstance(item, dict):
            continue
        name, value = _text(item, "name"), _text(item, "value")
        style = _text(item, "style")
        if style == "export_inline":
            lines.append(f"export {name}={value}")
        elif style == "export":
            lines.append(f"{name}={value}")
            exported.append(name)
        else:
            prefixed.append(f"{name}={value}")
    if exported:
        lines.append("export " + " ".join(exported))

    call = f"{helper} {binary_path(entry)}"
    if argv:
        call = f"{call} {argv}"
    if prefixed:
        for item in prefixed:
            lines.append(f"{item} \\")
    lines.append(f'{call} "$@"')
    return "\n".join(lines) + "\n"


def _wrapper_normalising(entry: dict[str, object], wrapper: dict[str, object]) -> str:
    """-o/-c argv normalisation shared by the compilers that need it."""
    rec = recipe(entry)
    runner = _text(rec, "runner") or ("wine" if _text(rec, "shape") == "pe" else "exec")
    helper = {"wibo": "rebrew_run", "wine": "rebrew_run", "exec": "rebrew_exec"}[runner]
    default_ext = _text(wrapper, "default_extension") or "o"
    compile_flag = _text(wrapper, "compile_flag") or "-c"
    prefix = " ".join(str(a) for a in _list(wrapper.get("argv")))
    lines = _head(entry, "Entrypoint")
    lines += [
        'rebrew_pick_source "$@"',
        "",
        'OUT=""',
        'CC_FLAGS=""',
        'while [ "$#" -gt 0 ]; do',
        '    case "$1" in',
        "        -o)",
        '            [ "$#" -ge 2 ] || rebrew_die "-o requires an output file"',
        '            OUT="$2"',
        "            shift 2",
        "            ;;",
        f"        {compile_flag}) shift ;;",
        '        "$SRC") shift ;;',
        "        *)",
        '            CC_FLAGS="$CC_FLAGS $1"',
        "            shift",
        "            ;;",
        "    esac",
        "done",
        f'[ -n "$OUT" ] || OUT="$STEM.{default_ext}"',
        'case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac',
        'case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac',
        "",
        "extras=",
    ]
    for extra in _list(wrapper.get("convert")):
        lines.append(f"# converter: {extra}")
    lines += [
        "# shellcheck disable=SC2086  # CC_FLAGS is a deliberate flag list, word-split",
        f'{helper} {binary_path(entry)} {prefix} "$CC_FLAGS -o "$OUT_ABS" "$SRC_ABS""',
    ]
    return "\n".join(lines) + "\n"


def generated_paths(entry: dict[str, object]) -> list[pathlib.Path]:
    host = REPO / _text(entry, "host_dir")
    return [host / "Dockerfile", host / wrapper_filename(entry)]


def render_all(entries: dict[str, dict[str, object]]) -> dict[pathlib.Path, str]:
    out: dict[pathlib.Path, str] = {}
    for profile, entry in entries.items():
        if recipe(entry).get("handwritten"):
            continue
        host = REPO / _text(entry, "host_dir")
        out[host / "Dockerfile"] = render_dockerfile(profile, entry)
        if not handwritten_wrapper(entry):
            out[host / wrapper_filename(entry)] = render_wrapper(profile, entry)
    return out


def main(argv: list[str]) -> int:
    entries = manifest()
    try:
        rendered = render_all(entries)
    except (ValueError, AssertionError) as error:
        print(f"generate: {error}", file=sys.stderr)
        return 1
    if "--check" in argv:
        stale = [
            str(path.relative_to(REPO))
            for path, text in rendered.items()
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        if stale:
            print("generate: these files are stale — run `make generate`:", file=sys.stderr)
            for path in stale[:20]:
                print(f"  {path}", file=sys.stderr)
            return 1
        print(f"generate: {len(rendered)} file(s) up to date")
        return 0
    for target, text in rendered.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print(f"generate: wrote {len(rendered)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
