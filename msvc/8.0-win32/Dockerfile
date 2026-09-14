# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-8.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 8.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 8.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc800.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc800/tar.gz/refs/heads/master" \
    && echo "ab819164ebd9e9d367c1178a86eb9c3337b1a8d85d1357322a3252b63ad64453  /tmp/msvc800.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc8.0 \
    && tar xzf /tmp/msvc800.tar.gz --strip-components=1 -C /opt/msvc8.0 \
    && rm /tmp/msvc800.tar.gz \
    && ls /opt/msvc8.0/VC/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
