# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: borland-2.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Turbo C 2.0 (win16, DOSBox)" \
      org.opencontainers.image.description="Turbo C 2.0 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/tc20.tar.gz \
        "https://codeload.github.com/archaic-toolchains/tc20/tar.gz/refs/heads/main" \
    && echo "2eca4c26c1b30ce2bd7e61573eb9f40096994405fc173c28143f06a93da269d1  /tmp/tc20.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/tc20 \
    && tar xzf /tmp/tc20.tar.gz --strip-components=1 -C /opt/tc20 \
    && rm /tmp/tc20.tar.gz \
    && ls /opt/tc20/BIN/TCC.EXE \
    && chmod +x /usr/local/bin/tcc

COPY tc20-run.sh /usr/local/bin/tcc
RUN chmod +x /usr/local/bin/tcc

ENTRYPOINT ["/usr/local/bin/tcc"]

USER rebrew
