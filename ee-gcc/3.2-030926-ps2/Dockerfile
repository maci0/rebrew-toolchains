# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ee-gcc-3.2-030926

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 3.2-030926 (PS2)" \
      org.opencontainers.image.description="EE-GCC 3.2-030926 (PS2 Emotion Engine, native i386) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-030926.tar.gz" \
    && echo "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ee-gcc-3.2-030926 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/ee-gcc-3.2-030926 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-3.2-030926/bin/ee-gcc

COPY ee-gcc-wrapper.sh /usr/local/bin/ee-gcc
RUN chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
