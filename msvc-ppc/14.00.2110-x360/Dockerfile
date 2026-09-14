# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-ppc-14.00.2110

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC PPC 14.00.2110 (Xbox 360)" \
      org.opencontainers.image.description="MSVC for Xbox 360 (PowerPC, 14.00.2110.00, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251015.zip" \
    && echo "491cb62317c7f3669ac283ae159e82e3c97a5713b78299571ba4cf023dc7e95e  /tmp/compilers.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/msvc-ppc-14.00.2110 \
    && unzip -q /tmp/compilers.zip 'X360/14.00.2110/*' -d /tmp/x360 \
    && cp -a /tmp/x360/X360/14.00.2110/. /opt/msvc-ppc-14.00.2110/ \
    && rm -rf /tmp/x360 /tmp/compilers.zip \
    && ls /opt/msvc-ppc-14.00.2110/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
