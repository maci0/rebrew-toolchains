# MWCCPSP 3.0.1-121 (CodeWarrior for PSP) — decomp.me "mwccpsp_3.0.1_121".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (flat: mwccpsp.exe + LMGR license DLL, Windows PE) and runs the
# compiler through the shared wine/wibo dispatcher — wibo by default (its
# LMGR licensing path fails under wine with a FLEXlm error).
#
# Build:  docker build -t rebrew/mwccpsp:3.0.1-121-psp mwccpsp/3.0.1-121-psp
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwccpsp:3.0.1-121-psp -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCPSP 3.0.1-121 (PSP)" \
      org.opencontainers.image.description="MWCCPSP 3.0.1-121 (CodeWarrior PSP, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwccpsp.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccpsp_3.0.1_121.tar.gz" \
    && echo "44836bb4d19fbe216b55fbd638420c000f7dd373c84493de0e732e85f81656af  /tmp/mwccpsp.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/mwccpsp-3.0.1-121 \
    && tar xzf /tmp/mwccpsp.tar.gz -C /opt/mwccpsp-3.0.1-121 \
    && rm /tmp/mwccpsp.tar.gz \
    && ls /opt/mwccpsp-3.0.1-121/mwccpsp.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwccpsp-3.0.1-121/mwccpsp.exe "$@"' \
        > /usr/local/bin/mwccpsp \
    && chmod +x /usr/local/bin/mwccpsp

ENTRYPOINT ["/usr/local/bin/mwccpsp"]

USER rebrew
