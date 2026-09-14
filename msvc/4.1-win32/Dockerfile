# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-4.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 4.1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 4.1 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc410.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc410/tar.gz/refs/heads/master" \
    && echo "21486aecd108397bdced6e2cf6a5170a3cc30280a3eba97a4a8f92985a9cc5c4  /tmp/msvc410.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc4.1 \
    && tar xzf /tmp/msvc410.tar.gz --strip-components=1 -C /opt/msvc4.1 \
    && rm /tmp/msvc410.tar.gz \
    && ls /opt/msvc4.1/bin/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
