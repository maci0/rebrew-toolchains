# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: psyq-4.5

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 4.5 (PS1)" \
      org.opencontainers.image.description="PSY-Q 4.5 (gcc 2.8.1-psx + SDK headers/libs, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc281.tar.gz \
        "https://github.com/decompals/old-gcc/releases/download/0.17/gcc-2.8.1-psx.tar.gz" \
    && echo "f6f6e883942d4d3289d048236c672e71ed410e546aaae8ff655952f1567e1be0  /tmp/gcc281.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://codeload.github.com/FoxdieTeam/psyq_sdk/tar.gz/91719fa5bdca0b7e55c5c4b9e045da407db93510" \
    && echo "495697696a3288866d83ff7b7aff423560ffaffd3e212274417f3348cc0b29f8  /tmp/psyq.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/psyq/4.5/bin \
    && tar xzf /tmp/gcc281.tar.gz -C /opt/psyq/4.5/bin \
    && rm /tmp/gcc281.tar.gz \
    && chmod +x /opt/psyq/4.5/bin/gcc \
    && mkdir -p /tmp/psyq \
    && tar xzf /tmp/psyq.tar.gz --strip-components=1 -C /tmp/psyq \
    && cp -a /tmp/psyq/psyq_4.5/include /tmp/psyq/psyq_4.5/lib /opt/psyq/4.5/ \
    && rm -rf /tmp/psyq.tar.gz /tmp/psyq \
    && ls /opt/psyq/4.5/lib/libgte.lib \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/cross/bin /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1 \
    && cp /opt/psyq/4.5/bin/cc1 /opt/psyq/4.5/bin/cc1plus /opt/psyq/4.5/bin/cpp /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1/ \
    && cp /opt/psyq/4.5/bin/gcc /opt/cross/bin/gcc \
    && cp /opt/psyq/4.5/bin/g++ /opt/cross/bin/g++ \
    && ln -s /usr/bin/mipsel-linux-gnu-as /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1/as \
    && ln -s /usr/bin/mipsel-linux-gnu-ld /opt/cross/lib/gcc-lib/mips-sony-psx/2.8.1/ld \
    && /opt/cross/bin/gcc --version

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
