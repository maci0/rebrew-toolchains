# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ee-gcc-3.2-040921

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 3.2-040921 (PS2)" \
      org.opencontainers.image.description="EE-GCC 3.2-040921 (PS2 Emotion Engine, native i386) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ee-gcc.tar.xz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-040921.tar.xz" \
    && echo "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f  /tmp/ee-gcc.tar.xz" | sha256sum -c -

RUN mkdir -p /opt/ee-gcc-3.2-040921 \
    && tar xJf /tmp/ee-gcc.tar.xz -C /opt/ee-gcc-3.2-040921 \
    && rm /tmp/ee-gcc.tar.xz \
    && chmod +x /opt/ee-gcc-3.2-040921/bin/ee-gcc \
    && /opt/ee-gcc-3.2-040921/bin/ee-gcc --version

COPY ee-gcc-wrapper.sh /usr/local/bin/ee-gcc
RUN chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
