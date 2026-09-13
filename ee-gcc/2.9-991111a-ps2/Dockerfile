# rebrew EE-GCC 2.9-991111a (PS2) — decomp.me "ee-gcc2.9-991111a".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (bin/ee-gcc[.exe] + lib/gcc-lib tree: native 32-bit i386 Linux binaries) and runs the
# driver directly — the base image's i386 libs (installed for wine) let it
# run natively, no wine needed.
#
# Build:  docker build -t rebrew/ee-gcc:2.9-991111a-ps2 ee-gcc/2.9-991111a-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ee-gcc:2.9-991111a-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.9-991111a (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.9-991111a (PS2 Emotion Engine, native i386) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-991111a.tar.xz" \
    && echo "f07d1f38afa847197fb816237dbce64e79b2d37b738cb93fa4df3ac7aa1d16f3  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/ee-gcc-2.9-991111a \
    && tar xJf /tmp/compiler.tar.gz -C /opt/ee-gcc-2.9-991111a \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-2.9-991111a/bin/ee-gcc

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/ee-gcc-2.9-991111a/bin/ee-gcc "$@"' \
        > /usr/local/bin/ee-gcc \
    && chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
