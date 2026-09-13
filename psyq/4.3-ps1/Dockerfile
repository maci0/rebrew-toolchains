# PSY-Q 4.3 — PS1 SDK compiler pipeline (CC1PSX + ASPSX).
#
# Inherits the shared rebrew/base; this image installs the pinned mkst/esa
# `psyq-binaries` release (CC1PSX.EXE, ASPSX.EXE, PSYLIB, ...) and the
# decompme/compilers psyq-obj-parser.  Unlike 4.5/4.6 there is no CCPSX
# driver here: the SDK compiles through CC1PSX.EXE and assembles with
# ASPSX.EXE, so the `cc` wrapper runs that pipeline (see cc-wrapper.sh) and
# converts the resulting Sony object with psyq-obj-parser.  Both PE tools run
# through the shared wine/wibo dispatcher — wibo by default, as decomp.me's
# own recipe uses (REBREW_RUNNER=wine still forces wine).
#
# Build:  docker build -t rebrew/psyq:4.3-ps1 psyq/4.3-ps1
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/psyq:4.3-ps1 -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 4.3 (PS1)" \
      org.opencontainers.image.description="PSY-Q 4.3 (CC1PSX + ASPSX pipeline + obj parser, PE/x86_32) toolchain image"

# The pipeline needs a preprocessor to feed CC1PSX.
RUN apt-get update \
    && apt-get install -y --no-install-recommends cpp dos2unix \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/mkst/esa/releases/download/psyq-binaries/psyq4.3.tar.gz" \
    && echo "577038d66507d3aa5423de0ba3f540e121a4f60f637f4794aa4350135d4f9a46  /tmp/psyq.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/psyq-4.3 \
    && tar xzf /tmp/psyq.tar.gz -C /opt/psyq-4.3 --strip-components=1 \
    && rm /tmp/psyq.tar.gz \
    && ls /opt/psyq-4.3/CC1PSX.EXE

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/parser.tar.gz -C /opt/psyq-4.3 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/psyq-4.3/psyq-obj-parser

ENV PSYQ_ROOT=/opt/psyq-4.3 \
    REBREW_RUNNER=wibo

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
