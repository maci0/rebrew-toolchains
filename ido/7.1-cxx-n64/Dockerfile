# IDO 7.1 C++ — SGI MIPS C++ compiler (N64) via ido-static-recomp, native Linux.
#
# Same pinned decompals/ido-static-recomp v1.2 tarball as `ido/7.1-n64`; the
# difference is the driver.  IDO 7.1's C++ mode lives behind `NCC` (which
# drives `acpp` + the EDG front end `edgcpfe`), while the tree's `cc` driver
# only speaks C and rejects C++ sources — decomp.me's `ido7.1_c++` recipe
# calls `NCC` for exactly that reason.  Statically recompiled IDO, so it runs
# natively on Linux x86_64: no wine/DOSBox, no qemu, no host files.
#
# Build:  docker build -t rebrew/ido:7.1-cxx-n64 ido/7.1-cxx-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ido:7.1-cxx-n64 -c t.C -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 7.1 C++ (MIPS, N64)" \
      org.opencontainers.image.description="IDO 7.1 C++ reimplementation (MIPS-II big-endian, N64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido71.tar.gz \
        "https://github.com/decompals/ido-static-recomp/releases/download/v1.2/ido-7.1-recomp-linux.tar.gz" \
    && echo "0d411696e178fcca34c31c3bf02011b928d7fd9c1fa7f8bf45070e0781b58e15  /tmp/ido71.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/ido/7.1 \
    && tar xzf /tmp/ido71.tar.gz -C /opt/ido/7.1 \
    && rm /tmp/ido71.tar.gz \
    && chmod +x /opt/ido/7.1/NCC \
    && ls /opt/ido/7.1/acpp

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'rebrew_exec /opt/ido/7.1/NCC "$@"' \
        > /usr/local/bin/cc \
    && chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
