# rebrew MWCC 2.3.3-163e (GameCube) — decomp.me "mwcc_233_163e".
#
# Inherits the shared rebrew/base; this image extracts the GC/1.2.5e subtree
# (mwcceppc.exe + assembler/linker/license DLL) from the pinned
# files.decomp.dev compilers zip.  The compiler is a 32-bit Windows PE
# binary, so the entrypoint runs it through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/mwcc:2.3.3-163e-gc mwcc/2.3.3-163e-gc
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwcc:2.3.3-163e-gc -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCC 2.3.3-163e (GameCube)" \
      org.opencontainers.image.description="MWCC 2.3.3-163e (CodeWarrior GameCube, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20240706.zip" \
    && echo "399889e059cc86804267eb9376c9c2c4e197d7204936421c45e35fb6c01256c5  /tmp/compilers.zip" | sha256sum -c - \
    && mkdir -p /opt/mwcc-2.3.3-163e \
    && unzip -q /tmp/compilers.zip 'GC/1.2.5e/*' -d /tmp/x \
    && cp -a /tmp/x/GC/1.2.5e/. /opt/mwcc-2.3.3-163e/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/mwcc-2.3.3-163e/mwcceppc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwcc-2.3.3-163e/mwcceppc.exe "$@"' \
        > /usr/local/bin/mwcceppc \
    && chmod +x /usr/local/bin/mwcceppc

ENTRYPOINT ["/usr/local/bin/mwcceppc"]

USER rebrew
