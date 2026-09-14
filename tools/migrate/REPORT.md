# Toolchain generation: state of the migration

Branch `toolchain-generation`.  `main` is untouched: nothing here is wired into
`build.sh`, the tests or CI until the corpus verifies end to end.

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

1. Implement the `normalising` wrapper shape (largest missing group) and re-run
   the comparator until those 46 profiles report identical.
2. Add the DOSBox and dosemu2 shapes; then the pipeline shapes one family at a
   time (SN64, Apple GCC, PSY-Q 4.x, SHC), each verified by the comparator.
3. Close the derivation gaps listed under (2) above.
4. Inject the recipes into `sources.json`, generate, and only then wire
   `make generate` + the CI staleness check, the handwritten-exception test, and
   the catalog reading runtime/notes from the recipe instead of grepping text.
5. Merge to `main` only when the comparator reports zero differences.
