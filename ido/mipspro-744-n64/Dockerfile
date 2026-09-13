# rebrew MIPSpro 7.4.4 (N64, qemu-irix) — N64 compiler, original IRIX binaries under qemu-irix.
#
# Inherits the shared rebrew/base; this image installs the pinned
# LLONSIT/qemu-irix-helpers tarball (usr/bin/qemu-irix plus the IRIX tree).
# The entrypoint is the qemu user-mode IRIX emulator with the vendor driver
# as its payload — the same invocation decomp.me uses.  Native ELF, no
# wine/DOSBox; qemu-irix needs libglib2.0.
#
# Build:  docker build -t rebrew/ido:mipspro-744-n64 ido/mipspro-744-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ido:mipspro-744-n64 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MIPSpro 7.4.4 (N64, qemu-irix)" \
      org.opencontainers.image.description="MIPSpro 7.4.4 (SGI MIPS, N64, IRIX binaries under qemu-irix) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido.tar.xz \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/mipspro7.4.4.tar.xz" \
    && echo "df33be0d9605b00b44070e567121fc00283a9b1f97763403f0898d2216028d24  /tmp/ido.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/ido-mipspro-744 \
    && tar xJf /tmp/ido.tar.xz -C /opt/ido-mipspro-744 \
    && rm /tmp/ido.tar.xz \
    && chmod +x /opt/ido-mipspro-744/usr/bin/qemu-irix \
    && ls /opt/ido-mipspro-744/usr/lib/driver

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/ido-mipspro-744/usr/bin/qemu-irix -L /opt/ido-mipspro-744 /opt/ido-mipspro-744/usr/lib/driver -I /opt/ido-mipspro-744/usr/include "$@"' \
        > /usr/local/bin/cc \
    && chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
