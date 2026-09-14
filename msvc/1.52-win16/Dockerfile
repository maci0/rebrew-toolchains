# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-1.52

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.52 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.52 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc152.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc152/tar.gz/refs/heads/main" \
    && echo "18fbdb547aa6a6cdbb3a77b00b5453f6fd9ae2b543a1c4842552643384e4711b  /tmp/msvc152.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc152 \
    && tar xzf /tmp/msvc152.tar.gz --strip-components=1 -C /opt/msvc152 \
    && rm /tmp/msvc152.tar.gz \
    && ls /opt/msvc152/BIN/CL.EXE \
    && chmod +x /usr/local/bin/cl16

COPY cl16-wrapper.sh /usr/local/bin/cl16
RUN chmod +x /usr/local/bin/cl16

ENTRYPOINT ["/usr/local/bin/cl16"]

USER rebrew
