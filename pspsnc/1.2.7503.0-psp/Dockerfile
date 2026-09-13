# rebrew PSPSNC 1.2.7503.0 (PSP) — decomp.me "pspsnc_1.2.7503.0".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (pspsnc.exe, Windows PE) and runs the driver through the shared
# wine/wibo dispatcher (wine by default; REBREW_RUNNER=wibo selects the
# minimal loader).
#
# Build:  docker build -t rebrew/pspsnc:1.2.7503.0-psp pspsnc/1.2.7503.0-psp
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/pspsnc:1.2.7503.0-psp -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSPSNC 1.2.7503.0 (PSP)" \
      org.opencontainers.image.description="PSPSNC 1.2.7503.0 (Sony PSP, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/pspsnc_1.2.7503.0.tar.gz" \
    && echo "0d10a4b387e45b62369eea21b6693fc5517335033bf65e65aa7b543a916f4d6d  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/pspsnc-1.2.7503.0 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/pspsnc-1.2.7503.0 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/pspsnc-1.2.7503.0/pspsnc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/pspsnc-1.2.7503.0/pspsnc.exe -td=. "$@"' \
        > /usr/local/bin/pspsnc \
    && chmod +x /usr/local/bin/pspsnc

ENTRYPOINT ["/usr/local/bin/pspsnc"]

USER rebrew
