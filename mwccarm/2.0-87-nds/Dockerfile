# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwccarm-2.0-87

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCARM 2.0-87 (NDS)" \
      org.opencontainers.image.description="MWCCARM 2.0-87 (CodeWarrior NDS ARM9, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwccarm.zip \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccarm.zip" \
    && echo "dc386e37b2176e960954a733de928337d9b7e7620b9e94228008c31774339ace  /tmp/mwccarm.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/mwccarm-2.0-87 \
    && unzip -q /tmp/mwccarm.zip 'mwccarm/1.2/sp4/*' 'mwccarm/license.dat' -d /tmp/mwccarm \
    && cp -a /tmp/mwccarm/mwccarm/1.2/sp4/. /opt/mwccarm-2.0-87/ \
    && cp /tmp/mwccarm/mwccarm/license.dat /opt/mwccarm-2.0-87/ \
    && rm -rf /tmp/mwccarm /tmp/mwccarm.zip \
    && ls /opt/mwccarm-2.0-87/mwccarm.exe

COPY mwccarm-wrapper.sh /usr/local/bin/mwccarm
RUN chmod +x /usr/local/bin/mwccarm

ENTRYPOINT ["/usr/local/bin/mwccarm"]

USER rebrew
