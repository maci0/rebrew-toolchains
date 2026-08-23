# rebrew-toolchains

Standalone docker images for legacy Windows/DOS compilers — MSVC 1.0–11.0
(every preserved service pack), Borland C/C++ (Turbo C 2.0, Turbo C++ 3.1,
bcc32 5.5), Watcom C (Open Watcom 2.0) and Delphi 1.0.  Each image is a
self-contained compiler container: the runtime (wine / wibo / DOSBox) and
the compiler are baked in, and the entrypoint is the compiler wrapper — you
just mount a workdir and pass compiler flags.

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
./build.sh                # base + all 35 images
./build.sh msvc6          # one image (accepts msvc/6.0-win32 or 6.0-win32)
```

`PREFIX` env var re-tags the images (`PREFIX=archaic ./build.sh` →
`archaic/msvc:6.0-win32`).  Every image is self-contained; no extra inputs
are needed.

## Use

Every image's ENTRYPOINT is the compiler wrapper; the container sees your
source through `/work` (bind-mount your dir, `-w /work`), flags and source
follow, and the artifact lands back in the mounted dir:

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
```

The 32-bit wrappers run the compiler through `rebrew_run`, which dispatches
on the `REBREW_RUNNER` env var: `wine` (default, full Wine — most
compatible) or `wibo` (the minimal [decompals/wibo](https://github.com/decompals/wibo)
PE loader baked into the base image — an order of magnitude faster to start,
good for plain console compilers, but it only implements a subset of Win32;
if a tool misbehaves, fall back to wine).  The 16-bit DOSBox toolchains
always use DOSBox and ignore `REBREW_RUNNER`.

The wrapper validates the source (`rebrew_pick_source`) and forwards every
other argument to the compiler verbatim, so any flag set works — except the
Delphi `dcc` wrapper, which runs DCC with a fixed configuration baked into
the image and ignores extra arguments.  Artifacts are named after the source
(`.obj`/`.o`/`.exe`), FAT-uppercased for the DOSBox runtimes (`f.OBJ`).

## Sources & provenance

`sources.json` records, per toolchain: the pinned download URL, sha256,
branch commit and layout.  Sources:

- **MSVC 1.0–11.0**: `archaic-msvc` (github.com/archaic-msvc) preservation
  repos, plus `archaic-toolchains/msvc600_sp{1,2,4}` and `msvc900_sp1` for the
  service-pack deltas; VC 6.0 SP3/SP4 from the decomp.me `msvc6.3`/`msvc6.4`
  releases (sha-verified byte-identical to the official SP4 CD).
- **16-bit MSVC 1.0/1.5/1.52**: reconstructed from the original Microsoft
  media — archive.org `en_vc152` / `en_vc152_202512`, WinWorld's VC 1.0
  3.5" floppy set (SZDD payloads decompressed).
- **Turbo C 2.0/3.1, Delphi 1.0**: archive.org `turboc20`, `turboc3.1_202112`,
  `delphi10` items.
- **Borland C++ 5.5**: archive.org `BorlandC55` (official free tools).
- **Open Watcom 2.0**: the project's CI snapshot (moving tag, re-pinned).

Every 32-bit Dockerfile curls its own source and verifies the sha256 inside
the build, so a build is reproducible from this repo alone.

## Copyright

The compiler binaries and media are **proprietary** (Microsoft / Borland /
Watcom) and are *not* in this repository.  What's here is our own build
glue: Dockerfiles, wrapper scripts, the shared base image and the manifest
— all MIT.

The 16-bit toolchains ultimately derive from scans of the original media
(archive.org items and WinWorld floppy sets noted under Sources &
provenance; abandonware — obtaining or using them is at your own
discretion).  The builds fetch the reconstructed trees from the
community-run `archaic-msvc` / `archaic-toolchains` GitHub repos, pinned by
sha256 in `sources.json`; see also the provenance notes in the
[rebrew TOOLCHAIN docs](https://github.com/maci0/rebrew/blob/main/docs/TOOLCHAIN.md).
