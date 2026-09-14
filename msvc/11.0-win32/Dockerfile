# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-11.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 11.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 11.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc1100.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc1100/tar.gz/refs/heads/master" \
    && echo "adba1882eb076cb774b7a5d0f2b1067544da7cd2f0bf0b12f284361516cbc825  /tmp/msvc1100.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc11.0 \
    && tar xzf /tmp/msvc1100.tar.gz --strip-components=1 -C /opt/msvc11.0 \
    && rm /tmp/msvc1100.tar.gz \
    && ls /opt/msvc11.0/VC/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
