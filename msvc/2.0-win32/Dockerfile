# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-2.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 2.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 2.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc200.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc200/tar.gz/refs/heads/master" \
    && echo "0b058f103fe6b615987a85d518d7fd23389fab67c9df3cadfae22f5a70d5d000  /tmp/msvc200.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc2.0 \
    && tar xzf /tmp/msvc200.tar.gz --strip-components=1 -C /opt/msvc2.0 \
    && rm /tmp/msvc200.tar.gz \
    && ls /opt/msvc2.0/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
