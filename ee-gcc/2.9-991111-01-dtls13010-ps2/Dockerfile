# rebrew EE-GCC 2.9-991111-01-dtls13010 (PS2) — decomp.me "ee-gcc2.9-991111-01-dtls13010".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (bin/ee-gcc[.exe] + lib/gcc-lib tree: native 32-bit i386 Linux binaries) and runs the
# driver directly — the base image's i386 libs (installed for wine) let it
# run natively, no wine needed.
#
# Build:  docker build -t rebrew/ee-gcc:2.9-991111-01-dtls13010-ps2 ee-gcc/2.9-991111-01-dtls13010-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ee-gcc:2.9-991111-01-dtls13010-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.9-991111-01-dtls13010 (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.9-991111-01-dtls13010 (PS2 Emotion Engine, native i386) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-991111-01-dtls13010.tar.gz" \
    && echo "3ab52a7ea962100f2a7df3e04d3e7a758aad669eb365251682e769b755d9d586  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/ee-gcc-2.9-991111-01-dtls13010 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/ee-gcc-2.9-991111-01-dtls13010 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-2.9-991111-01-dtls13010/bin/ee-gcc

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/ee-gcc-2.9-991111-01-dtls13010/bin/ee-gcc "$@"' \
        > /usr/local/bin/ee-gcc \
    && chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
