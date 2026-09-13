# MWCCARM 4.0-1026 (CodeWarrior for NDS) — decomp.me "mwccarm_40_1026".
#
# Inherits the shared rebrew/base; this image extracts the mwccarm/dsi/1.2 subtree
# (mwccarm.exe + license DLLs) from the pinned decompme/compilers
# mwccarm.zip.  The compiler is a 32-bit Windows PE binary, so the entrypoint
# runs it through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/mwccarm:4.0-1026-nds mwccarm/4.0-1026-nds
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwccarm:4.0-1026-nds -proc arm946e -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCARM 4.0-1026 (NDS)" \
      org.opencontainers.image.description="MWCCARM 4.0-1026 (CodeWarrior NDS, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccarm.zip" \
    && echo "dc386e37b2176e960954a733de928337d9b7e7620b9e94228008c31774339ace  /tmp/compilers.zip" | sha256sum -c - \
    && mkdir -p /opt/mwccarm-4.0-1026 \
    && unzip -q /tmp/compilers.zip 'mwccarm/dsi/1.2/*' 'mwccarm/license.dat' -d /tmp/x \
    && cp -a /tmp/x/mwccarm/dsi/1.2/. /opt/mwccarm-4.0-1026/ \
    && cp /tmp/x/mwccarm/license.dat /opt/mwccarm-4.0-1026/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/mwccarm-4.0-1026/mwccarm.exe

#
# The CodeWarrior build license-checks through its bundled LMGR DLL, which
# resolves under wibo (the loader decomp.me's own images use) but fails under
# wine with a FLEXlm error; wibo is the default here, REBREW_RUNNER=wine still
# forces wine.
ENV REBREW_RUNNER=wibo

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwccarm-4.0-1026/mwccarm.exe "$@"' \
        > /usr/local/bin/mwccarm \
    && chmod +x /usr/local/bin/mwccarm

ENTRYPOINT ["/usr/local/bin/mwccarm"]

USER rebrew
