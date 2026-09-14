# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600/tar.gz/refs/heads/master" \
    && echo "19b72020c8225f91d7345b16aa0acf1b31a4608ae1299693021491e7338d0ee8  /tmp/msvc600.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0 \
    && tar xzf /tmp/msvc600.tar.gz --strip-components=1 -C /opt/msvc6.0 \
    && rm /tmp/msvc600.tar.gz \
    && ls /opt/msvc6.0/VC98/Bin/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
