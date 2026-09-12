# GCC 12.3.0 — GNU C compiler built from source inside the image (native ELF).
#
# Inherits the shared rebrew/base; this image downloads the pinned GNU
# release tarball, builds C-only (rebrew compiles C) with
# --enable-languages=c, and installs it to /opt/gcc-12.3.0.  No bootstrap
# and no multilib: the compiler itself is the point, not a fully
# self-hosted toolchain.  The `gcc` entrypoint wrapper execs the installed
# driver natively — no wine/DOSBox.
#
# Build:  docker build -t rebrew/gcc:12.3.0-linux-x64 gcc/12.3.0-linux-x64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:12.3.0-linux-x64 -c t.c -o t.o  (ENTRYPOINT is the gcc wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 12.3.0 (ELF/x86_64, native, C)" \
      org.opencontainers.image.description="GCC 12.3.0 (ELF/x86_64, C only, built from source) toolchain image"

# Build prerequisites: the C toolchain itself, the three GCC prerequisites
# (GMP/MPFR/MPC), and zlib1g-dev for --with-system-zlib.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential libgmp-dev libmpfr-dev libmpc-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# GNU GCC 12.3.0 release tarball (sha256-verified), configured for C only.
# --disable-libsanitizer keeps the build to libgcc/libgomp: the sanitizer
# runtime is a large C++-era target library rebrew never links against.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.xz \
        "https://ftp.gnu.org/gnu/gcc/gcc-12.3.0/gcc-12.3.0.tar.xz" \
    && echo "949a5d4f99e786421a93b532b22ffab5578de7321369975b91aec97adfda8c3b  /tmp/gcc.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/gcc-12.3.0 /tmp/gcc-src /tmp/gcc-build \
    && tar xJf /tmp/gcc.tar.xz -C /tmp/gcc-src --strip-components=1 \
    && cd /tmp/gcc-build \
    && /tmp/gcc-src/configure \
        --prefix=/opt/gcc-12.3.0 \
        --enable-languages=c \
        --disable-bootstrap \
        --disable-multilib \
        --disable-nls \
        --disable-libsanitizer \
        --with-system-zlib \
    && make -j"$(nproc)" \
    && make install-strip \
    && rm -rf /tmp/gcc.tar.xz /tmp/gcc-src /tmp/gcc-build \
    && /opt/gcc-12.3.0/bin/gcc --version

# The `gcc` wrapper: exec the installed compiler under the shared watchdog
# (REBREW_RUNNER_TIMEOUT) so a hung compile fails loudly.  POSIX argv is
# passed through unchanged — no DOS/MSVC translation.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/gcc-12.3.0/bin/gcc "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

# Runtime drops back to the base image's non-root user.
USER rebrew
