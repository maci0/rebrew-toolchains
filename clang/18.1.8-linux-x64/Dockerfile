# Clang 18.1.8 — LLVM's official prebuilt x86_64 Linux release (native ELF).
#
# Inherits the shared rebrew/base; this image downloads the pinned
# clang+llvm 18.1.8 tarball published for the llvmorg-18.1.8 tag (x86_64,
# ubuntu-18.04 build — the only x86_64 Linux asset that release published)
# and exposes clang as the entrypoint.  The binaries run natively on Linux
# x86_64 — no wine/DOSBox.  libc6-dev is installed because clang's own
# builtin headers cover <stddef.h>/<stdarg.h> but not the C library headers
# a decompiled source includes (<stdint.h>, <string.h>, ...).  libtinfo5
# supplies the ncurses5 ABI (libtinfo.so.5) the ubuntu-18.04 build links
# against; bookworm ships the ncurses6 ABI only.
#
# Build:  docker build -t rebrew/clang:18.1.8-linux-x64 clang/18.1.8-linux-x64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/clang:18.1.8-linux-x64 -c t.c -o t.o  (ENTRYPOINT is the clang wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 18.1.8 (ELF/x86_64, native)" \
      org.opencontainers.image.description="Clang 18.1.8 (ELF/x86_64, native, LLVM release build) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev libtinfo5 \
    && rm -rf /var/lib/apt/lists/*

# clang+llvm 18.1.8 release tarball (sha256-verified).  The tarball's single
# top-level directory is stripped so the install root is /opt/clang-18.1.8.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://github.com/llvm/llvm-project/releases/download/llvmorg-18.1.8/clang+llvm-18.1.8-x86_64-linux-gnu-ubuntu-18.04.tar.xz" \
    && echo "54ec30358afcc9fb8aa74307db3046f5187f9fb89fb37064cdde906e062ebf36  /tmp/clang.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/clang-18.1.8 \
    && tar xJf /tmp/clang.tar.xz -C /opt/clang-18.1.8 --strip-components=1 \
    && rm /tmp/clang.tar.xz \
    && /opt/clang-18.1.8/bin/clang --version

# The `clang` wrapper: exec the compiler under the shared watchdog
# (REBREW_RUNNER_TIMEOUT) so a hung compile fails loudly.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/clang-18.1.8/bin/clang "$@"' \
        > /usr/local/bin/clang \
    && chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

# Runtime drops back to the base image's non-root user.
USER rebrew
