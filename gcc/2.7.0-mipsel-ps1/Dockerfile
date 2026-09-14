# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.7.0-mipsel

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.0-mipsel (PS1)" \
      org.opencontainers.image.description="GCC 2.7.0-mipsel (mipsel flavour, decompals/old-gcc prebuilt, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.7.0.tar.gz" \
    && echo "157a26ae5ecd60d395bf9ab0d9c8321920f62f789dec0223cb79ed6c9a96ee48  /tmp/gcc.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/gcc-2.7.0-mipsel /opt/cross/bin /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.0 \
    && tar xzf /tmp/gcc.tar.gz -C /opt/gcc-2.7.0-mipsel \
    && rm /tmp/gcc.tar.gz \
    && chmod +x /opt/gcc-2.7.0-mipsel/gcc \
    && cp /opt/gcc-2.7.0-mipsel/cc1 /opt/gcc-2.7.0-mipsel/cc1plus /opt/gcc-2.7.0-mipsel/cpp /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.0/ \
    && cp /opt/gcc-2.7.0-mipsel/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.7.0-mipsel/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.0/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-linux-gnu/2.7.0/ld \
    && /opt/cross/bin/gcc --version

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
