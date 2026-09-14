# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-win9x

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0 win9x repack (win32)" \
      org.opencontainers.image.description="MSVC 6.0 (Windows 9x preservation repack, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc6.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/msvcwin9x/msvc6.0.tar.gz" \
    && echo "5c81e9c2ab0ac5545022c1418a23392cb514db950cf6dcb1f48327270403fcd3  /tmp/msvc6.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/msvc6.0-win9x \
    && tar xzf /tmp/msvc6.tar.gz -C /opt/msvc6.0-win9x \
    && rm /tmp/msvc6.tar.gz \
    && ls /opt/msvc6.0-win9x/Bin/CL.EXE

COPY cc-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
