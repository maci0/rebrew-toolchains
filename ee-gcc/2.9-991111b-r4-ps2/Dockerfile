# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ee-gcc-2.9-991111b-r4

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 2.9-991111b-r4 (PS2)" \
      org.opencontainers.image.description="EE-GCC 2.9-991111b-r4 (PS2 Emotion Engine, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-991111.tar.gz" \
    && echo "9ebbb042eb1e5d33d772293c5e9286a54dbec29865a3d7fbb398c97436f33583  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ee-gcc-2.9-991111b-r4 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/ee-gcc-2.9-991111b-r4 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-2.9-991111b-r4/bin/ee-gcc.exe

COPY ee-gcc-wrapper.sh /usr/local/bin/ee-gcc
RUN chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
