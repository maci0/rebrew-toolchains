# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwcc-2.3.3-163

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCC 2.3.3 b163 (GameCube)" \
      org.opencontainers.image.description="MWCC 2.3.3 build 163 (CodeWarrior GameCube, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251015.zip" \
    && echo "491cb62317c7f3669ac283ae159e82e3c97a5713b78299571ba4cf023dc7e95e  /tmp/compilers.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/mwcc-2.3.3 \
    && unzip -q /tmp/compilers.zip 'GC/1.2.5/*' -d /tmp/mwcc \
    && cp -a /tmp/mwcc/GC/1.2.5/. /opt/mwcc-2.3.3/ \
    && rm -rf /tmp/mwcc /tmp/compilers.zip \
    && ls /opt/mwcc-2.3.3/mwcceppc.exe

COPY mwcceppc-wrapper.sh /usr/local/bin/mwcceppc
RUN chmod +x /usr/local/bin/mwcceppc

ENTRYPOINT ["/usr/local/bin/mwcceppc"]

USER rebrew
