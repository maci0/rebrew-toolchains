# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwccarm-4.0-1027

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCARM 4.0-1027 (NDS)" \
      org.opencontainers.image.description="MWCCARM 4.0-1027 (CodeWarrior NDS, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccarm.zip" \
    && echo "dc386e37b2176e960954a733de928337d9b7e7620b9e94228008c31774339ace  /tmp/compilers.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/mwccarm-4.0-1027 \
    && unzip -q /tmp/compilers.zip 'mwccarm/dsi/1.2p1/*' 'mwccarm/license.dat' -d /tmp/x \
    && cp -a /tmp/x/mwccarm/dsi/1.2p1/. /opt/mwccarm-4.0-1027/ \
    && cp /tmp/x/mwccarm/license.dat /opt/mwccarm-4.0-1027/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/mwccarm-4.0-1027/mwccarm.exe

COPY mwccarm-wrapper.sh /usr/local/bin/mwccarm
RUN chmod +x /usr/local/bin/mwccarm

ENTRYPOINT ["/usr/local/bin/mwccarm"]

USER rebrew
