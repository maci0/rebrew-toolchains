# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.6.3-ps1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.6.3 (PS1)" \
      org.opencontainers.image.description="GCC 2.6.3 (mips-sony-psx, decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc263.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.6.3-psx.tar.gz" \
    && echo "01e6e8c4933414ea3f8d8e3bc766a1f5fafd4fc0110e0b75d1f691bd791989b1  /tmp/gcc263.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/gcc-2.6.3-ps1 \
    && tar xzf /tmp/gcc263.tar.gz -C /opt/gcc-2.6.3-ps1 \
    && rm /tmp/gcc263.tar.gz \
    && chmod +x /opt/gcc-2.6.3-ps1/gcc \
    && /opt/gcc-2.6.3-ps1/gcc --version \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/cross/bin /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3 \
    && cp /opt/gcc-2.6.3-ps1/cc1 /opt/gcc-2.6.3-ps1/cc1plus /opt/gcc-2.6.3-ps1/cpp /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3/ \
    && cp /opt/gcc-2.6.3-ps1/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.6.3-ps1/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-sony-psx/2.6.3/ld

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
