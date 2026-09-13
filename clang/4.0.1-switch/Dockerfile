# Clang 4.0.1 — LLVM official prebuilt x86_64 Linux release (Switch decomp).
#
# Inherits the shared rebrew/base; this image downloads the pinned
# clang+llvm 4.0.1 debian8 tarball from releases.llvm.org (the llvmorg-4.0.1
# GitHub release carries no binary assets) and exposes clang as the
# entrypoint.  Native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/clang:4.0.1-switch clang/4.0.1-switch
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/clang:4.0.1-switch -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 4.0.1 (Switch)" \
      org.opencontainers.image.description="Clang 4.0.1 (LLVM prebuilt, native x86_64, Switch decomp) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# clang+llvm 4.0.1 release tarball (sha256-verified; strip-1 install root).
# The 2017 debian8 build links libtinfo.so.5, which bookworm no longer ships
# — symlink the soname to the installed libtinfo6 (the API the tools use is
# unchanged for setupterm-style calls).
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://releases.llvm.org/4.0.1/clang+llvm-4.0.1-x86_64-linux-gnu-debian8.tar.xz" \
    && echo "ca48a4def4cbc9dd6af3f46ce1dc2bd903d26c7ad51387f57884ad1eaa58e42f  /tmp/clang.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/clang-4.0.1 \
    && tar xJf /tmp/clang.tar.xz -C /opt/clang-4.0.1 --strip-components=1 \
    && rm /tmp/clang.tar.xz \
    && ln -s "$(ldconfig -p | awk '/libtinfo\.so\.6/{print $NF; exit}')" /opt/clang-4.0.1/lib/libtinfo.so.5 \
    && LD_LIBRARY_PATH=/opt/clang-4.0.1/lib /opt/clang-4.0.1/bin/clang --version

ENV LD_LIBRARY_PATH="/opt/clang-4.0.1/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# The `clang` wrapper: exec the compiler under the shared watchdog.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/clang-4.0.1/bin/clang "$@"' \
        > /usr/local/bin/clang \
    && chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
