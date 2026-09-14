# rebrew-toolchains

Standalone docker images for legacy and modern C compilers — MSVC 1.0–11.0
(every preserved service pack), Borland C/C++ (Turbo C 2.0, Turbo C++ 3.1,
bcc32 5.5), Watcom C (Open Watcom 2.0, 32- and 16-bit), Delphi 1.0, MinGW-w64
GCC (i686 PE), GNU GCC (ELF/x86_64), Clang (ELF/x86_64), the SGI IDO
reimplementations and the original IRIX IDO under qemu-irix (N64), the
Apple/PowerPC-Darwin cross compilers (macOS) and the console decomp
toolchains: GCC 2.6.3/2.7.2/2.8.1/2.95.2 + PSY-Q 4.5/4.6
(PS1), GCC 2.7.2 KMC and 2.8.1 papermario (N64), agbcc/agbccpp/FE8J and GCC
2.96 Camelot (GBA), MWCC 2.3.3 b163 / 2.4.2 b81 / 2.4.7 92p1 / 4.3 b213,
MWCCARM (NDS ARM9) and ProDG 3.9.3 (GameCube/Wii), MWCPS2 3.0.3, EE-GCC
2.95.3-136 and IOP-GCC 2.8.1 (PS2), MWCCPSP and ARM Compiler (PSP/3DS),
Green Hills 5.3.22 (Wii U), SHC 5.1r08/5.1r11/5.1r13 (Dreamcast), MSVC for
Xbox 360 (PowerPC) and clang
3.9.1/4.0.1/8.0.0/9.0.0 (Switch).  Each image is a self-contained compiler
container: the runtime (wine / wibo / DOSBox / native Linux) and the compiler
are baked in, and the entrypoint is the compiler wrapper — you just mount a
workdir and pass compiler flags.

The complete list — every image with its entrypoint, runtime, aliases and
pin — is the generated [toolchain catalog](docs/TOOLCHAINS.md) (which states
the current count); how to add another is
[docs/ADDING-TOOLCHAIN.md](docs/ADDING-TOOLCHAIN.md).

This repo is the *build source*: Dockerfiles, the shared `base` image,
wrapper scripts and the pinned-source manifest.  **No compiler binaries
live in this repo** — every image downloads its sha256-verified source at
build time from the URL recorded in `sources.json` (the proprietary trees
live in the community preservation repos the build pulls from; see
[Copyright](#copyright)).

## Why

These are the same images [rebrew](https://github.com/maci0/rebrew) uses for
compiler-in-the-loop decompilation, packaged so any tool can use them without
rebrew itself — e.g. a `recompile`-style compiler-as-a-service
(submit C source + toolchain id, get back the object; a local `recompile`
service is the reference consumer).

## Build

```bash
./build.sh                # base + every toolchain image
./build.sh msvc-6.0          # one image (accepts msvc/6.0-win32 or 6.0-win32)
./build.sh gcc-14.2.0     # the GCC image (gcc/14.2.0-linux-x64)
./build.sh mwcc_233_163   # community alias → mwcc/2.3.3-163-gc
```

`PREFIX` env var re-tags the images (`PREFIX=archaic ./build.sh` →
`archaic/msvc:6.0-win32`).  Three shared bases are built first, in
dependency order: `rebrew/base` (Debian + wine/wibo/dosbox), `rebrew/base-noble`
(Ubuntu 24.04 + the wrapper helpers and user, for toolchains Debian cannot
host) and `rebrew/base-dosemu` (base-noble + dosemu2 + dj64, for the 16-bit DOS
toolchains).  Each Dockerfile declares the one it needs in its `ARG BASE_IMAGE=`
default, and `build.sh` honours it, so an image never inherits a runtime it does
not use.  Naming is normalized everywhere: a toolchain
lives in `<family>/<version>-<platform>` (platform suffixes: `win16`,
`win32`, `linux-x64`, or the console — `n64`, `ps1`, `ps2`, `gba`, `nds`,
`3ds`, `psp`, `gc`, `wii`, `wiiu`, `dreamcast`, `saturn`, `x360`, `switch`), its
manifest key in `sources.json` is
`<family>-<version>[-<variant>]`, and its image tag is
`<PREFIX>/<family>:<version>-<platform>`.  Every profile may also carry
`aliases` — the decomp.me ids and pre-normalization rebrew names
(`mwcc_233_163`, `ido7.1`, `shc-v5.1r13`, `ee-gcc2.95.3-136`, ...) — so
`./build.sh <alias>` resolves to the same canonical dir; an alias that would
shadow a profile name or a second dir is rejected at startup.  The base image is built first, then the
toolchain images build in parallel (`REBREW_BUILD_JOBS` concurrent builds,
default 4; set it to 1 for strictly sequential) — each build downloads its
pinned source tarball, so a full sweep is network-bound and parallelism cuts
wall-clock roughly by the job count.  Every image is self-contained; no extra inputs
are needed.

## Static analysis

The repo's own glue is checked by three analyzers; `make lint` runs them
all and must stay green.  Both `make lint` and the behavioral `make test`
are CI gates (`.github/workflows/lint.yml`), so findings and contract
breaks block merges.  The environment
is pinned twice over: tool versions are exact-pinned in `pyproject.toml`'s
`[dependency-groups]` (`lint`) and fully resolved — with sha256 hashes for
every artifact — in the committed `uv.lock`.  CI installs with
`uv sync --group lint --locked`, so local runs and CI get byte-identical,
hash-verified packages or fail loudly on drift:

- **shellcheck** over every `.sh` script (`enable=all` via `.shellcheckrc`;
  the two disabled style codes are recorded there with their reasons).
  The wrappers' `# shellcheck source=` directives point at
  `base/wrapper-common.sh`, so the shared helpers are analyzed in context.
- **ruff** (`pyproject.toml`) checks and formats the Python sources — every
  defect-oriented rule group that passes clean today is enabled, with any
  exclusion recorded and justified in the config (100-column hard cap).
- **mypy** in `strict` mode, scoped to the whole tree: new Python files are
  checked by default, dot-directories are skipped automatically.

`make pins` is the network check: every pinned download URL must still
resolve (scheduled weekly in CI, since an upstream deleting an asset must not
look like a broken manifest).

`make smoke` is the Docker-requiring counterpart: it builds one image per
runtime class and compiles with it, which is how "the build succeeded but the
compiler emitted nothing" gets caught (see below).  It is not part of
`make test` because it needs network and, for the dosemu2 family, `/dev/kvm`.

Behavioral tests (`make test`) pin the contracts: the wrapper
runner/watchdog behavior via stub runners; the image matrix itself (every Dockerfile has a complete manifest pin that also
appears inside it, the OCI labels, the `/opt` install root, the non-root
runtime user and the shared wrapper helpers); and the generated
[toolchain catalog](docs/TOOLCHAINS.md), which fails when `make docs` has
not been re-run after a manifest change.  They also pin the generation
direction: every Dockerfile and wrapper is rendered from `sources.json` by
`make generate`, and a test fails when a committed one differs from its
rendering — a hand edit is a change to the wrong file.

After editing Python config locally, `uv sync --group lint --locked` (or
just `uv run make lint`) reproduces exactly what CI installs.

## Use

Every image's ENTRYPOINT is the compiler wrapper; the container sees your
source through `/work` (bind-mount your dir, `-w /work`), flags and source
follow, and the artifact lands back in the mounted dir.

Images drop to the unprivileged user `rebrew` (uid/gid 1000), so the mounted
directory must be readable **and writable** by that uid — a `0700` scratch dir
or a host account with a different uid will fail with `no readable source file`
(or a silently missing object).  If your uid differs, either relax the
directory's mode or map the user yourself with `--user "$(id -u):$(id -g)"`
(only the native-ELF families support an arbitrary uid; wine needs the prefix
owner, which is uid 1000):

```bash
# MSVC 6.0 (wine inside the image)
docker run --rm -v "$PWD":/work -w /work rebrew/msvc:6.0-win32 /c /O2 f.c   # → f.obj

# Same image, wibo instead of wine — much faster for plain console tools.
# The wrapper reads REBREW_RUNNER (wine is the default; wibo is the minimal
# decompals PE loader baked into the base image).
docker run --rm -e REBREW_RUNNER=wibo -v "$PWD":/work -w /work rebrew/msvc:6.0-win32 /c /O2 f.c

# MSVC 1.52 / Turbo C 3.1 / Delphi 1.0 (DOSBox inside the image)
docker run --rm -v "$PWD":/work -w /work rebrew/msvc:1.52-win16 /c /O2 f.c
docker run --rm -v "$PWD":/work -w /work rebrew/borland:3.1-win16 -c f.c
docker run --rm -v "$PWD":/work -w /work rebrew/delphi:1.0-win16 hello.dpr

# Watcom (native Linux binary in the image, POSIX-ish flags)
docker run --rm -v "$PWD":/work -w /work rebrew/watcom:2.0-win32 -fo=f.obj -zq f.c

# 16-bit DOS compilers that need a DPMI host — PSY-Q 3.x/2.6.3 and Saturn
# Cygnus.  These run under dosemu2 (DOSBox cannot load their DJGPP stub), which
# drives the CPU through KVM, so they take --device /dev/kvm:
docker run --rm --device /dev/kvm -v "$PWD":/work -w /work rebrew/psyq:3.3-ps1 -c f.c -o f.o

# GCC / Clang (native Linux compilers in the image; the GCC image is built
# from the GNU source tarball, Clang from LLVM's prebuilt release)
docker run --rm -v "$PWD":/work -w /work rebrew/gcc:14.2.0-linux-x64 -c f.c -o f.o
docker run --rm -v "$PWD":/work -w /work rebrew/gcc:12.3.0-linux-x64 -c f.c -o f.o
docker run --rm -v "$PWD":/work -w /work rebrew/clang:18.1.8-linux-x64 -c f.c -o f.o

# MinGW-w64 GCC (i686 target): the driver is a Windows PE binary, so the
# wrapper runs it through wine like the MSVC images
docker run --rm -v "$PWD":/work -w /work rebrew/mingw:16.2.0-win32 -c f.c -o f.o

# Console decomp toolchains (platform-suffixed tags: <family>:<ver>-<platform>)
docker run --rm -v "$PWD":/work -w /work rebrew/ido:7.1-n64 -c f.c -o f.o        # N64
docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.2-kmc-n64 -c f.c -o f.o  # N64 (KMC)
docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.6.3-ps1 -c f.c -o f.o      # PS1
docker run --rm -v "$PWD":/work -w /work rebrew/psyq:4.5-ps1 -c f.c -o f.o       # PS1 SDK
docker run --rm -v "$PWD":/work -w /work rebrew/agbcc:gba -O2 f.c -o f.s         # GBA (asm out)
docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.96-gba -c f.c -o f.o       # GBA (Camelot)
docker run --rm -v "$PWD":/work -w /work rebrew/mwcc:2.3.3-163-gc -c f.c -o f.o  # GameCube (wine)
docker run --rm -v "$PWD":/work -w /work rebrew/mwcc:2.4.7-92p1-wii -c f.c -o f.o # Wii
docker run --rm -v "$PWD":/work -w /work rebrew/prodg:3.9.3-gc -c f.c -o f.o     # GameCube (ProDG)
docker run --rm -v "$PWD":/work -w /work rebrew/mwcps2:3.0.3-ps2 -c f.c -o f.o   # PS2 (wine)
docker run --rm -v "$PWD":/work -w /work rebrew/ee-gcc:2.95.3-136-ps2 -c f.c -o f.o # PS2 EE
docker run --rm -v "$PWD":/work -w /work rebrew/iop-gcc:2.8.1-ps2 -c f.c -o f.o  # PS2 IOP
docker run --rm -v "$PWD":/work -w /work rebrew/shc:5.1r13-dreamcast -c f.c -o f.o # Dreamcast
docker run --rm -v "$PWD":/work -w /work rebrew/mwccarm:2.0-87-nds -proc arm946e -c f.c -o f.o # NDS
docker run --rm -v "$PWD":/work -w /work rebrew/armcc:5.04-82-3ds --cpu=MPCore -c f.c -o f.o  # 3DS
docker run --rm -v "$PWD":/work -w /work rebrew/mwccpsp:3.0.1-210-psp -c f.c -o f.o  # PSP
docker run --rm -v "$PWD":/work -w /work rebrew/ghs:5.3.22-wiiu -c f.c -o f.o    # Wii U
docker run --rm -v "$PWD":/work -w /work rebrew/ido:5.2-n64 -c -G0 -non_shared -32 f.c -o f.o # N64 (IRIX IDO)
docker run --rm -v "$PWD":/work -w /work rebrew/psyq:4.6-ps1 -c f.c -o f.obj      # PS1 (CCPSX)
docker run --rm -v "$PWD":/work -w /work rebrew/msvc-ppc:16.00.11886-x360 /c f.c  # Xbox 360
docker run --rm -v "$PWD":/work -w /work rebrew/clang:4.0.1-switch -c f.c -o f.o # Switch
```

The PE-driving wrappers (the 32-bit MSVC/Borland images and the MinGW images)
run the compiler through `rebrew_run`, which dispatches
on the `REBREW_RUNNER` env var: `wine` (default, full Wine — most
compatible) or `wibo` (the minimal [decompals/wibo](https://github.com/decompals/wibo)
PE loader baked into the base image — an order of magnitude faster to start,
good for plain console compilers, but it only implements a subset of Win32;
if a tool misbehaves, fall back to wine).  The native images (Watcom, GCC,
Clang, IDO) exec their compiler directly.  The 16-bit DOSBox toolchains
always use DOSBox and ignore `REBREW_RUNNER`.

Both runners and the headless DOSBox runs are wrapped in a watchdog so a hung
compile fails loudly instead of blocking forever (the native Watcom entrypoint
is capped by the same knob):
`REBREW_RUNNER_TIMEOUT` / `REBREW_DOSBOX_TIMEOUT` cap a run in seconds
(default 600); on expiry the wrapper exits with an explicit error naming
the knob.

The wrapper validates the source (`rebrew_pick_source`) and forwards every
other argument to the compiler verbatim, so any flag set works — except the
Delphi `dcc` wrapper, which runs DCC with a fixed configuration baked into
the image and ignores extra arguments.  Artifacts are named after the source
(`.obj`/`.o`/`.exe`), FAT-uppercased for the DOSBox runtimes (`f.OBJ`).
Three console toolchains produce something other than a linked object in one
step, and ship the converter the decomp flows use next:

- `agbcc`/`agbccpp`/agbcc-FE8J emit assembly (`-O2 f.c -o f.s`);
- `shc` emits a Hitachi ROF object (`shc f.c -cpu=sh4 -endian=little
  -object=f.obj`) that the image's `rof2elf.py` turns into an ELF;
- `psyq:4.6-ps1` runs the genuine Sony `CCPSX.EXE`, whose Sony-format object
  the bundled `psyq-obj-parser` converts (`psyq-obj-parser f.obj -o f.o`).

The images built from decomp.me's own packaging (`mwccarm`, `mwccpsp`) set
`REBREW_RUNNER=wibo` as their default: their bundled LMGR license manager
resolves under wibo and fails under wine with a FLEXlm error.  `-e
REBREW_RUNNER=wine` still forces wine.

## Docs

- **[docs/TOOLCHAINS.md](docs/TOOLCHAINS.md)** — the full catalog: every image
  tag, its entrypoint, how it runs (native / wine / wibo / DOSBox), its
  aliases, the pinned source and any second-step caveat.  **Generated** from
  `sources.json` + the Dockerfiles by `make docs`, and verified by
  `make test`, so it cannot drift from the images.
- **[tools/decompme_drift.py](tools/decompme_drift.py)** — how this catalogue
  stands against decomp.me's: which of its compiler ids resolve to an image
  here, how many pin the same upstream artifact, and which ids are not
  provided.  Every gap is declared in the tool with a reason, so a change on
  their side fails rather than passing unnoticed.  Needs network; not part of
  `make test`.
- **[docs/PROVENANCE.md](docs/PROVENANCE.md)** — where every pinned download
  comes from, which upstreams are our own preservation repos, the licence
  class of each, and the catalogued-but-not-shipped list with its reasons.
  **Generated** from the manifest, with a test that fails on an undocumented
  upstream.
- **[docs/ADDING-TOOLCHAIN.md](docs/ADDING-TOOLCHAIN.md)** — how to add one:
  where to find preserved compilers, how to pin them (and what the contract
  tests enforce), the naming rules, which wrapper to pick, the traps
  (flat old-GCC dumps, 32-bit i386 drivers, LMGR licensing, backslash-eating
  `echo`), and the build-and-prove checklist.
- **[docs/RELATED-WORK.md](docs/RELATED-WORK.md)** — how Compiler Explorer
  ("godbolt") organises the same problem — its YAML install list, shared
  compiler tree and per-compiler properties — and where this repo's
  image-per-toolchain model differs on purpose.
- **[sources.json](sources.json)** — the manifest itself: per toolchain the
  pinned `url` + `sha256` (+ `commit` for branch pins), archive `layout`,
  secondary pins and `aliases`.  `build.sh` validates it in both directions
  before any image is built.

## Sources & provenance

**[docs/PROVENANCE.md](docs/PROVENANCE.md)** is the generated provenance and
licensing record: every upstream, what it hosts, its licence class and how
many toolchains it supplies, plus the catalogued-but-not-shipped list with
its reasons.  `make test` fails when a pinned download's upstream is not
documented there, so provenance cannot drift.

The chain is: original vendor media → preservation repos → sha256-pinned
downloads → images.  Two of those preservation orgs are **our own**:

- **[`archaic-msvc`](https://github.com/archaic-msvc)** — the archived 32-bit
  Microsoft VC++ trees (`msvc1000`, `msvc1100`, `msvc200`, `msvc410`,
  `msvc420`, `msvc500(+sp1..sp3)`, `msvc600(+sp5, sp5_vcpp, sp6)`,
  `msvc700(+sp1)`, `msvc710_sp1`, `msvc800(+sp1)`, `msvc900`): MSVC 2.0–11.0
  and every service pack available there.
- **[`archaic-toolchains`](https://github.com/archaic-toolchains)** — the
  reconstructed 16-bit trees and the Borland/Delphi media (`msvc10`,
  `msvc15`, `msvc152`, `msvc400`, `msvc600_sp{1,2,3,4}`, `msvc900_sp1`,
  `tc20`, `tc31`, `borlandc55`, `delphi10`).

`sources.json` records, per toolchain: the pinned download URL, sha256,
branch commit, layout and any aliases.  The community compiler ids and
version mappings follow
[decompme/compilers](https://github.com/decompme/compilers) (pinned at
`0884197d`), which is where the preserved console compilers are catalogued.
Per-family notes:

- **MSVC 1.0–11.0**: `archaic-msvc` (github.com/archaic-msvc) preservation
  repos, plus `archaic-toolchains/msvc400` and the `archaic-toolchains`
  service-pack repos (`msvc600_sp{1,2,3,4}`, `msvc900_sp1`); VC 6.0 SP3/SP4
  from the decomp.me `msvc6.3`/`msvc6.4` releases (sha-verified byte-identical
  to the official SP4 CD).
- **16-bit MSVC 1.0/1.5/1.52**: reconstructed from the original Microsoft
  media — archive.org `en_vc152` / `en_vc152_202512`, WinWorld's VC 1.0
  3.5" floppy set (SZDD payloads decompressed).
- **Turbo C 2.0/3.1, Delphi 1.0**: archive.org `turboc20`, `turboc3.1_202112`,
  `delphi10` items.
- **Borland C++ 5.5**: archive.org `BorlandC55` (official free tools).
- **MinGW-w64 GCC 14.2.0/16.2.0**: `niXman/mingw-builds-binaries` release
  assets (i686-w64-mingw32 target, `.7z`); the driver is a Windows PE binary,
  so the image runs it under wine.
- **GNU GCC 12.3.0/14.2.0**: `ftp.gnu.org` release tarballs, compiled C-only
  inside the image (`--enable-languages=c --disable-bootstrap
  --disable-multilib --with-system-zlib`).
- **Clang 16.0.4/18.1.8**: LLVM's official prebuilt x86_64 Linux release
  tarballs (`clang+llvm-*`); 16.0.4 is the newest 16.x with an x86_64 Linux
  asset (16.0.5/16.0.6 published aarch64 and powerpc64le only).
- **Watcom 32-bit**: the project's CI snapshot (moving tag, re-pinned).
  **Watcom 16-bit** (`wcc`) pins the dated `2026-09-01-Build` release instead:
  the moving-tag snapshot recorded for the 32-bit image no longer hashes to
  its pin upstream, and a dated release asset stays valid.
- **IDO 5.3/7.1 (N64)**: `decompals/ido-static-recomp` v1.2 release assets
  (statically recompiled SGI compilers, native Linux x86_64).
- **GCC 2.6.3/2.8.1/2.95.2 (PS1)**: `decompals/old-gcc` release 0.17 assets —
  statically linked x86_64 builds of the psx-flavour compilers (commit-pinned
  source, `b74211c9`).
- **PSY-Q 4.5 (PS1)**: the SDK's gcc 2.8.1-psx compiler from `decompals/old-gcc`
  plus the psyq_4.5 headers/libs from the `FoxdieTeam/psyq_sdk` preservation
  repo (commit-pinned branch tarball).
- **agbcc / agbccpp (GBA)**: the `pret/agbcc` `release` asset and the
  `notyourav/agbcc` `cp`-tag asset (the C++ frontend lives in the fork).
  Both tags are rebuilt on pushes to their branches — moving tags, re-pinned
  on drift.
- **MWCC 2.3.3 b163 (GC) / 2.4.7 92p1 (Wii)**: the dated
  `files.decomp.dev/compilers_20251015.zip` bundle (`GC/1.2.5` and `GC/2.0p1`
  subtrees, per decompme/compilers' mappings); Windows PE binaries run under
  wine/wibo.
- **MWCPS2 3.0.3 (PS2)**: the `mwcps2-3.0.3-020716` release asset from
  `decompme/compilers` (flat tarball; build 020716 is the correctly labelled
  3.0.3); Windows PE, wine/wibo.
- **GCC 2.7.2 KMC (N64)**: `decompals/mips-gcc-2.7.2` + `mips-binutils-2.6`
  release assets (static x86_64, target `mips-mips-gnu`).
- **GCC 2.96 Camelot (GBA)**: `SBird1337/camelot-gcc` 2.96 release asset
  (`arm-elf`, complete `--prefix=/usr/local` tree).
- **EE-GCC 2.95.3-136 / IOP-GCC 2.8.1 (PS2)**: `decompme/compilers` release
  assets (EE is a Windows PE driver; IOP is a native Linux driver with its
  own `mipsel-scei-elfl` prefix tree).
- **SHC 5.1r13 (Dreamcast)**: `decompme/compilers` release asset (Hitachi
  SuperH PE tools) plus the revision-pinned `rof2elf.py` gist.
- **MWCC 2.4.2 b81 (GC) / 4.3 b213 (Wii), ProDG 3.9.3 (GC), MSVC PPC for
  Xbox 360**: the same dated `files.decomp.dev/compilers_20251015.zip`
  bundle (`GC/1.3.2`, `Wii/1.7`, `ProDG/3.9.3`, `X360/16.00.11886.00`
  subtrees); Windows PE, wine/wibo.
- **Clang 3.9.1/4.0.1/8.0.0/9.0.0 (Switch)**: LLVM's official prebuilt x86_64
  Linux tarballs from `releases.llvm.org` (the corresponding GitHub releases
  carry no binary assets).  Those builds link `libtinfo.so.5`, which bookworm
  no longer ships: 3.9.1/4.0.1 are satisfied by the soname symlink, while
  8.0.0/9.0.0 check the versioned symbol and get a sha256-pinned Debian
  `libtinfo5` `.deb` unpacked into their `lib/`.
- **MWCCARM (NDS ARM9) / ARM Compiler (3DS)**: the decompme/compilers
  `mwccarm.zip` and `armcc.zip` bundles (version → subtree mappings taken
  from decompme/compilers' generated Dockerfiles and recorded in each
  profile's `layout`); the NDS images also install the zip's shared
  `license.dat`.  Windows PE, wibo by default.
- **MWCCPSP (PSP)**: the `mwccpsp_3.0.1_210` decompme/compilers release
  asset; Windows PE, wibo by default (its LMGR licensing path fails under
  wine).  `psp-gcc-1.7.1` is catalogued but **not** implemented: the pinned
  asset ships an empty `as`/`ld` and none of the `pspspecs`/`pspfixup`/
  `psplibgen` scripts the driver hard-codes, so it cannot compile as shipped.
- **Green Hills 5.3.22 (Wii U)**: the `ghs5.3.22` decompme/compilers release
  asset (PowerPC `bin/cxppc.exe` toolset); Windows PE, wine/wibo.
- **IDO 5.2/6.0 (N64)**: `LLONSIT/qemu-irix-helpers` tarballs at branch
  commit `d577d165` — the genuine IRIX IDO executables plus the static
  `qemu-irix` user-mode emulator (the image needs `libglib2.0-0` for it).
- **GCC 2.8.1 papermario (N64)**: `pmret/gcc-papermario` and
  `pmret/binutils-papermario` release assets, merged into one directory the
  wrapper points `-B` at.
- **PSY-Q 4.6 (PS1)**: the `mkst/esa` `psyq-binaries` release (the genuine
  Sony `CCPSX.EXE` + `psyq.ini`) and the decompme/compilers
  `psyq-obj-parser`; the wrapper writes the drive-letter `SN.INI` CCPSX
  requires in the working directory.
- **agbcc FE8J (GBA)**: the `laqieer/agbcc` `fe8j-v1` release asset.
- **SHC 5.1r08/5.1r11 (Dreamcast)**: `decompme/compilers` release assets
  (r08 ships uppercase `SHC.EXE`) plus the revision-pinned `rof2elf.py` gist.

Catalogued upstream but deliberately not shipped — DOS-based PSY-Q 3.x and
Saturn Cygnus (their DJGPP-stub DOS binaries need DOSEMU, which bookworm does
not package), IDO 4.1, `psp-gcc` and Intel C++ 5.0.1 — are listed with their
concrete reasons in
[docs/PROVENANCE.md](docs/PROVENANCE.md#catalogued-but-not-shipped).

Every Dockerfile curls its own source and verifies the sha256 inside the
build, so a build is reproducible from this repo alone (the four `.7z`/
`.tar.xz` acquisitions above are content-addressed by their release tag).

## Copyright

The compiler binaries and media are **proprietary** (Microsoft / Borland /
Watcom / Sony / Nintendo / Sega / SN Systems / Silicon Graphics) and are
*not* in this repository.  What's here is our own build
glue: Dockerfiles, wrapper scripts, the shared base image and the manifest
— all MIT.  The GCC-derived console compilers (ido-static-recomp, old-gcc,
agbcc, Camelot gcc, EE/IOP-GCC) are GPL and fetched from their community
rebuild repos at build time.

The 16-bit toolchains ultimately derive from scans of the original media
(archive.org items and WinWorld floppy sets noted under Sources &
provenance; abandonware — obtaining or using them is at your own
discretion).  The builds fetch the reconstructed trees from the
community-run `archaic-msvc` / `archaic-toolchains` GitHub repos, pinned by
sha256 in `sources.json`; see also the provenance notes in the
[rebrew TOOLCHAIN docs](https://github.com/maci0/rebrew/blob/main/docs/TOOLCHAIN.md).
