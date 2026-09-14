# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-9.0-sp1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 9.0-sp1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 9.0-sp1 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc900_sp1.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc900_sp1/tar.gz/refs/heads/main" \
    && echo "33a66c779da39ab40518f24b75656f1f93cb1837a3d65a9b79188f41c2f2bd97  /tmp/msvc900_sp1.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc9.0-sp1 \
    && tar xzf /tmp/msvc900_sp1.tar.gz --strip-components=1 -C /opt/msvc9.0-sp1 \
    && rm /tmp/msvc900_sp1.tar.gz \
    && ls /opt/msvc9.0-sp1/VC/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
