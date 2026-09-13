# SHC 5.1 revision 13 — Hitachi SuperH C compiler (Dreamcast, decomp.me id
# shc-v5.1r13).
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (Windows PE tools: bin/shc.exe driver + shcgen/asmsh/... and the
# bundled headers) and the pinning gist revision of rof2elf.py, the
# relocatable-object converter the SH decomp flows use.  The compiler runs
# through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/shc:5.1r13-dreamcast shc/5.1r13-dreamcast
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/shc:5.1r13-dreamcast -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew SHC 5.1r13 (Dreamcast)" \
      org.opencontainers.image.description="SHC 5.1r13 (Hitachi SuperH, Dreamcast, PE/x86_32) toolchain image"

# The gist is pinned to its revision in the URL; the sha256 below is that
# revision's content, so a rewritten gist fails the build.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/shc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/shc-v5.1r13.tar.gz" \
    && echo "0da9982adc576171d93ceeeedff15c946fc570b0473e39b388e18d9e4ee1427a  /tmp/shc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/shc-5.1r13 \
    && tar xzf /tmp/shc.tar.gz -C /opt/shc-5.1r13 \
    && rm /tmp/shc.tar.gz \
    && curl -fsSL --retry 3 --retry-all-errors -o /opt/shc-5.1r13/rof2elf.py \
        "https://gist.githubusercontent.com/Mc-muffin/c2d3f30e50c5c5749f994973441c503a/raw/18fbf1a19bd720d02774ed634b00b0508eaf474c/rof2elf.py" \
    && echo "f5a52b69b619e206172da4dc74182ecc97eeac5dcfcf5466c537af5ea6310821  /opt/shc-5.1r13/rof2elf.py" | sha256sum -c - \
    && chmod +x /opt/shc-5.1r13/rof2elf.py /opt/shc-5.1r13/bin/*.exe \
    && ls /opt/shc-5.1r13/bin/shc.exe

# rof2elf.py (the .obj → ELF converter this SHC release needs) is a Python
# script; the base image has no interpreter.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*

# The compiler locates its sibling passes through SHC_LIB and writes its
# temporary files under SHC_TMP; without both it dies with
# "(0) : 3321 (F) Illegal environment variable".  SHC emits a relocatable
# object (.obj, ROF), so the toolchain ships rof2elf.py for the conversion
# step the Dreamcast decomp flows run next:
#   shc f.c -cpu=sh4 -endian=little -object=f.obj
#   rof2elf.py f.obj f.o --isa=sh4
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'SHC_LIB=/opt/shc-5.1r13/bin' \
        'SHC_TMP=${TMPDIR:-/tmp}' \
        'export SHC_LIB SHC_TMP' \
        'rebrew_run /opt/shc-5.1r13/bin/shc.exe "$@"' \
        > /usr/local/bin/shc \
    && chmod +x /usr/local/bin/shc

ENTRYPOINT ["/usr/local/bin/shc"]

USER rebrew
