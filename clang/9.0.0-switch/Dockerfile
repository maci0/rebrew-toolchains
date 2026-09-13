# Clang 9.0.0 — LLVM official prebuilt x86_64 Linux release (Switch decomp).
#
# Inherits the shared rebrew/base; this image downloads the pinned
# clang+llvm 9.0.0 ubuntu-18.04 tarball from releases.llvm.org (the matching
# GitHub release carries no binary assets) and exposes clang as the
# entrypoint.  Native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/clang:9.0.0-switch clang/9.0.0-switch
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/clang:9.0.0-switch -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 9.0.0 (Switch)" \
      org.opencontainers.image.description="Clang 9.0.0 (LLVM prebuilt, native x86_64, Switch decomp) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev binutils \
    && rm -rf /var/lib/apt/lists/*

# clang+llvm 9.0.0 (sha256-verified; strip-1 install root) plus the real
# libtinfo5 the 9.0.0 build links against: bookworm ships libtinfo6 only, and
# the soname symlink trick does not satisfy the versioned symbol check.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://releases.llvm.org/9.0.0/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz" \
    && echo "a23b082b30c128c9831dbdd96edad26b43f56624d0ad0ea9edec506f5385038d  /tmp/clang.tar.xz" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/libtinfo5.deb \
        "http://deb.debian.org/debian/pool/main/n/ncurses/libtinfo5_6.4-4_amd64.deb" \
    && echo "dd347f794e651039e7b4c391f86c674fed7f415b3dca6b0937beb0d470f09c1a  /tmp/libtinfo5.deb" | sha256sum -c - \
    && mkdir -p /opt/clang-9.0.0 /tmp/tinfo5 \
    && tar xJf /tmp/clang.tar.xz -C /opt/clang-9.0.0 --strip-components=1 \
    && cd /tmp/tinfo5 \
    && ar x /tmp/libtinfo5.deb data.tar.xz \
    && tar xJf data.tar.xz \
    && cp lib/x86_64-linux-gnu/libtinfo.so.5* /opt/clang-9.0.0/lib/ \
    && rm -rf /tmp/tinfo5 /tmp/clang.tar.xz /tmp/libtinfo5.deb \
    && LD_LIBRARY_PATH=/opt/clang-9.0.0/lib /opt/clang-9.0.0/bin/clang --version

ENV LD_LIBRARY_PATH=/opt/clang-9.0.0/lib

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/clang-9.0.0/bin/clang "$@"' \
        > /usr/local/bin/clang \
    && chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
