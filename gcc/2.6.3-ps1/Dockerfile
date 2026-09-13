# GCC 2.6.3 mipsel — PS1 decomp compiler (decompals/old-gcc prebuilt).
#
# Inherits the shared rebrew/base; this image downloads the pinned
# gcc-2.6.3-psx release asset (statically linked Linux x86_64 binaries:
# gcc/cc1/cc1plus/cpp/g++, target mips-sony-psx little-endian) and exposes
# the gcc driver as the entrypoint.  Native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/gcc:2.6.3-ps1 gcc/2.6.3-ps1
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.6.3-ps1 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.6.3 (PS1)" \
      org.opencontainers.image.description="GCC 2.6.3 (mips-sony-psx, decompals/old-gcc prebuilt, native x86_64) toolchain image"

# Flat release asset (no top-level directory) — extract in place.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc263.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.6.3-psx.tar.gz" \
    && echo "01e6e8c4933414ea3f8d8e3bc766a1f5fafd4fc0110e0b75d1f691bd791989b1  /tmp/gcc263.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/gcc-2.6.3-ps1 \
    && tar xzf /tmp/gcc263.tar.gz -C /opt/gcc-2.6.3-ps1 \
    && rm /tmp/gcc263.tar.gz \
    && chmod +x /opt/gcc-2.6.3-ps1/gcc \
    && /opt/gcc-2.6.3-ps1/gcc --version

# The release asset is a *flat* dump of the built tools, but the driver was
# configured --prefix=/opt/cross, so it looks for cpp/cc1 under
# /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3/.  Recreate that tree (the
# asset's real layout is the compiler's own prefix) and give it an
# assembler: binutils-mipsel-linux-gnu's `as` symlinked where the driver
# looks, so `-c` produces a real MIPS object.
RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/cross/bin /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3 \
    && cp /opt/gcc-2.6.3-ps1/cc1 /opt/gcc-2.6.3-ps1/cc1plus /opt/gcc-2.6.3-ps1/cpp \
        /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3/ \
    && cp /opt/gcc-2.6.3-ps1/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.6.3-ps1/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3/ld

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/cross/bin/gcc "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
