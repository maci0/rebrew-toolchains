# rebrew MWCCPSP 3.0.1-134 (PSP) — decomp.me "mwccpsp_3.0.1_134".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (mwccpsp.exe + LMGR license DLL, Windows PE) and runs the compiler through the shared
# wine/wibo dispatcher — wibo by default, because the bundled LMGR licensing
# path fails under wine with a FLEXlm error (REBREW_RUNNER=wine still forces
# wine).
#
# Build:  docker build -t rebrew/mwccpsp:3.0.1-134-psp mwccpsp/3.0.1-134-psp
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwccpsp:3.0.1-134-psp -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCPSP 3.0.1-134 (PSP)" \
      org.opencontainers.image.description="MWCCPSP 3.0.1-134 (CodeWarrior PSP, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccpsp_3.0.1_134.tar.gz" \
    && echo "a4a00c2450ee2b6f7be29fc73470446994fcf2b1b1003b8ac34568f3358e1c99  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/mwccpsp-3.0.1-134 /tmp/x \
    && tar xzf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/. /opt/mwccpsp-3.0.1-134/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/mwccpsp-3.0.1-134/mwccpsp.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwccpsp-3.0.1-134/mwccpsp.exe "$@"' \
        > /usr/local/bin/mwccpsp \
    && chmod +x /usr/local/bin/mwccpsp

ENTRYPOINT ["/usr/local/bin/mwccpsp"]

USER rebrew
