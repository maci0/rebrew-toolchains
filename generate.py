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
                {"op": "unzip", "from": ..., "into": ...}
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
                (their Dockerfile and wrapper are left alone)

Anything the schema cannot express is a `wrapper.shape` of `handwritten`, which a test
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


def _title(profile: str, entry: dict[str, object]) -> tuple[str, str]:
    """The image's OCI labels.

    They are recipe data because they are documentation — what the image is and
    where it came from — and every profile carries them.  The old fallback
    rendered the directory name, which is a worse label nobody chose; a missing
    one is a manifest gap, and the manifest is expected to say so.
    """
    rec = recipe(entry)
    title, description = _text(rec, "title"), _text(rec, "description")
    _require(title, f"{profile}: recipe has no title")
    _require(description, f"{profile}: recipe has no description")
    return title, description


def _require(condition: object, message: str) -> None:
    """Validation that survives `python -O`; `assert` does not."""
    if not condition:
        raise ValueError(message)


def render_dockerfile(profile: str, entry: dict[str, object]) -> str:
    rec = recipe(entry)
    base = _text(rec, "base") or "base"
    _require(base in BASES, f"{profile}: unknown base {base}")
    lines = [MARKER, f"# profile: {profile}", ""]

    lines += [f"ARG BASE_IMAGE=rebrew/{base}:1.0", "", "FROM ${BASE_IMAGE}", "", "USER root", ""]
    title, description = _title(profile, entry)
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
    return "cc"


def wrapper_filename(entry: dict[str, object]) -> str:
    """The wrapper file's name: what the recipe names, or the entrypoint's.

    `recipe.wrapper.file` is the only place this lives; a second top-level
    `wrapper_file` key used to shadow it for 53 profiles.
    """
    wrapper = recipe(entry).get("wrapper")
    name = _text(wrapper, "file") if isinstance(wrapper, dict) else ""
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
            out.append(f"unzip -q {step['from']} -d {step['into']}")
        elif op == "cp":
            raw = step.get("from")
            sources = raw if isinstance(raw, list) else [raw]
            flags = _text(step, "flags") or "-a"
            out.append(f"cp {flags} {' '.join(str(s) for s in sources)} {step['into']}")
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
    if shape == "dosbox_compile":
        return _wrapper_dosbox_compile(entry, wrapper)
    if shape == "psyq_dosemu":
        return _wrapper_psyq_dosemu(entry, wrapper)
    if shape == "psyq_native":
        return _wrapper_psyq_native(entry, wrapper)
    if shape == "sn64_pe":
        return _wrapper_sn64_pe(entry, wrapper)
    if shape == "apple_gcc":
        return _wrapper_apple_gcc(entry, wrapper)
    raise ValueError(f"{profile}: wrapper shape {shape!r} is not expressible; mark it handwritten")


def _head(entry: dict[str, object], what: str, wrapper: dict[str, object]) -> list[str]:
    """The wrapper's opening block: marker, entrypoint line, then its prose.

    The prose is the wrapper's documentation and lives in the recipe as
    `notes`; it sits between the generated header and the shellcheck directive,
    where a reader looks for it.
    """
    lines = ["#!/bin/sh", MARKER, f"# {what} — {_text(entry, 'host_dir')}"]
    lines.extend(f"# {note}".rstrip() for note in _list(wrapper.get("notes")))
    return [
        *lines,
        "#",
        "# shellcheck source=base/wrapper-common.sh",
        ". /usr/local/lib/rebrew/wrapper-common.sh",
        "",
    ]


def _wrapper_passthrough(profile: str, entry: dict[str, object], wrapper: dict[str, object]) -> str:
    rec = recipe(entry)
    runner = _text(rec, "runner")
    helper = {"wibo": "rebrew_run", "wine": "rebrew_run", "exec": "rebrew_exec"}[runner]
    binary = _text(rec, "binary")
    _require(binary, f"{profile}: passthrough wrapper needs a binary")
    argv = " ".join(str(a) for a in _list(wrapper.get("argv")))

    lines = _head(entry, "Entrypoint", wrapper)
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


#: The PSY-Q 2.6.3 / 3.x pipeline, verbatim: the host `cpp` preprocesses
#: with DOS line endings, CC1PSX and ASPSX each run in their own dosemu2
#: session (their DJGPP `go32` stub cannot load under DOSBox), and the
#: image's `psyq-obj-parser` turns the Sony object into an ELF relocatable.
#: Four images run exactly this, so the body lives here once; `{dir}` is the
#: recipe's install root.  Raw string on purpose: the printf formats below
#: contain literal `\r\n`, which a regular literal would turn into bytes.
_PSYQ_DOSEMU_BODY = r"""rebrew_pick_source "$@"

OUT=""
CC_FLAGS=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] || rebrew_die "-o requires an output file"
            OUT="$2"
            shift 2
            ;;
        -c) shift ;;
        "$SRC") shift ;;
        *)
            CC_FLAGS="$CC_FLAGS $1"
            shift
            ;;
    esac
done
[ -n "$OUT" ] || OUT="$STEM.o"
case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac
case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT
cd "$_work" || rebrew_die "cannot enter temporary directory"

# CC1PSX wants preprocessed input with DOS line endings; the DOS side sees this
# directory as drive D: (dosemu2's `+0 <dir> +1` image, set by the helper).
# shellcheck disable=SC2086  # CC_FLAGS is a deliberate flag list, word-split
/usr/bin/cpp -E "$SRC_ABS" | unix2dos > dos_src.c \
    || rebrew_die "preprocessing $SRC failed"
{
    printf '@echo off\r\n'
    printf 'CC1PSX.EXE -quiet %s D:\\dos_src.c -o D:\\output.s\r\n' "$CC_FLAGS"
    printf 'EXIT /B\r\n'
} > COMPILE.BAT

rebrew_dosemu_run "$_work" {dir} "D:\\COMPILE.BAT"
if [ ! -s "$_work/output.s" ]; then
    # Assign first: SC2312 — a command substitution inside the message would
    # mask rebrew_dosemu_failure_note's own exit status.
    _note=$(rebrew_dosemu_failure_note)
    printf 'cc1psx produced no assembly for %s%s\n' "$SRC" "$_note" >&2
    sed -n '$p' "$_work/dosemu.log" >&2 2>/dev/null
    exit 1
fi

rebrew_dosemu_run "$_work" {dir} "ASPSX.EXE -quiet D:\\output.s -o D:\\output.obj"
if [ ! -s "$_work/output.obj" ]; then
    _note=$(rebrew_dosemu_failure_note)
    rebrew_die "aspsx produced no object for $SRC$_note"
fi

{dir}/psyq-obj-parser "$_work/output.obj" -o "$OUT_ABS"
"""


#: The PSY-Q 4.x pipeline, verbatim: the SDK's own `CC1PSX.EXE` and
#: `ASPSX.EXE` behind a host `cpp -P`, with the image's obj parser turning
#: the Sony object into an ELF relocatable.  Nothing in the body names a
#: version — the SDK tree comes from the image's `PSYQ_ROOT` — so four
#: images share it exactly.  Raw string on purpose: the trailing `\`
#: line continuations are the shell's, not Python's.
_PSYQ_4X_BODY = r"""# The image sets this; failing loudly beats exec'ing "/CC1PSX.EXE".
PSYQ_ROOT="${PSYQ_ROOT:?PSYQ_ROOT must point at the SDK tree (set by the image)}"

rebrew_pick_source "$@"

OUT=""
CC_FLAGS=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] || rebrew_die "-o requires an output file"
            OUT="$2"
            shift 2
            ;;
        -c) shift ;;  # CC1PSX always compiles; the driver flag is ours
        "$SRC") shift ;;
        *)
            CC_FLAGS="$CC_FLAGS $1"
            shift
            ;;
    esac
done
[ -n "$OUT" ] || OUT="$STEM.o"

# resolve the caller's paths before changing directory
case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac
case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT

cd "$_work" || rebrew_die "cannot enter temporary directory"

# CC1PSX consumes the preprocessed source on stdin and the SDK's own flow
# converts it to DOS line endings first, so keep both steps.
# shellcheck disable=SC2310  # rebrew_die exits; the `||` is the documented contract
/usr/bin/cpp -P "$SRC_ABS" | unix2dos > src.i \
    || rebrew_die "preprocessing $SRC failed"

# SC2310: the stage helpers exit on completion by design, so they are called
# in a subshell under `||`; set -e must not turn a handled failure into an exit.
# shellcheck disable=SC2086,SC2310  # CC_FLAGS is a deliberate flag list, word-split
( rebrew_run "$PSYQ_ROOT/CC1PSX.EXE" -quiet $CC_FLAGS -o out.s < src.i ) \
    || rebrew_die "CC1PSX failed on $SRC"
# shellcheck disable=SC2310  # same subshell contract as the CC1PSX stage
( rebrew_run "$PSYQ_ROOT/ASPSX.EXE" -quiet out.s -o out.bj ) \
    || rebrew_die "ASPSX failed on the assembly CC1PSX produced"

"$PSYQ_ROOT/psyq-obj-parser" out.bj -o "$OUT_ABS"
"""


#: The SN64 PE pipeline, verbatim: the host `cpp` preprocesses, `cc1n64.exe`
#: and `asn64.exe` each run in a subshell (the shared run helper exits by
#: design, which would end the pipeline after stage one) inside a scratch
#: directory with relative filenames (they mangle absolute Unix paths), and
#: `psyq-obj-parser` turns the resulting object into an ELF relocatable.
#: Seven images share the skeleton and differ in four places, which are the
#: holes below; `{root}` is the recipe's install root.  Raw string on
#: purpose: the trailing `\` line continuations are the shell's, not
#: Python's.
_SN64_PE_BODY = r"""rebrew_pick_source "$@"

OUT=""
CC_FLAGS=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] || rebrew_die "-o requires an output file"
            OUT="$2"
            shift 2
            ;;
        -c) shift ;;
        "$SRC") shift ;;
        *)
            CC_FLAGS="$CC_FLAGS $1"
            shift
            ;;
    esac
done
[ -n "$OUT" ] || OUT="$STEM.o"
case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac
case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT
cd "$_work" || rebrew_die "cannot enter temporary directory"

# SC2310: the run helper exits by design, so a stage is called in a subshell
# under `||`; set -e must not turn a handled failure into an exit.
# shellcheck disable=SC2086,SC2310  # CC_FLAGS is a flag list, word-split
{cpp} "$SRC_ABS" | ( rebrew_run /opt/{root}/{cc1} {cc1_flags} $CC_FLAGS -o out.s ) \
    || rebrew_die "{cc1_stem} failed on $SRC"
# shellcheck disable=SC2310  # same subshell contract as the {cc1_stem} stage
( rebrew_run /opt/{root}/asn64.exe {as_flags} out.s -o out.obj ) \
    || rebrew_die "asn64 failed on the assembly {cc1_stem} produced"
/opt/{root}/psyq-obj-parser out.obj -o "$OUT_ABS" {parser_flags}
"""


#: The Apple GCC pipeline: the shipped `cc1` (or `cc1plus` for C++), the
#: image's `convert_gas_syntax.py` to rewrite the assembly into what the
#: host assembler accepts, then GNU `as`.  Four images share it and differ
#: in where `cc1` lives inside the tree and which binary is the C++ front
#: end.  Raw string on purpose: the trailing `\` continuations are the
#: shell's, not Python's.
_APPLE_GCC_BODY = r"""
rebrew_pick_source "$@"

OUT=""
CC_FLAGS=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] || rebrew_die "-o requires an output file"
            OUT="$2"
            shift 2
            ;;
        -c) shift ;;
        "$SRC") shift ;;
        *)
            CC_FLAGS="$CC_FLAGS $1"
            shift
            ;;
    esac
done
[ -n "$OUT" ] || OUT="$STEM.o"
case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac
case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac

_cc1=/opt/{root}/{cc1_dir}cc1
case "$SRC" in
    *.cpp | *.cc | *.cxx | *.C)
        [ -x /opt/{root}/{cc1_dir}{cxx_probe} ] && _cc1=/opt/{root}/{cc1_dir}{cxx_probe}
        ;;
    *) ;;
esac

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT

# shellcheck disable=SC2086,SC2310  # CC_FLAGS is a flag list; the helper exits by design
( rebrew_exec "$_cc1" -quiet $CC_FLAGS "$SRC_ABS" -o "$_work/out.s" ) \
    || rebrew_die "cc1 failed on $SRC"
python3 /opt/{root}/convert_gas_syntax.py "$_work/out.s" "$STEM" new > "$_work/out_new.s" \
    || rebrew_die "assembler-syntax conversion failed for $SRC"
powerpc-linux-gnu-as "$_work/out_new.s" -o "$OUT_ABS"
"""


def _wrapper_apple_gcc(entry: dict[str, object], wrapper: dict[str, object]) -> str:
    """The Apple GCC pipeline (cc1, syntax converter, GNU as)."""
    body = _APPLE_GCC_BODY.replace("{root}", install_root(entry))
    body = body.replace("{cc1_dir}", _text(wrapper, "cc1_dir"))
    body = body.replace("{cxx_probe}", _text(wrapper, "cxx_probe"))
    return "\n".join(_head(entry, "Entrypoint", wrapper)) + body


def _wrapper_sn64_pe(entry: dict[str, object], wrapper: dict[str, object]) -> str:
    """The SN64 PE pipeline (cc1n64/asn64 under the run helper)."""
    body = _SN64_PE_BODY.replace("{root}", install_root(entry))
    for hole in ("cpp", "cc1", "cc1_flags", "as_flags", "parser_flags"):
        body = body.replace("{" + hole + "}", _text(wrapper, hole))
    cc1 = _text(wrapper, "cc1")
    body = body.replace("{cc1_stem}", cc1.removesuffix(".exe"))
    return "\n".join(_head(entry, "Entrypoint", wrapper)) + body


def _wrapper_psyq_native(entry: dict[str, object], wrapper: dict[str, object]) -> str:
    """The PSY-Q 4.x compile pipeline, from recipe data."""
    return "\n".join(_head(entry, "Entrypoint", wrapper)) + _PSYQ_4X_BODY


def _wrapper_psyq_dosemu(entry: dict[str, object], wrapper: dict[str, object]) -> str:
    """The PSY-Q 2.6.3/3.x compile pipeline, from recipe data."""
    body = _PSYQ_DOSEMU_BODY.replace("{dir}", f"/opt/{install_root(entry)}")
    return "\n".join(_head(entry, "Entrypoint", wrapper)) + body


def _wrapper_dosbox_compile(entry: dict[str, object], wrapper: dict[str, object]) -> str:
    """A 16-bit compiler run through the shared DOSBox compile flow.

    Nine images do exactly this and differ only in data: the toolchain's home
    in the image, the tag DOSBox mounts it under, the DOS command line, the log
    file it writes, and the prose at the top of the wrapper (which is recipe
    data — `notes` — because a good wrapper says what it is doing and why).
    """
    lines = _head(entry, "Entrypoint", wrapper)
    lines += [
        "set -e",
        'rebrew_pick_source "$@"',
        'rebrew_flags_except_source "$@"',
        "",
        f"rebrew_dosbox_compile {_text(wrapper, 'dir')} {_text(wrapper, 'tool')} \\",
        f'    "{_text(wrapper, "command")}" \\',
        f"    {_text(wrapper, 'log')}",
    ]
    return "\n".join(lines) + "\n"


def _wrapper_normalising(entry: dict[str, object], wrapper: dict[str, object]) -> str:
    """The wrapper for a compiler that only needs `-o` normalised.

    Its driver finds its own `cc1` and binutils through the prefix baked in at
    build time, so the wrapper separates the output flag from the flags that go
    to the driver and passes the source explicitly.  The template had been left
    unused and did not render (it emitted a stray `extras=` and folded the flags
    into one quoted string); psp-gcc 1.3.1 is the case that fixed it.
    """
    rec = recipe(entry)
    runner = _text(rec, "runner") or "exec"
    helper = {"wibo": "rebrew_run", "wine": "rebrew_run", "exec": "rebrew_exec"}[runner]
    default_ext = _text(wrapper, "default_extension") or "o"
    compile_flag = _text(wrapper, "compile_flag") or "-c"
    prefix = " ".join(str(a) for a in _list(wrapper.get("argv")))
    if prefix:
        prefix += " "
    lines = _head(entry, "Entrypoint", wrapper)
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
        "# shellcheck disable=SC2086  # CC_FLAGS is a deliberate flag list, word-split",
        f'{helper} {binary_path(entry)} {prefix}$CC_FLAGS -o "$OUT_ABS" "$SRC_ABS"',
    ]
    return "\n".join(lines) + "\n"


def render_all(entries: dict[str, dict[str, object]]) -> dict[pathlib.Path, str]:
    out: dict[pathlib.Path, str] = {}
    for profile, entry in entries.items():
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
