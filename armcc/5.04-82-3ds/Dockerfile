# ARMCC 5.04-82 (ARM Compiler, Nintendo 3DS) — decomp.me "armcc_504_82".
#
# Inherits the shared rebrew/base; this image extracts the 5.04/b82 subtree
# (bin/armcc.exe + include/) from the pinned decompme/compilers armcc zip.
# The compiler is a 32-bit Windows PE binary, so the entrypoint runs it
# through the shared wine/wibo dispatcher; the wrapper bakes in the SDK
# include dir, as decomp.me's own recipe does.
#
# Build:  docker build -t rebrew/armcc:5.04-82-3ds armcc/5.04-82-3ds
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/armcc:5.04-82-3ds --cpu=MPCore -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew ARMCC 5.04-82 (3DS)" \
      org.opencontainers.image.description="ARM Compiler 5.04-82 (Nintendo 3DS, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/armcc.zip \
        "https://github.com/decompme/compilers/releases/download/compilers/armcc.zip?2026-03-04" \
    && echo "bda0cea5b13a9c3f08322fa76f9f9dcda59bda290f57f1a06e05cd80044fafdb  /tmp/armcc.zip" | sha256sum -c - \
    && mkdir -p /opt/armcc-5.04-82 \
    && unzip -q /tmp/armcc.zip '5.04/b82/*' -d /tmp/armcc \
    && cp -a /tmp/armcc/5.04/b82/. /opt/armcc-5.04-82/ \
    && rm -rf /tmp/armcc /tmp/armcc.zip \
    && ls /opt/armcc-5.04-82/bin/armcc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/armcc-5.04-82/bin/armcc.exe -I /opt/armcc-5.04-82/include "$@"' \
        > /usr/local/bin/armcc \
    && chmod +x /usr/local/bin/armcc

ENTRYPOINT ["/usr/local/bin/armcc"]

USER rebrew
