# IDO 5.3 (IRIX originals) — SGI MIPS compiler for N64, under qemu-irix.
#
# Inherits the shared rebrew/base; this image installs the original IRIX IDO
# 5.3 tree from LLONSIT/qemu-irix-helpers (`ssb_ido5.3.tar`) and exposes its
# driver through the qemu user-mode IRIX emulator, exactly as the other IDO
# images here do.
#
# This is a *different toolchain* from `ido/5.3-n64`: that one is decompals'
# static recompilation of IDO 5.3 (native Linux binaries), while this image
# runs the original IRIX executables under emulation — the binaries matching
# decomp projects reach for when the recompilation's codegen differs.
#
# The tarball's own `usr/bin/qemu-irix` needs GLIBC_2.38 (bookworm ships
# 2.36), so the image replaces it with the older emulator from the same repo's
# `ido_root.tar.xz`, which runs on this base.  The IRIX4-flavoured trees
# (`ssb_ido7.1.tar`, and the `usr/irix4` sub-trees here) need an IRIX
# 4.0-capable emulator and are not shipped — see docs/PROVENANCE.md.
#
# Build:  docker build -t rebrew/ido:5.3-irix-n64 ido/5.3-irix-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ido:5.3-irix-n64 -c -G0 -non_shared -32 t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 5.3 IRIX originals (N64, qemu-irix)" \
      org.opencontainers.image.description="IDO 5.3 (SGI MIPS, N64, original IRIX binaries under qemu-irix) toolchain image"

# qemu-irix links glib at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# IRIX IDO 5.3 tree (sha256-verified).
RUN mkdir -p /opt/ido-irix-5.3 /tmp/ido \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido/ssb.tar \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/ssb_ido5.3.tar" \
    && echo "a8a5bfa1713cc63c157ed4d61d0fb19f2d2ab10612fd9df2ceeb1de517cda4d4  /tmp/ido/ssb.tar" | sha256sum -c - \
    && tar xf /tmp/ido/ssb.tar -C /opt/ido-irix-5.3 \
    && rm -rf /tmp/ido \
    && ls /opt/ido-irix-5.3/usr/lib/driver

# Replace the bundled emulator (needs glibc 2.38) with the older build from
# the same repository, which runs on this base image.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido_root.tar.xz \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/ido_root.tar.xz" \
    && echo "d0d8a0deb1508fb1d3e91d5eaaded16a267af0be8e98aac7a104ba1bf4f677fb  /tmp/ido_root.tar.xz" | sha256sum -c - \
    && tar xJf /tmp/ido_root.tar.xz -C /tmp \
    && cp /tmp/ido_root/usr/bin/qemu-irix /opt/ido-irix-5.3/usr/bin/qemu-irix \
    && rm -rf /tmp/ido_root.tar.xz /tmp/ido_root \
    && chmod +x /opt/ido-irix-5.3/usr/bin/qemu-irix \
    && /opt/ido-irix-5.3/usr/bin/qemu-irix --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/ido-irix-5.3/usr/bin/qemu-irix -L /opt/ido-irix-5.3 /opt/ido-irix-5.3/usr/lib/driver -I /opt/ido-irix-5.3/usr/include "$@"' \
        > /usr/local/bin/cc \
    && chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
