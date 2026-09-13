# MWCCARM 2.0-56 (CodeWarrior for NDS ARM9) — decomp.me "mwcc_20_56".
#
# Inherits the shared rebrew/base; this build predates the shared mwccarm.zip
# and ships as its own pinned decompme tarball (flat: mwccarm.exe).  It is a
# 32-bit Windows PE binary, so the entrypoint runs it through the shared
# wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/mwccarm:2.0-56-nds mwccarm/2.0-56-nds
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwccarm:2.0-56-nds -proc arm946e -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCARM 2.0-56 (NDS)" \
      org.opencontainers.image.description="MWCCARM 2.0-56 (CodeWarrior NDS ARM9, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwccarm.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwcc_20_56.tar.gz" \
    && echo "91e10b9826bb985641a6db075da444a51bf25dd53df3216cb8bc05548561ec45  /tmp/mwccarm.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/mwccarm-2.0-56 \
    && tar xzf /tmp/mwccarm.tar.gz -C /opt/mwccarm-2.0-56 \
    && rm /tmp/mwccarm.tar.gz \
    && ls /opt/mwccarm-2.0-56/mwccarm.exe

# This build ships no LMGR DLL of its own; wibo is the default (as for the
# other NDS MWCCARM images) and REBREW_RUNNER=wine still forces wine.
ENV REBREW_RUNNER=wibo

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwccarm-2.0-56/mwccarm.exe "$@"' \
        > /usr/local/bin/mwccarm \
    && chmod +x /usr/local/bin/mwccarm

ENTRYPOINT ["/usr/local/bin/mwccarm"]

USER rebrew
