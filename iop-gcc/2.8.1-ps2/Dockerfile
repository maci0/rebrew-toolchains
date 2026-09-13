# IOP-GCC 2.8.1 — PS2 I/O processor compiler (decomp.me id iop-gcc2.8.1).
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# tarball (native Linux `bin/iop-gcc` driver with its own
# lib/gcc-lib/mipsel-scei-elfl/2.8.1/{cc1,cpp,as} prefix tree) and exposes
# the driver as the entrypoint.  Native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/iop-gcc:2.8.1-ps2 iop-gcc/2.8.1-ps2
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/iop-gcc:2.8.1-ps2 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IOP-GCC 2.8.1 (PS2)" \
      org.opencontainers.image.description="IOP-GCC 2.8.1 (PS2 IOP, mipsel-scei-elfl, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/iop-gcc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/iop-gcc2.8.1.tar.gz" \
    && echo "1f602e146f5be218cb3c84cda615432035bcf4a4f1a5f249164163a456ac929a  /tmp/iop-gcc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/iop-gcc-2.8.1 \
    && tar xzf /tmp/iop-gcc.tar.gz -C /opt/iop-gcc-2.8.1 \
    && rm /tmp/iop-gcc.tar.gz \
    && chmod +x /opt/iop-gcc-2.8.1/bin/iop-gcc \
    && /opt/iop-gcc-2.8.1/bin/iop-gcc --version

# The driver's baked-in prefix is the original SDK path
# (/usr/local/sce/iop/gcc), so the wrapper passes -B at the shipped
# lib/gcc-lib tree — exactly how decomp.me invokes it.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/iop-gcc-2.8.1/bin/iop-gcc -B /opt/iop-gcc-2.8.1/lib/gcc-lib/mipsel-scei-elfl/2.8.1/ "$@"' \
        > /usr/local/bin/iop-gcc \
    && chmod +x /usr/local/bin/iop-gcc

ENTRYPOINT ["/usr/local/bin/iop-gcc"]

USER rebrew
