# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-4.2

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 4.2 (win32, wine)" \
      org.opencontainers.image.description="MSVC 4.2 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc420.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc420/tar.gz/refs/heads/master" \
    && echo "651db241202416be7e870ff8d98928179b94515068e7895008b8a82cb0b7001c  /tmp/msvc420.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc4.2 \
    && tar xzf /tmp/msvc420.tar.gz --strip-components=1 -C /opt/msvc4.2 \
    && rm /tmp/msvc420.tar.gz \
    && ls /opt/msvc4.2/bin/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
