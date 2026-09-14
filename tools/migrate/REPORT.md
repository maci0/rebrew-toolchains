# Toolchain generation: state of the migration

Merged to `main`.  `make generate`, `make verify` and the tests in
`tests/test_generation.py` are the gates now; this file records how the
migration was done and what is left.

## Outcome

The migration is done and verified.  Every one of the 272 images is now
rendered from `sources.json`; the semantics of each — base, apt packages, pins
and their hashes, env, labels, install steps, wrapper commands — were compared
against the file it replaced, checked out from the baseline revision:

    make verify                       # (== verify_migration.py --baseline 07a7268)
    verify: 272 compared, 0 new, 3 acknowledged, 0 differ

`07a7268` is the last revision that held the hand-written files; `--baseline
main` stopped meaning anything the moment the migration landed on `main`.

Three *independent* comparisons run, because a comparison that shares a parser
with the renderer can agree with it by making the same mistake twice — which
happened, repeatedly:

| stage | what it compares | what it caught |
| --- | --- | --- |
| classified semantics | base, apt, pins, env, labels, entrypoint, ops, wrapper cmds (deduped, normalised) | the label regression, the duplicate `chmod` delivery |
| raw install clauses | the `&&`-separated clauses as written | the truncated `ln -s "$(ldconfig -p`, `cp -r` vs `cp -a` |
| raw wrapper lines | the wrapper as written (the classified one sorts tokens) | a swapped argument would be invisible otherwise |

The three acknowledged differences are the clang images' `libtinfo5` pin, which
was fetched over plaintext http and now uses https (same sha256, verified).  Two
more findings came out of the migration and were fixed rather than papered over:
the PSY-Q 4.5 SDK download had no hash at all in the manifest (it is stable
across fetches, so it is now verified like the other 309 pins), and the contract
test only ever checked the *primary* pin, which is why it went unnoticed.

23 wrappers stay hand-written and say so in the manifest
(`wrapper.shape == "handwritten"` plus a reason); a test counts and lists them,
so the exception list cannot grow quietly.

`main`'s smoke job caught five real defects that the comparisons had agreed
with, all fixed:

* 53 images ran `chmod +x /usr/local/bin/<entrypoint>` *before* the COPY that
  installed it — the install RUN failed, because the file did not exist yet;
* msvc-6.0-sp5/-sp5-pp/-sp6 lost the `cp` of `MSPDB60.DLL`, because a comment
  inside a continued `RUN` swallowed the rest of the command (and the
  comparison read the comment the same way);
* two images downloaded into `/tmp/tools` and `/tmp/msc` before the `mkdir`
  that creates those directories ran;
* `tar` was rendered with the archive's members before its options, which GNU
  tar reads as members;
* clang-4.0.1's `libtinfo` symlink was truncated at the pipe by the classifier.

The lesson worth keeping: none of these were found by the comparison that
reused the renderer's own assumptions, and all of them were found by something
that did not — a smoke build, or a comparison written from scratch.

The same lesson paid twice more when shapes started landing:

* the wrapper comparison skipped comment lines on both sides, so the generator
  could delete a wrapper's prose and still compare equal.  It had: 18 wrappers
  (borland 5.5/5.6, four GCC rebuilds, every Watcom image) lost the paragraph
  that says how their compiler has to be driven;
* `runner` was guessed by `apply.py` (any wrapper calling `rebrew_run` became
  `wibo`) and the catalog sniffed the rendered file instead of reading the
  manifest, so 151 profiles recorded a runtime their image does not have.  The
  generated files never noticed, because both values render the same wrapper.

Both are now data with a test: wrappers carry their prose as `notes`, recipes
carry `runner`, and the contract test reads the wrapper's *code* (not its
comments) to check the declared value.

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

## What is left

1. **The 19 hand-written wrappers.** Their reasons in the manifest are the
   queue: the SN64 pipeline (9: gcc 2.7.2-sn0001/0004/0006 ×2 and snew, 2.8.1-sn
   ×2 and snew-cxx), Apple GCC (4: 3.1-1041, 4.0.0-5026, 4.0.1-5363/5370),
   saturn-cygnus (1), psyq-4.6 (1), delphi (1: staged DOSBox run + collect) and
   three one-offs (icc 5.0.1, ido 4.1, psp-gcc 1.3.1).  Each is the same loop:
   teach the generator a shape, teach `classify_wrapper` to recognise it, then

       python3 tools/migrate/apply.py --baseline 07a7268     # re-derive
       make verify                                          # must stay 0 differ
       make test                                            # the list shrinks

   `apply.py --baseline` is what makes this possible after the migration: the
   working tree holds generated files now, so the *derivation source* has to be
   the revision that held the hand-written ones.  It refuses a generated
   revision, because deriving from generated files bakes their scaffolding into
   the recipes and still compares equal.
2. **`catalog.py` still greps the rendered Dockerfile** for the per-image notes
   (`_runs`, `notes`).  The runtime column reads the recipe now; the notes are
   about what a converter *does* (`rof2elf.py`, `psyq-obj-parser`), which the
   recipe still knows only indirectly.
3. **`layout`** duplicates the recipe's unpack step and is still read by the
   catalog for its note.  Either the note moves to the recipe or the field does.
4. `tools/migrate/` is scaffolding with a purpose: `verify_migration.py` is the
   migration's proof and runs in CI; `derive_and_verify.py` and `apply.py` exist
   for (1).  If no further shape is ever added, the two can go.
