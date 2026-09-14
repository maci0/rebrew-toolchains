# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: prodg-3.7

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PRODG 3.7 (GameCube)" \
      org.opencontainers.image.description="PRODG 3.7 (SN Systems ProDG GameCube, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

ENV SN_NGC_PATH='Z:\\opt\\prodg-3.7'

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251015.zip" \
    && echo "491cb62317c7f3669ac283ae159e82e3c97a5713b78299571ba4cf023dc7e95e  /tmp/compilers.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/prodg-3.7 \
    && unzip -q /tmp/compilers.zip 'ProDG/3.7/*' -d /tmp/x \
    && cp -a /tmp/x/ProDG/3.7/. /opt/prodg-3.7/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/prodg-3.7/ngccc.exe

COPY ngccc-wrapper.sh /usr/local/bin/ngccc
RUN chmod +x /usr/local/bin/ngccc

ENTRYPOINT ["/usr/local/bin/ngccc"]

USER rebrew
