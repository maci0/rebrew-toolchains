# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-1.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.0 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.0 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc10.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc10/tar.gz/refs/heads/main" \
    && echo "4858446b957fe327fedbb3a511316bebc060b72f22557a47397b905522668ce9  /tmp/msvc10.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc10 \
    && tar xzf /tmp/msvc10.tar.gz --strip-components=1 -C /opt/msvc10 \
    && rm /tmp/msvc10.tar.gz \
    && ls /opt/msvc10/BIN/CL.EXE \
    && chmod +x /usr/local/bin/cl10

COPY cl10-wrapper.sh /usr/local/bin/cl10
RUN chmod +x /usr/local/bin/cl10

ENTRYPOINT ["/usr/local/bin/cl10"]

USER rebrew
