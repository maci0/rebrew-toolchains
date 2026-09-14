# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-5.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 5.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 5.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc500.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc500/tar.gz/refs/heads/master" \
    && echo "46745771c0805310212415450f097134f3871d1786434e86c080e0b8cb9a38fb  /tmp/msvc500.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc5.0 \
    && tar xzf /tmp/msvc500.tar.gz --strip-components=1 -C /opt/msvc5.0 \
    && rm /tmp/msvc500.tar.gz \
    && ls /opt/msvc5.0/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
