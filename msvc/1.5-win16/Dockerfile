# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-1.5

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.5 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.5 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc15.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc15/tar.gz/refs/heads/main" \
    && echo "5cd1e4d9fd70fe97587fd3edfd0cebe3276e7b59ea5eb0848510f15c95d79aec  /tmp/msvc15.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc15 \
    && tar xzf /tmp/msvc15.tar.gz --strip-components=1 -C /opt/msvc15 \
    && rm /tmp/msvc15.tar.gz \
    && ls /opt/msvc15/BIN/CL.EXE \
    && chmod +x /usr/local/bin/cl15

COPY cl15-wrapper.sh /usr/local/bin/cl15
RUN chmod +x /usr/local/bin/cl15

ENTRYPOINT ["/usr/local/bin/cl15"]

USER rebrew
