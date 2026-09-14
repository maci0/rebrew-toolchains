# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ee-gcc-2.95.3-136

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.95.3-136 (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.95.3 build 136 (PS2 Emotion Engine, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ee-gcc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-136.tar.gz" \
    && echo "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f  /tmp/ee-gcc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ee-gcc-2.95.3 \
    && tar xzf /tmp/ee-gcc.tar.gz -C /opt/ee-gcc-2.95.3 \
    && rm /tmp/ee-gcc.tar.gz \
    && ls /opt/ee-gcc-2.95.3/bin/ee-gcc.exe

COPY ee-gcc-wrapper.sh /usr/local/bin/ee-gcc
RUN chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
