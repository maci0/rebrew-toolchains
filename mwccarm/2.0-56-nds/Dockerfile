# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwccarm-2.0-56

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCARM 2.0-56 (NDS)" \
      org.opencontainers.image.description="MWCCARM 2.0-56 (CodeWarrior NDS ARM9, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwccarm.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwcc_20_56.tar.gz" \
    && echo "91e10b9826bb985641a6db075da444a51bf25dd53df3216cb8bc05548561ec45  /tmp/mwccarm.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwccarm-2.0-56 \
    && tar xzf /tmp/mwccarm.tar.gz -C /opt/mwccarm-2.0-56 \
    && rm /tmp/mwccarm.tar.gz \
    && ls /opt/mwccarm-2.0-56/mwccarm.exe

COPY mwccarm-wrapper.sh /usr/local/bin/mwccarm
RUN chmod +x /usr/local/bin/mwccarm

ENTRYPOINT ["/usr/local/bin/mwccarm"]

USER rebrew
