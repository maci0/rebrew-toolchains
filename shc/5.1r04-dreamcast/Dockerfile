# SHC 5.1r04 — Hitachi SuperH C compiler (Dreamcast), decomp.me "shc-v5.1r04".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (Windows PE tools + bundled headers) and the revision-pinned
# rof2elf.py converter.  The compiler runs through the shared wine/wibo
# dispatcher.
#
# SHC locates its sibling passes through SHC_LIB and writes temporaries under
# SHC_TMP; without both it dies with "(0) : 3321 (F) Illegal environment
# variable".  It emits a relocatable object (.obj, ROF), so the conversion
# step the Dreamcast decomp flows run next is separate:
#   shc f.c -cpu=sh4 -endian=little -object=f.obj
#   rof2elf.py f.obj f.o --isa=sh4
#
# Build:  docker build -t rebrew/shc:5.1r04-dreamcast shc/5.1r04-dreamcast
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/shc:5.1r04-dreamcast t.c -cpu=sh4 -endian=little -object=t.obj

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew SHC 5.1r04 (Dreamcast)" \
      org.opencontainers.image.description="SHC 5.1r04 (Hitachi SuperH, Dreamcast, PE/x86_32) toolchain image"

# rof2elf.py (the .obj → ELF converter this SHC release needs) is a Python
# script; the base image has no interpreter.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*

# The gist is pinned to its revision in the URL; the sha256 below is that
# revision's content, so a rewritten gist fails the build.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/shc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/shc-v5.1r04.tar.gz" \
    && echo "277065890128db57816d40a968d510c6a7f9e3c97929d75fd45226755eebb34d  /tmp/shc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/shc-5.1r04 \
    && tar xzf /tmp/shc.tar.gz -C /opt/shc-5.1r04 \
    && rm /tmp/shc.tar.gz \
    && curl -fsSL --retry 3 --retry-all-errors -o /opt/shc-5.1r04/rof2elf.py \
        "https://gist.githubusercontent.com/Mc-muffin/c2d3f30e50c5c5749f994973441c503a/raw/18fbf1a19bd720d02774ed634b00b0508eaf474c/rof2elf.py" \
    && echo "f5a52b69b619e206172da4dc74182ecc97eeac5dcfcf5466c537af5ea6310821  /opt/shc-5.1r04/rof2elf.py" | sha256sum -c - \
    && chmod +x /opt/shc-5.1r04/rof2elf.py /opt/shc-5.1r04/bin/* \
    && ls /opt/shc-5.1r04/bin/shc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'SHC_LIB=/opt/shc-5.1r04/bin' \
        'SHC_TMP=${TMPDIR:-/tmp}' \
        'export SHC_LIB SHC_TMP' \
        'rebrew_run /opt/shc-5.1r04/bin/shc.exe "$@"' \
        > /usr/local/bin/shc \
    && chmod +x /usr/local/bin/shc

ENTRYPOINT ["/usr/local/bin/shc"]

USER rebrew
