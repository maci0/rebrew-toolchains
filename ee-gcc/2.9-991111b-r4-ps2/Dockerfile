# rebrew EE-GCC 2.9-991111b-r4 (PS2) — decomp.me "ee-gcc2.9-991111b-r4".
#
# (Upstream publishes this build as ee-gcc2.9-991111.tar.gz — the b-r4 id is
# decomp.me's; it is a different file from the ee-gcc2.9-991111.tar.xz image.)
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (bin/ee-gcc[.exe] + lib/gcc-lib tree, Windows PE) and runs the driver through the shared
# wine/wibo dispatcher (wine by default; REBREW_RUNNER=wibo selects the
# minimal loader).
#
# Build:  docker build -t rebrew/ee-gcc:2.9-991111b-r4-ps2 ee-gcc/2.9-991111b-r4-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ee-gcc:2.9-991111b-r4-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.9-991111b-r4 (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.9-991111b-r4 (PS2 Emotion Engine, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-991111.tar.gz" \
    && echo "9ebbb042eb1e5d33d772293c5e9286a54dbec29865a3d7fbb398c97436f33583  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/ee-gcc-2.9-991111b-r4 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/ee-gcc-2.9-991111b-r4 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-2.9-991111b-r4/bin/ee-gcc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/ee-gcc-2.9-991111b-r4/bin/ee-gcc.exe "$@"' \
        > /usr/local/bin/ee-gcc \
    && chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
