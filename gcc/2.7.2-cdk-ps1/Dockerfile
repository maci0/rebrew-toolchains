# GCC 2.7.2-cdk — PS1 decomp compiler (decompals/old-gcc prebuilt, CDK/cygnus flavour).
#
# Inherits the shared rebrew/base; this image installs the pinned release
# asset (statically linked Linux x86_64 binaries) and exposes the gcc driver.
# Like the other old-gcc images the asset is a *flat* dump while the driver
# was configured --prefix=/opt/cross (target mips-sony-psx), so cpp/cc1 are
# placed in that tree and binutils-mipsel-linux-gnu supplies the assembler.
#
# Build:  docker build -t rebrew/gcc:2.7.2-cdk-ps1 gcc/2.7.2-cdk-ps1
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.2-cdk-ps1 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2-cdk (PS1)" \
      org.opencontainers.image.description="GCC 2.7.2-cdk (CDK/cygnus flavour, decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.7.2-cdk.tar.gz" \
    && echo "42bb0df96db11a9b5d2e23d78bdc962791f40046280d3d360da93fe5eef6f0bb  /tmp/gcc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/gcc-2.7.2-cdk /opt/cross/bin /opt/cross/lib/gcc-lib/mips-sony-psx/cygnus-2.7.2-970404 \
    && tar xzf /tmp/gcc.tar.gz -C /opt/gcc-2.7.2-cdk \
    && rm /tmp/gcc.tar.gz \
    && chmod +x /opt/gcc-2.7.2-cdk/gcc \
    && cp /opt/gcc-2.7.2-cdk/cc1 /opt/gcc-2.7.2-cdk/cc1plus /opt/gcc-2.7.2-cdk/cpp \
        /opt/cross/lib/gcc-lib/mips-sony-psx/cygnus-2.7.2-970404/ \
    && cp /opt/gcc-2.7.2-cdk/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.7.2-cdk/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-sony-psx/cygnus-2.7.2-970404/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-sony-psx/cygnus-2.7.2-970404/ld \
    && /opt/cross/bin/gcc --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/cross/bin/gcc "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
