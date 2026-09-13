# IDO 6.0 — SGI MIPS compiler (N64), original IRIX binaries under qemu-irix.
#
# Inherits the shared rebrew/base; this image installs the pinned
# LLONSIT/qemu-irix-helpers tarball (usr/bin/qemu-irix plus the IRIX IDO
# tree under usr/lib and usr/include).  Unlike the ido-static-recomp images
# (5.3/7.1) these are the genuine IRIX executables, so the entrypoint is the
# qemu user-mode IRIX emulator with the driver as its payload — the same
# invocation decomp.me uses.  No wine/DOSBox.
#
# Build:  docker build -t rebrew/ido:6.0-n64 ido/6.0-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ido:6.0-n64 -c -G0 -non_shared -32 t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 6.0 (N64, qemu-irix)" \
      org.opencontainers.image.description="IDO 6.0 (SGI MIPS, N64, IRIX binaries under qemu-irix) toolchain image"

# qemu-irix links glib at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido.tar.xz \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/ido6.0.tar.xz" \
    && echo "c56d4be020bdaf76310ceec455ebc0d443fb7a46c740491f74898b04f6a60356  /tmp/ido.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/ido-6.0 \
    && tar xJf /tmp/ido.tar.xz -C /opt/ido-6.0 \
    && rm /tmp/ido.tar.xz \
    && chmod +x /opt/ido-6.0/usr/bin/qemu-irix \
    && /opt/ido-6.0/usr/bin/qemu-irix --version 2>&1 | head -1 || true

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/ido-6.0/usr/bin/qemu-irix -L /opt/ido-6.0 /opt/ido-6.0/usr/lib/driver -I /opt/ido-6.0/usr/include "$@"' \
        > /usr/local/bin/cc \
    && chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
