# Clang 8.0.0 — LLVM official prebuilt x86_64 Linux release (Switch decomp).
#
# Inherits the shared rebrew/base; this image downloads the pinned
# clang+llvm 8.0.0 ubuntu-18.04 tarball from releases.llvm.org (the
# llvmorg-8.0.0 GitHub release carries no binary assets) and exposes clang
# as the entrypoint.  Native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/clang:8.0.0-switch clang/8.0.0-switch
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/clang:8.0.0-switch -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 8.0.0 (Switch)" \
      org.opencontainers.image.description="Clang 8.0.0 (LLVM prebuilt, native x86_64, Switch decomp) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev binutils \
    && rm -rf /var/lib/apt/lists/*

# clang+llvm 8.0.0 release tarball (sha256-verified; strip-1 install root).
# The 2019 build links libtinfo.so.5 *with a versioned symbol check*, so the
# bookworm symlink trick is not enough — the real libtinfo5 (bookworm-era
# 6.4 build, sha256-pinned .deb) is unpacked into the install root's lib/.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://releases.llvm.org/8.0.0/clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz" \
    && echo "0f5c314f375ebd5c35b8c1d5e5b161d9efaeff0523bac287f8b4e5b751272f51  /tmp/clang.tar.xz" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/libtinfo5.deb \
        "http://deb.debian.org/debian/pool/main/n/ncurses/libtinfo5_6.4-4_amd64.deb" \
    && echo "dd347f794e651039e7b4c391f86c674fed7f415b3dca6b0937beb0d470f09c1a  /tmp/libtinfo5.deb" | sha256sum -c - \
    && mkdir -p /opt/clang-8.0.0 /tmp/tinfo5 \
    && tar xJf /tmp/clang.tar.xz -C /opt/clang-8.0.0 --strip-components=1 \
    && cd /tmp/tinfo5 \
    && ar x /tmp/libtinfo5.deb data.tar.xz \
    && tar xJf data.tar.xz \
    && cp lib/x86_64-linux-gnu/libtinfo.so.5* /opt/clang-8.0.0/lib/ \
    && rm -rf /tmp/tinfo5 /tmp/clang.tar.xz /tmp/libtinfo5.deb \
    && LD_LIBRARY_PATH=/opt/clang-8.0.0/lib /opt/clang-8.0.0/bin/clang --version

ENV LD_LIBRARY_PATH=/opt/clang-8.0.0/lib

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/clang-8.0.0/bin/clang "$@"' \
        > /usr/local/bin/clang \
    && chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
