# agbcc (FE8J fork) — GBA decomp compiler, decomp.me "agbcc-fe8j".
#
# Inherits the shared rebrew/base; this image installs the pinned
# laqieer/agbcc release asset (bin/, include/, lib/ at the tarball root) and
# exposes the agbcc driver as the entrypoint.  Native ELF — no wine/DOSBox.
# Like the pret image, this is a cc1-style compiler: it consumes a
# preprocessed/plain C file and writes assembly.
#
# Build:  docker build -t rebrew/agbcc:fe8j-gba agbcc/fe8j-gba
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/agbcc:fe8j-gba -O2 t.c -o t.s

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew agbcc FE8J (GBA)" \
      org.opencontainers.image.description="agbcc (laqieer FE8J fork, GBA, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/agbcc.tar.gz \
        "https://github.com/laqieer/agbcc/releases/download/fe8j-v1/agbcc.tar.gz" \
    && echo "5bdeac906031476a341f09929d303c5834d8adda8dc00bd85934eb4b2463daa7  /tmp/agbcc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/agbcc-fe8j \
    && tar xzf /tmp/agbcc.tar.gz -C /opt/agbcc-fe8j \
    && rm /tmp/agbcc.tar.gz \
    && chmod +x /opt/agbcc-fe8j/bin/agbcc \
    && ls /opt/agbcc-fe8j/bin/agbcc

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/agbcc-fe8j/bin/agbcc "$@"' \
        > /usr/local/bin/agbcc \
    && chmod +x /usr/local/bin/agbcc

ENTRYPOINT ["/usr/local/bin/agbcc"]

USER rebrew
