# EE-GCC 2.95.3 build 136 — PS2 Emotion Engine compiler (decomp.me id
# ee-gcc2.95.3-136).
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (bin/ee-gcc.exe driver + lib/gcc-lib/ee/2.95.3/{cc1,cpp,as,...},
# Windows PE) and runs the driver through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/ee-gcc:2.95.3-136-ps2 ee-gcc/2.95.3-136-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ee-gcc:2.95.3-136-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.95.3-136 (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.95.3 build 136 (PS2 Emotion Engine, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ee-gcc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-136.tar.gz" \
    && echo "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f  /tmp/ee-gcc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/ee-gcc-2.95.3 \
    && tar xzf /tmp/ee-gcc.tar.gz -C /opt/ee-gcc-2.95.3 \
    && rm /tmp/ee-gcc.tar.gz \
    && ls /opt/ee-gcc-2.95.3/bin/ee-gcc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/ee-gcc-2.95.3/bin/ee-gcc.exe "$@"' \
        > /usr/local/bin/ee-gcc \
    && chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
