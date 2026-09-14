# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: borland-5.6

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 5.6 (win32, wine)" \
      org.opencontainers.image.description="Borland C++ 5.6 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc56.tar.gz \
        "https://codeload.github.com/earthsiege2/borland-cpp-ide/tar.gz/09bcecc81184" \
    && echo "8e5a93db99330b816646a14bdfa1c90d2e80a41810ce8c65f4942378cb621882  /tmp/bcc56.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/bcc56 \
    && tar xzf /tmp/bcc56.tar.gz --strip-components=1 -C /opt/bcc56 borland-cpp-ide-09bcecc81184/BIN borland-cpp-ide-09bcecc81184/INCLUDE borland-cpp-ide-09bcecc81184/LIB \
    && rm /tmp/bcc56.tar.gz \
    && ls /opt/bcc56/BIN/BCC32.EXE

COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

USER rebrew
