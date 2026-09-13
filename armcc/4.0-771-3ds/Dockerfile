# ARMCC 4.0-771 (CodeWarrior for 3DS) — decomp.me "armcc_40_771".
#
# Inherits the shared rebrew/base; this image extracts the 4.0/b771 subtree
# (armcc.exe + license DLLs) from the pinned decompme/compilers
# armcc.zip.  The compiler is a 32-bit Windows PE binary, so the entrypoint
# runs it through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/armcc:4.0-771-3ds armcc/4.0-771-3ds
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/armcc:4.0-771-3ds -c --cpu=MPCore t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew ARMCC 4.0-771 (3DS)" \
      org.opencontainers.image.description="ARMCC 4.0-771 (CodeWarrior 3DS, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://github.com/decompme/compilers/releases/download/compilers/armcc.zip?2026-03-04" \
    && echo "bda0cea5b13a9c3f08322fa76f9f9dcda59bda290f57f1a06e05cd80044fafdb  /tmp/compilers.zip" | sha256sum -c - \
    && mkdir -p /opt/armcc-4.0-771 \
    && unzip -q /tmp/compilers.zip '4.0/b771/*' -d /tmp/x \
    && cp -a /tmp/x/4.0/b771/. /opt/armcc-4.0-771/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/armcc-4.0-771/bin/armcc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/armcc-4.0-771/bin/armcc.exe -I /opt/armcc-4.0-771/include "$@"' \
        > /usr/local/bin/armcc \
    && chmod +x /usr/local/bin/armcc

ENTRYPOINT ["/usr/local/bin/armcc"]

USER rebrew
