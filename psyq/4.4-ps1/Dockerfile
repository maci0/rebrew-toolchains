# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: psyq-4.4

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 4.4 (PS1)" \
      org.opencontainers.image.description="PSY-Q 4.4 (CC1PSX + ASPSX pipeline + obj parser, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cpp dos2unix \
    && rm -rf /var/lib/apt/lists/*

ENV PSYQ_ROOT=/opt/psyq-4.4 \
    REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/mkst/esa/releases/download/psyq-binaries/psyq4.4.tar.gz" \
    && echo "72e73934bab0d51933eb95af514afb14f3d432f01530eac3ddb16dfbb57ab66c  /tmp/psyq.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/psyq-4.4 \
    && tar xzf /tmp/psyq.tar.gz --strip-components=1 -C /opt/psyq-4.4 \
    && rm /tmp/psyq.tar.gz \
    && ls /opt/psyq-4.4/CC1PSX.EXE \
    && tar xzf /tmp/parser.tar.gz -C /opt/psyq-4.4 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/psyq-4.4/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
