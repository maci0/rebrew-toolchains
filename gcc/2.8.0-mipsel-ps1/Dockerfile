# GCC 2.8.0 — PS1 decomp compiler (decompals/old-gcc prebuilt, mipsel flavour).
#
# Inherits the shared rebrew/base; this image installs the pinned release
# asset (statically linked Linux x86_64 binaries) and exposes the gcc driver.
# Like the other old-gcc images the asset is a *flat* dump while the driver
# was configured --prefix=/opt/cross (target mips-linux-gnu), so cpp/cc1 are
# placed in that tree and binutils-mipsel-linux-gnu supplies the assembler.
#
# Build:  docker build -t rebrew/gcc:2.8.0-mipsel-ps1 gcc/2.8.0-mipsel-ps1
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.8.0-mipsel-ps1 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.8.0 (PS1)" \
      org.opencontainers.image.description="GCC 2.8.0 (mipsel flavour, decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.8.0.tar.gz" \
    && echo "f4d0bea985cd53bc7ee43f366a4058c631071e925b6ba25fc919d15e7c6a8ba0  /tmp/gcc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/gcc-2.8.0 /opt/cross/bin /opt/cross/lib/gcc-lib/mips-linux-gnu/2.8.0 \
    && tar xzf /tmp/gcc.tar.gz -C /opt/gcc-2.8.0 \
    && rm /tmp/gcc.tar.gz \
    && chmod +x /opt/gcc-2.8.0/gcc \
    && cp /opt/gcc-2.8.0/cc1 /opt/gcc-2.8.0/cc1plus /opt/gcc-2.8.0/cpp \
        /opt/cross/lib/gcc-lib/mips-linux-gnu/2.8.0/ \
    && cp /opt/gcc-2.8.0/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.8.0/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-linux-gnu/2.8.0/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-linux-gnu/2.8.0/ld \
    && /opt/cross/bin/gcc --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/cross/bin/gcc "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
