# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-7.0-sp1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 7.0-sp1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 7.0-sp1 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc700_sp1.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc700_sp1/tar.gz/refs/heads/master" \
    && echo "bc1300625c89e855e1c0160b43c6fe2576ad68426483bd73c3cde2682165ba8a  /tmp/msvc700_sp1.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc7.0-sp1 \
    && tar xzf /tmp/msvc700_sp1.tar.gz --strip-components=1 -C /opt/msvc7.0-sp1 \
    && rm /tmp/msvc700_sp1.tar.gz \
    && ls /opt/msvc7.0-sp1/Vc7/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
