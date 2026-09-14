# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.91.66-psx

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.91.66-psx (PS1)" \
      org.opencontainers.image.description="GCC 2.91.66-psx (psx flavour (egcs), decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.91.66-psx.tar.gz" \
    && echo "f773a0a9659fa4ff74313ac4363d939312e8125675cd09ad9f8c1202f587f1fd  /tmp/gcc.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/gcc-2.91.66-psx /opt/cross/bin /opt/cross/lib/gcc-lib/mips-sony-psx/egcs-2.91.66 \
    && tar xzf /tmp/gcc.tar.gz -C /opt/gcc-2.91.66-psx \
    && rm /tmp/gcc.tar.gz \
    && chmod +x /opt/gcc-2.91.66-psx/gcc \
    && cp /opt/gcc-2.91.66-psx/cc1 /opt/gcc-2.91.66-psx/cc1plus /opt/gcc-2.91.66-psx/cpp /opt/cross/lib/gcc-lib/mips-sony-psx/egcs-2.91.66/ \
    && cp /opt/gcc-2.91.66-psx/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.91.66-psx/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-sony-psx/egcs-2.91.66/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-sony-psx/egcs-2.91.66/ld \
    && /opt/cross/bin/gcc --version

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
