# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: borland-3.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Turbo C++ 3.1 (win16, DOSBox)" \
      org.opencontainers.image.description="Turbo C++ 3.1 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/tc31.tar.gz \
        "https://codeload.github.com/archaic-toolchains/tc31/tar.gz/refs/heads/main" \
    && echo "3d534741ebdc31ffdceb87db8de3b7d494ad5c912b7cd1a4f326b4a94d0c2ba1  /tmp/tc31.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/tc31 \
    && tar xzf /tmp/tc31.tar.gz --strip-components=1 -C /opt/tc31 \
    && rm /tmp/tc31.tar.gz \
    && ls /opt/tc31/BIN/TCC.EXE \
    && chmod +x /usr/local/bin/tcc

COPY tc16-run.sh /usr/local/bin/tcc
RUN chmod +x /usr/local/bin/tcc

ENTRYPOINT ["/usr/local/bin/tcc"]

USER rebrew
