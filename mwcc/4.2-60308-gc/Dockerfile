# rebrew MWCC 4.2-60308 (GameCube) — decomp.me "mwcc_42_60308".
#
# Inherits the shared rebrew/base; this image extracts the GC/3.0a3.4 subtree
# (mwcceppc.exe + assembler/linker/license DLL) from the pinned
# files.decomp.dev compilers zip.  The compiler is a 32-bit Windows PE
# binary, so the entrypoint runs it through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/mwcc:4.2-60308-gc mwcc/4.2-60308-gc
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwcc:4.2-60308-gc -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCC 4.2-60308 (GameCube)" \
      org.opencontainers.image.description="MWCC 4.2-60308 (CodeWarrior GameCube, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251015.zip" \
    && echo "491cb62317c7f3669ac283ae159e82e3c97a5713b78299571ba4cf023dc7e95e  /tmp/compilers.zip" | sha256sum -c - \
    && mkdir -p /opt/mwcc-4.2-60308 \
    && unzip -q /tmp/compilers.zip 'GC/3.0a3.4/*' -d /tmp/x \
    && cp -a /tmp/x/GC/3.0a3.4/. /opt/mwcc-4.2-60308/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/mwcc-4.2-60308/mwcceppc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwcc-4.2-60308/mwcceppc.exe "$@"' \
        > /usr/local/bin/mwcceppc \
    && chmod +x /usr/local/bin/mwcceppc

ENTRYPOINT ["/usr/local/bin/mwcceppc"]

USER rebrew
