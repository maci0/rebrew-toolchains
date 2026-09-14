# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ee-gcc-2.95.3-107

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.95.3-107 (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.95.3-107 (PS2 Emotion Engine, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ps2_compilers.tar.xz" \
    && echo "f337a65a4fbab5cf0e335efe266dcbc7cf69b19c665c6b3a8924736df151a02a  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ee-gcc-2.95.3-107 /tmp/x \
    && tar xJf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/ee-gcc2.95.3-107/. /opt/ee-gcc-2.95.3-107/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-2.95.3-107/bin/ee-gcc.exe

COPY ee-gcc-wrapper.sh /usr/local/bin/ee-gcc
RUN chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
