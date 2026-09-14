# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-8.0-sp1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 8.0-sp1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 8.0-sp1 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc800_sp1.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc800_sp1/tar.gz/refs/heads/master" \
    && echo "9b53b515d79839c7404944c29cdae862d3a8c1ff0d0a27a202bfc37a31f587c5  /tmp/msvc800_sp1.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc8.0-sp1 \
    && tar xzf /tmp/msvc800_sp1.tar.gz --strip-components=1 -C /opt/msvc8.0-sp1 \
    && rm /tmp/msvc800_sp1.tar.gz \
    && ls /opt/msvc8.0-sp1/VC/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
