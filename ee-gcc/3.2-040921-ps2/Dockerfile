# EE-GCC 3.2-040921 — PS2 Emotion Engine compiler (decomp.me "ee-gcc3.2-040921").
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball, a self-contained tree (bin/ driver, ee/bin/ assembler,
# lib/gcc-lib/) of 32-bit i386 Linux binaries — the base image's i386 libs
# (installed for wine) let them run natively, no wine needed.
#
# Build:  docker build -t rebrew/ee-gcc:3.2-040921-ps2 ee-gcc/3.2-040921-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ee-gcc:3.2-040921-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 3.2-040921 (PS2)" \
      org.opencontainers.image.description="EE-GCC 3.2-040921 (PS2 Emotion Engine, native i386) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ee-gcc.tar.xz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-040921.tar.xz" \
    && echo "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f  /tmp/ee-gcc.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/ee-gcc-3.2-040921 \
    && tar xJf /tmp/ee-gcc.tar.xz -C /opt/ee-gcc-3.2-040921 \
    && rm /tmp/ee-gcc.tar.xz \
    && chmod +x /opt/ee-gcc-3.2-040921/bin/ee-gcc \
    && /opt/ee-gcc-3.2-040921/bin/ee-gcc --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/ee-gcc-3.2-040921/bin/ee-gcc "$@"' \
        > /usr/local/bin/ee-gcc \
    && chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
