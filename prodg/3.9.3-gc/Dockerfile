# ProDG 3.9.3 (SN Systems) — GameCube compiler (decomp.me id prodg_393).
#
# Inherits the shared rebrew/base; this image extracts the ProDG/3.9.3
# subtree (ngccc.exe driver with cc1/cc1plus/cpp/assembler/linker, Windows
# PE) from the pinned files.decomp.dev compilers zip and runs it through the
# shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/prodg:3.9.3-gc prodg/3.9.3-gc
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/prodg:3.9.3-gc -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew ProDG 3.9.3 (GameCube)" \
      org.opencontainers.image.description="ProDG 3.9.3 (SN Systems GameCube, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251015.zip" \
    && echo "491cb62317c7f3669ac283ae159e82e3c97a5713b78299571ba4cf023dc7e95e  /tmp/compilers.zip" | sha256sum -c - \
    && mkdir -p /opt/prodg-3.9.3 \
    && unzip -q /tmp/compilers.zip 'ProDG/3.9.3/*' -d /tmp/prodg \
    && cp -a /tmp/prodg/ProDG/3.9.3/. /opt/prodg-3.9.3/ \
    && rm -rf /tmp/prodg /tmp/compilers.zip \
    && ls /opt/prodg-3.9.3/ngccc.exe

# ngccc refuses to run without SN_NGC_PATH ("Unable to initialise settings
# - possible problem in sn.ini"), and it wants a *Windows-style directory*
# path (it appends its own separator + sn.ini): wine maps the container root
# to Z:, so the install dir is spelled Z:\opt\prodg-3.9.3.
ENV SN_NGC_PATH='Z:\\opt\\prodg-3.9.3'

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/prodg-3.9.3/ngccc.exe "$@"' \
        > /usr/local/bin/ngccc \
    && chmod +x /usr/local/bin/ngccc

ENTRYPOINT ["/usr/local/bin/ngccc"]

USER rebrew
