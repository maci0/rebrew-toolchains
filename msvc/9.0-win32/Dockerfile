# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-9.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 9.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 9.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc900.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc900/tar.gz/refs/heads/master" \
    && echo "9121d184d9cb88c13b95d3d2e770c8d8ae9d2531a5d8ea90c53a14f765e3f904  /tmp/msvc900.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc9.0 \
    && tar xzf /tmp/msvc900.tar.gz --strip-components=1 -C /opt/msvc9.0 \
    && rm /tmp/msvc900.tar.gz \
    && ls /opt/msvc9.0/VC/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
