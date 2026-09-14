# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.7.2-kmc

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2 KMC (N64)" \
      org.opencontainers.image.description="GCC 2.7.2 KMC (mips-mips-gnu, decompals mips-gcc-2.7.2 prebuilt, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc272.tar.gz \
        "https://github.com/decompals/mips-gcc-2.7.2/releases/download/main/gcc-2.7.2-linux.tar.gz" \
    && echo "ff3e299c1d952c0a5cb39f7790a208d0c547cf93986eb5607f820c935cedc288  /tmp/gcc272.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/binutils26.tar.gz \
        "https://github.com/decompals/mips-binutils-2.6/releases/download/main/binutils-2.6-linux.tar.gz" \
    && echo "405a7ddb29a0b2eb472b167e8f15472223df1eff3093a5ff31d6e545d3a6c670  /tmp/binutils26.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/gcc-2.7.2-kmc \
    && tar xzf /tmp/gcc272.tar.gz -C /opt/gcc-2.7.2-kmc \
    && rm /tmp/gcc272.tar.gz \
    && chmod +x /opt/gcc-2.7.2-kmc/gcc \
    && mkdir -p /opt/mips-binutils-2.6 \
    && tar xzf /tmp/binutils26.tar.gz -C /opt/mips-binutils-2.6 \
    && rm /tmp/binutils26.tar.gz \
    && chmod +x /opt/mips-binutils-2.6/* \
    && mkdir -p /opt/cross/bin /opt/cross/lib/gcc-lib/mips-mips-gnu/2.7.2 \
    && cp /opt/gcc-2.7.2-kmc/cc1 /opt/gcc-2.7.2-kmc/cc1plus /opt/gcc-2.7.2-kmc/cpp /opt/cross/lib/gcc-lib/mips-mips-gnu/2.7.2/ \
    && cp /opt/gcc-2.7.2-kmc/gcc /opt/cross/bin/gcc \
    && cp /opt/gcc-2.7.2-kmc/g++ /opt/cross/bin/g++ \
    && cp /opt/mips-binutils-2.6/* /opt/cross/bin/ \
    && ln -s /opt/cross/bin/as /opt/cross/lib/gcc-lib/mips-mips-gnu/2.7.2/as \
    && /opt/cross/bin/gcc --version

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
