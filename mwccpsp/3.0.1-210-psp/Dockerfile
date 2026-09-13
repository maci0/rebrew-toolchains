# MWCCPSP 3.0.1 build 210 (CodeWarrior for PSP) — decomp.me
# "mwccpsp_3.0.1_210".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (mwccpsp.exe + LMGR8C.DLL, Windows PE) and runs the compiler
# through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/mwccpsp:3.0.1-210-psp mwccpsp/3.0.1-210-psp
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwccpsp:3.0.1-210-psp -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCPSP 3.0.1-210 (PSP)" \
      org.opencontainers.image.description="MWCCPSP 3.0.1 build 210 (CodeWarrior PSP, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwccpsp.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccpsp_3.0.1_210.tar.gz" \
    && echo "a8a0bf3a0ec3545f6578717516aad0f262a40dd1538a6e462b77efc29e79a969  /tmp/mwccpsp.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/mwccpsp-3.0.1-210 \
    && tar xzf /tmp/mwccpsp.tar.gz -C /opt/mwccpsp-3.0.1-210 \
    && rm /tmp/mwccpsp.tar.gz \
    && ls /opt/mwccpsp-3.0.1-210/mwccpsp.exe

# See mwccarm/2.0-87-nds: the bundled LMGR licensing path works under wibo
# and fails under wine (FLEXlm error).
ENV REBREW_RUNNER=wibo

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwccpsp-3.0.1-210/mwccpsp.exe "$@"' \
        > /usr/local/bin/mwccpsp \
    && chmod +x /usr/local/bin/mwccpsp

ENTRYPOINT ["/usr/local/bin/mwccpsp"]

USER rebrew
