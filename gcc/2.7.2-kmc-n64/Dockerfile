# GCC 2.7.2 (KMC) mips — N64 decomp compiler (decompals/mips-gcc-2.7.2).
#
# Inherits the shared rebrew/base; this image installs the pinned gcc 2.7.2
# and binutils 2.6 prebuilts (statically linked Linux x86_64, target
# mips-mips-gnu) and exposes the gcc driver as the entrypoint.  Native ELF.
#
# Build:  docker build -t rebrew/gcc:2.7.2-kmc-n64 gcc/2.7.2-kmc-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.2-kmc-n64 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2 KMC (N64)" \
      org.opencontainers.image.description="GCC 2.7.2 KMC (mips-mips-gnu, decompals mips-gcc-2.7.2 prebuilt, native x86_64) toolchain image"

# Both assets are flat tarballs (no top-level directory).
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc272.tar.gz \
        "https://github.com/decompals/mips-gcc-2.7.2/releases/download/main/gcc-2.7.2-linux.tar.gz" \
    && echo "ff3e299c1d952c0a5cb39f7790a208d0c547cf93986eb5607f820c935cedc288  /tmp/gcc272.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/gcc-2.7.2-kmc \
    && tar xzf /tmp/gcc272.tar.gz -C /opt/gcc-2.7.2-kmc \
    && rm /tmp/gcc272.tar.gz \
    && chmod +x /opt/gcc-2.7.2-kmc/gcc

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/binutils26.tar.gz \
        "https://github.com/decompals/mips-binutils-2.6/releases/download/main/binutils-2.6-linux.tar.gz" \
    && echo "405a7ddb29a0b2eb472b167e8f15472223df1eff3093a5ff31d6e545d3a6c670  /tmp/binutils26.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/mips-binutils-2.6 \
    && tar xzf /tmp/binutils26.tar.gz -C /opt/mips-binutils-2.6 \
    && rm /tmp/binutils26.tar.gz \
    && chmod +x /opt/mips-binutils-2.6/*

# The driver was configured --prefix=/opt/cross (target mips-mips-gnu), so
# its cpp/cc1 must live under that prefix; the assembler joins them there.
RUN mkdir -p /opt/cross/bin /opt/cross/lib/gcc-lib/mips-mips-gnu/2.7.2 \
    && cp /opt/gcc-2.7.2-kmc/cc1 /opt/gcc-2.7.2-kmc/cc1plus /opt/gcc-2.7.2-kmc/cpp \
        /opt/cross/lib/gcc-lib/mips-mips-gnu/2.7.2/ \
    && cp /opt/gcc-2.7.2-kmc/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.7.2-kmc/g++ /opt/cross/bin/g++ \
    && cp /opt/mips-binutils-2.6/* /opt/cross/bin/ \
    && ln -s /opt/cross/bin/as /opt/cross/lib/gcc-lib/mips-mips-gnu/2.7.2/as \
    && /opt/cross/bin/gcc --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/cross/bin/gcc "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
