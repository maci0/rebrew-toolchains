# rebrew IDO 5.3 C++ (N64, qemu-irix) — N64 compiler, original IRIX binaries under qemu-irix.
#
# Inherits the shared rebrew/base; this image installs the pinned
# LLONSIT/qemu-irix-helpers tarball (usr/bin/qemu-irix plus the IRIX tree).
# The entrypoint is the qemu user-mode IRIX emulator with the vendor *C++*
# driver (`usr/lib/CC`) as its payload — exactly decomp.me's `ido5.3_c++`
# recipe.  The generic `usr/lib/driver` shipped in the same tree only knows
# the C front end and rejects C++ sources, so `CC` is what makes this the C++
# image.  Native ELF, no wine/DOSBox; qemu-irix needs libglib2.0.
#
# Build:  docker build -t rebrew/ido:5.3-cxx-n64 ido/5.3-cxx-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ido:5.3-cxx-n64 -c t.C -o t.o
# Trap:   the IRIX driver predates the `.cpp` convention and only treats `.C` and
#         `.cc` as C++.  A `.cpp` input is *silently ignored* — exit 0, no object.

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 5.3 C++ (N64, qemu-irix)" \
      org.opencontainers.image.description="IDO 5.3 C++ (SGI MIPS, N64, IRIX binaries under qemu-irix) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido.tar.xz \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/ido5.3_c++.tar.xz" \
    && echo "851426c63ffb0688c702793113c2d9aa3c703c7a4e9d4240fc99d1862f79e4b9  /tmp/ido.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/ido-5.3-c++ \
    && tar xJf /tmp/ido.tar.xz -C /opt/ido-5.3-c++ \
    && rm /tmp/ido.tar.xz \
    && chmod +x /opt/ido-5.3-c++/usr/bin/qemu-irix \
    && ls /opt/ido-5.3-c++/usr/lib/CC

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/ido-5.3-c++/usr/bin/qemu-irix -silent -L /opt/ido-5.3-c++ /opt/ido-5.3-c++/usr/lib/CC -I /opt/ido-5.3-c++/usr/include "$@"' \
        > /usr/local/bin/cc \
    && chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
