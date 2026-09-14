# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: prodg-3.9.3

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

ENV SN_NGC_PATH='Z:\\opt\\prodg-3.9.3'

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251015.zip" \
    && echo "491cb62317c7f3669ac283ae159e82e3c97a5713b78299571ba4cf023dc7e95e  /tmp/compilers.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/prodg-3.9.3 \
    && unzip -q /tmp/compilers.zip 'ProDG/3.9.3/*' -d /tmp/prodg \
    && cp -a /tmp/prodg/ProDG/3.9.3/. /opt/prodg-3.9.3/ \
    && rm -rf /tmp/prodg /tmp/compilers.zip \
    && ls /opt/prodg-3.9.3/ngccc.exe

COPY ngccc-wrapper.sh /usr/local/bin/ngccc
RUN chmod +x /usr/local/bin/ngccc

ENTRYPOINT ["/usr/local/bin/ngccc"]

USER rebrew
