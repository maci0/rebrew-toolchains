# GCC 2.8.1 (papermario build) — N64 decomp compiler.
#
# Inherits the shared rebrew/base; this image installs the pinned
# pmret/gcc-papermario and pmret/binutils-papermario prebuilts.  Both are
# flat dumps of the built tools (gcc/cc1/cpp + as/ar/objcopy), merged into
# one directory that the wrapper points -B at, exactly how decomp.me
# invokes it.  Native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/gcc:2.8.1-pm-n64 gcc/2.8.1-pm-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.8.1-pm-n64 -G0 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.8.1 PM (N64)" \
      org.opencontainers.image.description="GCC 2.8.1 (papermario, N64, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.gz \
        "https://github.com/pmret/gcc-papermario/releases/download/master/linux.tar.gz" \
    && echo "1156cf0d6a88a64c20e2a10fc9445d99cb9a38518f432b1669528dfa82ebb45f  /tmp/gcc.tar.gz" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/binutils.tar.gz \
        "https://github.com/pmret/binutils-papermario/releases/download/master/linux.tar.gz" \
    && echo "c3cd88db47ac41f78b557042c7e7ad47ac9c04cee6f0d1069a489c1c9e8c103c  /tmp/binutils.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/gcc-2.8.1-pm \
    && tar xzf /tmp/gcc.tar.gz -C /opt/gcc-2.8.1-pm \
    && tar xzf /tmp/binutils.tar.gz -C /opt/gcc-2.8.1-pm \
    && rm /tmp/gcc.tar.gz /tmp/binutils.tar.gz \
    && chmod +x /opt/gcc-2.8.1-pm/gcc /opt/gcc-2.8.1-pm/as \
    && /opt/gcc-2.8.1-pm/gcc --version

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/gcc-2.8.1-pm/gcc -B /opt/gcc-2.8.1-pm/ "$@"' \
        > /usr/local/bin/gcc \
    && chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
