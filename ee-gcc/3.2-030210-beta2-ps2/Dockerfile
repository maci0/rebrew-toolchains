# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ee-gcc-3.2-030210-beta2

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EE-GCC 3.2-030210-beta2 (PS2)" \
      org.opencontainers.image.description="EE-GCC 3.2-030210-beta2 (PS2 Emotion Engine, PE/x86_32) toolchain image"

ENV WINEPATH="Z:\\opt\\ee-gcc-3.2-030210-beta2\\dll"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-030210-beta2.tar.gz" \
    && echo "5244521973d3fa9712cc9f945e6e45c489d69d846ca6639b0c07c3e885a923a1  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ee-gcc-3.2-030210-beta2 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/ee-gcc-3.2-030210-beta2 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/ee-gcc-3.2-030210-beta2/bin/ee-gcc.exe

COPY ee-gcc-wrapper.sh /usr/local/bin/ee-gcc
RUN chmod +x /usr/local/bin/ee-gcc

ENTRYPOINT ["/usr/local/bin/ee-gcc"]

USER rebrew
