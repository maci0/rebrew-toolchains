# MWCPS2 3.0.3 (CodeWarrior PlayStation 2) — decomp.me "mwcps2-3.0.3".
#
# Inherits the shared rebrew/base; this image installs the pinned
# mwcps2-3.0.3-020716 release asset from decompme/compilers (flat tarball:
# mwccps2.exe, asm_r5900_elf.exe, LMGR326B.dll — Windows PE, run under
# wine/wibo; build 020716 is the correctly-labelled 3.0.3).
#
# Build:  docker build -t rebrew/mwcps2:3.0.3-ps2 mwcps2/3.0.3-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mwcps2:3.0.3-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCPS2 3.0.3 (PS2)" \
      org.opencontainers.image.description="MWCPS2 3.0.3 (CodeWarrior PS2, PE/x86_32) toolchain image"

# Flat release asset (no top-level directory) — extract in place.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwcps2.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwcps2-3.0.3-020716.tar.gz" \
    && echo "63f89baae691403294724178efbcfc9e1b9ac48151536b6a321b17eb8f9970e5  /tmp/mwcps2.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/mwcps2-3.0.3 \
    && tar xzf /tmp/mwcps2.tar.gz -C /opt/mwcps2-3.0.3 \
    && rm /tmp/mwcps2.tar.gz \
    && ls /opt/mwcps2-3.0.3/mwccps2.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mwcps2-3.0.3/mwccps2.exe "$@"' \
        > /usr/local/bin/mwccps2 \
    && chmod +x /usr/local/bin/mwccps2

ENTRYPOINT ["/usr/local/bin/mwccps2"]

USER rebrew
