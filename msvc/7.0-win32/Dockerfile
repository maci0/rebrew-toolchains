# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-7.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 7.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 7.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc700.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc700/tar.gz/refs/heads/master" \
    && echo "5f75462fb6134ad56c3ae28cf8b1e3b2869578d4171568b7a1fcdfb0bf97830b  /tmp/msvc700.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc7.0 \
    && tar xzf /tmp/msvc700.tar.gz --strip-components=1 -C /opt/msvc7.0 \
    && rm /tmp/msvc700.tar.gz \
    && ls /opt/msvc7.0/Vc7/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
