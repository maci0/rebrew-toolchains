# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.7.2.3-mipsel

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2.3 (PS1)" \
      org.opencontainers.image.description="GCC 2.7.2.3 (mipsel flavour, decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.7.2.3.tar.gz" \
    && echo "34e525c1feb9a6f4ef98b590e72dacb4c79a67c5f135db11d6a9cb62a5e74edb  /tmp/gcc.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/gcc-2.7.2.3 /opt/cross/bin /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.2.3 \
    && tar xzf /tmp/gcc.tar.gz -C /opt/gcc-2.7.2.3 \
    && rm /tmp/gcc.tar.gz \
    && chmod +x /opt/gcc-2.7.2.3/gcc \
    && cp /opt/gcc-2.7.2.3/cc1 /opt/gcc-2.7.2.3/cc1plus /opt/gcc-2.7.2.3/cpp /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.2.3/ \
    && cp /opt/gcc-2.7.2.3/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.7.2.3/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.2.3/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.2.3/ld \
    && /opt/cross/bin/gcc --version

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
