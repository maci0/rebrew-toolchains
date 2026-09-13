# MWCC 2.3.3 build 163 (CodeWarrior GameCube) — decomp.me "mwcc_233_163".
#
# Inherits the shared rebrew/base; this image extracts the GC/1.2.5 tree
# (mwcceppc.exe + assembler/linker/license DLL) from the pinned
# files.decomp.dev compilers zip.  The compiler is a 32-bit Windows PE
# binary, so the entrypoint runs it through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/mwcc:2.3.3-163-gc mwcc/2.3.3-163-gc
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwcc:2.3.3-163-gc -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCC 2.3.3 b163 (GameCube)" \
      org.opencontainers.image.description="MWCC 2.3.3 build 163 (CodeWarrior GameCube, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

# Pinned compilers zip (dated, content-addressed by filename).  Only the
# GC/1.2.5 subtree is extracted (build 163, per decompme/compilers'
# mwcc_233_163 mapping) — the zip is 75 MB with every decomp compiler.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251015.zip" \
    && echo "491cb62317c7f3669ac283ae159e82e3c97a5713b78299571ba4cf023dc7e95e  /tmp/compilers.zip" | sha256sum -c - \
    && mkdir -p /opt/mwcc-2.3.3 \
    && unzip -q /tmp/compilers.zip 'GC/1.2.5/*' -d /tmp/mwcc \
    && cp -a /tmp/mwcc/GC/1.2.5/. /opt/mwcc-2.3.3/ \
    && rm -rf /tmp/mwcc /tmp/compilers.zip \
    && ls /opt/mwcc-2.3.3/mwcceppc.exe

# The `mwcceppc` wrapper: PE binary, shared runner + watchdog, verbatim argv.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwcc-2.3.3/mwcceppc.exe "$@"' \
        > /usr/local/bin/mwcceppc \
    && chmod +x /usr/local/bin/mwcceppc

ENTRYPOINT ["/usr/local/bin/mwcceppc"]

USER rebrew
