# rebrew EE-GCC 2.95.2-273a (PS2) — decomp.me "ee-gcc2.95.2-273a".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (bin/ee-gcc.exe + lib/gcc-lib tree, Windows PE) and runs the driver through the shared
# wine/wibo dispatcher (wine by default; REBREW_RUNNER=wibo selects the
# minimal loader).
#
# Build:  docker build -t rebrew/ee-gcc:2.95.2-273a-ps2 ee-gcc/2.95.2-273a-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ee-gcc:2.95.2-273a-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.95.2-273a (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.95.2-273a (PS2 Emotion Engine, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ps2_compilers.tar.xz" \
    && echo "f337a65a4fbab5cf0e335efe266dcbc7cf69b19c665c6b3a8924736df151a02a  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/ee-gcc-2.95.2-273a /tmp/x \
    && tar xJf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/ee-gcc2.95.2-273a/. /opt/ee-gcc-2.95.2-273a/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-2.95.2-273a/bin/ee-gcc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/ee-gcc-2.95.2-273a/bin/ee-gcc.exe "$@"' \
        > /usr/local/bin/ee-gcc \
    && chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
