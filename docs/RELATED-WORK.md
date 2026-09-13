# How this compares to Compiler Explorer

[Compiler Explorer](https://godbolt.org) ("godbolt") is the other large public
collection of old and new compilers, and it solves the same first problem we do
— how do you keep hundreds of pinned toolchains installable and honest.  Its
pipeline, from the project's own
[overview](https://github.com/compiler-explorer/compiler-explorer/blob/main/docs/AddingCustomCompilersOverview.md):

1. build each compiler (for GCC, in
   [`compiler-explorer/gcc-builder`](https://github.com/compiler-explorer/gcc-builder),
   itself a Docker build);
2. upload the tarball to S3;
3. install it with
   [`ce_install`](https://github.com/compiler-explorer/infra/blob/main/bin/lib/ce_install.py)
   driven by YAML such as
   [`bin/yaml/cpp.yaml`](https://github.com/compiler-explorer/infra/blob/main/bin/yaml/cpp.yaml),
   into a shared NFS tree at `/opt/compiler-explorer/<compiler>-<version>/`;
4. point the site at it from an
   [`etc/config/*.properties`](https://github.com/compiler-explorer/compiler-explorer/blob/main/etc/config/c%2B%2B.amazon.properties)
   entry (`exe`, `options`, `versionRe`, `semver`, …), with per-compiler
   behaviour in the TypeScript
   [drivers](https://github.com/compiler-explorer/compiler-explorer/tree/main/lib/compilers).

The YAML and our `sources.json` are recognisably the same idea: a declarative
list of downloads with a verification step (`check_exe`/`check_file` there, a
`sha256sum -c` inside the Docker build here).  The differences are deliberate:

| | Compiler Explorer | rebrew (this repo) |
| --- | --- | --- |
| Unit | a compiler install in a shared tree | one self-contained OCI image per toolchain |
| Isolation | host install plus CE's own execution sandbox | the container boundary; `--network none` runs |
| Fetch | tarballs, S3, installer scripts, `url` templates with `{{name}}` | one pinned URL + sha256 per profile (secondary pins for binutils/parsers/SDKs) |
| Verification | `check_exe` runs the installed binary once | sha256 verified in-build, plus a per-image smoke compile and contract tests |
| Name normalisation | `compiler.<id>` entries may share one install, differing in flags/target | `aliases` map community ids to a profile, with hash evidence in [`PROVENANCE.md`](PROVENANCE.md) |
| Per-compiler flags/version regex | yes, first-class (`options`, `versionRe`) | no: the wrapper forwards argv, the consumer supplies flags |
| Scope | a compile *service* (execution, caching, UI) | the toolchains and their runtimes only |

What we borrowed conceptually: a pinned, declarative source list; an explicit
install-verification step (ours is the smoke test in
[`ADDING-TOOLCHAIN.md`](ADDING-TOOLCHAIN.md)); and keeping one installation
behind several names — CE does it with per-compiler flag sets, we do it with
`aliases` when the compiler binary is byte-identical and with a separate image
when the entry point differs (`ido7.1_c++`, `wpp10.0a`, `agbcc_arm`).

What we deliberately do not have: CE's `versionRe`/`options` metadata, its
runtime sandboxing and caching, and its hundreds of *upstream GCC/Clang builds*
fetched from CE's own S3 — that repository is the source of truth for those, and
this one is the source of truth for preserved, vendor and console toolchains.
