# GCC 2.96 arm-elf (Camelot flavour) — GBA decomp compiler.
#
# Inherits the shared rebrew/base; this image installs the pinned Camelot
# gcc-2.96-20000731 arm-elf tree (SBird1337/camelot-gcc) and exposes the
# arm-elf-gcc driver as the entrypoint.  Native ELF — no wine/DOSBox.
#
# The tarball is a complete `--prefix=/usr/local` install (bin/, arm-elf/bin/,
# lib/gcc-lib/), so it is extracted at the image root: the driver resolves
# its cc1/as relative to that baked-in prefix.
#
# Build:  docker build -t rebrew/gcc:2.96-gba gcc/2.96-gba
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.96-gba -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.96 Camelot (GBA)" \
      org.opencontainers.image.description="GCC 2.96 arm-elf (Camelot, GBA, native x86_64) toolchain image"

# The tarball is a complete `--prefix=/usr/local` install (bin/,
# arm-elf/bin/, lib/gcc-lib/), so it lands under /opt like every other
# image and the two trees the driver resolves through its baked-in prefix
# are symlinked into place: cc1/cpp through lib/gcc-lib, the assembler and
# linker through arm-elf/bin.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc296.tar.gz \
        "https://github.com/SBird1337/camelot-gcc/releases/download/2.96/gcc-2.96-20000731-armelf.tar.gz" \
    && echo "c0613784e1c3b228512db2abebdce1e7b8afc211dc904d9ae23b913fd9025af9  /tmp/gcc296.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/camelot-2.96 \
    && tar xzf /tmp/gcc296.tar.gz -C /opt/camelot-2.96 \
    && rm /tmp/gcc296.tar.gz \
    && ln -s /opt/camelot-2.96/usr/local/lib/gcc-lib /usr/local/lib/gcc-lib \
    && ln -s /opt/camelot-2.96/usr/local/arm-elf /usr/local/arm-elf \
    && /opt/camelot-2.96/usr/local/bin/arm-elf-gcc --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/camelot-2.96/usr/local/bin/arm-elf-gcc "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
