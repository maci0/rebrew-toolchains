# rebrew IOP-GCC 2.95.2-102 (PS2) — decomp.me "iop-gcc2.95.2-102".
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (bin/iop-gcc.exe + lib/gcc-lib/mipsel-scei-elfl tree, Windows PE) and runs the driver through the shared
# wine/wibo dispatcher (wine by default; REBREW_RUNNER=wibo selects the
# minimal loader).
#
# Build:  docker build -t rebrew/iop-gcc:2.95.2-102-ps2 iop-gcc/2.95.2-102-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/iop-gcc:2.95.2-102-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IOP-GCC 2.95.2-102 (PS2)" \
      org.opencontainers.image.description="IOP-GCC 2.95.2 build 102 (PS2 IOP, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/iop-gcc2.95.2-102.tar.gz" \
    && echo "84016c5899358f65bb320081087f7fb82e32fd5f4ab25733bec094d4baa9728a  /tmp/compiler.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/iop-gcc-2.95.2-102 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/iop-gcc-2.95.2-102 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/iop-gcc-2.95.2-102/bin/iop-gcc.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/iop-gcc-2.95.2-102/bin/iop-gcc.exe -B /opt/iop-gcc-2.95.2-102/lib/gcc-lib/mipsel-scei-elfl/2.95.2/ "$@"' \
        > /usr/local/bin/iop-gcc \
    && chmod +x /usr/local/bin/iop-gcc

ENTRYPOINT ["/usr/local/bin/iop-gcc"]

USER rebrew
