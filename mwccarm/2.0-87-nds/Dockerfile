# MWCCARM 2.0-87 (CodeWarrior for NDS ARM9) — decomp.me "mwcc_20_87".
#
# Inherits the shared rebrew/base; this image extracts the mwccarm/1.2/sp4 subtree
# (mwccarm.exe + lmgr8c.dll) from the pinned decompme/compilers mwccarm zip.
# The compiler is a 32-bit Windows PE binary, so the entrypoint runs it
# through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/mwccarm:2.0-87-nds mwccarm/2.0-87-nds
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwccarm:2.0-87-nds -proc arm946e -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCARM 2.0-87 (NDS)" \
      org.opencontainers.image.description="MWCCARM 2.0-87 (CodeWarrior NDS ARM9, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwccarm.zip \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccarm.zip" \
    && echo "dc386e37b2176e960954a733de928337d9b7e7620b9e94228008c31774339ace  /tmp/mwccarm.zip" | sha256sum -c - \
    && mkdir -p /opt/mwccarm-2.0-87 \
    && unzip -q /tmp/mwccarm.zip 'mwccarm/1.2/sp4/*' 'mwccarm/license.dat' -d /tmp/mwccarm \
    && cp -a /tmp/mwccarm/mwccarm/1.2/sp4/. /opt/mwccarm-2.0-87/ \
    && cp /tmp/mwccarm/mwccarm/license.dat /opt/mwccarm-2.0-87/ \
    && rm -rf /tmp/mwccarm /tmp/mwccarm.zip \
    && ls /opt/mwccarm-2.0-87/mwccarm.exe

# The CodeWarrior builds license-check through their bundled LMGR DLL, which
# resolves under wibo (the loader decomp.me's own images use) but fails under
# wine with a FLEXlm error; wibo is the default here, REBREW_RUNNER=wine
# still forces wine.
ENV REBREW_RUNNER=wibo

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwccarm-2.0-87/mwccarm.exe "$@"' \
        > /usr/local/bin/mwccarm \
    && chmod +x /usr/local/bin/mwccarm

ENTRYPOINT ["/usr/local/bin/mwccarm"]

USER rebrew
