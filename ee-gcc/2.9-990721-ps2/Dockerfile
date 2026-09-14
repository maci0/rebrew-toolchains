# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ee-gcc-2.9-990721

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.9-990721 (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.9-990721 (PS2 Emotion Engine, native i386) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-990721.tar.xz" \
    && echo "ad2ea68afff2be25d21a1d51a75e8a0eea8f259018e6580622355cd01b95676b  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ee-gcc-2.9-990721 \
    && tar xJf /tmp/compiler.tar.gz -C /opt/ee-gcc-2.9-990721 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-2.9-990721/bin/ee-gcc

COPY ee-gcc-wrapper.sh /usr/local/bin/ee-gcc
RUN chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
