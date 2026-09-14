# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: borland-5.5

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 5.5 (win32, wine)" \
      org.opencontainers.image.description="Borland C++ 5.5 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc55.tar.gz \
        "https://codeload.github.com/archaic-toolchains/borlandc55/tar.gz/refs/heads/main" \
    && echo "e9319c3904303ca4424cfed855b17837d10aa9653a3d8e6329d2adb3326392b0  /tmp/bcc55.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/bcc55 \
    && tar xzf /tmp/bcc55.tar.gz --strip-components=1 -C /opt/bcc55 \
    && rm /tmp/bcc55.tar.gz \
    && ls /opt/bcc55/Bin/bcc32.exe

COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

USER rebrew
