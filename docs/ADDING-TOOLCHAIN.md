# Adding a toolchain

A toolchain is three things: a directory, a Dockerfile, and a manifest entry.
Nothing else — no compiler binaries live in this repo, every image downloads
its own sha256-verified source at build time.

```
<family>/<version>-<platform>/Dockerfile      the image recipe + entrypoint wrapper
sources.json                                  the pin: url, sha256, commit, aliases
docs/TOOLCHAINS.md                            generated catalog (make docs)
```

Read [TOOLCHAINS.md](TOOLCHAINS.md) for what already exists, and the
[README](../README.md) for how consumers run the images.

## 1. Find the source and pin it

Prefer, in order:

1. **An already-pinned bundle.** Several families share one artifact
   (`files.decomp.dev/compilers_20251015.zip` carries all GameCube/Wii
   MWCC, ProDG and Xbox 360 MSVC trees; `mwccarm.zip` and `armcc.zip` carry
   whole version lines). Adding a version then costs one Dockerfile and no
   new hash.
2. **[decompme/compilers](https://github.com/decompme/compilers)** —
   `values.yaml` lists every preserved console compiler with its download
   URLs, and `platforms/<platform>/<id>/Dockerfile` shows the **exact
   subtree** each id maps to. Copy that mapping into our `layout` verbatim;
   do not guess it from the id (the ids use internal build numbers, the
   archives use marketing versions: `mwcc_20_87` is `mwccarm/1.2/sp4`).
3. **The vendor/community release asset** (GCC tarballs, LLVM prebuilts,
   `archaic-toolchains` repos, …).

**Know the traps in the big preservation repos.**  `decompals/IDO` is a ~1.2 GB
media archive of IRIX IDO installs, not a per-toolchain source: the IRIX trees
we actually pin come as individual tarballs from `LLONSIT/qemu-irix-helpers`
(`ido5.2.tar.xz`, `ido5.3_c++.tar.xz`, `ido6.0.tar.xz`, `ssb_ido5.3.tar`, …).
`qemu-irix-helpers` also publishes near-duplicate containers of the same tree —
`ido6.0.tar.gz` is `ido6.0.tar.xz` minus the bundled emulator (207 shared files,
all byte-identical) — so diff the file lists before picking one.

**Sweep the upstream release's asset list against our pins.**  A catalogued
id list is not the whole story: `decompme/compilers`' release holds assets the
catalogue never references.  Diffing `.../releases/expanded_assets/compilers`
against every URL in `sources.json` surfaced 22 unclaimed names, of which one
was a new toolchain (**Microsoft C 6.0**, now `msc/6.0-msdos`) and the rest
were alternate packagings of compilers we already ship.

Before adding a candidate, **check it against what we already ship**: hash the
compiler binary.  Preservation archives are often the same build under another
name — `bitch-code/Turbo-C-` is byte-identical to our `borland/3.1-win16`
(`tcc.exe` `2548e4ba9c88b280`), so it is not a gap; conversely
`earthsiege2/borland-cpp-ide` turned out to hold **Borland C++ 5.6**, a newer
build than the 5.5 we had, which is now `borland/5.6-win32`.  A duplicate
finding is worth recording in the PR/commit, not in the catalog — from this
repo's own sweeps: `n64_sn272_build0001` is byte-identical to
`n64_sn272_0001`, the `build0006cygnus` tarball's `cc1n64.exe`/`asn64.exe`
match `n64_sn272_0006`'s, and decomp.me's `msvc4.1` `cl.exe` matches
`archaic-msvc/msvc410`'s.  Two more from the MSVC sweeps: `widberg/msvc8.0`'s
`msvc8.0` commit is byte-identical to our tree (the *other* commit, `msvc8.0p`,
is a patched portable build and is shipped as `msvc/8.0-portable-win32`), and
`itsmattkc/MSVC600` looks like a third VC6 build but is
**byte-identical** to our `msvc-6.0-sp6` tree (`cl.exe` `1bf99f206271`,
`c1.dll` `fc6771ed7352`, `c1xx.dll` `ab4610ad56f7`, `c2.dll` `3f2b5f43e317`),
so it is a repack of SP6 rather than a new compiler and is not shipped a third
time.

Two traps found while unblocking the last DOS toolchains (2026):

- **DOSBox cannot run DJGPP `go32` binaries.**  PSY-Q 3.x's `CC1PSX.EXE` and
  Cygnus's `CPP/CC1/AS` are 1994 DOS-extended executables; under DOSBox 0.74-3
  *and* DOSBox-X they exit silently with no object (verified both).  They need
  dosemu2 with the dj64 DPMI host — the runtime `base-dosemu` builds — and
  dosemu2 drives the CPU through KVM, so those images run with
  `--device /dev/kvm` (the wrapper says so if the device is missing).
- **A recipe may fetch more than one file for one id.**  decomp.me's
  `icc5.0.1-010525z` entry lists Microsoft C 6.0 (for the linker) *and* the
  Intel tree; downloading only the first made an earlier round here record the
  id as "a plain MSVC 6.0 tree — contains no Intel compiler", which was wrong.

Then pin it by content:

```bash
curl -fsSL -o /tmp/artifact "<url>"
sha256sum /tmp/artifact                       # → sources.json sha256
git ls-remote <repo> refs/heads/<branch>      # → sources.json commit
```

Rules the contract tests enforce (`tests/test_image_contract.py`):

- `url` starts with `https://`, `sha256` is 64 hex chars, `commit` is
  recorded whenever the URL contains `refs/heads/` (a branch moves).
- The **same** url and sha256 strings appear inside the toolchain
  Dockerfile (`build.sh` checks this before building anything, and the test
  suite checks it on every run). A one-sided edit fails the build rather
  than fetching something the manifest does not pin.
- Prefer immutable URLs: commit-pinned codeload/raw URLs, dated release
  assets, tag-pinned release assets.
- **codeload tar.gz streams are not byte-stable** — a commit-pinned
  codeload URL can hash differently between downloads. Pin the commit
  instead and pipe the download straight into `tar` (see
  `psyq/4.5-ps1/Dockerfile` for the pattern and its comment).

## 2. Name it

| Thing | Convention | Example |
| --- | --- | --- |
| directory | `<family>/<version>-<platform>` | `mwcc/2.4.7-92p1-wii` |
| manifest key | `<family>-<version>[-<variant>]` | `mwcc-2.4.7-92p1` |
| image tag | `rebrew/<family>:<version>-<platform>` | `rebrew/mwcc:2.4.7-92p1-wii` |

Platforms: `win16`, `win32`, `linux-x64`, `n64`, `ps1`, `ps2`, `gba`, `nds`,
`3ds`, `psp`, `gc`, `wii`, `wiiu`, `dreamcast`, `x360`, `switch`.

Add `aliases` for the names the community and older rebrew configs use
(decomp.me ids, pre-normalization names): `mwcc_233_163`, `ido7.1`,
`shc-v5.1r13`, `ee-gcc2.95.3-136`. `./build.sh <alias>` then resolves to the
same directory. Two rules apply, both enforced at startup: an alias may not
equal a profile name (that is a no-op — drop it) and may not map to two
different directories.

## 3. Write the Dockerfile

Copy the closest existing image and adjust. The shape is fixed:

```dockerfile
# <one-line title> — <family/version/platform>, <source>.
#
# Inherits the shared rebrew/base; this image <what it installs> and exposes
# <entrypoint> as the entrypoint.  <native ELF | Windows PE under wine/wibo>.
#
# Build:  docker build -t rebrew/<family>:<ver>-<platform> <dir>
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/<family>:<ver>-<platform> <flags>

ARG BASE_IMAGE=rebrew/base:1.0
FROM ${BASE_IMAGE}

USER root                       # install steps need root
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="..." \
      org.opencontainers.image.description="..."

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/x.tar.gz "<url>" \
    && echo "<sha256>  /tmp/x.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/<name> && tar xzf /tmp/x.tar.gz -C /opt/<name> \
    && rm /tmp/x.tar.gz && ls /opt/<name>/<driver>      # fail loudly if absent

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/<name>/<driver> "$@"' \
        > /usr/local/bin/<driver-name> && chmod +x /usr/local/bin/<driver-name>

ENTRYPOINT ["/usr/local/bin/<driver-name>"]
USER rebrew                     # runtime drops to the unprivileged user
```

Wrapper choices (all of them dispatch through `base/wrapper-common.sh`, so
the timeout watchdog and `REBREW_RUNNER` handling are shared):

| Compiler is | Use | Notes |
| --- | --- | --- |
| native Linux ELF | `rebrew_exec <driver> "$@"` | POSIX argv passes through |
| Windows PE | `rebrew_run <driver>.exe "$@"` | wine by default, `REBREW_RUNNER=wibo` |
| PE that only works under wibo | add `ENV REBREW_RUNNER=wibo` | decomp.me-packaged LMGR tools; see `mwccarm`, `mwccpsp`, `mwcps2` |
| 16-bit DOS | `rebrew_dosbox_*` | see `msvc/1.52-win16` |

Things that bite, learned the hard way:

- **Every instruction must come after `FROM`.** A shell block, `ENV` or
  `LABEL` that ends up above it fails with `no build stage in current
  context` — a header comment block before `FROM` is fine, instructions are
  not.
- **A generator must assert that nothing is left unrendered.** Two separate
  bulk runs shipped files whose placeholders were never substituted
  (`{cpp_flags}` reaching the container, `{{version}}` in a path) because the
  guard only looked for double braces, or only for `[a-z_]` names and not
  `cc1_flags`.  Match `\{[a-z0-9_]+\}` after rendering and fail loudly.
- **Generate Dockerfiles from a template file, not from nested shell/Python
  string escapes.** Line continuations (`\`) and `printf '%s\n'` are easy to
  mangle: a swallowed `\` silently splits a `RUN` in two and the next build
  dies with `unknown instruction`. After any bulk generation, build one
  representative image before building the rest (38 images were once
  generated before finding out the `ENV` was misplaced), and `docker build`
  each family's first member.
- **Docker tags allow only `[A-Za-z0-9_.-]`.** A version containing `+`
  (`ido5.3_c++`) produces `invalid reference format`; keep the community id as
  an *alias* and normalise the canonical name (`5.3-cxx`).
- **`rebrew_run`/`rebrew_exec` end with `exit`.** That is right for a
  one-command wrapper and fatal for a pipeline: in a multi-stage wrapper call
  each stage in a subshell (`( rebrew_run … ) || rebrew_die "stage failed"`),
  otherwise only the first stage ever runs and the wrapper still exits 0.
- **Install under `/opt/`** and drop back to `USER rebrew`; a contract test
  enforces both (plus the OCI labels and an absolute `/usr/local/bin`
  entrypoint).
- **Old GCC release assets are flat dumps** whose drivers were configured
  `--prefix=/opt/cross`. Recreate that tree (`/opt/cross/lib/gcc-lib/
  <machine>/<version>/` + `/opt/cross/bin`) or pass `-B`; the machine and
  version strings come from `gcc -v -c x.c` on the flat binary.
- **Prebuilt drivers can be 32-bit i386** (`ee-gcc`, `psp-gcc`).  The base
  image's i386 libs (installed for wine) let them run natively.
- **Cygwin-built PE tools need their `dll/` directory on `WINEPATH`.**
  `ee-gcc` 3.2 betas ship `cygwin1.dll`; without
  `WINEPATH=Z:\\opt\\<install>\\dll` the driver dies before it finds its
  assembler (same fix as the MinGW image).  These builds also cannot run
  under wibo — keep wine as their default.
- **The decomp.me id is not the upstream filename.** `ee-gcc2.9-991111b-r4`
  lives at `ee-gcc2.9-991111.tar.gz` (a *different* file from the
  `ee-gcc2.9-991111.tar.xz` build), and `mwcc_20_87` is `mwccarm/1.2/sp4`.
  Always take both the URL and the subtree from the catalog's Dockerfile,
  then confirm the download actually resolves (`curl -fsSL -o /dev/null`).
- **Baked flags need their separator.** A wrapper line built as
  `driver{{FLAGS}} "$@"` silently becomes `driver-B` when FLAGS is
  `-B /path`; keep the leading space with the flag string.  Smoke-testing
  catches it immediately (`failed to run command '/opt/.../ee-gcc-B'`).
- **PE tools may need a fixed env var or config file** before they will
  compile at all: `SN_NGC_PATH='Z:\opt\prodg-3.9.3'` (ProDG, Windows-style
  *directory*), `SHC_LIB`/`SHC_TMP` (SHC), `SN.INI` with drive-letter paths
  written into the working directory (PSY-Q `CCPSX.EXE`).
- Backslash-heavy wrapper lines belong in a **quoted heredoc**, not
  `echo`: `echo "tmpdir=Z:\\tmp"` turns `\t` into a tab and the compiler
  then fails on a mangled temp path.
- If the compiler emits something other than an object (assembly, a Hitachi
  ROF `.obj`, a Sony object), note it in the Dockerfile header and ship the
  converter in the image — the catalog's notes column is generated from
  those Dockerfile markers.

## 4. Document the provenance

Adding a source means documenting it: append its entry to `SOURCES` in
`catalog.py` (upstream key, what it hosts, licence class) and re-run
`make docs`.  `tests/test_catalog.py` fails when a pinned URL's upstream is
not listed, so an undocumented download cannot be merged — that is the whole
point of [`PROVENANCE.md`](PROVENANCE.md), which is generated from the same
manifest.

Check the licence class honestly: GPL for rebuilds of GPL toolchains
(`decompals`, `pret/agbcc`, in-image GNU GCC), proprietary for preserved
vendor binaries (Microsoft, Sony, Nintendo, Sega, SN Systems, SGI), and note
mixed bundles (the IRIX images combine a GPL emulator with proprietary IRIX
binaries).  If a toolchain cannot be shipped — a missing script in the asset,
a host-glibc mismatch, a pipeline our base image does not implement — add it
to `GAPS` with the concrete reason instead of leaving it silently absent.

Two provenance checks worth running before you trust a pin:

- **Sibling assets are not interchangeable.**  `qemu-irix-helpers` publishes
  `ido6.0.tar.gz` *and* `ido6.0.tar.xz`; the gz is the same 207-file tree
  (byte-identical, verified) **minus** `usr/bin/qemu-irix*`, `lib/rld` and
  `usr/lib/libc.so.1`.  Pinning the gz would ship a tree with no emulator.
  Diff the file lists of near-duplicate assets before choosing one.
- **Pick the driver that matches the language.**  An IDO tree ships several
  (`usr/lib/driver`, `usr/lib/CC`, `NCC`); `driver`/`cc` reject C++ sources
  outright, `CC`/`NCC` are the C++ entry points.  The entrypoint decides what
  the image *is*, so a C++ profile whose wrapper calls `driver` compiles C and
  silently cannot do the one thing its name promises.

## 5. Register it

Add the profile to `sources.json` (keys: `family`, `host_dir`, `url`,
`sha256`, `commit`, `layout`, `in_repo_tarball`, optional `aliases` and the
secondary pins `binutils_url`/`binutils_sha256`, `parser_url`/`parser_sha256`,
`helper_url`/`helper_sha256`, `sdk_url`/`sdk_sha256`/`sdk_commit`). Use the
same `layout` vocabulary as the neighbouring profiles (`tar`, `tar-strip1`,
`tar-root`, `7z-strip1`, `zip-subpath:<path>`).

Then regenerate the catalog:

```bash
make docs
```

## 6. Build, run, prove it

```bash
./build.sh <profile-or-alias>          # e.g. ./build.sh mwcc_233_163
mkdir -p /tmp/smoke && cd /tmp/smoke
printf 'int f(void){return 42;}\n' > t.c
docker run --rm -v "$PWD":/work -w /work rebrew/<family>:<ver>-<platform> <flags>
file t.o                               # an object of the right target, or the documented artifact
```

Every image in this repo was smoke-tested that way before it landed — a
build that succeeds but produces no artifact is not done.  Three traps that
have produced false results here:

- **DOSBox artifacts are FAT-uppercased** (`f.obj` → `F.OBJ`).  A case-sensitive
  `[ -s f.o ]` check reports a pass or fail that has nothing to do with the
  run; check the exact name the flow documents.
- **Isolate the output artifact** before each run (`rm -f` it).  Sharing one
  scratch directory across images let a previous compiler's `t.obj` make a
  broken image look green.
- **Check the artifact has the symbol you asked for, not just that it exists.**
  A `cpp | cc1 | as | parser` pipeline reports the *last* stage's status, so a
  first stage that dies still exits 0 with a plausible, empty object.  The SN64
  C++ images were briefly that: `cpp -lang-c++` needs `cc1plus` (install `g++`,
  not just `cpp`), and without it every compile "succeeded" into a 444-byte
  object whose `.symtab` held nothing but a `FILE` symbol.

Then:

```bash
make lint && make test                 # analyzers + contract/catalog tests
make smoke                             # build+compile one image per runtime (needs Docker)
make pins                              # every pinned URL still resolves (needs network)
./build.sh this-is-not-a-toolchain     # exercises the manifest validation sweep
```

`build.sh` validation is bidirectional: a manifest entry without a
Dockerfile fails, and a Dockerfile without a manifest entry fails (its
download pins would otherwise go unverified).

A second sweep catches copy-paste provenance bugs — two profiles that pin the
*same* source when they claim to be different compilers (bundles like the
compilers zip are legitimately shared, so read the output rather than treating
it as an error).  This is how `msvc-7.0` was found to be pinning the 7.1 tree,
i.e. shipping the same compiler as `msvc-7.1` under a 7.0 name:

```bash
python3 - <<'EOF'
import json
groups = {}
for name, e in json.load(open("sources.json")).items():
    groups.setdefault((e["url"], e["sha256"]), []).append(name)
for names in groups.values():
    if len(names) > 1:
        print(len(names), names)
EOF
```

One sweep is worth running whenever toolchains are renamed or re-pinned
(nothing in CI can do it — it needs Docker): every manifest profile must have
a built image under its **current** tag.  A rename that updates the manifest
but leaves the old tag behind is invisible otherwise, which is how
`ido/5.3-linux` → `ido/5.3-n64` once ended up with a manifest entry and no
image:

```bash
python3 - <<'EOF'
import json, subprocess
for p, e in json.load(open("sources.json")).items():
    fam, tag = e["host_dir"].split("/")
    if subprocess.run(["docker", "image", "inspect", f"rebrew/{fam}:{tag}"],
                      capture_output=True).returncode:
        print("no image:", p, e["host_dir"])
EOF
```

## The manifest, field by field

| Field | Meaning |
| --- | --- |
| `family` | image namespace and directory prefix (`mwcc` → `rebrew/mwcc:…`) |
| `host_dir` | `<family>/<version>-<platform>`; the Dockerfile lives here |
| `url`, `sha256` | the primary pinned download, verified inside the build |
| `commit` | the git commit a branch-pinned URL came from; `""` for release assets |
| `layout` | how the archive is unpacked (`tar-strip1`, `zip-subpath:GC/1.2.5`, …) |
| `aliases` | extra names `build.sh` accepts for this profile |
| `*_url`/`*_sha256`/`*_commit` | additional pinned sources the image needs |
| `in_repo_tarball` | reserved: path of a vendored tarball; empty everywhere today |
