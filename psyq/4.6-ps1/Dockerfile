# PSY-Q 4.6 — PS1 SDK with the genuine Sony CCPSX.EXE driver.
#
# Inherits the shared rebrew/base; this image installs the pinned
# mkst/esa `psyq-binaries` release (CCPSX.EXE, CC1PSX.EXE, PSYLIB, ...) and
# the decompme/compilers psyq-obj-parser, which converts the Sony object
# CCPSX writes into an ELF relocatable.  The PE driver runs through the
# shared wine/wibo dispatcher.
#
# CCPSX reads its configuration from SN.INI in the working directory, so the
# wrapper writes that file: the paths must carry the wine drive letter
# (Z: is the container root) — a backslash-only path makes CCPSX mangle its
# temporary file names and abort
# and then execs the driver with the caller's arguments verbatim; the output
# is a Sony-format object, so the conversion step is separate:
#   cc -c f.c -o f.obj              # CCPSX.EXE via wine, writes f.obj
#   psyq-obj-parser f.obj -o f.o    # bundled converter
#
# Build:  docker build -t rebrew/psyq:4.6-ps1 psyq/4.6-ps1
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/psyq:4.6-ps1 -c f.c -o f.obj

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 4.6 (PS1)" \
      org.opencontainers.image.description="PSY-Q 4.6 (Sony CCPSX.EXE + obj parser, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/mkst/esa/releases/download/psyq-binaries/psyq4.6.tar.gz" \
    && echo "635603e09a452c9c2923492fea8b8eb051959dd94f240933b88e94866814b894  /tmp/psyq.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/psyq-4.6 \
    && tar xzf /tmp/psyq.tar.gz -C /opt/psyq-4.6 --strip-components=1 \
    && rm /tmp/psyq.tar.gz \
    && ls /opt/psyq-4.6/CCPSX.EXE

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/parser.tar.gz -C /opt/psyq-4.6 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/psyq-4.6/psyq-obj-parser

# The `cc` wrapper: SN.INI is written into the working directory (CCPSX reads
# it from there), then the driver gets the caller's argv unchanged inside it.
# The paths need the wine drive letter (Z: is the container root); the
# quoted heredoc keeps the backslashes literal — a shell echo would turn
# \tmp into a tab and CCPSX would fail on its own temp file name.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'cat > SN.INI <<\INI' \
        '[ccpsx]' \
        'compiler_path=Z:\opt\psyq-4.6' \
        'assembler_path=Z:\opt\psyq-4.6' \
        'tmpdir=Z:\tmp' \
        'INI' \
        'SN_PATH=. rebrew_run /opt/psyq-4.6/CCPSX.EXE "$@"' \
        > /usr/local/bin/cc \
    && chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
