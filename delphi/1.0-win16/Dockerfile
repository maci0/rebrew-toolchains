# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: delphi-1.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Delphi 1.0 (win16, DOSBox)" \
      org.opencontainers.image.description="Delphi 1.0 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/delphi10.tar.gz \
        "https://codeload.github.com/archaic-toolchains/delphi10/tar.gz/refs/heads/main" \
    && echo "24cd23f0ef555f3582eda27b4bb655e17215366b556dfaabd9f2ba5daf61b55e  /tmp/delphi10.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/delphi10/DELPHI \
    && tar xzf /tmp/delphi10.tar.gz --strip-components=1 -C /opt/delphi10 \
    && rm /tmp/delphi10.tar.gz \
    && mv /opt/delphi10/delphi-lib /opt/delphi10/DELPHI/LIB \
    && ls /opt/delphi10/DCC.EXE \
    && chmod +x /usr/local/bin/dcc

COPY dcc-wrapper.sh /usr/local/bin/dcc
RUN chmod +x /usr/local/bin/dcc

ENTRYPOINT ["/usr/local/bin/dcc"]

USER rebrew
