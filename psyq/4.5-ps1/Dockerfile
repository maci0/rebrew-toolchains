# PSY-Q 4.5 — PS1 SDK toolchain: the SDK's gcc 2.8.1-psx compiler (the
# compiler Sony shipped in PSY-Q 4.5, rebuilt natively by decompals/old-gcc)
# plus the PSY-Q 4.5 headers and libraries from the FoxdieTeam/psyq_sdk
# preservation repo.
#
# Inherits the shared rebrew/base; both pinned sources download inside the
# build.  The compiler runs natively (static ELF); the wrapper prepends the
# PSY-Q include dir so plain `cc -c f.c` sees the SDK headers, and everything
# else passes through verbatim.
#
# Build:  docker build -t rebrew/psyq:4.5-ps1 psyq/4.5-ps1
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/psyq:4.5-ps1 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 4.5 (PS1)" \
      org.opencontainers.image.description="PSY-Q 4.5 (gcc 2.8.1-psx + SDK headers/libs, native x86_64) toolchain image"

# The compiler: gcc 2.8.1 psx flavour (flat release asset, static ELF).
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc281.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.8.1-psx.tar.gz" \
    && echo "f6f6e883942d4d3289d048236c672e71ed410e546aaae8ff655952f1567e1be0  /tmp/gcc281.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/psyq/4.5/bin \
    && tar xzf /tmp/gcc281.tar.gz -C /opt/psyq/4.5/bin \
    && rm /tmp/gcc281.tar.gz \
    && chmod +x /opt/psyq/4.5/bin/gcc

# The SDK: PSY-Q 4.5 include/ + lib/ from the FoxdieTeam preservation repo
# (commit-pinned branch tarball).  ponytail: no byte pin possible here —
# codeload gzip streams are not byte-stable, so the git commit is the pin.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://codeload.github.com/FoxdieTeam/psyq_sdk/tar.gz/91719fa5bdca0b7e55c5c4b9e045da407db93510" \
    && mkdir -p /tmp/psyq \
    && tar xzf /tmp/psyq.tar.gz -C /tmp/psyq --strip-components=1 \
    && cp -a /tmp/psyq/psyq_4.5/include /tmp/psyq/psyq_4.5/lib /opt/psyq/4.5/ \
    && rm -rf /tmp/psyq.tar.gz /tmp/psyq \
    && ls /opt/psyq/4.5/lib/libgte.lib

# See gcc/2.6.3-ps1: the release asset is a flat dump but the driver was
# configured --prefix=/opt/cross, so its cpp/cc1 must live under
# /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1/ (and get an assembler).
RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/cross/bin /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1 \
    && cp /opt/psyq/4.5/bin/cc1 /opt/psyq/4.5/bin/cc1plus /opt/psyq/4.5/bin/cpp \
        /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1/ \
    && cp /opt/psyq/4.5/bin/gcc /opt/cross/bin/gcc \
    && cp /opt/psyq/4.5/bin/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1/ld \
    && /opt/cross/bin/gcc --version

# The `cc` wrapper: the PSY-Q include dir is baked in so SDK sources compile
# without per-call -I flags; the compiler argv is otherwise verbatim.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/cross/bin/gcc -I /opt/psyq/4.5/include "$@"' \
        > /usr/local/bin/cc \
    && chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
