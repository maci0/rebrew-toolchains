# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.95.2-ps1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.95.2 (PS1)" \
      org.opencontainers.image.description="GCC 2.95.2 (mips-sony-psx, decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc2952.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.95.2-psx.tar.gz" \
    && echo "932ed3669710a82b12570c29c46ff42989b6505b2af10db84d4551d55dfc0b1c  /tmp/gcc2952.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/gcc-2.95.2-ps1 \
    && tar xzf /tmp/gcc2952.tar.gz -C /opt/gcc-2.95.2-ps1 \
    && rm /tmp/gcc2952.tar.gz \
    && chmod +x /opt/gcc-2.95.2-ps1/gcc \
    && /opt/gcc-2.95.2-ps1/gcc --version \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/cross/bin /opt/cross/lib/gcc-lib/mips-sony-psx/2.95.2 \
    && cp /opt/gcc-2.95.2-ps1/cc1 /opt/gcc-2.95.2-ps1/cc1plus /opt/gcc-2.95.2-ps1/cpp /opt/cross/lib/gcc-lib/mips-sony-psx/2.95.2/ \
    && cp /opt/gcc-2.95.2-ps1/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.95.2-ps1/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-sony-psx/2.95.2/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-sony-psx/2.95.2/ld

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
