# Clang 16.0.4 — LLVM's official prebuilt x86_64 Linux release (native ELF).
#
# Inherits the shared rebrew/base; this image downloads the pinned
# clang+llvm 16.0.4 tarball published for the llvmorg-16.0.4 tag (x86_64,
# ubuntu-22.04 build) and exposes clang as the entrypoint.  The binaries run
# natively on Linux x86_64 — no wine/DOSBox.  16.0.4 is the newest 16.x
# release LLVM published an x86_64 Linux asset for: llvmorg-16.0.5 and
# llvmorg-16.0.6 shipped aarch64 and powerpc64le builds only.
#
# Build:  docker build -t rebrew/clang:16.0.4-linux-x64 clang/16.0.4-linux-x64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/clang:16.0.4-linux-x64 -c t.c -o t.o  (ENTRYPOINT is the clang wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 16.0.4 (ELF/x86_64, native)" \
      org.opencontainers.image.description="Clang 16.0.4 (ELF/x86_64, native, LLVM release build) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# clang+llvm 16.0.4 release tarball (sha256-verified).  The tarball's single
# top-level directory is stripped so the install root is /opt/clang-16.0.4.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://github.com/llvm/llvm-project/releases/download/llvmorg-16.0.4/clang+llvm-16.0.4-x86_64-linux-gnu-ubuntu-22.04.tar.xz" \
    && echo "fd464333bd55b482eb7385f2f4e18248eb43129a3cda4c0920ad9ac3c12bdacf  /tmp/clang.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/clang-16.0.4 \
    && tar xJf /tmp/clang.tar.xz -C /opt/clang-16.0.4 --strip-components=1 \
    && rm /tmp/clang.tar.xz \
    && /opt/clang-16.0.4/bin/clang --version

# The `clang` wrapper: exec the compiler under the shared watchdog
# (REBREW_RUNNER_TIMEOUT) so a hung compile fails loudly.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/clang-16.0.4/bin/clang "$@"' \
        > /usr/local/bin/clang \
    && chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

# Runtime drops back to the base image's non-root user.
USER rebrew
