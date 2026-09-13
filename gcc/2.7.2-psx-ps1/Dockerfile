# GCC 2.7.2 psx flavour — PS1 decomp compiler (decompals/old-gcc prebuilt).
#
# Inherits the shared rebrew/base; this image installs the pinned
# gcc-2.7.2-psx release asset (statically linked Linux x86_64 binaries,
# target mips-sony-psx little-endian) and exposes the gcc driver, with the
# same --prefix=/opt/cross tree and mipsel assembler wiring the 2.6.3/2.95.2
# images use.  Native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/gcc:2.7.2-psx-ps1 gcc/2.7.2-psx-ps1
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.2-psx-ps1 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2 psx (PS1)" \
      org.opencontainers.image.description="GCC 2.7.2 (mips-sony-psx, decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc272.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.7.2-psx.tar.gz" \
    && echo "500a459b3485e885a8d302cac23c2a4632f3900e03a09153f6190699fd723571  /tmp/gcc272.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/gcc-2.7.2-psx /opt/cross/bin /opt/cross/lib/gcc-lib/mips-sony-psx/2.7.2 \
    && tar xzf /tmp/gcc272.tar.gz -C /opt/gcc-2.7.2-psx \
    && rm /tmp/gcc272.tar.gz \
    && chmod +x /opt/gcc-2.7.2-psx/gcc \
    && cp /opt/gcc-2.7.2-psx/cc1 /opt/gcc-2.7.2-psx/cc1plus /opt/gcc-2.7.2-psx/cpp \
        /opt/cross/lib/gcc-lib/mips-sony-psx/2.7.2/ \
    && cp /opt/gcc-2.7.2-psx/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.7.2-psx/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-sony-psx/2.7.2/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-sony-psx/2.7.2/ld \
    && /opt/cross/bin/gcc --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/cross/bin/gcc "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
