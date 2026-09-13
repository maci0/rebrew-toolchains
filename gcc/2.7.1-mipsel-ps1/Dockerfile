# GCC 2.7.1-mipsel — PS1 decomp compiler (decompals/old-gcc prebuilt, mipsel flavour).
#
# Inherits the shared rebrew/base; this image installs the pinned release
# asset (statically linked Linux x86_64 binaries) and exposes the gcc driver.
# Like the other old-gcc images the asset is a *flat* dump while the driver
# was configured --prefix=/opt/cross (target mips-linux-gnu), so cpp/cc1 are placed in
# that tree and binutils-mipsel-linux-gnu supplies the assembler.
#
# Build:  docker build -t rebrew/gcc:2.7.1-mipsel-ps1 gcc/2.7.1-mipsel-ps1
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.1-mipsel-ps1 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.1-mipsel (PS1)" \
      org.opencontainers.image.description="GCC 2.7.1-mipsel (mipsel flavour, decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.7.1.tar.gz" \
    && echo "e13476a0539055faf9aefc846a1b6b774ec84b8f02bbecaff09b6ce0774ca746  /tmp/gcc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/gcc-2.7.1-mipsel /opt/cross/bin /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.1 \
    && tar xzf /tmp/gcc.tar.gz -C /opt/gcc-2.7.1-mipsel \
    && rm /tmp/gcc.tar.gz \
    && chmod +x /opt/gcc-2.7.1-mipsel/gcc \
    && cp /opt/gcc-2.7.1-mipsel/cc1 /opt/gcc-2.7.1-mipsel/cc1plus /opt/gcc-2.7.1-mipsel/cpp \
        /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.1/ \
    && cp /opt/gcc-2.7.1-mipsel/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.7.1-mipsel/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.1/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.1/ld \
    && /opt/cross/bin/gcc --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/cross/bin/gcc "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
