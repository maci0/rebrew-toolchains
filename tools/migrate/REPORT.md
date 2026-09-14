# Toolchain generation: state of the migration

Branch `toolchain-generation`.  `main` is untouched: nothing here is wired into
`build.sh`, the tests or CI until the corpus verifies end to end.

## Outcome

The migration is done and verified.  Every one of the 272 images is now
rendered from `sources.json`; the semantics of each — base, apt packages, pins
and their hashes, env, labels, install steps, wrapper commands — were compared
against the file it replaced, checked out from the baseline revision:

    python3 tools/migrate/verify_migration.py --baseline main
    verify: 272 compared, 0 new, 3 acknowledged, 0 differ

The three acknowledged differences are the clang images' `libtinfo5` pin, which
was fetched over plaintext http and now uses https (same sha256, verified).  Two
more findings came out of the migration and were fixed rather than papered over:
the PYQ-Q 4.5 SDK download had no hash at all in the manifest (it is stable
across fetches, so it is now verified like the other 309 pins), and the contract
test only ever checked the *primary* pin, which is why it went unnoticed.

39 wrappers stay hand-written and say so in the manifest
(`wrapper.shape == "handwritten"` plus a reason); a test counts and lists them,
so the exception list cannot grow quietly.

## Why generation is the right target

Measured on `main` (272 images):

| what | count |
| --- | --- |
| distinct *procedures* (`apt`, `curl+sha256`, `tar`/`unzip`, `chmod`, `ls` guard, wrapper `printf`, `ENTRYPOINT`) | **37 shapes, 223 images in shapes of ≥5** |
| DISTINCT Dockerfile texts | 272 (the variation above the shape is data: pins, packages, dest paths) |
| wrappers that are `rebrew_run|rebrew_exec <binary> "$@"` plus boilerplate | **193** |
| wrapper shapes in total | 45, of which 5 clusters hold 153 |
| RUN command vocabulary across the whole repo | **13 verbs** (`rm chmod curl sha256 apt-get mkdir printf tar cp ls unzip ln` + `check_run` + `script`) |
| decomp.me ids whose first pinned URL we share byte for byte | 178 of 235 |

So: the *data* is not duplicated (we pin what they pin, deliberately verified),
the *engineering* is — 272 copies of eight procedures.

## What is built

- `generate.py` — the generator and the recipe schema (documented in its
  docstring).  `--check` re-renders in memory and diffs, for a CI staleness
  gate mirroring `make docs`.
- `tools/migrate/derive_and_verify.py` — throwaway harness that (a) derives a
  recipe from each existing Dockerfile + wrapper, and (b) compares the *generated*
  replacement with the original **semantically**: ordered pins, apt set, install
  operations, env, entrypoint, and the commands the wrapper actually runs — with
  paths, URLs, hashes, tar flag order and comments normalised away.

## Where the derivation stands

```
derived         148 of 272 profiles
identical        78            (generated == original, semantically)
differing        70            (wrapper/ops derivation gaps)
not derivable   124            (wrapper or install shape not yet expressed)
```

The remaining work is mechanical but not small, and none of it is guesswork:

1. **Wrapper shapes still missing** (124 profiles): `normalising` with
   per-family flag spellings (`/c /Fo` for cl, `-c -o` for bcc/wcc, `/c` for icc),
   the DOSBox shape (`rebrew_dosbox_compile` + FAT-cased artifacts), the dosemu2
   shape (`COMPILE.BAT` + multi-stage DOS), the SN64/Apple/PSY-Q pipelines
   (`cpp | cc1 | as | converter`), the qemu-irix shape (`-L` + `-EL`), and the
   cc1-style agbcc front ends.  Roughly ten templates, in the order of the counts.
2. **Derivation gaps** (70): tar flag order in rendering, `ln -s "$( … )"`
   command substitutions, wrapper `env` prefixes, `apt_meta` (the
   `update && install && rm` idiom), and profiles whose install root is reached
   through a `link` (psp-gcc, camelot) rather than `mkdir`.
3. **Install-op derivation for the tail**: source builds (`make`, `configure` —
   the two linux-x64 GCCs), `ar`/`mv`/`cd` one-offs; these want `script` steps or
   an explicit `handwritten` reason rather than a template.

## Verification plan (already implemented, to run at the end)

1. `generate.py --check` clean for every generated file.
2. `derive_and_verify.py` reports **0 differing** — i.e. every generated image is
   semantically identical to the one that ships today.
3. `make lint && make test` (contract tests police generated output too).
4. `make smoke` extended to one image per *shape* (~12 builds, including
   generated ones) so each template is compiled with, not just rendered.
5. Everything else (variants as `variant_of` rows, the decomp.me drift check,
   the registry publisher) only after 1–4 pass.

## Next round, concretely

1. Implement the `normalising` wrapper shape (largest missing group, 39 profiles
   across msvc/watcom/psyq/DOSBox/dosemu2/pipelines) and re-run the comparator
   until those report identical.  Each shape is added the same way: teach the
   generator, generate, and let `verify_migration.py` prove the file did not
   change.
2. Wire `make generate` + the staleness check into CI.
3. Make `catalog.py` read the runtime and per-image notes from the recipe
   instead of grepping the rendered Dockerfile.
4. Merge to `main`.
