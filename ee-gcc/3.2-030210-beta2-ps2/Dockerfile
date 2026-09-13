# rebrew EE-GCC 3.2-030210-beta2 (PS2) — decomp.me "ee-gcc3.2-030210-beta2".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (bin/ee-gcc[.exe] + lib/gcc-lib tree, Windows PE) and runs the driver through the shared
# wine/wibo dispatcher (wine by default; REBREW_RUNNER=wibo selects the
# minimal loader).
#
# Build:  docker build -t rebrew/ee-gcc:3.2-030210-beta2-ps2 ee-gcc/3.2-030210-beta2-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ee-gcc:3.2-030210-beta2-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 3.2-030210-beta2 (PS2)" \
      org.opencontainers.image.description="EE-GCC 3.2-030210-beta2 (PS2 Emotion Engine, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-030210-beta2.tar.gz" \
    && echo "5244521973d3fa9712cc9f945e6e45c489d69d846ca6639b0c07c3e885a923a1  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/ee-gcc-3.2-030210-beta2 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/ee-gcc-3.2-030210-beta2 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-3.2-030210-beta2/bin/ee-gcc.exe

# The driver is a Cygwin build: wine resolves a spawned tool's imports
# through WINEPATH, so point it at the bundled dll/ (cygwin1.dll et al) —
# without it the driver fails before it finds its assembler.
ENV WINEPATH="Z:\\opt\\ee-gcc-3.2-030210-beta2\\dll"

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/ee-gcc-3.2-030210-beta2/bin/ee-gcc.exe "$@"' \
        > /usr/local/bin/ee-gcc \
    && chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
