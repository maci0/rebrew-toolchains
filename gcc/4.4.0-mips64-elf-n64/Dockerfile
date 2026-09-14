# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-4.4.0-mips64-elf

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 4.4.0 mips64-elf (N64)" \
      org.opencontainers.image.description="GCC 4.4.0 mips64-elf (N64) (N64, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmpfr6 libgmp10 libmpc3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/gcc-4.4.0-mips64-elf /tmp/tools && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/gcc440-mips64.tar.gz \
        "https://github.com/devwizard64/gcc4.4.0-mips64-elf/releases/download/latest/gcc4.4.0-mips64-elf.tar.gz" \
    && echo "d1a9815f730582ff65f8c14371c62436790655b20a21a5f8ee8b39b4fafa2f58  /tmp/tools/gcc440-mips64.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && tar xzf /tmp/tools/gcc440-mips64.tar.gz -C /opt/gcc-4.4.0-mips64-elf \
    && rm -rf /tmp/tools

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
