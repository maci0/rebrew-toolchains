# rebrew MWCPS2 3.0.1b198-051011 (PS2) — decomp.me "mwcps2-3.0.1b198-051011".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (mwccps2/mwccmips.exe + assembler + LMGR license DLL, Windows PE) and runs the compiler through the shared
# wine/wibo dispatcher — wibo by default, because the bundled LMGR licensing
# path fails under wine with a FLEXlm error (REBREW_RUNNER=wine still forces
# wine).
#
# Build:  docker build -t rebrew/mwcps2:3.0.1b198-051011-ps2 mwcps2/3.0.1b198-051011-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwcps2:3.0.1b198-051011-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCPS2 3.0.1b198-051011 (PS2)" \
      org.opencontainers.image.description="MWCPS2 3.0.1b198-051011 (CodeWarrior PS2, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwcps2-3.0.1b198-051011.tar.gz" \
    && echo "436af8060249e7ea0aa2dfa98a86b4667ee3716b3384cca577c52c5b68e4934a  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/mwcps2-3.0.1b198-051011 /tmp/x \
    && tar xzf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/. /opt/mwcps2-3.0.1b198-051011/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/mwcps2-3.0.1b198-051011/mwccps2.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwcps2-3.0.1b198-051011/mwccps2.exe "$@"' \
        > /usr/local/bin/mwcps2 \
    && chmod +x /usr/local/bin/mwcps2

ENTRYPOINT ["/usr/local/bin/mwcps2"]

USER rebrew
