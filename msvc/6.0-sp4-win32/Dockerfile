# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-sp4

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0-sp4 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp4 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600_sp4.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc600_sp4/tar.gz/refs/heads/main" \
    && echo "7aeb03f65858000bb6988a64cc066a4a2aec9fc591400db400ffe6fc99ae2dbc  /tmp/msvc600_sp4.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0-sp4 \
    && tar xzf /tmp/msvc600_sp4.tar.gz --strip-components=1 -C /opt/msvc6.0-sp4 \
    && rm /tmp/msvc600_sp4.tar.gz \
    && ls /opt/msvc6.0-sp4/VC98/bin/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
