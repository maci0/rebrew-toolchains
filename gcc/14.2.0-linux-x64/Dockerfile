# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-14.2.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 14.2.0 (ELF/x86_64, native, C)" \
      org.opencontainers.image.description="GCC 14.2.0 (ELF/x86_64, C only, built from source) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libgmp-dev libmpfr-dev libmpc-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.xz \
        "https://ftp.gnu.org/gnu/gcc/gcc-14.2.0/gcc-14.2.0.tar.xz" \
    && echo "a7b39bc69cbf9e25826c5a60ab26477001f7c08d85cec04bc0e29cabed6f3cc9  /tmp/gcc.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/gcc-14.2.0 /tmp/gcc-src /tmp/gcc-build \
    && tar xJf /tmp/gcc.tar.xz --strip-components=1 -C /tmp/gcc-src \
    && cd /tmp/gcc-build \
    && /tmp/gcc-src/configure --prefix=/opt/gcc-14.2.0 --enable-languages=c --disable-bootstrap --disable-multilib --disable-nls --disable-libsanitizer --with-system-zlib \
    && make -j"$(nproc)" \
    && make install-strip \
    && rm -rf /tmp/gcc.tar.xz /tmp/gcc-src /tmp/gcc-build \
    && /opt/gcc-14.2.0/bin/gcc --version

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
